// Junta el interleaver y el deinterleaver para poder probarlos juntos.
// El interleaver entrega cada bit un ciclo tarde (tiene un registro a la
// salida), así que el deinterleaver arranca un ciclo después para que los
// dos conmutadores vayan sincronizados.

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
