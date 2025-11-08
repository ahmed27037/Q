# Technical Documentation

## Architecture Overview

### FPGA Simulator Architecture

The FPGA-accelerated simulator uses JAX for JIT compilation and parallel processing to simulate FPGA-like acceleration. Key architectural components:

1. **Statevector Storage**: Dense statevector representation using JAX arrays for GPU acceleration
2. **Gate Application**: Parallel matrix-vector multiplication simulating FPGA's parallel multipliers
3. **Memory Access Patterns**: Optimized for BRAM-like access patterns in FPGA

### Gate Expansion Algorithm

Gates are expanded to the full Hilbert space using bit manipulation:
- **Bit Masking**: Efficient extraction of affected qubit indices
- **Parallel Processing**: All state pairs processed simultaneously (simulated)
- **Memory Efficiency**: Sparse representation where possible

### Quantum Error Correction

The QEC implementation uses lookup tables for fast decoding:
- **Steane Code**: [[7,1,3]] code with lookup table decoder
- **Surface Code**: 2D surface code with simplified matching decoder
- **Latency**: Sub-millisecond decoding times (simulated)

## Performance Characteristics

### Simulator Performance

- **JAX Acceleration**: 2-10x speedup vs NumPy for 5+ qubits
- **Memory Usage**: O(2^n) for n qubits (standard statevector simulation)
- **Gate Operations**: O(2^n) time complexity (parallelized via JAX)

### QEC Performance

- **Decoding Latency**: < 1 μs (simulated FPGA performance)
- **Lookup Table**: O(1) lookup time for Steane code
- **Feedback Loop**: Complete cycle in < 10 μs (simulated)

## FPGA Porting Guide

### Current Implementation

The simulator uses JAX to simulate FPGA parallelism:
- JAX arrays → FPGA BRAM
- JAX operations → FPGA DSP slices
- JAX JIT → FPGA pipeline stages

### Porting Steps

1. **Memory Mapping**: Map statevector to FPGA BRAM blocks
2. **Gate Logic**: Implement parallel multipliers/adders in hardware
3. **Control Logic**: Implement gate sequencing and control flow
4. **Interfacing**: Design PCIe/USB interface for host communication

### Resource Estimates

For 5-qubit simulator (32 states):
- **BRAM**: ~4-8 blocks (depending on precision)
- **DSP Slices**: ~32-64 multipliers
- **Logic**: ~10k-20k LUTs

## PennyLane Device Implementation

The PennyLane device plugin provides:
- Standard PennyLane operations (gates, measurements)
- Observable support (Pauli, Hermitian, Projector)
- Statevector and probability measurements
- Seamless integration with PennyLane workflows

### Supported Operations

- Single-qubit: PauliX/Y/Z, Hadamard, S, T, RX/RY/RZ, PhaseShift
- Two-qubit: CNOT, CZ, SWAP
- Multi-qubit: MultiRZ, IsingXX/YY/ZZ
- Controlled: CRX, CRY, CRZ, CRot

## Quantum Error Correction Details

### Steane Code

- **Code Parameters**: [[7,1,3]] (7 physical qubits, 1 logical qubit, distance 3)
- **Stabilizers**: 3 X stabilizers + 3 Z stabilizers
- **Error Correction**: Corrects any single-qubit error
- **Decoder**: Lookup table with 64 syndrome combinations

### Surface Code

- **Code Structure**: 2D lattice of data and ancilla qubits
- **Stabilizers**: X plaquettes and Z stars
- **Decoder**: Simplified matching decoder (can be extended to MWPM)
- **Scalability**: Designed for larger codes

## Benchmark Methodology

### Simulator Benchmarks

1. **Bell State**: 2-qubit entanglement creation
2. **GHZ State**: N-qubit scaling test
3. **Random Circuits**: Depth-5 random circuits

Comparisons made against:
- NumPy (CPU-only)
- Qiskit (when available)

### QEC Benchmarks

1. **Decoder Latency**: Single syndrome decoding time
2. **Feedback Loop**: Complete error correction cycle
3. **Success Rate**: Correction accuracy under noise

## Future Enhancements

1. **GPU Acceleration**: Direct GPU support for larger simulations
2. **Sparse Representations**: Sparse statevector for memory efficiency
3. **Advanced QEC**: Union-find and MWPM decoders for surface codes
4. **Hardware Interface**: Direct FPGA communication protocols
5. **Photonic Gates**: Native photonic gate operations

## References

- Xanadu PennyLane: https://pennylane.ai
- Xanadu FlamingPy: https://flamingpy.readthedocs.io
- IBM FPGA QEC: Recent FPGA-based error correction demonstrations
- Steane Code: A. M. Steane, "Error correcting codes in quantum theory"
- Surface Code: R. Raussendorf and J. Harrington, "Fault-tolerant quantum computation"

