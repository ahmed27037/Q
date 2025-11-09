# SystemVerilog Simulation with Icarus Verilog

Simulate the FPGA hardware design without needing actual FPGA hardware!

## Why Icarus Verilog?

- **Free & Open Source**: No expensive FPGA tools needed
- **Cross-Platform**: Works on Windows, Linux, macOS
- **Fast**: Quick compile and simulate
- **Educational**: Great for learning hardware design

## Installation

### Windows (PowerShell/CMD)
1. Download Icarus Verilog from: http://bleyer.org/icarus/
2. Install to default location (usually `C:\iverilog`)
3. Add to PATH or use full path in commands
4. GTKWave included in installation

**Or use WSL/Linux subsystem**

### Linux/WSL
```bash
sudo apt-get update
sudo apt-get install iverilog gtkwave
```

### macOS
```bash
brew install icarus-verilog gtkwave
```

## Running Simulations

### Quick Test - Windows PowerShell

```powershell
# Navigate to simulation directory
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q\fpga\sim

# Run all tests (PowerShell)
.\run_all_tests.ps1

# Or run all tests (CMD/Batch)
run_all_tests.bat

# Or run individual test
iverilog -g2012 -o gate_sim.exe ../quantum_gate_core.sv ../testbenches/quantum_gate_core_tb.sv
vvp gate_sim.exe

# View waveforms (optional)
gtkwave gate_sim.vcd
```

### Quick Test - Linux/macOS

```bash
# Navigate to simulation directory
cd quantum-fpga-simulator/fpga/sim

# Run all tests
chmod +x run_all_tests.sh
./run_all_tests.sh

# Or run individual test
iverilog -g2012 -o gate_sim ../quantum_gate_core.sv ../testbenches/quantum_gate_core_tb.sv
vvp gate_sim

# View waveforms (optional)
gtkwave gate_sim.vcd
```

### QEC Decoder Simulation

```bash
cd quantum-fpga-simulator/fpga/sim

# Compile QEC decoder testbench
iverilog -g2012 -o qec_sim \
    ../qec_decoder.sv \
    qec_decoder_tb.sv

# Run simulation
vvp qec_sim

# Check results
cat qec_results.txt
```

### Memory Module Simulation

```bash
cd quantum-fpga-simulator/fpga/sim

# Compile memory testbench
iverilog -g2012 -o mem_sim \
    ../statevector_memory.sv \
    statevector_memory_tb.sv

# Run simulation
vvp mem_sim
```

### Full System Simulation

```bash
cd quantum-fpga-simulator/fpga/sim

# Compile all modules
iverilog -g2012 -o system_sim \
    ../quantum_gate_core.sv \
    ../qec_decoder.sv \
    ../statevector_memory.sv \
    ../control_interface.sv \
    full_system_tb.sv

# Run complete system test
vvp system_sim

# View all signals
gtkwave system_sim.vcd
```

## Automated Testing

```bash
cd quantum-fpga-simulator/fpga/sim

# Run all tests
./run_all_tests.sh

# This will:
# - Compile all modules
# - Run all testbenches
# - Generate reports
# - Check for errors
```

## What Gets Simulated?

✅ **Quantum Gate Core**
- Complex number multiplication
- Parallel processing (simulated)
- Gate application logic

✅ **QEC Decoder**
- Syndrome lookup
- Correction pattern generation
- Decoder timing

✅ **Statevector Memory**
- BRAM behavior
- Dual-port access
- Read/write operations

✅ **Control Interface**
- AXI-Lite protocol
- Register access
- Command/response flow

## Performance Notes

**Simulation vs Real FPGA:**
- Simulation: Functional verification
- Real FPGA: Actual performance (100x faster)
- Simulation shows correct behavior, not real-time performance

## Viewing Waveforms

```bash
# After running simulation with VCD output
gtkwave gate_sim.vcd

# Or use built-in viewer
gtkwave -f gate_sim.vcd -a signals.gtkw
```

## Debugging

```bash
# Run with verbose output
vvp -v gate_sim

# Generate detailed logs
vvp gate_sim > simulation.log 2>&1

# Check for warnings
grep -i warning simulation.log
```

## CI/CD Integration

```yaml
# .github/workflows/test.yml
- name: Test SystemVerilog
  run: |
    sudo apt-get install iverilog
    cd fpga/sim
    ./run_all_tests.sh
```

## Next Steps

1. **Simulate First**: Verify design works
2. **Synthesize Later**: Deploy to real FPGA when ready
3. **Iterate**: Make changes and re-simulate quickly

