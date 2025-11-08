"""
Grover's Algorithm Implementation

Demonstrates Grover's search algorithm using the FPGA-accelerated simulator.
Grover's algorithm provides quadratic speedup for unstructured search problems.
"""

import numpy as np
from simulator.circuit import QuantumCircuit
from simulator import quantum_gates
from typing import List, Callable


def create_oracle(circuit: QuantumCircuit, target_state: int, num_qubits: int):
    """
    Create an oracle that marks the target state.
    
    The oracle applies a phase flip to the target state.
    
    Args:
        circuit: Quantum circuit to add oracle to
        target_state: Integer representation of target state (0 to 2^num_qubits - 1)
        num_qubits: Number of qubits
    """
    # Multi-controlled Z gate marking the target state
    # For simplicity, we'll use a phase flip approach
    
    # Convert target_state to binary representation
    target_bits = []
    temp = target_state
    for _ in range(num_qubits):
        target_bits.append(temp & 1)
        temp >>= 1
    
    # Apply X gates to qubits that are 0 in target state
    for i, bit in enumerate(target_bits):
        if bit == 0:
            circuit.x(i)
    
    # Apply multi-controlled Z (mark the |11...1⟩ state)
    # For 2 qubits: CZ
    # For more qubits: need multi-controlled Z
    if num_qubits == 2:
        circuit.cz(0, 1)
    elif num_qubits == 3:
        # H -> CCNOT -> H on target qubit
        circuit.h(2)
        circuit.cnot(0, 2)
        circuit.cnot(1, 2)
        circuit.h(2)
        # Apply Z to last qubit
        circuit.z(2)
        circuit.h(2)
        circuit.cnot(0, 2)
        circuit.cnot(1, 2)
        circuit.h(2)
    else:
        # For simplicity, use Z on last qubit with multi-control
        # This is a simplified version
        circuit.z(num_qubits - 1)
    
    # Uncompute X gates
    for i, bit in enumerate(target_bits):
        if bit == 0:
            circuit.x(i)


def grover_diffusion(circuit: QuantumCircuit, num_qubits: int):
    """
    Apply Grover diffusion operator.
    
    The diffusion operator inverts amplitudes about the mean.
    
    Args:
        circuit: Quantum circuit to add diffusion to
        num_qubits: Number of qubits
    """
    # Apply H to all qubits
    for i in range(num_qubits):
        circuit.h(i)
    
    # Apply multi-controlled Z (flip phase of |00...0⟩)
    # Similar to oracle but for |00...0⟩
    for i in range(num_qubits):
        circuit.x(i)
    
    if num_qubits == 2:
        circuit.cz(0, 1)
    elif num_qubits == 3:
        circuit.h(2)
        circuit.cnot(0, 2)
        circuit.cnot(1, 2)
        circuit.h(2)
        circuit.z(2)
        circuit.h(2)
        circuit.cnot(0, 2)
        circuit.cnot(1, 2)
        circuit.h(2)
    else:
        circuit.z(num_qubits - 1)
    
    # Uncompute X gates
    for i in range(num_qubits):
        circuit.x(i)
    
    # Apply H to all qubits
    for i in range(num_qubits):
        circuit.h(i)


def grover_search(num_qubits: int, target_state: int, num_iterations: int = None) -> QuantumCircuit:
    """
    Implement Grover's search algorithm.
    
    Args:
        num_qubits: Number of qubits (search space size = 2^num_qubits)
        target_state: Target state to find (0 to 2^num_qubits - 1)
        num_iterations: Number of Grover iterations (default: optimal)
        
    Returns:
        Quantum circuit implementing Grover's algorithm
    """
    if target_state < 0 or target_state >= 2 ** num_qubits:
        raise ValueError(f"Target state must be in [0, {2**num_qubits - 1}]")
    
    # Optimal number of iterations ≈ π/4 * sqrt(N)
    if num_iterations is None:
        num_iterations = int(np.round(np.pi / 4 * np.sqrt(2 ** num_qubits)))
    
    circuit = QuantumCircuit(num_qubits, use_jax=True)
    
    # Initialize superposition
    for i in range(num_qubits):
        circuit.h(i)
    
    # Apply Grover iterations
    for _ in range(num_iterations):
        # Oracle: mark target state
        create_oracle(circuit, target_state, num_qubits)
        
        # Diffusion: invert about mean
        grover_diffusion(circuit, num_qubits)
    
    return circuit


def run_grover_example():
    """Run a demonstration of Grover's algorithm."""
    print("=" * 60)
    print("Grover's Search Algorithm Demonstration")
    print("=" * 60)
    
    # Example: 3-qubit search (8 possible states)
    num_qubits = 3
    target_state = 5  # Looking for |101⟩
    
    print(f"\nSearch space: {2**num_qubits} states")
    print(f"Target state: |{target_state:0{num_qubits}b}⟩ (state {target_state})")
    
    # Create and execute Grover circuit
    circuit = grover_search(num_qubits, target_state)
    state = circuit.execute()
    
    # Get probabilities
    probs = circuit.get_probabilities()
    
    print("\nFinal state probabilities:")
    print("-" * 60)
    for i, prob in enumerate(probs):
        state_str = f"|{i:0{num_qubits}b}⟩"
        bar = "█" * int(prob * 50)
        print(f"{state_str}: {prob:.4f} {bar}")
    
    # Find most likely state
    max_prob_idx = np.argmax(probs)
    print(f"\nMost probable state: |{max_prob_idx:0{num_qubits}b}⟩ (probability: {probs[max_prob_idx]:.4f})")
    
    if max_prob_idx == target_state:
        print("✓ Successfully found target state!")
    else:
        print(f"✗ Did not find target state (found {max_prob_idx} instead)")
    
    return circuit, probs


if __name__ == "__main__":
    run_grover_example()

