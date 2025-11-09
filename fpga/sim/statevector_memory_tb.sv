/**
 * Testbench for Statevector Memory
 * 
 * Tests dual-port BRAM functionality
 */

`timescale 1ns / 1ps

module statevector_memory_tb;

    parameter NUM_QUBITS = 3;
    parameter AMPLITUDE_WIDTH = 32;
    parameter NUM_STATES = 2**NUM_QUBITS;
    
    logic clk;
    
    // Port A
    logic porta_en;
    logic porta_we;
    logic [$clog2(NUM_STATES)-1:0] porta_addr;
    logic [AMPLITUDE_WIDTH-1:0] porta_din_re;
    logic [AMPLITUDE_WIDTH-1:0] porta_din_im;
    logic [AMPLITUDE_WIDTH-1:0] porta_dout_re;
    logic [AMPLITUDE_WIDTH-1:0] porta_dout_im;
    
    // Port B
    logic portb_en;
    logic [$clog2(NUM_STATES)-1:0] portb_addr;
    logic [AMPLITUDE_WIDTH-1:0] portb_dout_re;
    logic [AMPLITUDE_WIDTH-1:0] portb_dout_im;
    
    // DUT
    statevector_memory #(
        .NUM_QUBITS(NUM_QUBITS),
        .AMPLITUDE_WIDTH(AMPLITUDE_WIDTH)
    ) dut (
        .clk(clk),
        .porta_en(porta_en),
        .porta_we(porta_we),
        .porta_addr(porta_addr),
        .porta_din_re(porta_din_re),
        .porta_din_im(porta_din_im),
        .porta_dout_re(porta_dout_re),
        .porta_dout_im(porta_dout_im),
        .portb_en(portb_en),
        .portb_addr(portb_addr),
        .portb_dout_re(portb_dout_re),
        .portb_dout_im(portb_dout_im)
    );
    
    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end
    
    // Test variables
    integer errors;
    integer i;
    
    // Test sequence
    initial begin
        $display("=== Statevector Memory Testbench ===");
        
        // Initialize
        porta_en = 0;
        porta_we = 0;
        porta_addr = 0;
        porta_din_re = 0;
        porta_din_im = 0;
        portb_en = 0;
        portb_addr = 0;
        errors = 0;
        
        #20;
        
        // Test 1: Read initial state (should be |000⟩)
        $display("\n[Test 1] Read initial state");
        porta_en = 1;
        porta_addr = 0;
        #10;
        if (porta_dout_re != 0 && porta_dout_im == 0) begin
            $display("  PASS: Initial state is |000⟩");
        end else begin
            $display("  FAIL: Initial state incorrect");
        end
        
        // Test 2: Write to memory
        $display("\n[Test 2] Write amplitude");
        porta_we = 1;
        porta_addr = 1;
        porta_din_re = 32'h3f000000;  // 0.5
        porta_din_im = 32'h3f000000;  // 0.5
        #10;
        porta_we = 0;
        #10;
        
        // Test 3: Read back
        $display("\n[Test 3] Read back written value");
        porta_addr = 1;
        #10;
        if (porta_dout_re == 32'h3f000000 && porta_dout_im == 32'h3f000000) begin
            $display("  PASS: Read matches write");
        end else begin
            $display("  FAIL: Read doesn't match write");
        end
        
        // Test 4: Dual-port access
        $display("\n[Test 4] Dual-port simultaneous read");
        porta_addr = 0;
        portb_en = 1;
        portb_addr = 1;
        #10;
        $display("  Port A[0]: re=%h im=%h", porta_dout_re, porta_dout_im);
        $display("  Port B[1]: re=%h im=%h", portb_dout_re, portb_dout_im);
        
        // Test 5: Write all states
        $display("\n[Test 5] Write all memory locations");
        for (i = 0; i < NUM_STATES; i = i + 1) begin
            porta_we = 1;
            porta_addr = i;
            porta_din_re = i * 100;
            porta_din_im = i * 200;
            #10;
        end
        porta_we = 0;
        
        // Test 6: Verify all states
        $display("\n[Test 6] Verify all memory locations");
        errors = 0;
        for (i = 0; i < NUM_STATES; i = i + 1) begin
            porta_addr = i;
            #10;
            if (porta_dout_re != i * 100 || porta_dout_im != i * 200) begin
                $display("  ERROR at address %0d", i);
                errors = errors + 1;
            end
        end
        
        if (errors == 0) begin
            $display("  PASS: All locations verified");
        end else begin
            $display("  FAIL: %0d errors found", errors);
        end
        
        $display("\n=== All memory tests completed ===");
        $finish;
    end
    
    // Timeout
    initial begin
        #5000;
        $display("ERROR: Testbench timeout!");
        $finish;
    end

endmodule

