#!/bin/bash
# Run all SystemVerilog simulations

set -e  # Exit on error

echo "================================"
echo "SystemVerilog Simulation Suite"
echo "================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

FAILED_TESTS=0
PASSED_TESTS=0

# Function to run a test
run_test() {
    local name=$1
    local sources=$2
    local testbench=$3
    
    echo ""
    echo "Testing: $name"
    echo "----------------------------"
    
    # Compile
    if iverilog -g2012 -o ${name}_sim $sources $testbench 2>&1 | tee ${name}_compile.log; then
        echo "✓ Compilation successful"
        
        # Run simulation
        if vvp ${name}_sim > ${name}_run.log 2>&1; then
            if grep -q "ERROR" ${name}_run.log; then
                echo -e "${RED}✗ Test FAILED${NC}"
                FAILED_TESTS=$((FAILED_TESTS + 1))
            else
                echo -e "${GREEN}✓ Test PASSED${NC}"
                PASSED_TESTS=$((PASSED_TESTS + 1))
            fi
            
            # Show summary
            cat ${name}_run.log
        else
            echo -e "${RED}✗ Simulation failed${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        echo -e "${RED}✗ Compilation failed${NC}"
        cat ${name}_compile.log
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Test 1: Quantum Gate Core
run_test "gate_core" \
    "../quantum_gate_core.sv" \
    "../testbenches/quantum_gate_core_tb.sv"

# Test 2: QEC Decoder
run_test "qec_decoder" \
    "../qec_decoder.sv" \
    "qec_decoder_tb.sv"

# Test 3: Statevector Memory
run_test "memory" \
    "../statevector_memory.sv" \
    "statevector_memory_tb.sv"

# Summary
echo ""
echo "================================"
echo "Test Summary"
echo "================================"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi

