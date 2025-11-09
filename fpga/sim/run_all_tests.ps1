# PowerShell script to run all SystemVerilog simulations
# Windows compatible version

Write-Host "================================" -ForegroundColor Cyan
Write-Host "SystemVerilog Simulation Suite" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$FailedTests = 0
$PassedTests = 0

function Run-Test {
    param(
        [string]$Name,
        [string[]]$Sources,
        [string]$Testbench
    )
    
    Write-Host ""
    Write-Host "Testing: $Name" -ForegroundColor Yellow
    Write-Host "----------------------------"
    
    # Compile
    $compileOutput = & iverilog -g2012 -o "${Name}_sim" @Sources $Testbench 2>&1
    $compileOutput | Out-File -FilePath "${Name}_compile.log"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "√ Compilation successful" -ForegroundColor Green
        
        # Run simulation
        $runOutput = & vvp "${Name}_sim" 2>&1
        $runOutput | Out-File -FilePath "${Name}_run.log"
        
        # Check for actual test failures (case-sensitive "ERROR" or "FAIL" in uppercase)
        if ($runOutput -cmatch "\b(ERROR|FAIL)\b" -and $runOutput -notmatch "Failed:\s+0") {
            Write-Host "× Test FAILED" -ForegroundColor Red
            $script:FailedTests++
        } else {
            Write-Host "√ Test PASSED" -ForegroundColor Green
            $script:PassedTests++
        }
        
        # Show output
        Write-Host $runOutput
    } else {
        Write-Host "× Compilation failed" -ForegroundColor Red
        Get-Content "${Name}_compile.log"
        $script:FailedTests++
    }
}

# Change to fpga/sim directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Test 1: Quantum Gate Core
Run-Test -Name "gate_core" `
    -Sources @("../quantum_gate_core.sv") `
    -Testbench "../testbenches/quantum_gate_core_tb.sv"

# Test 2: QEC Decoder
Run-Test -Name "qec_decoder" `
    -Sources @("../qec_decoder.sv") `
    -Testbench "qec_decoder_tb.sv"

# Test 3: Statevector Memory
Run-Test -Name "memory" `
    -Sources @("../statevector_memory.sv") `
    -Testbench "statevector_memory_tb.sv"

# Summary
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Passed: $PassedTests" -ForegroundColor Green
Write-Host "Failed: $FailedTests" -ForegroundColor Red
Write-Host ""

if ($FailedTests -eq 0) {
    Write-Host "All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some tests failed." -ForegroundColor Red
    exit 1
}

