# Architecture Overview

## System Architecture: Software + Hardware

This project uses a **layered architecture** where components work together:

```
┌─────────────────────────────────────────────────┐
│           User Code / Applications              │
│  (Grover, VQE, QML, Custom Algorithms)         │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│              PennyLane Interface                │
│     (PennyLane Device Plugin - fpga.simulator)  │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│            Python Simulator Layer               │
│  (simulator/circuit.py, simulator/fpga_simulator.py) │
└─────────────────────────────────────────────────┘
                      ↓
         ┌────────────┴────────────┐
         ↓                         ↓
┌──────────────────┐    ┌──────────────────────┐
│  Software Backend│    │   Hardware Backend   │
│   (JAX/NumPy)    │    │   (FPGA Accelerator) │
│   Default Mode   │    │   Optional Mode      │
└──────────────────┘    └──────────────────────┘
```

## How They Work Together

### 1. Python Simulator (Default)

**Location**: `simulator/` directory

**Purpose**: Software-only quantum simulation

**How it works**:
- Uses JAX for parallel processing (simulates FPGA behavior)
- Runs on CPU/GPU
- **Default mode** - works out of the box
- No hardware needed

```python
# Software simulation (default)
from simulator.circuit import QuantumCircuit

circuit = QuantumCircuit(5, use_jax=True)  # Software only
circuit.h(0)
circuit.cnot(0, 1)
state = circuit.execute()  # Runs on CPU/GPU
```

### 2. FPGA Hardware (Optional Accelerator)

**Location**: `fpga/` directory (SystemVerilog)

**Purpose**: Hardware acceleration for production systems

**How it works**:
- Synthesized to actual FPGA chip
- Python code interfaces with FPGA via PCIe/USB
- **Optional mode** - requires FPGA hardware
- Used when you need maximum speed

```python
# Hardware acceleration (optional, requires FPGA)
from simulator.circuit import QuantumCircuit

circuit = QuantumCircuit(5, use_fpga=True, fpga_device='/dev/fpga0')
circuit.h(0)
circuit.cnot(0, 1)
state = circuit.execute()  # Runs on FPGA hardware
```

### 3. PennyLane Integration (Works with Both)

**Location**: `pennylane_device/` directory

**Purpose**: Seamless integration with PennyLane ecosystem

**How it works**:
- PennyLane circuits run on **either** software or hardware backend
- User doesn't need to change PennyLane code
- Backend is configurable

```python
# PennyLane works with both backends
import pennylane as qml

# Option A: Software backend (default)
dev = qml.device("fpga.simulator", wires=4, use_jax=True)

# Option B: Hardware backend (if you have FPGA)
dev = qml.device("fpga.simulator", wires=4, use_fpga=True)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(0)
    qml.CNOT(wires=[0, 1])
    return qml.state()

result = circuit()  # Runs on configured backend
```

## Typical Usage Patterns

### Development & Testing (Software Only)

Most users will use **only the Python simulator**:

```python
# Development work - no FPGA needed
from simulator.circuit import QuantumCircuit

circuit = QuantumCircuit(5)  # Software simulation
# ... build circuit ...
state = circuit.execute()
```

**Advantages**:
- No special hardware required
- Easy to debug
- Works on any computer
- Fast for small circuits (< 10 qubits)

### Production & Performance (With FPGA)

Advanced users with FPGA hardware can use hardware acceleration:

```python
# Production deployment - FPGA accelerated
from simulator.circuit import QuantumCircuit

circuit = QuantumCircuit(5, use_fpga=True)  # Hardware acceleration
# ... build circuit ...
state = circuit.execute()  # Much faster on FPGA
```

**Advantages**:
- Maximum performance
- Low latency (< 1 μs for QEC)
- Real-time quantum control
- Scalable to larger systems

## Component Independence

All components are **independent and optional**:

| Component | Required? | Purpose |
|-----------|-----------|---------|
| Python Simulator | ✅ Yes | Core simulation engine |
| PennyLane Plugin | ⚠️ Optional | Use if you want PennyLane integration |
| FPGA Hardware | ⚠️ Optional | Use if you need hardware acceleration |
| QEC Module | ⚠️ Optional | Use if you need error correction |

## Example: Complete Workflow

### For Software Development (Most Common)

```python
# 1. Use Python simulator (default)
from simulator.circuit import QuantumCircuit

circuit = QuantumCircuit(5)
circuit.h(0)
circuit.cnot(0, 1)
state = circuit.execute()

# 2. Or use PennyLane
import pennylane as qml
dev = qml.device("fpga.simulator", wires=5)

@qml.qnode(dev)
def my_circuit():
    qml.Hadamard(0)
    qml.CNOT(wires=[0, 1])
    return qml.state()

result = my_circuit()
```

### For Production with FPGA

```python
# Same code, just enable FPGA backend
from simulator.circuit import QuantumCircuit

# Change one parameter to use FPGA
circuit = QuantumCircuit(5, use_fpga=True, fpga_device='/dev/fpga0')
circuit.h(0)
circuit.cnot(0, 1)
state = circuit.execute()  # Now runs on FPGA hardware
```

## Why This Architecture?

### Flexibility
- Develop on laptop (software)
- Deploy to FPGA (hardware) when ready
- Same API for both

### Gradual Adoption
- Start with software simulator
- Add FPGA when you need performance
- No code changes required

### Real-World Alignment
- Mirrors how quantum companies work
- Software for algorithm development
- Hardware for production systems
- Xanadu does this with their X8 chip + PennyLane

## Summary

**The FPGA hardware does NOT replace anything. It's an optional accelerator.**

- **Default**: Python simulator (software only) ✅
- **Optional**: FPGA hardware acceleration 🚀
- **Always works**: PennyLane integration 🔌

Think of it like:
- **Software simulator** = Development car (everyone has one)
- **FPGA hardware** = Race car (upgrade when you need speed)
- **PennyLane** = Universal remote (works with both cars)

