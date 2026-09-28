// Prueba los doce candidatos vec ^ b_i y se queda con el primero que
// tenga peso <= 2. La fila b_i sale de pasar u_i por golay_mult_b.

module golay_row_search (
    input  wire [11:0] i_vec,
    output wire        o_found,
    output wire [3:0]  o_idx,
    output wire [11:0] o_res
);

    wire [11:0] b [0:11];
    wire [3:0]  w [0:11];

    genvar i;
    generate
        for (i = 0; i < 12; i = i + 1) begin : fila
            golay_mult_b u_b   (.i_vec(12'h800 >> i), .o_vec(b[i]));
            popcount12   u_pop (.i_vec(i_vec ^ b[i]), .o_weight(w[i]));
        end
    endgenerate

    logic        found;
    logic [3:0]  idx;
    logic [11:0] res;

    always_comb begin
        found = 0;
        idx   = 0;
        res   = 0;
        for (int k = 0; k < 12; k++) begin
            if (!found && w[k] <= 2) begin
                found = 1;
                idx   = k;
                res   = i_vec ^ b[k];
            end
        end
    end

    assign o_found = found;
    assign o_idx   = idx;
    assign o_res   = res;

endmodule
