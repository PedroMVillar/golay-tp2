// Interleaver seguido del deinterleaver, solo para el testbench.
// La salida del interleaver llega un ciclo tarde por su registro de
// salida, así que el deinterleaver sale del reset un ciclo después para
// que los dos conmutadores queden alineados.

module conv_chain #(
    parameter LAMBDA = 24,
    parameter J      = 1
) (
    input  wire i_clk,
    input  wire i_rst,
    input  wire i_bit,
    output wire o_bit
);

    wire  medio;
    logic rst_d;

    always_ff @(posedge i_clk)
        rst_d <= i_rst;

    conv_interleaver #(.LAMBDA(LAMBDA), .J(J)) u_int (
        .i_clk(i_clk),
        .i_rst(i_rst),
        .i_bit(i_bit),
        .o_bit(medio)
    );

    conv_deinterleaver #(.LAMBDA(LAMBDA), .J(J)) u_deint (
        .i_clk(i_clk),
        .i_rst(rst_d),
        .i_bit(medio),
        .o_bit(o_bit)
    );

endmodule
