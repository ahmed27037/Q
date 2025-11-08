"""
PennyLane Device Plugin for FPGA Simulator

This module provides a PennyLane device interface that uses the FPGA-accelerated
simulator as the backend. This enables seamless integration with PennyLane's
ecosystem and Xanadu's quantum computing tools.
"""

import numpy as np
import pennylane as qml
from typing import Sequence, Union
from simulator.circuit import QuantumCircuit
from simulator import quantum_gates


class FPGADevice(qml.Device):
    """
    PennyLane device using the FPGA-accelerated quantum simulator.
    
    This device enables PennyLane circuits to run on our FPGA simulator,
    demonstrating integration with Xanadu's quantum computing ecosystem.
    """
    
    name = "FPGA Simulator"
    short_name = "fpga.simulator"
    version = "0.1.0"
    author = "Quantum FPGA Projects"
    
    operations = {
        "PauliX", "PauliY", "PauliZ", "Hadamard",
        "S", "T", "SX", "CNOT", "CZ", "SWAP",
        "RX", "RY", "RZ", "PhaseShift",
        "CRX", "CRY", "CRZ", "CRot",
        "Rot", "MultiRZ", "IsingXX", "IsingYY", "IsingZZ"
    }
    
    observables = {
        "PauliX", "PauliY", "PauliZ",
        "Identity", "Hadamard",
        "Hermitian", "Projector"
    }
    
    def __init__(self, wires, shots=None, use_jax=True, **kwargs):
        """
        Initialize the FPGA device.
        
        Args:
            wires: Number of wires (qubits) or list of wire labels
            shots: Number of shots for measurements (None for exact statevector)
            use_jax: Whether to use JAX acceleration
            **kwargs: Additional arguments
        """
        if isinstance(wires, int):
            wires = list(range(wires))
        elif isinstance(wires, list):
            wires = wires
        else:
            raise ValueError(f"wires must be int or list, got {type(wires)}")
        
        super().__init__(wires=wires, shots=shots, **kwargs)
        
        self.num_qubits = len(wires)
        self.use_jax = use_jax
        self.circuit = None
        self.reset()
    
    def reset(self):
        """Reset the device."""
        self.circuit = QuantumCircuit(self.num_qubits, use_jax=self.use_jax)
    
    def _wire_to_index(self, wire):
        """Convert wire label to qubit index."""
        if isinstance(wire, int):
            return wire
        elif isinstance(wire, qml.wires.Wire):
            return self.wires.index(wire)
        else:
            return self.wires.index(wire)
    
    def apply(self, operations, rotations=None, **kwargs):
        """
        Apply quantum operations to the device.
        
        Args:
            operations: List of operations to apply
            rotations: List of rotations for observables
            **kwargs: Additional arguments
        """
        for op in operations:
            self._apply_operation(op)
    
    def _apply_operation(self, operation):
        """Apply a single operation to the circuit."""
        op_name = operation.name
        wires = [self._wire_to_index(w) for w in operation.wires]
        
        # Map PennyLane operations to our gates
        if op_name == "PauliX":
            self.circuit.x(wires[0])
        elif op_name == "PauliY":
            self.circuit.y(wires[0])
        elif op_name == "PauliZ":
            self.circuit.z(wires[0])
        elif op_name == "Hadamard":
            self.circuit.h(wires[0])
        elif op_name == "S":
            self.circuit.apply(quantum_gates.S, wires[0])
        elif op_name == "T":
            self.circuit.apply(quantum_gates.T, wires[0])
        elif op_name == "SX":
            # SX = (X + Y) / sqrt(2)
            self.circuit.apply(quantum_gates.S, wires[0])
            self.circuit.h(wires[0])
            self.circuit.apply(quantum_gates.S, wires[0])
        elif op_name == "CNOT":
            self.circuit.cnot(wires[0], wires[1])
        elif op_name == "CZ":
            self.circuit.cz(wires[0], wires[1])
        elif op_name == "SWAP":
            self.circuit.swap(wires[0], wires[1])
        elif op_name == "RX":
            self.circuit.rx(wires[0], operation.parameters[0])
        elif op_name == "RY":
            self.circuit.ry(wires[0], operation.parameters[0])
        elif op_name == "RZ":
            self.circuit.rz(wires[0], operation.parameters[0])
        elif op_name == "PhaseShift":
            # PhaseShift(phi) = RZ(phi)
            self.circuit.rz(wires[0], operation.parameters[0])
        elif op_name == "CRX":
            self.circuit.crx(wires[0], wires[1], operation.parameters[0])
        elif op_name == "CRY":
            self.circuit.cry(wires[0], wires[1], operation.parameters[0])
        elif op_name == "CRZ":
            self.circuit.crz(wires[0], wires[1], operation.parameters[0])
        elif op_name == "Rot":
            # Rot(phi, theta, omega) = RZ(omega) RY(theta) RZ(phi)
            phi, theta, omega = operation.parameters
            self.circuit.rz(wires[0], phi)
            self.circuit.ry(wires[0], theta)
            self.circuit.rz(wires[0], omega)
        elif op_name == "CRot":
            # Controlled rotation
            phi, theta, omega = operation.parameters
            self.circuit.rz(wires[1], phi)
            self.circuit.cry(wires[0], wires[1], theta)
            self.circuit.rz(wires[1], omega)
        elif op_name == "MultiRZ":
            # MultiRZ(theta) = exp(-i*theta/2 * Z1 ⊗ Z2 ⊗ ...)
            theta = operation.parameters[0]
            # For 2 qubits: apply CZ then phase
            if len(wires) == 2:
                self.circuit.rz(wires[0], theta / 2)
                self.circuit.cnot(wires[0], wires[1])
                self.circuit.rz(wires[1], -theta / 2)
                self.circuit.cnot(wires[0], wires[1])
                self.circuit.rz(wires[0], theta / 2)
        elif op_name == "IsingXX":
            # IsingXX(phi) = exp(-i*phi/2 * X ⊗ X)
            phi = operation.parameters[0]
            self.circuit.h(wires[0])
            self.circuit.h(wires[1])
            self.circuit.cnot(wires[0], wires[1])
            self.circuit.rz(wires[1], -phi)
            self.circuit.cnot(wires[0], wires[1])
            self.circuit.h(wires[0])
            self.circuit.h(wires[1])
        elif op_name == "IsingYY":
            # IsingYY(phi) = exp(-i*phi/2 * Y ⊗ Y)
            phi = operation.parameters[0]
            self.circuit.ry(wires[0], -np.pi / 2)
            self.circuit.ry(wires[1], -np.pi / 2)
            self.circuit.cnot(wires[0], wires[1])
            self.circuit.rz(wires[1], -phi)
            self.circuit.cnot(wires[0], wires[1])
            self.circuit.ry(wires[0], np.pi / 2)
            self.circuit.ry(wires[1], np.pi / 2)
        elif op_name == "IsingZZ":
            # IsingZZ(phi) = exp(-i*phi/2 * Z ⊗ Z)
            phi = operation.parameters[0]
            self.circuit.cnot(wires[0], wires[1])
            self.circuit.rz(wires[1], -phi)
            self.circuit.cnot(wires[0], wires[1])
        else:
            raise NotImplementedError(f"Operation {op_name} not implemented")
    
    def execute(self, circuit, **kwargs):
        """
        Execute a quantum circuit.
        
        Args:
            circuit: Quantum function or tape
            **kwargs: Additional arguments
            
        Returns:
            Measurement results
        """
        # Execute the circuit
        self.circuit.execute()
        
        # Get measurement results
        if self.shots is None:
            # Return statevector
            return self.circuit.get_statevector()
        else:
            # Sample from probabilities
            probs = self.circuit.get_probabilities()
            samples = np.random.choice(len(probs), size=self.shots, p=probs)
            return samples
    
    def expval(self, observable, **kwargs):
        """
        Compute expectation value of an observable.
        
        Args:
            observable: Observable to measure
            **kwargs: Additional arguments
            
        Returns:
            Expectation value
        """
        # Execute circuit first
        self.circuit.execute()
        
        # Get observable matrix
        if isinstance(observable, qml.operation.Observable):
            obs_matrix = self._get_observable_matrix(observable)
        else:
            obs_matrix = observable
        
        return self.circuit.get_expectation_value(obs_matrix)
    
    def _get_observable_matrix(self, observable):
        """Convert PennyLane observable to matrix."""
        op_name = observable.name
        wires = [self._wire_to_index(w) for w in observable.wires]
        
        if op_name == "PauliX":
            op = quantum_gates.X()
        elif op_name == "PauliY":
            op = quantum_gates.Y()
        elif op_name == "PauliZ":
            op = quantum_gates.Z()
        elif op_name == "Identity":
            op = quantum_gates.I()
        elif op_name == "Hadamard":
            op = quantum_gates.H()
        elif op_name == "Hermitian":
            op = observable.parameters[0]
        elif op_name == "Projector":
            # Projector onto specific state
            state = observable.parameters[0]
            dim = 2 ** len(wires)
            op = np.zeros((dim, dim), dtype=np.complex128)
            op[state, state] = 1.0
        else:
            raise NotImplementedError(f"Observable {op_name} not implemented")
        
        # Expand to full Hilbert space if needed
        if len(wires) == 1 and self.num_qubits > 1:
            # Tensor product with identities
            full_op = quantum_gates.I()
            for i in range(self.num_qubits):
                if i == wires[0]:
                    full_op = np.kron(full_op, op)
                else:
                    full_op = np.kron(full_op, quantum_gates.I())
            return full_op
        else:
            return op
    
    def var(self, observable, **kwargs):
        """Compute variance of an observable."""
        expval = self.expval(observable, **kwargs)
        expval_sq = self.expval(observable @ observable, **kwargs)
        return expval_sq - expval ** 2
    
    def prob(self, wires=None, **kwargs):
        """
        Return the probability of each computational basis state.
        
        Args:
            wires: Wires to measure (None for all)
            **kwargs: Additional arguments
            
        Returns:
            Probabilities
        """
        self.circuit.execute()
        return self.circuit.get_probabilities()
    
    def sample(self, observable, **kwargs):
        """
        Sample from an observable.
        
        Args:
            observable: Observable to sample
            **kwargs: Additional arguments
            
        Returns:
            Samples
        """
        if self.shots is None:
            raise ValueError("Cannot sample without shots specified")
        
        # For now, return probabilities
        return self.prob(**kwargs)


# Register the device with PennyLane
qml.register_device(FPGADevice, short_name="fpga.simulator", name="FPGA Simulator")

