# FPGA Hardware Acceleration Layer

**Hardware backend for the PennyLane-integrated Python simulator.** This directory contains SystemVerilog implementations of the SAME quantum operations implemented in the Python software layer.

## Integration with Python Simulator

### NOT Two Separate Projects ✋

This is **ONE system** with **TWO backends**:

| Component | Software Backend (Python) | Hardware Backend (FPGA) |
|-----------|--------------------------|------------------------|
| **Gate Operations** | `simulator/fpga_simulator.py` (JAX) | `quantum_gate_core.sv` |
| **QEC Decoding** | `qec/decoder.py` (Python) | `qec_decoder.sv` |
| **Statevector Storage** | NumPy arrays | `statevector_memory.sv` (BRAM) |
| **Interface** | Direct Python API | `control_interface.sv` (PCIe) |

### How They Work Together

```
PennyLane Circuit
       ↓
FPGADevice Plugin (pennylane_device/fpga_device.py)
       ↓
Backend Selection:
  ├─→ Software: simulator/fpga_simulator.py (JAX, ~ms latency)
  └─→ Hardware: FPGA via PCIe driver (<μs latency)
```

**Same quantum operations, different performance characteristics.**

## Hardware is OPTIONAL

**The Python simulator works perfectly fine without any FPGA hardware.** This directory is for:
- Production deployment with maximum performance
- Real-time quantum control systems
- Users with FPGA hardware access (Xilinx/Intel)

**Most users can use the Python simulator only and still benefit from the PennyLane integration and QEC features.**

## Components

1. **quantum_gate_core.sv** - Parallel quantum gate application engine
2. **statevector_memory.sv** - Optimized statevector storage using BRAM
3. **qec_decoder.sv** - Hardware QEC decoder with lookup tables
4. **control_interface.sv** - PCIe/AXI interface for host communication

## Architecture

### Quantum Gate Core

The gate core implements parallel complex matrix-vector multiplication:
- Uses DSP slices for complex multiplication
- Parallel processing of multiple amplitudes
- Pipeline stages for high throughput

### Statevector Memory

Optimized memory structure:
- Dual-port BRAM for simultaneous read/write
- Distributed across multiple BRAM blocks
- Efficient addressing for qubit operations

### QEC Decoder

Hardware-accelerated error correction:
- Lookup table for syndrome decoding (Steane code)
- Sub-microsecond latency
- Parallel syndrome processing

## Target FPGAs

Designed for:
- Xilinx Artix-7 / Zynq-7000 (small systems)
- Xilinx Kintex / Virtex (medium systems)
- Intel Stratix / Arria (alternative platform)

## Resource Estimates

For 5-qubit system (32 complex amplitudes):
- **BRAM**: 8-16 blocks (storing 32 × 64-bit complex numbers)
- **DSP Slices**: 32-64 multipliers (parallel processing)
- **LUTs**: 10K-20K (control logic and addressing)
- **FFs**: 5K-10K (pipeline registers)

## Building

### Xilinx Vivado

```bash
cd fpga
vivado -mode batch -source build_quantum_core.tcl
```

### Intel Quartus

```bash
cd fpga
quartus_sh -t build_quantum_core.tcl
```

## Simulation

Testbenches are provided for each module:

```bash
cd fpga/testbenches
./run_simulation.sh
```

## Integration with Python Simulator

The FPGA can be used as an accelerator for the Python simulator:
1. Host sends circuit description via PCIe/USB
2. FPGA executes gates in hardware
3. Results sent back to host

See `control_interface.sv` for communication protocol.

