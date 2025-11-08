# StellarForge ⭐

**StellarForge** - A high-performance quantum computing framework featuring FPGA-accelerated simulation, seamless PennyLane integration, and real-time quantum error correction.

*Forging the future of quantum computing through hardware acceleration.*

## Overview

StellarForge is a comprehensive quantum computing framework that combines three powerful components:

1. **FPGA-Accelerated Quantum Circuit Simulator** - High-performance simulator using JAX/optimized NumPy for FPGA-like parallel processing
2. **PennyLane Device Plugin** - Native device plugin for seamless integration with the PennyLane quantum computing ecosystem
3. **Quantum Error Correction Decoder** - Real-time QEC decoder with low-latency processing for fault-tolerant quantum computing

## Features

- **Parallel Statevector Operations**: JAX-powered matrix-vector multiplications simulating FPGA parallelism
- **PennyLane Integration**: Native PennyLane device plugin for seamless workflow integration
- **Quantum Error Correction**: Optimized decoders for Steane and surface codes
- **Performance Benchmarks**: Comprehensive comparisons vs CPU-only implementations
- **Example Algorithms**: Grover's search, VQE, and quantum machine learning demos

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Quick Install

```bash
# Clone the repository
git clone https://github.com/ahmed27037/Q.git
cd Q

# Install dependencies
pip install -r requirements.txt

# Install StellarForge as a package (recommended)
pip install -e .
```

That's it! You're ready to use StellarForge.

## Quick Start

### Example 1: Basic Quantum Circuit

```python
from simulator.circuit import QuantumCircuit

# Create a 3-qubit circuit
circuit = QuantumCircuit(3, use_jax=True)

# Apply quantum gates
circuit.h(0)                    # Hadamard gate on qubit 0
circuit.cnot(0, 1)             # CNOT: control=0, target=1
circuit.x(2)                    # Pauli-X gate on qubit 2

# Execute and get statevector
state = circuit.execute()
print("Final statevector:", state)

# Get measurement probabilities
probs = circuit.get_probabilities()
print("Probabilities:", probs)
```

### Example 2: PennyLane Integration

```python
import pennylane as qml

# Use StellarForge as a PennyLane device
dev = qml.device("fpga.simulator", wires=4)

@qml.qnode(dev)
def my_circuit():
    qml.Hadamard(0)
    qml.CNOT(wires=[0, 1])
    qml.RY(0.5, wires=2)
    return qml.state()

# Execute the circuit
result = my_circuit()
print("Result:", result)
```

### Example 3: Quantum Error Correction

```python
from qec.decoder import SteaneDecoder
from qec.simulator import ErrorSimulator

# Initialize decoder and error simulator
decoder = SteaneDecoder()
simulator = ErrorSimulator(code_type="steane", error_rate=0.1)

# Introduce errors
errors = simulator.introduce_errors()
print("Errors introduced:", errors)

# Measure syndrome
syndrome_x, syndrome_z = simulator.measure_syndrome()
print("Syndrome X:", syndrome_x)
print("Syndrome Z:", syndrome_z)

# Decode and correct
correction = decoder.decode(syndrome_x, syndrome_z)
success = simulator.apply_correction(correction)
print("Correction successful:", success)
```

### Example 4: Run Example Algorithms

```bash
# Run Grover's search algorithm
python examples/grover.py

# Run Variational Quantum Eigensolver (VQE)
python examples/vqe.py

# Run Quantum Machine Learning classifier
python examples/qml_classifier.py

# Run PennyLane integration demo
python examples/pennylane_demo.py

# Run surface code QEC example
python examples/surface_code.py
```

## Project Structure

```
StellarForge/
├── simulator/          # Core FPGA-accelerated simulator
│   ├── fpga_simulator.py
│   ├── circuit.py
│   └── quantum_gates.py
├── pennylane_device/   # PennyLane device plugin
│   └── fpga_device.py
├── qec/               # Quantum error correction
│   ├── decoder.py
│   ├── simulator.py
│   └── feedback_loop.py
├── benchmarks/        # Performance benchmarks
│   ├── benchmark.py
│   └── qec_benchmark.py
├── examples/          # Example algorithms and demos
│   ├── grover.py
│   ├── vqe.py
│   ├── qml_classifier.py
│   └── pennylane_demo.py
├── tests/             # Unit tests
└── docs/              # Documentation
```

## Performance

The simulator demonstrates significant speedups for quantum circuits:

- **2-10x speedup** vs CPU-only NumPy implementations (using JAX acceleration)
- **Sub-microsecond latency** for QEC decoding (simulated FPGA performance)
- **Seamless integration** with PennyLane workflows
- **Real-time error correction** with microsecond-level decoding latency

### Running Benchmarks

```bash
# Benchmark simulator performance
python benchmarks/benchmark.py

# Benchmark QEC decoder performance
python benchmarks/qec_benchmark.py
```

## Key Capabilities

### 1. PennyLane Integration
- **Native Device Plugin**: Full PennyLane device implementation supporting 20+ standard operations
- **Seamless Workflow**: Compatible with existing PennyLane circuits and algorithms
- **Quantum Machine Learning**: QML classifier example using quantum kernels
- **Ecosystem Compatibility**: Works with the broader PennyLane ecosystem

### 2. Quantum Error Correction (QEC)
- **Real-Time Decoding**: Low-latency decoders for Steane and surface codes
- **Multiple Algorithms**: Supports Steane code, surface code, and union-find decoders
- **Hardware Efficiency**: Optimized for FPGA implementation with lookup tables and parallel processing
- **Feedback Loops**: Complete error correction cycle with latency measurements

### 3. Hardware Acceleration
- **FPGA-Ready Design**: Parallel processing patterns match FPGA resource utilization
- **Low Latency**: Optimized for real-time quantum control requirements
- **Scalability**: Architecture designed to scale with increasing qubit counts
- **JAX Acceleration**: JIT compilation and parallel operations for maximum performance

## Future FPGA Porting

The current implementation uses optimized Python libraries (JAX) to simulate FPGA parallelism. The architecture is designed for straightforward porting to FPGA hardware:

- Parallel processing patterns match FPGA resource utilization
- Memory access patterns optimized for BRAM usage
- Latency measurements simulate FPGA timing constraints

## Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running quickly
- **[Technical Documentation](docs/TECHNICAL_DOCS.md)** - Detailed technical information
- **[Performance Analysis](docs/PERFORMANCE_ANALYSIS.md)** - Performance benchmarks and analysis
- **[Project Description](PROJECT_DESCRIPTION.md)** - Comprehensive project overview with diagrams

## License

MIT License

## Contributing

Contributions welcome! This project showcases quantum computing and FPGA integration capabilities.

## Support

For issues, questions, or contributions, please open an issue on GitHub.
