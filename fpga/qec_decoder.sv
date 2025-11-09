/**
 * QEC Decoder - Steane Code Implementation
 * 
 * Hardware-accelerated quantum error correction decoder for [[7,1,3]] Steane code.
 * Uses lookup table for O(1) syndrome decoding.
 * 
 * Key Features:
 * - Sub-microsecond latency decoding
 * - Lookup table stored in distributed RAM
 * - Parallel syndrome processing
 * - Supports both X and Z error correction
 */

module qec_steane_decoder (
    input  logic clk,
    input  logic rst_n,
    
    // Control
    input  logic decode_start,
    output logic decode_done,
    
    // Syndrome input (3 X + 3 Z stabilizers)
    input  logic [2:0] syndrome_x,
    input  logic [2:0] syndrome_z,
    
    // Correction output (which qubits to correct)
    output logic [6:0] correction_x,  // 7 qubits
    output logic [6:0] correction_z   // 7 qubits
);

    // Syndrome lookup tables - separate arrays for Icarus Verilog compatibility
    // Maps 6-bit syndrome to correction pattern
    logic [6:0] lookup_x [0:63];
    logic [6:0] lookup_z [0:63];
    
    // Lookup table initialization
    initial begin
        integer i;
        
        // Initialize all to no correction
        for (i = 0; i < 64; i = i + 1) begin
            lookup_x[i] = 7'b0000000;
            lookup_z[i] = 7'b0000000;
        end
        
        // No error
        lookup_x[6'b000000] = 7'b0000000;
        lookup_z[6'b000000] = 7'b0000000;
        
        // Single X errors (detected by Z stabilizers)
        lookup_x[6'b000111] = 7'b0000001;
        lookup_z[6'b000111] = 7'b0000000;
        
        lookup_x[6'b000011] = 7'b0000010;
        lookup_z[6'b000011] = 7'b0000000;
        
        lookup_x[6'b000101] = 7'b0000100;
        lookup_z[6'b000101] = 7'b0000000;
        
        lookup_x[6'b000110] = 7'b0001000;
        lookup_z[6'b000110] = 7'b0000000;
        
        lookup_x[6'b000001] = 7'b0010000;
        lookup_z[6'b000001] = 7'b0000000;
        
        lookup_x[6'b000010] = 7'b0100000;
        lookup_z[6'b000010] = 7'b0000000;
        
        lookup_x[6'b000100] = 7'b1000000;
        lookup_z[6'b000100] = 7'b0000000;
        
        // Single Z errors (detected by X stabilizers)
        lookup_x[6'b111000] = 7'b0000000;
        lookup_z[6'b111000] = 7'b0000001;
        
        lookup_x[6'b011000] = 7'b0000000;
        lookup_z[6'b011000] = 7'b0000010;
        
        lookup_x[6'b101000] = 7'b0000000;
        lookup_z[6'b101000] = 7'b0000100;
        
        lookup_x[6'b110000] = 7'b0000000;
        lookup_z[6'b110000] = 7'b0001000;
        
        lookup_x[6'b001000] = 7'b0000000;
        lookup_z[6'b001000] = 7'b0010000;
        
        lookup_x[6'b010000] = 7'b0000000;
        lookup_z[6'b010000] = 7'b0100000;
        
        lookup_x[6'b100000] = 7'b0000000;
        lookup_z[6'b100000] = 7'b1000000;
        
        // Y errors (both X and Z components)
        lookup_x[6'b111111] = 7'b0000001;
        lookup_z[6'b111111] = 7'b0000001;
        
        lookup_x[6'b011011] = 7'b0000010;
        lookup_z[6'b011011] = 7'b0000010;
        
        lookup_x[6'b101101] = 7'b0000100;
        lookup_z[6'b101101] = 7'b0000100;
        
        lookup_x[6'b110110] = 7'b0001000;
        lookup_z[6'b110110] = 7'b0001000;
    end
    
    // Combine syndrome into single address
    logic [5:0] syndrome_addr;
    assign syndrome_addr = {syndrome_x, syndrome_z};
    
    // State machine for decoding
    typedef enum logic [1:0] {
        IDLE,
        LOOKUP,
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
            IDLE: if (decode_start) next_state = LOOKUP;
            LOOKUP: next_state = DONE;
            DONE: next_state = IDLE;
            default: next_state = IDLE;
        endcase
    end
    
    // Lookup and output
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            correction_x <= 7'b0000000;
            correction_z <= 7'b0000000;
        end else if (state == LOOKUP) begin
            correction_x <= lookup_x[syndrome_addr];
            correction_z <= lookup_z[syndrome_addr];
        end
    end
    
    assign decode_done = (state == DONE);

endmodule


/**
 * QEC Feedback Controller
 * 
 * Manages the complete error correction cycle:
 * 1. Measure syndrome
 * 2. Decode correction
 * 3. Apply correction
 * 
 * Achieves sub-microsecond cycle time on FPGA
 */
module qec_feedback_controller (
    input  logic clk,
    input  logic rst_n,
    
    // Control
    input  logic cycle_start,
    output logic cycle_done,
    
    // Syndrome measurement interface
    output logic measure_start,
    input  logic measure_done,
    input  logic [2:0] syndrome_x,
    input  logic [2:0] syndrome_z,
    
    // Correction application interface
    output logic apply_start,
    input  logic apply_done,
    output logic [6:0] correction_x,
    output logic [6:0] correction_z
);

    // Decoder instance
    logic decode_start, decode_done;
    
    qec_steane_decoder decoder (
        .clk(clk),
        .rst_n(rst_n),
        .decode_start(decode_start),
        .decode_done(decode_done),
        .syndrome_x(syndrome_x),
        .syndrome_z(syndrome_z),
        .correction_x(correction_x),
        .correction_z(correction_z)
    );
    
    // State machine
    typedef enum logic [2:0] {
        IDLE,
        MEASURE,
        DECODE,
        APPLY,
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
        measure_start = 1'b0;
        decode_start = 1'b0;
        apply_start = 1'b0;
        cycle_done = 1'b0;
        
        case (state)
            IDLE: begin
                if (cycle_start) next_state = MEASURE;
            end
            
            MEASURE: begin
                measure_start = 1'b1;
                if (measure_done) next_state = DECODE;
            end
            
            DECODE: begin
                decode_start = 1'b1;
                if (decode_done) next_state = APPLY;
            end
            
            APPLY: begin
                apply_start = 1'b1;
                if (apply_done) next_state = DONE;
            end
            
            DONE: begin
                cycle_done = 1'b1;
                next_state = IDLE;
            end
        endcase
    end

endmodule

