# Complete Commands Reference

Quick reference for all project commands.

## Software Simulator (Default - No FPGA Required)

### Installation

```bash
cd quantum-fpga-simulator
pip install -r requirements.txt
pip install -e .
```

### Run Examples

```bash
cd quantum-fpga-simulator

# Grover's algorithm
python examples/grover.py

# VQE (Variational Quantum Eigensolver)
python examples/vqe.py

# PennyLane integration demo
python examples/pennylane_demo.py

# Quantum machine learning
python examples/qml_classifier.py

# Surface code QEC
python examples/surface_code.py
```

### Run Benchmarks

```bash
cd quantum-fpga-simulator

# Simulator performance benchmarks
python benchmarks/benchmark.py

# QEC performance benchmarks
python benchmarks/qec_benchmark.py
```

### Run Tests

```bash
cd quantum-fpga-simulator
pytest tests/
```

## SystemVerilog Simulation (No FPGA Hardware Needed!)

### Install Icarus Verilog

**Windows:**
1. Download from: http://bleyer.org/icarus/
2. Install (adds to PATH automatically)

**Linux/WSL:**
```bash
sudo apt-get install iverilog gtkwave
```

**macOS:**
```bash
brew install icarus-verilog gtkwave
```

### Run Simulations

**Windows PowerShell:**
```powershell
# Navigate to sim directory (replace with your path)
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q\fpga\sim

# Run all tests
.\run_all_tests.ps1

# Or run individual test
iverilog -g2012 -o gate_sim.exe ../quantum_gate_core.sv ../testbenches/quantum_gate_core_tb.sv
vvp gate_sim.exe
gtkwave gate_sim.vcd
```

**Windows CMD:**
```cmd
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q\fpga\sim
run_all_tests.bat
```

**Linux/macOS:**
```bash
cd quantum-fpga-simulator/fpga/sim
chmod +x run_all_tests.sh
./run_all_tests.sh
```

### What Gets Tested

✅ Quantum gate core (parallel processing)
✅ QEC decoder (syndrome lookup)
✅ Statevector memory (BRAM behavior)
✅ All without FPGA hardware!

---

## FPGA Hardware (Optional - Requires Real FPGA)

### Prerequisites

Install Xilinx Vivado or Intel Quartus, then:

```bash
# Install FPGA drivers (Linux)
cd quantum-fpga-simulator
sudo ./fpga/scripts/install_drivers.sh
sudo modprobe fpga_quantum_accel
```

### Synthesize & Program FPGA

```bash
cd quantum-fpga-simulator/fpga

# Synthesize design (Xilinx)
vivado -mode batch -source build_quantum_core.tcl

# Program FPGA (Xilinx)
vivado -mode batch -source program_fpga.tcl

# Or for Intel Quartus
quartus_sh -t build_quantum_core_intel.tcl
quartus_pgm -c USB-Blaster -m JTAG -o "p;quantum_core.sof"
```

### Test FPGA Connection

```bash
cd quantum-fpga-simulator

# Check if FPGA is detected
python -c "from simulator.fpga_backend import FPGABackend; print(FPGABackend.check_connection())"

# Run FPGA test
python fpga/tests/test_fpga_connection.py
```

### Run Examples with FPGA

```bash
cd quantum-fpga-simulator

# Run Grover on FPGA
python examples/grover_fpga.py

# Run QEC with hardware decoder
python examples/qec_fpga_demo.py

# Run PennyLane with FPGA
python examples/pennylane_fpga_demo.py
```

### FPGA Performance Benchmarks

```bash
cd quantum-fpga-simulator

# Compare FPGA vs software
python benchmarks/fpga_benchmark.py

# QEC decoder latency test
python benchmarks/qec_fpga_latency.py

# Full comparison
python benchmarks/compare_backends.py --backends software fpga
```

## Python API Quick Reference

### Software Simulator

```python
from simulator.circuit import QuantumCircuit

# Create circuit (software only)
circuit = QuantumCircuit(5, use_jax=True)

# Apply gates
circuit.h(0)
circuit.cnot(0, 1)
circuit.rz(2, 1.5)

# Execute
state = circuit.execute()
probs = circuit.get_probabilities()
```

### FPGA Accelerator

```python
from simulator.circuit import QuantumCircuit

# Create circuit with FPGA backend
circuit = QuantumCircuit(
    num_qubits=5,
    use_fpga=True,
    fpga_device='/dev/fpga0'
)

# Apply gates (runs on FPGA)
circuit.h(0)
circuit.cnot(0, 1)

# Execute on FPGA
state = circuit.execute()
```

### PennyLane Integration

```python
import pennylane as qml

# Software backend (default)
dev = qml.device("fpga.simulator", wires=4)

# Or FPGA backend
dev = qml.device("fpga.simulator", wires=4, use_fpga=True)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(0)
    qml.CNOT(wires=[0, 1])
    return qml.state()

result = circuit()
```

### Quantum Error Correction

```python
from qec.decoder import SteaneDecoder
from qec.simulator import ErrorSimulator

# Software decoder
decoder = SteaneDecoder()
simulator = ErrorSimulator(code_type="steane")

errors = simulator.introduce_errors()
syndrome_x, syndrome_z = simulator.measure_syndrome()
correction = decoder.decode(syndrome_x, syndrome_z)
success = simulator.apply_correction(correction)

# Or FPGA decoder (if available)
from qec.decoder import FPGASteaneDecoder
decoder = FPGASteaneDecoder(fpga_device='/dev/fpga0')
```

## Troubleshooting

### Import Errors

```bash
# Make sure you're in project directory
cd quantum-fpga-simulator

# Reinstall
pip install -e .
```

### FPGA Not Detected

```bash
# Check PCIe devices
lspci | grep -i xilinx

# Reload driver
sudo rmmod fpga_quantum_accel
sudo modprobe fpga_quantum_accel

# Check device
ls -l /dev/fpga0
```

### Permission Denied

```bash
# Add user to fpga group
sudo usermod -a -G fpga $USER

# Or change permissions (temporary)
sudo chmod 666 /dev/fpga0
```

## Performance Comparison

| Mode | Setup | Speed | Use Case |
|------|-------|-------|----------|
| **Software (JAX)** | `pip install` | 1x (baseline) | Development, testing |
| **Software (NumPy)** | `pip install` | 0.1-0.5x | CPU-only fallback |
| **FPGA Hardware** | FPGA board + synthesis | 10-100x | Production, real-time |

## Next Steps

1. **Start with software**: Run examples with default software simulator
2. **Try PennyLane**: Integrate with PennyLane for QML
3. **Benchmark**: Compare performance characteristics
4. **FPGA (optional)**: Deploy to FPGA if you have hardware

## Documentation

- [`README.md`](README.md) - Project overview
- [`QUICKSTART.md`](QUICKSTART.md) - Quick start guide
- [`ARCHITECTURE.md`](ARCHITECTURE.md) - System architecture
- [`FPGA_COMMANDS.md`](FPGA_COMMANDS.md) - Detailed FPGA guide
- [`docs/TECHNICAL_DOCS.md`](docs/TECHNICAL_DOCS.md) - Technical details
- [`docs/PERFORMANCE_ANALYSIS.md`](docs/PERFORMANCE_ANALYSIS.md) - Performance analysis

