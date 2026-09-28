// Arma el patrón de error según los cuatro casos del algoritmo.
// Si no entra en ninguno, levanta o_uncorrectable y deja el error en 0.

module golay_err_gen (
    input  wire [11:0] i_syn, i_q,
                       i_res_syn, i_res_q,
    input  wire [3:0]  i_w_syn, i_w_q,
                       i_idx_syn, i_idx_q,
    input  wire        i_found_syn, i_found_q,
    output wire [23:0] o_err,
    output wire        o_uncorrectable
);

    logic [23:0] err;
    logic        unc;

    always_comb begin
        err = 0;
        unc = 0;
        if (i_w_syn <= 3)
            err = {12'h000, i_syn};
        else if (i_found_syn)
            err = {12'h800 >> i_idx_syn, i_res_syn};
        else if (i_w_q <= 3)
            err = {i_q, 12'h000};
        else if (i_found_q)
            err = {i_res_q, 12'h800 >> i_idx_q};
        else
            unc = 1;
    end

    assign o_err           = err;
    assign o_uncorrectable = unc;

endmodule
