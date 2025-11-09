/**
 * Testbench for QEC Decoder
 * 
 * Tests the Steane code decoder with various syndromes
 */

`timescale 1ns / 1ps

module qec_decoder_tb;

    // Clock and reset
    logic clk;
    logic rst_n;
    
    // Decoder signals
    logic decode_start;
    logic decode_done;
    logic [2:0] syndrome_x;
    logic [2:0] syndrome_z;
    logic [6:0] correction_x;
    logic [6:0] correction_z;
    
    // DUT
    qec_steane_decoder dut (
        .clk(clk),
        .rst_n(rst_n),
        .decode_start(decode_start),
        .decode_done(decode_done),
        .syndrome_x(syndrome_x),
        .syndrome_z(syndrome_z),
        .correction_x(correction_x),
        .correction_z(correction_z)
    );
    
    // Clock generation (100 MHz)
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end
    
    // Test counter
    int test_count = 0;
    int pass_count = 0;
    int fail_count = 0;
    
    // Test task
    task test_syndrome(
        input [2:0] syn_x,
        input [2:0] syn_z,
        input [6:0] expected_corr_x,
        input [6:0] expected_corr_z,
        input string description
    );
        test_count++;
        syndrome_x = syn_x;
        syndrome_z = syn_z;
        decode_start = 1;
        #10;
        decode_start = 0;
        
        // Wait for completion
        wait(decode_done);
        #10;
        
        // Check results
        if (correction_x == expected_corr_x && correction_z == expected_corr_z) begin
            $display("[PASS] Test %0d: %s", test_count, description);
            pass_count++;
        end else begin
            $display("[FAIL] Test %0d: %s", test_count, description);
            $display("  Expected: X=%07b Z=%07b", expected_corr_x, expected_corr_z);
            $display("  Got:      X=%07b Z=%07b", correction_x, correction_z);
            fail_count++;
        end
        
        #20; // Wait between tests
    endtask
    
    // Main test sequence
    initial begin
        $display("=== QEC Decoder Testbench ===");
        $display("Testing Steane Code Decoder");
        
        // Initialize
        rst_n = 0;
        decode_start = 0;
        syndrome_x = 3'b000;
        syndrome_z = 3'b000;
        
        #20;
        rst_n = 1;
        #20;
        
        // Test 1: No error
        test_syndrome(
            3'b000, 3'b000,
            7'b0000000, 7'b0000000,
            "No error syndrome"
        );
        
        // Test 2: X error on qubit 0
        test_syndrome(
            3'b000, 3'b111,
            7'b0000001, 7'b0000000,
            "X error on qubit 0"
        );
        
        // Test 3: X error on qubit 1
        test_syndrome(
            3'b000, 3'b011,
            7'b0000010, 7'b0000000,
            "X error on qubit 1"
        );
        
        // Test 4: Z error on qubit 0
        test_syndrome(
            3'b111, 3'b000,
            7'b0000000, 7'b0000001,
            "Z error on qubit 0"
        );
        
        // Test 5: Z error on qubit 1
        test_syndrome(
            3'b011, 3'b000,
            7'b0000000, 7'b0000010,
            "Z error on qubit 1"
        );
        
        // Test 6: Y error on qubit 0 (X and Z)
        test_syndrome(
            3'b111, 3'b111,
            7'b0000001, 7'b0000001,
            "Y error on qubit 0"
        );
        
        // Summary
        $display("");
        $display("=== Test Summary ===");
        $display("Total tests: %0d", test_count);
        $display("Passed:      %0d", pass_count);
        $display("Failed:      %0d", fail_count);
        
        if (fail_count == 0) begin
            $display("All tests PASSED!");
        end else begin
            $display("Some tests FAILED!");
        end
        
        $finish;
    end
    
    // Timeout
    initial begin
        #10000;
        $display("ERROR: Testbench timeout!");
        $finish;
    end

endmodule

