/**
 * Statevector Memory Module
 * 
 * Optimized memory structure for quantum statevector storage using FPGA BRAM.
 * Supports dual-port access for simultaneous read/write operations.
 * 
 * Key Features:
 * - Dual-port BRAM for parallel access
 * - Distributed across multiple BRAM blocks
 * - Complex number storage (real + imaginary)
 * - Configurable precision (32-bit or 64-bit)
 */

module statevector_memory #(
    parameter NUM_QUBITS = 5,
    parameter AMPLITUDE_WIDTH = 32,  // 32-bit float
    parameter NUM_STATES = 2**NUM_QUBITS
) (
    input  logic clk,
    
    // Port A (read/write)
    input  logic porta_en,
    input  logic porta_we,
    input  logic [$clog2(NUM_STATES)-1:0] porta_addr,
    input  logic [AMPLITUDE_WIDTH-1:0] porta_din_re,
    input  logic [AMPLITUDE_WIDTH-1:0] porta_din_im,
    output logic [AMPLITUDE_WIDTH-1:0] porta_dout_re,
    output logic [AMPLITUDE_WIDTH-1:0] porta_dout_im,
    
    // Port B (read-only for parallel access)
    input  logic portb_en,
    input  logic [$clog2(NUM_STATES)-1:0] portb_addr,
    output logic [AMPLITUDE_WIDTH-1:0] portb_dout_re,
    output logic [AMPLITUDE_WIDTH-1:0] portb_dout_im
);

    // BRAM for real parts
    (* ram_style = "block" *) logic [AMPLITUDE_WIDTH-1:0] bram_re [0:NUM_STATES-1];
    
    // BRAM for imaginary parts
    (* ram_style = "block" *) logic [AMPLITUDE_WIDTH-1:0] bram_im [0:NUM_STATES-1];
    
    // Initialize to |00...0⟩ state
    initial begin
        for (int i = 0; i < NUM_STATES; i++) begin
            if (i == 0) begin
                bram_re[i] = {1'b0, {(AMPLITUDE_WIDTH-1){1'b0}}} | ({{(AMPLITUDE_WIDTH-1){1'b0}}, 1'b1} << (AMPLITUDE_WIDTH-2)); // 1.0
                bram_im[i] = '0;
            end else begin
                bram_re[i] = '0;
                bram_im[i] = '0;
            end
        end
    end
    
    // Port A: Read/Write
    always_ff @(posedge clk) begin
        if (porta_en) begin
            if (porta_we) begin
                bram_re[porta_addr] <= porta_din_re;
                bram_im[porta_addr] <= porta_din_im;
            end
            porta_dout_re <= bram_re[porta_addr];
            porta_dout_im <= bram_im[porta_addr];
        end
    end
    
    // Port B: Read-only
    always_ff @(posedge clk) begin
        if (portb_en) begin
            portb_dout_re <= bram_re[portb_addr];
            portb_dout_im <= bram_im[portb_addr];
        end
    end

endmodule


/**
 * Statevector Memory Controller
 * 
 * Manages access to statevector memory with optimized addressing
 * for quantum gate operations.
 */
module statevector_controller #(
    parameter NUM_QUBITS = 5,
    parameter AMPLITUDE_WIDTH = 32
) (
    input  logic clk,
    input  logic rst_n,
    
    // Gate operation interface
    input  logic gate_start,
    input  logic [NUM_QUBITS-1:0] qubit_mask,
    output logic gate_ready,
    
    // Memory interface
    output logic mem_porta_en,
    output logic mem_porta_we,
    output logic [$clog2(2**NUM_QUBITS)-1:0] mem_porta_addr,
    output logic [AMPLITUDE_WIDTH-1:0] mem_porta_din_re,
    output logic [AMPLITUDE_WIDTH-1:0] mem_porta_din_im,
    input  logic [AMPLITUDE_WIDTH-1:0] mem_porta_dout_re,
    input  logic [AMPLITUDE_WIDTH-1:0] mem_porta_dout_im
);

    // Address generation for affected qubit operations
    logic [$clog2(2**NUM_QUBITS)-1:0] base_addr;
    logic [$clog2(2**NUM_QUBITS)-1:0] offset_addr;
    
    // State machine
    typedef enum logic [1:0] {
        IDLE,
        COMPUTE_ADDR,
        ACCESS,
        DONE
    } state_t;
    
    state_t state, next_state;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end
    
    always_comb begin
        next_state = state;
        case (state)
            IDLE: if (gate_start) next_state = COMPUTE_ADDR;
            COMPUTE_ADDR: next_state = ACCESS;
            ACCESS: next_state = DONE;
            DONE: next_state = IDLE;
            default: next_state = IDLE;
        endcase
    end
    
    // Address computation for qubit operations
    // Computes which amplitudes are affected by gate on specified qubits
    always_ff @(posedge clk) begin
        if (state == COMPUTE_ADDR) begin
            // Extract unaffected qubit bits
            base_addr <= base_addr & ~qubit_mask;
            
            // Generate offset for affected qubits
            offset_addr <= '0;
            for (int i = 0; i < NUM_QUBITS; i++) begin
                if (qubit_mask[i])
                    offset_addr[i] <= 1'b1;
            end
        end
    end
    
    assign mem_porta_addr = base_addr | offset_addr;
    assign mem_porta_en = (state == ACCESS);
    assign gate_ready = (state == IDLE);

endmodule

