@echo off
REM Batch script to run all SystemVerilog simulations
REM Windows compatible version

echo ================================
echo SystemVerilog Simulation Suite
echo ================================

set FAILED_TESTS=0
set PASSED_TESTS=0

REM Change to the script directory
cd /d "%~dp0"

echo.
echo Testing: Quantum Gate Core
echo ----------------------------
iverilog -g2012 -o gate_sim.exe ../quantum_gate_core.sv ../testbenches/quantum_gate_core_tb.sv > gate_compile.log 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Compilation successful
    vvp gate_sim.exe > gate_run.log 2>&1
    findstr /C:"ERROR" gate_run.log > nul
    if %ERRORLEVEL% EQU 0 (
        echo [FAIL] Test FAILED
        set /a FAILED_TESTS+=1
    ) else (
        echo [PASS] Test PASSED
        set /a PASSED_TESTS+=1
    )
    type gate_run.log
) else (
    echo [FAIL] Compilation failed
    type gate_compile.log
    set /a FAILED_TESTS+=1
)

echo.
echo Testing: QEC Decoder
echo ----------------------------
iverilog -g2012 -o qec_sim.exe ../qec_decoder.sv qec_decoder_tb.sv > qec_compile.log 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Compilation successful
    vvp qec_sim.exe > qec_run.log 2>&1
    findstr /C:"ERROR" qec_run.log > nul
    if %ERRORLEVEL% EQU 0 (
        echo [FAIL] Test FAILED
        set /a FAILED_TESTS+=1
    ) else (
        echo [PASS] Test PASSED
        set /a PASSED_TESTS+=1
    )
    type qec_run.log
) else (
    echo [FAIL] Compilation failed
    type qec_compile.log
    set /a FAILED_TESTS+=1
)

echo.
echo Testing: Memory Module
echo ----------------------------
iverilog -g2012 -o mem_sim.exe ../statevector_memory.sv statevector_memory_tb.sv > mem_compile.log 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Compilation successful
    vvp mem_sim.exe > mem_run.log 2>&1
    findstr /C:"ERROR" mem_run.log > nul
    if %ERRORLEVEL% EQU 0 (
        echo [FAIL] Test FAILED
        set /a FAILED_TESTS+=1
    ) else (
        echo [PASS] Test PASSED
        set /a PASSED_TESTS+=1
    )
    type mem_run.log
) else (
    echo [FAIL] Compilation failed
    type mem_compile.log
    set /a FAILED_TESTS+=1
)

echo.
echo ================================
echo Test Summary
echo ================================
echo Passed: %PASSED_TESTS%
echo Failed: %FAILED_TESTS%
echo.

if %FAILED_TESTS% EQU 0 (
    echo All tests passed!
    exit /b 0
) else (
    echo Some tests failed.
    exit /b 1
)

