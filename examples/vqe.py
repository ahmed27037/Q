"""
Variational Quantum Eigensolver (VQE) Implementation

Demonstrates the VQE algorithm for finding ground states of quantum Hamiltonians
using the FPGA-accelerated simulator.
"""

import numpy as np
from simulator.circuit import QuantumCircuit
from simulator import quantum_gates
from scipy.optimize import minimize
from typing import Callable, Tuple


def create_ansatz(circuit: QuantumCircuit, params: np.ndarray, num_layers: int = 2):
    """
    Create a parameterized ansatz (variational form).
    
    Uses alternating layers of rotation gates and entangling gates.
    
    Args:
        circuit: Quantum circuit to build ansatz on
        params: Parameter array (flattened)
        num_layers: Number of ansatz layers
    """
    num_qubits = circuit.num_qubits
    params_per_layer = 3 * num_qubits  # RY, RZ, RY per qubit
    
    param_idx = 0
    
    for layer in range(num_layers):
        # Rotation layer
        for q in range(num_qubits):
            if param_idx < len(params):
                circuit.ry(q, params[param_idx])
                param_idx += 1
            if param_idx < len(params):
                circuit.rz(q, params[param_idx])
                param_idx += 1
            if param_idx < len(params):
                circuit.ry(q, params[param_idx])
                param_idx += 1
        
        # Entangling layer
        if layer < num_layers - 1:  # No entangling after last layer
            for q in range(num_qubits - 1):
                circuit.cnot(q, q + 1)


def compute_expectation_value(circuit: QuantumCircuit, hamiltonian: np.ndarray) -> float:
    """
    Compute expectation value <ψ|H|ψ>.
    
    Args:
        circuit: Quantum circuit (state)
        hamiltonian: Hamiltonian matrix
        
    Returns:
        Expectation value
    """
    return circuit.get_expectation_value(hamiltonian)


def vqe_objective(params: np.ndarray, hamiltonian: np.ndarray, num_qubits: int, 
                  num_layers: int) -> float:
    """
    Objective function for VQE optimization.
    
    Args:
        params: Variational parameters
        hamiltonian: Hamiltonian matrix
        num_qubits: Number of qubits
        num_layers: Number of ansatz layers
        
    Returns:
        Energy (expectation value)
    """
    circuit = QuantumCircuit(num_qubits, use_jax=True)
    create_ansatz(circuit, params, num_layers)
    circuit.execute()
    
    energy = compute_expectation_value(circuit, hamiltonian)
    return energy


def run_vqe(hamiltonian: np.ndarray, num_qubits: int, num_layers: int = 2, 
            initial_params: np.ndarray = None) -> Tuple[float, np.ndarray, dict]:
    """
    Run VQE to find ground state energy.
    
    Args:
        hamiltonian: Hamiltonian matrix (2^num_qubits × 2^num_qubits)
        num_qubits: Number of qubits
        num_layers: Number of ansatz layers
        initial_params: Initial parameters (random if None)
        
    Returns:
        Tuple of (ground_energy, optimal_params, optimization_info)
    """
    # Initialize parameters
    params_per_layer = 3 * num_qubits
    num_params = num_layers * params_per_layer
    
    if initial_params is None:
        initial_params = np.random.uniform(0, 2 * np.pi, num_params)
    
    # Optimize
    result = minimize(
        vqe_objective,
        initial_params,
        args=(hamiltonian, num_qubits, num_layers),
        method='L-BFGS-B',
        options={'maxiter': 100}
    )
    
    # Get exact ground state for comparison
    eigenvals, eigenvecs = np.linalg.eigh(hamiltonian)
    exact_ground_energy = eigenvals[0]
    
    return result.fun, result.x, {
        'exact_energy': exact_ground_energy,
        'iterations': result.nit,
        'success': result.success
    }


def create_heisenberg_hamiltonian(num_qubits: int, J: float = 1.0, h: float = 0.5) -> np.ndarray:
    """
    Create a Heisenberg model Hamiltonian.
    
    H = -J Σ (X_i X_{i+1} + Y_i Y_{i+1} + Z_i Z_{i+1}) - h Σ Z_i
    
    Args:
        num_qubits: Number of qubits
        J: Coupling strength
        h: Magnetic field strength
        
    Returns:
        Hamiltonian matrix
    """
    dim = 2 ** num_qubits
    hamiltonian = np.zeros((dim, dim), dtype=np.complex128)
    
    # Pauli matrices
    X = quantum_gates.X()
    Y = quantum_gates.Y()
    Z = quantum_gates.Z()
    I = quantum_gates.I()
    
    # Interaction terms
    for i in range(num_qubits - 1):
        # XX term
        xx_term = I
        for j in range(num_qubits):
            if j == i:
                xx_term = np.kron(xx_term, X)
            elif j == i + 1:
                xx_term = np.kron(xx_term, X)
            else:
                xx_term = np.kron(xx_term, I)
        hamiltonian -= J * xx_term
        
        # YY term
        yy_term = I
        for j in range(num_qubits):
            if j == i:
                yy_term = np.kron(yy_term, Y)
            elif j == i + 1:
                yy_term = np.kron(yy_term, Y)
            else:
                yy_term = np.kron(yy_term, I)
        hamiltonian -= J * yy_term
        
        # ZZ term
        zz_term = I
        for j in range(num_qubits):
            if j == i:
                zz_term = np.kron(zz_term, Z)
            elif j == i + 1:
                zz_term = np.kron(zz_term, Z)
            else:
                zz_term = np.kron(zz_term, I)
        hamiltonian -= J * zz_term
    
    # Magnetic field terms
    for i in range(num_qubits):
        z_term = I
        for j in range(num_qubits):
            if j == i:
                z_term = np.kron(z_term, Z)
            else:
                z_term = np.kron(z_term, I)
        hamiltonian -= h * z_term
    
    return hamiltonian


def run_vqe_example():
    """Run a demonstration of VQE."""
    print("=" * 60)
    print("Variational Quantum Eigensolver (VQE) Demonstration")
    print("=" * 60)
    
    # Example: 2-qubit Heisenberg model
    num_qubits = 2
    num_layers = 2
    
    print(f"\nSystem: {num_qubits}-qubit Heisenberg model")
    print(f"Ansatz: {num_layers} layers")
    
    # Create Hamiltonian
    hamiltonian = create_heisenberg_hamiltonian(num_qubits, J=1.0, h=0.5)
    
    # Get exact ground state
    eigenvals, eigenvecs = np.linalg.eigh(hamiltonian)
    exact_energy = eigenvals[0]
    print(f"\nExact ground state energy: {exact_energy:.6f}")
    
    # Run VQE
    print("\nRunning VQE optimization...")
    vqe_energy, optimal_params, info = run_vqe(
        hamiltonian, 
        num_qubits, 
        num_layers=num_layers,
        initial_params=np.random.uniform(0, 2 * np.pi, num_layers * 3 * num_qubits)
    )
    
    print(f"VQE ground state energy: {vqe_energy:.6f}")
    print(f"Error: {abs(vqe_energy - exact_energy):.6f}")
    print(f"Optimization iterations: {info['iterations']}")
    print(f"Success: {info['success']}")
    
    # Reconstruct final state
    circuit = QuantumCircuit(num_qubits, use_jax=True)
    create_ansatz(circuit, optimal_params, num_layers)
    final_state = circuit.execute()
    
    print(f"\nFinal statevector:")
    for i, amp in enumerate(final_state):
        print(f"  |{i:0{num_qubits}b}⟩: {amp:.4f}")
    
    return vqe_energy, optimal_params, info


if __name__ == "__main__":
    run_vqe_example()

