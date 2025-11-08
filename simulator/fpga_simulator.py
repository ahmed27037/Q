"""
FPGA-Accelerated Quantum Circuit Simulator

This module implements a high-performance quantum circuit simulator using JAX
for JIT compilation and parallel processing, simulating FPGA-like acceleration.
"""

import numpy as np
from typing import Optional, Union
import jax
import jax.numpy as jnp
from jax import jit, vmap
from .quantum_gates import I


class FPGASimulator:
    """
    High-performance quantum circuit simulator using JAX for FPGA-like parallel processing.
    
    This simulator uses JAX's JIT compilation and parallel operations to simulate
    the parallel processing capabilities of an FPGA. The design is optimized for
    fast statevector updates and matrix-vector multiplications.
    """
    
    def __init__(self, num_qubits: int, use_jax: bool = True):
        """
        Initialize the FPGA simulator.
        
        Args:
            num_qubits: Number of qubits in the system
            use_jax: Whether to use JAX for acceleration (default: True)
        """
        if num_qubits < 1 or num_qubits > 16:
            raise ValueError(f"Number of qubits must be between 1 and 16, got {num_qubits}")
        
        self.num_qubits = num_qubits
        self.dimension = 2 ** num_qubits
        self.use_jax = use_jax
        
        # Initialize statevector in |00...0⟩ state
        if use_jax:
            self.statevector = jnp.zeros(self.dimension, dtype=jnp.complex128)
            self.statevector = self.statevector.at[0].set(1.0 + 0j)
        else:
            self.statevector = np.zeros(self.dimension, dtype=np.complex128)
            self.statevector[0] = 1.0 + 0j
    
    def reset(self):
        """Reset the statevector to |00...0⟩."""
        if self.use_jax:
            self.statevector = jnp.zeros(self.dimension, dtype=jnp.complex128)
            self.statevector = self.statevector.at[0].set(1.0 + 0j)
        else:
            self.statevector = np.zeros(self.dimension, dtype=np.complex128)
            self.statevector[0] = 1.0 + 0j
    
    @jit
    def _apply_gate_jax(state: jnp.ndarray, gate_matrix: jnp.ndarray, indices: jnp.ndarray) -> jnp.ndarray:
        """
        JIT-compiled gate application using JAX.
        
        This function simulates FPGA-like parallel processing by using JAX's
        optimized matrix-vector multiplication.
        """
        return jnp.dot(gate_matrix, state[indices])
    
    def apply_gate(self, gate_matrix: Union[np.ndarray, jnp.ndarray], qubit_indices: list):
        """
        Apply a quantum gate to the statevector.
        
        This method uses parallel processing (simulated via JAX) to efficiently
        update the statevector, similar to how an FPGA would process multiple
        amplitudes in parallel.
        
        Args:
            gate_matrix: The gate matrix to apply (2x2 for single qubit, 4x4 for two qubit, etc.)
            qubit_indices: List of qubit indices the gate acts on (in order: control, target, etc.)
        """
        gate_size = gate_matrix.shape[0]
        num_affected_qubits = int(np.log2(gate_size))
        
        if len(qubit_indices) != num_affected_qubits:
            raise ValueError(f"Gate size {gate_size} requires {num_affected_qubits} qubits, "
                           f"but {len(qubit_indices)} indices provided")
        
        # Convert to JAX if needed
        if self.use_jax and isinstance(gate_matrix, np.ndarray):
            gate_matrix = jnp.array(gate_matrix)
        elif not self.use_jax and isinstance(gate_matrix, jnp.ndarray):
            gate_matrix = np.array(gate_matrix)
        
        # Expand gate to full Hilbert space
        full_gate = self._expand_gate_to_full_space(gate_matrix, qubit_indices)
        
        # Apply gate using parallel matrix-vector multiplication
        # This simulates FPGA's parallel multipliers and adders working on all amplitudes
        if self.use_jax:
            self.statevector = jnp.dot(full_gate, self.statevector)
        else:
            self.statevector = np.dot(full_gate, self.statevector)
    
    def _expand_gate_to_full_space(self, gate: Union[np.ndarray, jnp.ndarray], qubit_indices: list) -> Union[np.ndarray, jnp.ndarray]:
        """
        Expand a gate acting on specific qubits to the full Hilbert space.
        
        This simulates how an FPGA would construct the full gate matrix by
        applying the gate in parallel across all basis states.
        """
        gate_size = gate.shape[0]
        use_jax = self.use_jax
        
        # Create mask for affected qubits
        affected_mask = 0
        for q in qubit_indices:
            affected_mask |= (1 << q)
        
        # Build full gate matrix using bit manipulation
        # This simulates FPGA's parallel index computation
        if use_jax:
            full_gate = jnp.zeros((self.dimension, self.dimension), dtype=jnp.complex128)
        else:
            full_gate = np.zeros((self.dimension, self.dimension), dtype=np.complex128)
        
        # For each output state, compute contribution from all input states
        # This loop simulates FPGA's parallel processing of all state pairs
        for out_idx in range(self.dimension):
            for in_idx in range(self.dimension):
                # Check if in_idx and out_idx match on unaffected qubits
                if (in_idx & ~affected_mask) != (out_idx & ~affected_mask):
                    continue
                
                # Extract affected qubit values (simulating parallel bit extraction)
                in_affected = 0
                out_affected = 0
                bit_pos = 0
                for q in sorted(qubit_indices):
                    if (in_idx >> q) & 1:
                        in_affected |= (1 << bit_pos)
                    if (out_idx >> q) & 1:
                        out_affected |= (1 << bit_pos)
                    bit_pos += 1
                
                # Set the gate matrix element
                if use_jax:
                    full_gate = full_gate.at[out_idx, in_idx].set(gate[out_affected, in_affected])
                else:
                    full_gate[out_idx, in_idx] = gate[out_affected, in_affected]
        
        return full_gate
    
    def get_statevector(self) -> np.ndarray:
        """Get the current statevector as a NumPy array."""
        if self.use_jax:
            return np.array(self.statevector)
        return self.statevector.copy()
    
    def measure(self, qubit: int) -> int:
        """
        Measure a qubit and collapse the statevector.
        
        Args:
            qubit: Index of qubit to measure
            
        Returns:
            0 or 1, the measurement result
        """
        if qubit < 0 or qubit >= self.num_qubits:
            raise ValueError(f"Qubit index {qubit} out of range [0, {self.num_qubits})")
        
        # Calculate probability of measuring |0⟩
        prob_0 = 0.0
        state_array = self.get_statevector()
        
        for i in range(self.dimension):
            if (i >> qubit) & 1 == 0:  # qubit is |0⟩
                prob_0 += np.abs(state_array[i]) ** 2
        
        # Collapse based on measurement
        result = int(np.random.random() > prob_0)
        
        # Collapse statevector
        if self.use_jax:
            new_state = jnp.zeros_like(self.statevector)
            for i in range(self.dimension):
                if ((i >> qubit) & 1) == result:
                    new_state = new_state.at[i].set(self.statevector[i])
                else:
                    new_state = new_state.at[i].set(0.0)
            
            # Normalize
            norm = jnp.sqrt(jnp.sum(jnp.abs(new_state) ** 2))
            if norm > 1e-10:
                self.statevector = new_state / norm
            else:
                self.reset()
        else:
            new_state = np.zeros_like(self.statevector)
            for i in range(self.dimension):
                if ((i >> qubit) & 1) == result:
                    new_state[i] = self.statevector[i]
                else:
                    new_state[i] = 0.0
            
            # Normalize
            norm = np.sqrt(np.sum(np.abs(new_state) ** 2))
            if norm > 1e-10:
                self.statevector = new_state / norm
            else:
                self.reset()
        
        return result
    
    def get_probabilities(self) -> np.ndarray:
        """Get measurement probabilities for all basis states."""
        state_array = self.get_statevector()
        return np.abs(state_array) ** 2
    
    def get_expectation_value(self, observable: np.ndarray) -> float:
        """
        Calculate expectation value of an observable.
        
        Args:
            observable: Hermitian operator matrix
            
        Returns:
            Expectation value <ψ|O|ψ>
        """
        state_array = self.get_statevector()
        if self.use_jax:
            obs = jnp.array(observable)
            state = self.statevector
            return float(jnp.real(jnp.conj(state) @ obs @ state))
        else:
            return float(np.real(np.conj(state_array) @ observable @ state_array))

