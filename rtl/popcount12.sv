// Peso de Hamming de un vector de 12 bits.

module popcount12 (
    input  wire [11:0] i_vec,
    output wire [3:0]  o_weight
);

    logic [3:0] peso;

    always_comb begin
        peso = 0;
        for (int k = 0; k < 12; k++)
            peso = peso + i_vec[k];
    end

    assign o_weight = peso;

endmodule
