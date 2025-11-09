# Windows Setup Guide

Complete setup guide for Windows users.

## Quick Start (Windows PowerShell)

```powershell
# 1. Clone or download the repository
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q

# 2. Install Python dependencies
pip install -r requirements.txt
pip install -e .

# 3. Run examples (no directory changes needed - commands include cd)
python examples/grover.py
python examples/vqe.py
python benchmarks/benchmark.py
```

## Python Simulator Commands (Windows)

All commands include full paths - no need to worry about directories!

### Run Examples

```powershell
# Grover's Algorithm
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q
python examples/grover.py

# VQE
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q
python examples/vqe.py

# PennyLane Demo
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q
python examples/pennylane_demo.py

# QML Classifier
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q
python examples/qml_classifier.py

# Surface Code QEC
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q
python examples/surface_code.py
```

### Run Benchmarks

```powershell
# Simulator benchmarks
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q
python benchmarks/benchmark.py

# QEC benchmarks
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q
python benchmarks/qec_benchmark.py
```

## SystemVerilog Simulation (Windows)

### Install Icarus Verilog

1. Download: http://bleyer.org/icarus/
2. Run installer (installs to `C:\iverilog`)
3. Installer adds to PATH automatically
4. Restart PowerShell/CMD

### Verify Installation

```powershell
iverilog -v
vvp -v
```

### Run Simulations

**Option 1: PowerShell Script (Recommended)**
```powershell
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q\fpga\sim
.\run_all_tests.ps1
```

**Option 2: Batch File**
```cmd
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q\fpga\sim
run_all_tests.bat
```

**Option 3: Manual (step by step)**
```powershell
# Navigate to sim directory
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q\fpga\sim

# Test 1: Quantum Gate Core
iverilog -g2012 -o gate_sim.exe ../quantum_gate_core.sv ../testbenches/quantum_gate_core_tb.sv
vvp gate_sim.exe

# Test 2: QEC Decoder
iverilog -g2012 -o qec_sim.exe ../qec_decoder.sv qec_decoder_tb.sv
vvp qec_sim.exe

# Test 3: Memory Module
iverilog -g2012 -o mem_sim.exe ../statevector_memory.sv statevector_memory_tb.sv
vvp mem_sim.exe

# View waveforms (optional)
gtkwave gate_sim.vcd
```

## Common Issues

### Issue 1: "Cannot find path"

**Solution:** Use absolute path (replace YOUR_USERNAME)
```powershell
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q
```

### Issue 2: "iverilog not recognized"

**Solution:** Add to PATH manually
```powershell
$env:Path += ";C:\iverilog\bin"
```

Or permanently:
1. Search Windows for "Environment Variables"
2. Edit System PATH
3. Add `C:\iverilog\bin`
4. Restart PowerShell

### Issue 3: "Permission denied" for .ps1 scripts

**Solution:** Enable script execution
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 4: Wrong directory

**Solution:** All commands now include `cd` - just replace `YOUR_USERNAME` with your actual username

Example:
```powershell
# Replace this
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q

# With this (if your username is "john")
cd C:\Users\john\Documents\next_gen\Q
```

## Finding Your Path

```powershell
# Show current directory
pwd

# Show your username
$env:USERNAME

# Your project should be at:
C:\Users\$env:USERNAME\Documents\next_gen\Q
```

## Copy-Paste Ready Commands

**Replace YOUR_USERNAME with your actual username:**

```powershell
# Set your username (example uses "john")
$USERNAME = "john"  # CHANGE THIS TO YOUR USERNAME!

# Navigate to project
cd C:\Users\$USERNAME\Documents\next_gen\Q

# Run Python examples
python examples/grover.py
python examples/vqe.py
python benchmarks/benchmark.py

# Run SystemVerilog tests
cd C:\Users\$USERNAME\Documents\next_gen\Q\fpga\sim
.\run_all_tests.ps1
```

## All-in-One Setup Script

Save as `setup.ps1` and run:

```powershell
# Windows PowerShell Setup Script
$PROJECT_DIR = "C:\Users\$env:USERNAME\Documents\next_gen\Q"

Write-Host "Setting up Quantum FPGA Simulator..." -ForegroundColor Cyan

# Check if directory exists
if (Test-Path $PROJECT_DIR) {
    Write-Host "√ Project directory found" -ForegroundColor Green
    
    # Install Python dependencies
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    cd $PROJECT_DIR
    pip install -r requirements.txt
    pip install -e .
    
    Write-Host "√ Python setup complete" -ForegroundColor Green
    
    # Test Python
    Write-Host "Testing Python simulator..." -ForegroundColor Yellow
    python -c "from simulator.circuit import QuantumCircuit; print('√ Import successful')"
    
    # Check for Icarus Verilog
    $iverilog = Get-Command iverilog -ErrorAction SilentlyContinue
    if ($iverilog) {
        Write-Host "√ Icarus Verilog found" -ForegroundColor Green
    } else {
        Write-Host "! Icarus Verilog not found" -ForegroundColor Yellow
        Write-Host "  Download from: http://bleyer.org/icarus/" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Setup complete! Try these commands:" -ForegroundColor Green
    Write-Host "  python examples/grover.py" -ForegroundColor Cyan
    Write-Host "  python benchmarks/benchmark.py" -ForegroundColor Cyan
    
} else {
    Write-Host "× Project directory not found: $PROJECT_DIR" -ForegroundColor Red
    Write-Host "  Please update the path in this script" -ForegroundColor Yellow
}
```

Run it:
```powershell
.\setup.ps1
```

