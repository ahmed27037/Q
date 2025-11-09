/**
 * Quantum Gate Core - FPGA Implementation
 * 
 * This module implements parallel quantum gate application using FPGA resources.
 * Performs complex matrix-vector multiplication for quantum statevector updates.
 * 
 * Key Features:
 * - Parallel processing of multiple amplitudes
 * - Pipelined complex multiplication
 * - Configurable gate size (2x2, 4x4, etc.)
 * - Uses DSP slices for efficient multiplication
 */

module quantum_gate_core #(
    parameter NUM_QUBITS = 5,
    parameter AMPLITUDE_WIDTH = 32,  // 32-bit float or 64-bit double
    parameter PARALLEL_UNITS = 4     // Number of parallel multiplication units
) (
    input  logic clk,
    input  logic rst_n,
    
    // Control signals
    input  logic gate_start,
    input  logic [1:0] gate_size,      // 0=1q, 1=2q, 2=3q
    input  logic [NUM_QUBITS-1:0] qubit_mask,
    output logic gate_done,
    
    // Gate matrix input (real and imaginary parts)
    input  logic [AMPLITUDE_WIDTH-1:0] gate_matrix_re [0:15],
    input  logic [AMPLITUDE_WIDTH-1:0] gate_matrix_im [0:15],
    
    // Statevector memory interface
    output logic [NUM_QUBITS-1:0] sv_addr,
    output logic sv_write_en,
    output logic [AMPLITUDE_WIDTH-1:0] sv_write_data_re,
    output logic [AMPLITUDE_WIDTH-1:0] sv_write_data_im,
    input  logic [AMPLITUDE_WIDTH-1:0] sv_read_data_re,
    input  logic [AMPLITUDE_WIDTH-1:0] sv_read_data_im
);

    // State machine
    typedef enum logic [2:0] {
        IDLE,
        READ_AMPLITUDES,
        COMPUTE,
        WRITE_RESULTS,
        DONE
    } state_t;
    
    state_t state, next_state;
    
    // Internal registers
    logic [NUM_QUBITS-1:0] current_addr;
    logic [3:0] gate_dim;  // Gate dimension (2, 4, 8, 16)
    logic [3:0] compute_idx;
    
    // Complex multiplication result buffers
    logic [AMPLITUDE_WIDTH-1:0] result_re [0:PARALLEL_UNITS-1];
    logic [AMPLITUDE_WIDTH-1:0] result_im [0:PARALLEL_UNITS-1];
    
    // Statevector amplitude cache
    logic [AMPLITUDE_WIDTH-1:0] amplitude_cache_re [0:15];
    logic [AMPLITUDE_WIDTH-1:0] amplitude_cache_im [0:15];
    
    // Gate dimension decoder
    always_comb begin
        case (gate_size)
            2'b00: gate_dim = 2;   // Single qubit
            2'b01: gate_dim = 4;   // Two qubit
            2'b10: gate_dim = 8;   // Three qubit
            2'b11: gate_dim = 16;  // Four qubit
            default: gate_dim = 2;
        endcase
    end
    
    // State machine transitions
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end
    
    always_comb begin
        next_state = state;
        case (state)
            IDLE: begin
                if (gate_start)
                    next_state = READ_AMPLITUDES;
            end
            
            READ_AMPLITUDES: begin
                if (current_addr >= gate_dim)
                    next_state = COMPUTE;
            end
            
            COMPUTE: begin
                if (compute_idx >= gate_dim)
                    next_state = WRITE_RESULTS;
            end
            
            WRITE_RESULTS: begin
                if (current_addr >= gate_dim)
                    next_state = DONE;
            end
            
            DONE: begin
                next_state = IDLE;
            end
        endcase
    end
    
    // Address generation
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_addr <= '0;
        end else begin
            case (state)
                IDLE: begin
                    current_addr <= '0;
                end
                
                READ_AMPLITUDES: begin
                    if (current_addr < gate_dim)
                        current_addr <= current_addr + 1;
                end
                
                WRITE_RESULTS: begin
                    if (current_addr < gate_dim)
                        current_addr <= current_addr + 1;
                end
                
                default: current_addr <= current_addr;
            endcase
        end
    end
    
    // Complex multiplication units (parallel)
    genvar i;
    generate
        for (i = 0; i < PARALLEL_UNITS; i++) begin : mult_units
            complex_multiplier #(
                .WIDTH(AMPLITUDE_WIDTH)
            ) cmult (
                .clk(clk),
                .a_re(gate_matrix_re[i]),
                .a_im(gate_matrix_im[i]),
                .b_re(amplitude_cache_re[i]),
                .b_im(amplitude_cache_im[i]),
                .result_re(result_re[i]),
                .result_im(result_im[i])
            );
        end
    endgenerate
    
    // Output assignments
    assign sv_addr = current_addr;
    assign gate_done = (state == DONE);
    assign sv_write_en = (state == WRITE_RESULTS);

endmodule


/**
 * Complex Multiplier
 * 
 * Implements: (a_re + j*a_im) * (b_re + j*b_im)
 *           = (a_re*b_re - a_im*b_im) + j*(a_re*b_im + a_im*b_re)
 * 
 * Uses DSP slices for efficient multiplication
 */
module complex_multiplier #(
    parameter WIDTH = 32
) (
    input  logic clk,
    input  logic [WIDTH-1:0] a_re,
    input  logic [WIDTH-1:0] a_im,
    input  logic [WIDTH-1:0] b_re,
    input  logic [WIDTH-1:0] b_im,
    output logic [WIDTH-1:0] result_re,
    output logic [WIDTH-1:0] result_im
);

    // Pipeline registers for DSP
    logic [WIDTH-1:0] mult1, mult2, mult3, mult4;
    
    // Stage 1: Multiply (uses DSP slices)
    always_ff @(posedge clk) begin
        mult1 <= a_re * b_re;  // Real * Real
        mult2 <= a_im * b_im;  // Imag * Imag
        mult3 <= a_re * b_im;  // Real * Imag
        mult4 <= a_im * b_re;  // Imag * Real
    end
    
    // Stage 2: Add/Subtract
    always_ff @(posedge clk) begin
        result_re <= mult1 - mult2;  // Real part
        result_im <= mult3 + mult4;  // Imaginary part
    end

endmodule

