// Decodificador completo, pipeline de tres etapas (latencia 3):
//   E1: síndrome
//   E2: q = s·B, pesos y búsquedas sobre s y q
//   E3: patrón de error y corrección
// Entra una palabra por ciclo y sale decodificada 3 ciclos después.

module golay_decoder (
    input  wire        i_clk, i_rst,
    input  wire [23:0] i_rx,
    output reg  [11:0] o_msg,
    output reg  [23:0] o_err,
    output reg         o_corrected,
    output reg         o_uncorrectable
);

    // ---------------- E1: síndrome
    // Si la palabra llega sin errores, s da 0.
    wire [11:0] syn;

    golay_syndrome u_syndrome (
        .i_rx(i_rx),
        .o_syn(syn)
    );

    // r viaja por el pipeline junto con s porque recién se corrige en E3
    logic [23:0] r1;
    logic [11:0] s1;

    always_ff @(posedge i_clk) begin
        if (i_rst) begin
            r1 <= 0;
            s1 <= 0;
        end else begin
            r1 <= i_rx;
            s1 <= syn;
        end
    end

    // ---------------- E2: todo lo que necesitan los cuatro casos
    // Con s se miran los casos 1 y 2, con q = s·B los casos 3 y 4.
    // Se calcula todo en paralelo y la decisión se toma en E3.
    wire [11:0] q;
    wire [3:0]  w_s, w_q;
    wire        found_s, found_q;
    wire [3:0]  idx_s, idx_q;
    wire [11:0] res_s, res_q;

    golay_mult_b u_mult_b (
        .i_vec(s1),
        .o_vec(q)
    );

    popcount12 u_pop_s (.i_vec(s1), .o_weight(w_s));
    popcount12 u_pop_q (.i_vec(q),  .o_weight(w_q));

    golay_row_search u_search_s (
        .i_vec(s1),
        .o_found(found_s),
        .o_idx(idx_s),
        .o_res(res_s)
    );

    golay_row_search u_search_q (
        .i_vec(q),
        .o_found(found_q),
        .o_idx(idx_q),
        .o_res(res_q)
    );

    // s también se registra acá porque err_gen lo usa en el caso 1
    logic [23:0] r2;
    logic [11:0] s2, q2, res_s2, res_q2;
    logic [3:0]  w_s2, w_q2, idx_s2, idx_q2;
    logic        found_s2, found_q2;

    always_ff @(posedge i_clk) begin
        if (i_rst) begin
            r2       <= 0;
            s2       <= 0;
            q2       <= 0;
            w_s2     <= 0;
            w_q2     <= 0;
            found_s2 <= 0;
            found_q2 <= 0;
            idx_s2   <= 0;
            idx_q2   <= 0;
            res_s2   <= 0;
            res_q2   <= 0;
        end else begin
            r2       <= r1;
            s2       <= s1;
            q2       <= q;
            w_s2     <= w_s;
            w_q2     <= w_q;
            found_s2 <= found_s;
            found_q2 <= found_q;
            idx_s2   <= idx_s;
            idx_q2   <= idx_q;
            res_s2   <= res_s;
            res_q2   <= res_q;
        end
    end

    // ---------------- E3: decisión y corrección
    // err_gen elige el caso y arma e; correct hace r xor e.
    // En el caso 5 e queda en 0 y o_msg/o_err no valen nada.
    wire [23:0] err;
    wire        unc;
    wire [23:0] cw;
    wire [11:0] msg;
    wire        corrected;

    golay_err_gen u_err_gen (
        .i_syn(s2),
        .i_q(q2),
        .i_res_syn(res_s2),
        .i_res_q(res_q2),
        .i_w_syn(w_s2),
        .i_w_q(w_q2),
        .i_idx_syn(idx_s2),
        .i_idx_q(idx_q2),
        .i_found_syn(found_s2),
        .i_found_q(found_q2),
        .o_err(err),
        .o_uncorrectable(unc)
    );

    golay_correct u_correct (
        .i_rx(r2),
        .i_err(err),
        .o_cw(cw),
        .o_msg(msg),
        .o_corrected(corrected)
    );

    always_ff @(posedge i_clk) begin
        if (i_rst) begin
            o_msg           <= 0;
            o_err           <= 0;
            o_corrected     <= 0;
            o_uncorrectable <= 0;
        end else begin
            o_msg           <= msg;
            o_err           <= err;
            o_corrected     <= corrected;
            o_uncorrectable <= unc;
        end
    end

endmodule
