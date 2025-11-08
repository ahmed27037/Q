"""
FPGA-Accelerated Quantum Circuit Simulator

A high-performance quantum circuit simulator using optimized parallel processing
to simulate FPGA-like acceleration for quantum computations.
"""

from .circuit import QuantumCircuit
from .fpga_simulator import FPGASimulator
from .quantum_gates import (
    I,
    X,
    Y,
    Z,
    H,
    S,
    T,
    CNOT,
    CZ,
    SWAP,
    RX,
    RY,
    RZ,
    CRX,
    CRY,
    CRZ,
)

__version__ = "0.1.0"
__all__ = [
    "QuantumCircuit",
    "FPGASimulator",
    "I",
    "X",
    "Y",
    "Z",
    "H",
    "S",
    "T",
    "CNOT",
    "CZ",
    "SWAP",
    "RX",
    "RY",
    "RZ",
    "CRX",
    "CRY",
    "CRZ",
]

