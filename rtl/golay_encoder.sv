// Codificador: la palabra es el mensaje seguido de su paridad m·B.
// Latencia de un ciclo.

module golay_encoder (
    input  wire        i_clk, i_rst,
    input  wire [11:0] i_msg,
    output reg  [23:0] o_cw
);

    wire [11:0] paridad;

    golay_mult_b u_mult_b (
        .i_vec(i_msg),
        .o_vec(paridad)
    );

    always_ff @(posedge i_clk) begin
        if (i_rst)
            o_cw <= 0;
        else
            o_cw <= {i_msg, paridad};
    end

endmodule
