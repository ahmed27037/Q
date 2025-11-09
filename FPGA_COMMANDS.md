# FPGA Hardware Commands & Deployment Guide

This guide provides complete commands for synthesizing, deploying, and using the FPGA hardware implementation.

## Prerequisites

### Hardware Requirements
- FPGA Development Board (Xilinx Artix-7, Zynq-7000, or equivalent)
- PCIe/USB connection to host computer
- Minimum 10K LUTs, 8 BRAM blocks, 32 DSP slices

### Software Requirements
- **Xilinx**: Vivado Design Suite 2021.1 or later
- **Intel**: Quartus Prime 21.1 or later
- Python 3.9+ with development packages
- FPGA device drivers

## Installation & Setup

### 1. Install Vivado (Xilinx)

```bash
# Download Vivado from Xilinx website
# Install to default location: /opt/Xilinx/Vivado/2023.2

# Add to PATH (Linux/WSL)
echo 'source /opt/Xilinx/Vivado/2023.2/settings64.sh' >> ~/.bashrc
source ~/.bashrc

# Verify installation
vivado -version
```

### 2. Install FPGA Drivers

```bash
# Linux - Install PCIe drivers
cd quantum-fpga-simulator
sudo ./fpga/scripts/install_drivers.sh

# Load kernel module
sudo modprobe fpga_quantum_accel

# Verify device
ls -l /dev/fpga0
```

## FPGA Synthesis & Programming

### Option A: Xilinx Vivado Flow

#### Step 1: Synthesize Design

```bash
cd quantum-fpga-simulator/fpga

# Run synthesis
vivado -mode batch -source build_quantum_core.tcl

# This will:
# - Synthesize all SystemVerilog modules
# - Run place and route
# - Generate bitstream (.bit file)
# - Create timing reports
```

#### Step 2: Program FPGA

```bash
# Program via JTAG
vivado -mode batch -source program_fpga.tcl

# Or use command line
vivado -mode tcl
> open_hw_manager
> connect_hw_server
> open_hw_target
> set_property PROGRAM.FILE {quantum_core.bit} [get_hw_devices xc7a35t_0]
> program_hw_devices [get_hw_devices xc7a35t_0]
> exit
```

#### Step 3: Verify Programming

```bash
# Check FPGA status
dmesg | grep fpga

# Test register access
cd quantum-fpga-simulator
python fpga/tests/test_fpga_connection.py
```

### Option B: Intel Quartus Flow

#### Step 1: Synthesize Design

```bash
cd quantum-fpga-simulator/fpga

# Run synthesis
quartus_sh -t build_quantum_core_intel.tcl

# Or use GUI
quartus quantum_core.qpf
```

#### Step 2: Program FPGA

```bash
# Program via USB-Blaster
quartus_pgm -c USB-Blaster -m JTAG -o "p;quantum_core.sof"

# For permanent programming (Flash)
quartus_pgm -c USB-Blaster -m JTAG -o "p;quantum_core.pof"
```

## Running Python Simulator with FPGA

### 1. Basic FPGA Usage

```bash
cd quantum-fpga-simulator

# Test FPGA connection
python -c "from simulator.fpga_backend import FPGABackend; print(FPGABackend.check_connection())"

# Run simple circuit on FPGA
python examples/fpga_hello_world.py
```

### 2. Enable FPGA in Python Code

```python
from simulator.circuit import QuantumCircuit

# Create circuit with FPGA backend
circuit = QuantumCircuit(
    num_qubits=5,
    use_fpga=True,              # Enable FPGA
    fpga_device='/dev/fpga0'    # Device path
)

# Apply gates - executed on FPGA hardware
circuit.h(0)
circuit.cnot(0, 1)
circuit.rz(2, 1.5)

# Execute on FPGA
state = circuit.execute()
print("Statevector from FPGA:", state)
```

### 3. PennyLane with FPGA

```bash
cd quantum-fpga-simulator

# Run PennyLane example with FPGA backend
python examples/pennylane_fpga_demo.py
```

```python
import pennylane as qml

# Create PennyLane device with FPGA backend
dev = qml.device(
    "fpga.simulator",
    wires=4,
    use_fpga=True,
    fpga_device='/dev/fpga0'
)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(0)
    qml.CNOT(wires=[0, 1])
    return qml.state()

# Execute on FPGA
result = circuit()
```

### 4. QEC with FPGA Decoder

```bash
cd quantum-fpga-simulator

# Run QEC with hardware decoder
python examples/qec_fpga_demo.py
```

```python
from qec.decoder import FPGASteaneDecoder
from qec.simulator import ErrorSimulator

# Initialize FPGA decoder
decoder = FPGASteaneDecoder(fpga_device='/dev/fpga0')

# Run error correction on FPGA
simulator = ErrorSimulator(code_type="steane")
errors = simulator.introduce_errors()
syndrome_x, syndrome_z = simulator.measure_syndrome()

# Decode on FPGA (< 1 μs latency)
correction = decoder.decode(syndrome_x, syndrome_z)
simulator.apply_correction(correction)
```

## Benchmarking FPGA Performance

### 1. Run FPGA Benchmarks

```bash
cd quantum-fpga-simulator

# Benchmark FPGA vs software
python benchmarks/fpga_benchmark.py

# QEC decoder latency test
python benchmarks/qec_fpga_latency.py
```

### 2. Monitor FPGA Performance

```bash
# Monitor FPGA utilization
watch -n 1 'cat /sys/class/fpga/fpga0/statistics'

# Check clock frequency
cat /sys/class/fpga/fpga0/clock_freq

# Monitor temperature
cat /sys/class/fpga/fpga0/temperature
```

## Troubleshooting

### FPGA Not Detected

```bash
# Check PCIe devices
lspci | grep -i xilinx

# Check USB devices (for USB-connected FPGAs)
lsusb | grep -i xilinx

# Reload driver
sudo rmmod fpga_quantum_accel
sudo modprobe fpga_quantum_accel
```

### Programming Fails

```bash
# Check JTAG connection
vivado -mode tcl
> open_hw_manager
> connect_hw_server
> get_hw_targets

# Reset FPGA
sudo sh -c 'echo 1 > /sys/class/fpga/fpga0/reset'
```

### Python Can't Access FPGA

```bash
# Check device permissions
ls -l /dev/fpga0

# Add user to fpga group
sudo usermod -a -G fpga $USER

# Or change permissions (temporary)
sudo chmod 666 /dev/fpga0

# Verify Python can import
python -c "from simulator.fpga_backend import FPGABackend; print('OK')"
```

## Complete Workflow Example

### End-to-End: Synthesis to Execution

```bash
# 1. Navigate to project
cd quantum-fpga-simulator

# 2. Synthesize FPGA design
cd fpga
vivado -mode batch -source build_quantum_core.tcl
cd ..

# 3. Program FPGA
vivado -mode batch -source fpga/program_fpga.tcl

# 4. Install Python package
pip install -e .

# 5. Test FPGA connection
python -c "from simulator.fpga_backend import FPGABackend; FPGABackend.test_connection()"

# 6. Run example with FPGA
python examples/grover_fpga.py

# 7. Run benchmarks
python benchmarks/fpga_benchmark.py

# 8. Compare performance
python benchmarks/compare_backends.py --backends software fpga
```

## Performance Expectations

| Operation | Software (JAX) | FPGA Hardware | Speedup |
|-----------|---------------|---------------|---------|
| Single Gate | 10-50 μs | 0.1-1 μs | 10-50x |
| QEC Decode | 50-500 μs | < 1 μs | 50-500x |
| Full Circuit (10 gates) | 100-500 μs | 1-10 μs | 10-100x |

## Configuration Files

### FPGA Configuration

```bash
# Edit fpga/config.yaml
cat > fpga/config.yaml << EOF
fpga:
  device: /dev/fpga0
  clock_freq: 200000000  # 200 MHz
  timeout_ms: 1000
  use_dma: true
  buffer_size: 4096

simulator:
  max_qubits: 8
  precision: 32  # 32-bit or 64-bit
  
qec:
  decoder_type: steane  # steane or surface
  lookup_table_addr: 0x1000
EOF
```

### Python Configuration

```python
# In your Python code
from simulator.config import FPGAConfig

# Configure FPGA backend
config = FPGAConfig(
    device='/dev/fpga0',
    clock_freq=200e6,
    use_dma=True,
    timeout_ms=1000
)

circuit = QuantumCircuit(5, use_fpga=True, fpga_config=config)
```

## Advanced: Custom FPGA Modules

### Adding Your Own Modules

```bash
# 1. Create SystemVerilog module
cat > fpga/my_custom_gate.sv << EOF
module my_custom_gate (
    input logic clk,
    input logic rst_n,
    // ... your module interface
);
    // ... your implementation
endmodule
EOF

# 2. Add to build script
echo "read_verilog fpga/my_custom_gate.sv" >> fpga/build_quantum_core.tcl

# 3. Rebuild
cd fpga
vivado -mode batch -source build_quantum_core.tcl
```

## Support & Resources

- **FPGA Synthesis Issues**: Check `fpga/build.log`
- **Python Interface Issues**: Run `python fpga/tests/diagnose.py`
- **Performance Issues**: Run `python benchmarks/profile_fpga.py`
- **Driver Issues**: Check `dmesg | grep fpga`

## Safety Notes

⚠️ **Important**:
- Always properly shut down FPGA before power off
- Monitor FPGA temperature during heavy workloads
- Use proper power supply (usually 12V, check your board)
- Don't hot-plug PCIe cards

```bash
# Safe shutdown
sudo sh -c 'echo 0 > /sys/class/fpga/fpga0/enable'
sudo rmmod fpga_quantum_accel
# Now safe to power off
```

