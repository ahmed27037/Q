/**
 * Control Interface - Host Communication
 * 
 * Provides interface between host computer and FPGA quantum accelerator.
 * Supports PCIe, AXI, or USB communication protocols.
 * 
 * Key Features:
 * - Command/response protocol
 * - Circuit upload interface
 * - Result readback
 * - Status monitoring
 */

module control_interface #(
    parameter DATA_WIDTH = 32,
    parameter ADDR_WIDTH = 16
) (
    input  logic clk,
    input  logic rst_n,
    
    // AXI-Lite interface (can be adapted to PCIe/USB)
    input  logic [ADDR_WIDTH-1:0] s_axi_awaddr,
    input  logic s_axi_awvalid,
    output logic s_axi_awready,
    
    input  logic [DATA_WIDTH-1:0] s_axi_wdata,
    input  logic s_axi_wvalid,
    output logic s_axi_wready,
    
    output logic [1:0] s_axi_bresp,
    output logic s_axi_bvalid,
    input  logic s_axi_bready,
    
    input  logic [ADDR_WIDTH-1:0] s_axi_araddr,
    input  logic s_axi_arvalid,
    output logic s_axi_arready,
    
    output logic [DATA_WIDTH-1:0] s_axi_rdata,
    output logic [1:0] s_axi_rresp,
    output logic s_axi_rvalid,
    input  logic s_axi_rready,
    
    // Quantum core interface
    output logic gate_start,
    input  logic gate_done,
    output logic [1:0] gate_type,
    output logic [31:0] gate_params,
    
    input  logic [31:0] result_data,
    input  logic result_valid
);

    // Register map
    localparam ADDR_CONTROL   = 16'h0000;  // Control register
    localparam ADDR_STATUS    = 16'h0004;  // Status register
    localparam ADDR_GATE_TYPE = 16'h0008;  // Gate type
    localparam ADDR_GATE_PARAMS = 16'h000C; // Gate parameters
    localparam ADDR_RESULT    = 16'h0010;  // Result readback
    
    // Control registers
    logic [DATA_WIDTH-1:0] ctrl_reg;
    logic [DATA_WIDTH-1:0] status_reg;
    logic [DATA_WIDTH-1:0] gate_type_reg;
    logic [DATA_WIDTH-1:0] gate_params_reg;
    logic [DATA_WIDTH-1:0] result_reg;
    
    // Write logic
    logic write_en;
    logic [ADDR_WIDTH-1:0] write_addr;
    
    assign write_en = s_axi_awvalid && s_axi_wvalid && s_axi_awready && s_axi_wready;
    assign write_addr = s_axi_awaddr;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ctrl_reg <= '0;
            gate_type_reg <= '0;
            gate_params_reg <= '0;
            s_axi_awready <= 1'b1;
            s_axi_wready <= 1'b1;
            s_axi_bvalid <= 1'b0;
        end else begin
            // Default
            s_axi_awready <= 1'b1;
            s_axi_wready <= 1'b1;
            
            if (write_en) begin
                case (write_addr)
                    ADDR_CONTROL: ctrl_reg <= s_axi_wdata;
                    ADDR_GATE_TYPE: gate_type_reg <= s_axi_wdata;
                    ADDR_GATE_PARAMS: gate_params_reg <= s_axi_wdata;
                    default: ;
                endcase
                s_axi_bvalid <= 1'b1;
                s_axi_bresp <= 2'b00; // OKAY
            end
            
            if (s_axi_bvalid && s_axi_bready)
                s_axi_bvalid <= 1'b0;
        end
    end
    
    // Read logic
    logic read_en;
    logic [ADDR_WIDTH-1:0] read_addr;
    
    assign read_en = s_axi_arvalid && s_axi_arready;
    assign read_addr = s_axi_araddr;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s_axi_rdata <= '0;
            s_axi_rvalid <= 1'b0;
            s_axi_arready <= 1'b1;
        end else begin
            s_axi_arready <= 1'b1;
            
            if (read_en) begin
                case (read_addr)
                    ADDR_CONTROL: s_axi_rdata <= ctrl_reg;
                    ADDR_STATUS: s_axi_rdata <= status_reg;
                    ADDR_GATE_TYPE: s_axi_rdata <= gate_type_reg;
                    ADDR_GATE_PARAMS: s_axi_rdata <= gate_params_reg;
                    ADDR_RESULT: s_axi_rdata <= result_reg;
                    default: s_axi_rdata <= '0;
                endcase
                s_axi_rvalid <= 1'b1;
                s_axi_rresp <= 2'b00; // OKAY
            end
            
            if (s_axi_rvalid && s_axi_rready)
                s_axi_rvalid <= 1'b0;
        end
    end
    
    // Status register
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            status_reg <= '0;
            result_reg <= '0;
        end else begin
            status_reg[0] <= gate_done;
            status_reg[1] <= result_valid;
            
            if (result_valid)
                result_reg <= result_data;
        end
    end
    
    // Output to quantum core
    assign gate_start = ctrl_reg[0];
    assign gate_type = gate_type_reg[1:0];
    assign gate_params = gate_params_reg;

endmodule


/**
 * Python Interface Example
 * 
 * This can be accessed from Python using:
 * - PCIe: pcie-dma or similar drivers
 * - USB: libusb or pyusb
 * - Ethernet: UDP/TCP sockets
 * 
 * Example Python code:
 * 
 * import mmap
 * import os
 * 
 * class FPGAQuantumAccelerator:
 *     def __init__(self, device_path='/dev/fpga0'):
 *         self.fd = os.open(device_path, os.O_RDWR | os.O_SYNC)
 *         self.mem = mmap.mmap(self.fd, 0)
 *     
 *     def apply_gate(self, gate_type, params):
 *         # Write gate type
 *         self.write_reg(0x08, gate_type)
 *         # Write parameters
 *         self.write_reg(0x0C, params)
 *         # Start execution
 *         self.write_reg(0x00, 0x01)
 *         # Wait for completion
 *         while not self.read_reg(0x04) & 0x01:
 *             pass
 *         # Read result
 *         return self.read_reg(0x10)
 */

