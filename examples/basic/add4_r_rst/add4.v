module add4(
    input [3:0] a,
    input [3:0] b,
    input clk,
    input rst,
    output reg [3:0] o
);

always @ (posedge clk) begin
    if (rst)
        o <= 1'b0;
    else 
        o <= a + b;
end

endmodule