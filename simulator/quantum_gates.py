"""
Optimized Quantum Gate Implementations

This module provides quantum gate matrices optimized for FPGA-like parallel processing.
All gates are designed to work efficiently with the FPGASimulator.
"""

import numpy as np
import jax.numpy as jnp
from typing import Union, Optional


# Single-qubit gates
def I() -> np.ndarray:
    """Identity gate."""
    return np.array([[1, 0], [0, 1]], dtype=np.complex128)


def X() -> np.ndarray:
    """Pauli-X (NOT) gate."""
    return np.array([[0, 1], [1, 0]], dtype=np.complex128)


def Y() -> np.ndarray:
    """Pauli-Y gate."""
    return np.array([[0, -1j], [1j, 0]], dtype=np.complex128)


def Z() -> np.ndarray:
    """Pauli-Z gate."""
    return np.array([[1, 0], [0, -1]], dtype=np.complex128)


def H() -> np.ndarray:
    """Hadamard gate."""
    return (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=np.complex128)


def S() -> np.ndarray:
    """Phase gate (S = √Z)."""
    return np.array([[1, 0], [0, 1j]], dtype=np.complex128)


def T() -> np.ndarray:
    """T gate (π/8 gate)."""
    return np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=np.complex128)


def RX(theta: float) -> np.ndarray:
    """Rotation around X-axis."""
    c = np.cos(theta / 2)
    s = -1j * np.sin(theta / 2)
    return np.array([[c, s], [s, c]], dtype=np.complex128)


def RY(theta: float) -> np.ndarray:
    """Rotation around Y-axis."""
    c = np.cos(theta / 2)
    s = np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=np.complex128)


def RZ(theta: float) -> np.ndarray:
    """Rotation around Z-axis."""
    return np.array([[np.exp(-1j * theta / 2), 0], 
                     [0, np.exp(1j * theta / 2)]], dtype=np.complex128)


# Two-qubit gates
def CNOT() -> np.ndarray:
    """Controlled-NOT gate (control on first qubit, target on second)."""
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0]
    ], dtype=np.complex128)


def CZ() -> np.ndarray:
    """Controlled-Z gate."""
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, -1]
    ], dtype=np.complex128)


def SWAP() -> np.ndarray:
    """SWAP gate."""
    return np.array([
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1]
    ], dtype=np.complex128)


def CRX(theta: float) -> np.ndarray:
    """Controlled-RX gate."""
    c = np.cos(theta / 2)
    s = -1j * np.sin(theta / 2)
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, c, s],
        [0, 0, s, c]
    ], dtype=np.complex128)


def CRY(theta: float) -> np.ndarray:
    """Controlled-RY gate."""
    c = np.cos(theta / 2)
    s = np.sin(theta / 2)
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, c, -s],
        [0, 0, s, c]
    ], dtype=np.complex128)


def CRZ(theta: float) -> np.ndarray:
    """Controlled-RZ gate."""
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, np.exp(-1j * theta / 2), 0],
        [0, 0, 0, np.exp(1j * theta / 2)]
    ], dtype=np.complex128)


# Helper function to create multi-qubit gates
def tensor_product(*gates: np.ndarray) -> np.ndarray:
    """
    Compute tensor product of multiple gates.
    
    This simulates FPGA's parallel multiplication units working on
    different qubit subspaces simultaneously.
    """
    result = gates[0]
    for gate in gates[1:]:
        result = np.kron(result, gate)
    return result


def create_controlled_gate(gate: np.ndarray, num_control_qubits: int = 1) -> np.ndarray:
    """
    Create a controlled version of a gate.
    
    Args:
        gate: The gate to make controlled
        num_control_qubits: Number of control qubits (default: 1)
        
    Returns:
        Controlled gate matrix
    """
    gate_size = gate.shape[0]
    total_size = 2 ** (num_control_qubits + int(np.log2(gate_size)))
    
    result = np.eye(total_size, dtype=np.complex128)
    
    # Set the controlled block
    control_mask = (1 << num_control_qubits) - 1  # All control qubits set to 1
    target_start = control_mask << int(np.log2(gate_size))
    
    for i in range(gate_size):
        for j in range(gate_size):
            idx_i = target_start | i
            idx_j = target_start | j
            result[idx_i, idx_j] = gate[i, j]
    
    return result


# Optimized gate application for common patterns
class GateOptimizer:
    """
    Optimizer for gate sequences that can be merged or optimized.
    This simulates FPGA's ability to optimize gate sequences.
    """
    
    @staticmethod
    def optimize_pauli_sequence(gates: list) -> np.ndarray:
        """
        Optimize a sequence of Pauli gates.
        X^2 = I, Y^2 = I, Z^2 = I, etc.
        """
        result = I()
        for gate in gates:
            result = result @ gate
        return result
    
    @staticmethod
    def merge_rotations(rotations: list) -> np.ndarray:
        """
        Merge consecutive rotations around the same axis.
        """
        # Implementation would merge RZ(θ1) RZ(θ2) = RZ(θ1 + θ2)
        # This is a simplified version
        result = I()
        for rot in rotations:
            result = result @ rot
        return result

