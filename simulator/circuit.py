"""
Quantum Circuit Representation and Execution Engine

This module provides a high-level interface for building and executing quantum circuits
using the FPGA-accelerated simulator.
"""

import numpy as np
from typing import List, Tuple, Optional, Callable, Union
from .fpga_simulator import FPGASimulator
from . import quantum_gates


class QuantumCircuit:
    """
    High-level quantum circuit representation.
    
    This class provides an intuitive interface for building quantum circuits
    and executing them on the FPGA simulator.
    """
    
    def __init__(self, num_qubits: int, use_jax: bool = True):
        """
        Initialize a quantum circuit.
        
        Args:
            num_qubits: Number of qubits in the circuit
            use_jax: Whether to use JAX acceleration (default: True)
        """
        self.num_qubits = num_qubits
        self.simulator = FPGASimulator(num_qubits, use_jax=use_jax)
        self.gates = []  # List of (gate_matrix, qubit_indices) tuples
        self.measurements = []  # List of qubit indices to measure
    
    def apply(self, gate: Union[np.ndarray, Callable], *qubits: int, **kwargs):
        """
        Apply a quantum gate to specified qubits.
        
        Args:
            gate: Gate matrix (np.ndarray) or gate function (e.g., H, CNOT)
            *qubits: Qubit indices the gate acts on
            **kwargs: Additional parameters for parameterized gates (e.g., theta for RX)
            
        Examples:
            circuit.apply(H, 0)
            circuit.apply(CNOT, 0, 1)
            circuit.apply(RX, 0, theta=np.pi/2)
        """
        if callable(gate):
            # Gate is a function, call it with kwargs
            gate_matrix = gate(**kwargs)
        elif isinstance(gate, np.ndarray):
            gate_matrix = gate
        else:
            raise TypeError(f"Gate must be a callable or numpy array, got {type(gate)}")
        
        qubit_list = list(qubits)
        
        # Validate qubit indices
        for q in qubit_list:
            if q < 0 or q >= self.num_qubits:
                raise ValueError(f"Qubit index {q} out of range [0, {self.num_qubits})")
        
        # Store gate for later execution
        self.gates.append((gate_matrix, qubit_list))
    
    def h(self, qubit: int):
        """Apply Hadamard gate."""
        self.apply(quantum_gates.H, qubit)
    
    def x(self, qubit: int):
        """Apply Pauli-X gate."""
        self.apply(quantum_gates.X, qubit)
    
    def y(self, qubit: int):
        """Apply Pauli-Y gate."""
        self.apply(quantum_gates.Y, qubit)
    
    def z(self, qubit: int):
        """Apply Pauli-Z gate."""
        self.apply(quantum_gates.Z, qubit)
    
    def cnot(self, control: int, target: int):
        """Apply CNOT gate."""
        self.apply(quantum_gates.CNOT, control, target)
    
    def cz(self, control: int, target: int):
        """Apply controlled-Z gate."""
        self.apply(quantum_gates.CZ, control, target)
    
    def swap(self, qubit1: int, qubit2: int):
        """Apply SWAP gate."""
        self.apply(quantum_gates.SWAP, qubit1, qubit2)
    
    def rx(self, qubit: int, theta: float):
        """Apply rotation around X-axis."""
        self.apply(quantum_gates.RX, qubit, theta=theta)
    
    def ry(self, qubit: int, theta: float):
        """Apply rotation around Y-axis."""
        self.apply(quantum_gates.RY, qubit, theta=theta)
    
    def rz(self, qubit: int, theta: float):
        """Apply rotation around Z-axis."""
        self.apply(quantum_gates.RZ, qubit, theta=theta)
    
    def crx(self, control: int, target: int, theta: float):
        """Apply controlled-RX gate."""
        self.apply(quantum_gates.CRX, control, target, theta=theta)
    
    def cry(self, control: int, target: int, theta: float):
        """Apply controlled-RY gate."""
        self.apply(quantum_gates.CRY, control, target, theta=theta)
    
    def crz(self, control: int, target: int, theta: float):
        """Apply controlled-RZ gate."""
        self.apply(quantum_gates.CRZ, control, target, theta=theta)
    
    def execute(self, reset: bool = True) -> np.ndarray:
        """
        Execute the circuit and return the final statevector.
        
        Args:
            reset: Whether to reset the simulator before execution (default: True)
            
        Returns:
            Final statevector as numpy array
        """
        if reset:
            self.simulator.reset()
        
        # Apply all gates in sequence
        for gate_matrix, qubit_indices in self.gates:
            self.simulator.apply_gate(gate_matrix, qubit_indices)
        
        return self.simulator.get_statevector()
    
    def measure(self, qubit: int) -> int:
        """
        Measure a qubit and collapse the statevector.
        
        Args:
            qubit: Index of qubit to measure
            
        Returns:
            Measurement result (0 or 1)
        """
        if qubit < 0 or qubit >= self.num_qubits:
            raise ValueError(f"Qubit index {qubit} out of range [0, {self.num_qubits})")
        
        # Execute circuit if not already executed
        if len(self.gates) > 0 and not hasattr(self, '_executed'):
            self.execute(reset=True)
            self._executed = True
        
        result = self.simulator.measure(qubit)
        self.measurements.append((qubit, result))
        return result
    
    def measure_all(self) -> List[int]:
        """
        Measure all qubits and return results.
        
        Returns:
            List of measurement results
        """
        results = []
        for qubit in range(self.num_qubits):
            results.append(self.measure(qubit))
        return results
    
    def get_probabilities(self) -> np.ndarray:
        """
        Get measurement probabilities for all basis states.
        
        Returns:
            Array of probabilities
        """
        return self.simulator.get_probabilities()
    
    def get_expectation_value(self, observable: np.ndarray) -> float:
        """
        Calculate expectation value of an observable.
        
        Args:
            observable: Hermitian operator matrix
            
        Returns:
            Expectation value
        """
        return self.simulator.get_expectation_value(observable)
    
    def reset(self):
        """Reset the circuit (clear gates and measurements)."""
        self.gates = []
        self.measurements = []
        self.simulator.reset()
        if hasattr(self, '_executed'):
            delattr(self, '_executed')
    
    def depth(self) -> int:
        """Return the depth (number of layers) of the circuit."""
        if not self.gates:
            return 0
        
        # Simple depth calculation: count gates
        # More sophisticated version would group parallel gates
        return len(self.gates)
    
    def __str__(self) -> str:
        """String representation of the circuit."""
        return f"QuantumCircuit(num_qubits={self.num_qubits}, num_gates={len(self.gates)})"
    
    def __repr__(self) -> str:
        return self.__str__()

