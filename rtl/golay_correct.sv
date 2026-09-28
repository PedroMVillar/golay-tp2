// Aplica el patrón de error a la palabra recibida y saca el mensaje.

module golay_correct (
    input  wire [23:0] i_rx, i_err,
    output wire [23:0] o_cw,
    output wire [11:0] o_msg,
    output wire        o_corrected
);

    assign o_cw        = i_rx ^ i_err;
    assign o_msg       = o_cw[23:12];
    assign o_corrected = |i_err;

endmodule
