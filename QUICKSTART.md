# Quick Start Guide

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd quantum-fpga-simulator

# Install dependencies
pip install -r requirements.txt

# Install the package (optional)
pip install -e .
```

## Running Examples

All examples should be run from the project root directory:

### 1. Basic Circuit Example

```bash
cd quantum-fpga-simulator
python examples/grover.py
```

### 2. VQE Example

```bash
cd quantum-fpga-simulator
python examples/vqe.py
```

### 3. PennyLane Integration

```bash
cd quantum-fpga-simulator
python examples/pennylane_demo.py
```

### 4. Quantum Machine Learning

```bash
cd quantum-fpga-simulator
python examples/qml_classifier.py
```

### 5. Quantum Error Correction

```bash
cd quantum-fpga-simulator
python examples/surface_code.py
```

## Running Benchmarks

All benchmarks should be run from the project root directory:

### Simulator Benchmarks

```bash
cd quantum-fpga-simulator
python benchmarks/benchmark.py
```

This will:
- Compare FPGA simulator vs Qiskit/NumPy
- Generate performance plots
- Show scaling characteristics

### QEC Benchmarks

```bash
cd quantum-fpga-simulator
python benchmarks/qec_benchmark.py
```

This will:
- Benchmark decoder latency
- Test feedback loop performance
- Show QEC success rates

## Project Structure Overview

```
.
├── simulator/              # Core FPGA simulator (Python)
│   ├── fpga_simulator.py  # Main simulator engine
│   ├── quantum_gates.py   # Gate implementations
│   └── circuit.py         # Circuit interface
├── pennylane_device/      # PennyLane plugin
│   └── fpga_device.py     # PennyLane device
├── qec/                   # Quantum error correction
│   ├── decoder.py         # QEC decoders
│   ├── simulator.py       # Error simulation
│   └── feedback_loop.py   # Feedback loop
├── fpga/                  # FPGA hardware implementation (SystemVerilog)
│   ├── quantum_gate_core.sv    # Hardware gate engine
│   ├── qec_decoder.sv          # Hardware QEC decoder
│   ├── statevector_memory.sv   # BRAM-based memory
│   ├── control_interface.sv    # PCIe/AXI interface
│   └── testbenches/            # Verification testbenches
├── benchmarks/            # Performance benchmarks
├── examples/              # Example algorithms
└── docs/                  # Documentation
```

## FPGA Hardware Implementation

This project includes actual **SystemVerilog HDL code** in the `fpga/` directory:

- **Dual approach**: Python simulator (software) + SystemVerilog (hardware)
- **Ready for synthesis**: Can be deployed to Xilinx or Intel FPGAs
- **See `fpga/README.md`** for synthesis and deployment instructions

## Next Steps

1. **Explore Examples**: Run the example scripts to see the simulator in action
2. **Read Documentation**: Check `docs/` for detailed technical documentation
3. **Run Benchmarks**: Evaluate performance characteristics
4. **Customize**: Modify examples for your own quantum circuits
5. **Contribute**: Consider contributing to the project or PennyLane

## Troubleshooting

### JAX Installation Issues

If JAX installation fails, try:
```bash
cd quantum-fpga-simulator
pip install jax jaxlib --upgrade
```

### PennyLane Not Found

Make sure PennyLane is installed:
```bash
cd quantum-fpga-simulator
pip install pennylane
```

### Import Errors

Ensure you're in the project root directory and dependencies are installed.

## Support

For issues or questions:
1. Check the documentation in `docs/`
2. Review example code in `examples/`
3. Check GitHub issues (if repository is public)

