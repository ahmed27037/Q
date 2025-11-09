/**
 * Testbench for Quantum Gate Core
 * 
 * Tests the FPGA quantum gate application module
 */

`timescale 1ns / 1ps

module quantum_gate_core_tb;

    // Parameters
    parameter NUM_QUBITS = 3;
    parameter AMPLITUDE_WIDTH = 32;
    parameter PARALLEL_UNITS = 4;
    parameter CLK_PERIOD = 10; // 100 MHz
    
    // Signals
    logic clk;
    logic rst_n;
    logic gate_start;
    logic [1:0] gate_size;
    logic [NUM_QUBITS-1:0] qubit_mask;
    logic gate_done;
    
    logic [AMPLITUDE_WIDTH-1:0] gate_matrix_re [0:15];
    logic [AMPLITUDE_WIDTH-1:0] gate_matrix_im [0:15];
    
    logic [NUM_QUBITS-1:0] sv_addr;
    logic sv_write_en;
    logic [AMPLITUDE_WIDTH-1:0] sv_write_data_re;
    logic [AMPLITUDE_WIDTH-1:0] sv_write_data_im;
    logic [AMPLITUDE_WIDTH-1:0] sv_read_data_re;
    logic [AMPLITUDE_WIDTH-1:0] sv_read_data_im;
    
    // DUT instantiation
    quantum_gate_core #(
        .NUM_QUBITS(NUM_QUBITS),
        .AMPLITUDE_WIDTH(AMPLITUDE_WIDTH),
        .PARALLEL_UNITS(PARALLEL_UNITS)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .gate_start(gate_start),
        .gate_size(gate_size),
        .qubit_mask(qubit_mask),
        .gate_done(gate_done),
        .gate_matrix_re(gate_matrix_re),
        .gate_matrix_im(gate_matrix_im),
        .sv_addr(sv_addr),
        .sv_write_en(sv_write_en),
        .sv_write_data_re(sv_write_data_re),
        .sv_write_data_im(sv_write_data_im),
        .sv_read_data_re(sv_read_data_re),
        .sv_read_data_im(sv_read_data_im)
    );
    
    // Clock generation
    initial begin
        clk = 0;
        forever #(CLK_PERIOD/2) clk = ~clk;
    end
    
    // Test sequence
    initial begin
        $display("=== Quantum Gate Core Testbench ===");
        
        // Initialize
        rst_n = 0;
        gate_start = 0;
        gate_size = 2'b00;
        qubit_mask = '0;
        
        // Initialize gate matrix (Hadamard gate)
        for (int i = 0; i < 16; i++) begin
            gate_matrix_re[i] = 32'h0;
            gate_matrix_im[i] = 32'h0;
        end
        
        // Hadamard matrix: 1/sqrt(2) * [[1, 1], [1, -1]]
        // Approximation: 0.707 ≈ 0x3f3504f3 (IEEE 754)
        gate_matrix_re[0] = 32'h3f3504f3;  // 0.707
        gate_matrix_re[1] = 32'h3f3504f3;  // 0.707
        gate_matrix_re[2] = 32'h3f3504f3;  // 0.707
        gate_matrix_re[3] = 32'hbf3504f3;  // -0.707
        
        // Reset
        #(CLK_PERIOD*2);
        rst_n = 1;
        #(CLK_PERIOD*2);
        
        // Test 1: Apply Hadamard gate to qubit 0
        $display("\n[TEST 1] Applying Hadamard gate to qubit 0");
        gate_size = 2'b00;  // Single qubit gate
        qubit_mask = 3'b001; // Qubit 0
        gate_start = 1;
        #CLK_PERIOD;
        gate_start = 0;
        
        // Wait for completion
        wait(gate_done);
        $display("Gate application complete");
        #(CLK_PERIOD*5);
        
        // Test 2: Apply CNOT gate
        $display("\n[TEST 2] Applying CNOT gate");
        gate_size = 2'b01;  // Two qubit gate
        qubit_mask = 3'b011; // Qubits 0 and 1
        
        // CNOT matrix
        for (int i = 0; i < 16; i++) begin
            gate_matrix_re[i] = 32'h0;
            gate_matrix_im[i] = 32'h0;
        end
        gate_matrix_re[0] = 32'h3f800000;  // 1.0
        gate_matrix_re[5] = 32'h3f800000;  // 1.0
        gate_matrix_re[11] = 32'h3f800000; // 1.0
        gate_matrix_re[14] = 32'h3f800000; // 1.0
        
        gate_start = 1;
        #CLK_PERIOD;
        gate_start = 0;
        
        wait(gate_done);
        $display("CNOT application complete");
        #(CLK_PERIOD*5);
        
        $display("\n=== All tests completed ===");
        $finish;
    end
    
    // Timeout
    initial begin
        #(CLK_PERIOD*1000);
        $display("ERROR: Testbench timeout");
        $finish;
    end
    
    // Monitor
    initial begin
        $monitor("Time=%0t state=%s addr=%0d done=%b", 
                 $time, dut.state.name(), sv_addr, gate_done);
    end

endmodule

