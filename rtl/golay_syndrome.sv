// Síndrome de la palabra recibida: s = r[23:12]·B xor r[11:0].

module golay_syndrome (
    input  wire [23:0] i_rx,
    output wire [11:0] o_syn
);

    wire [11:0] mb;

    golay_mult_b u_mult_b (
        .i_vec(i_rx[23:12]),
        .o_vec(mb)
    );

    assign o_syn = mb ^ i_rx[11:0];

endmodule
