// Multiplica un vector de 12 bits por B: es el XOR de las filas b_i
// donde el vector tiene un 1 (el bit 11 es el elemento 0).

module golay_mult_b (
    input  wire [11:0] i_vec,
    output wire [11:0] o_vec
);

    assign o_vec = ({12{i_vec[11]}} & 12'h98F)
                 ^ ({12{i_vec[10]}} & 12'h4E7)
                 ^ ({12{i_vec[9]}}  & 12'h357)
                 ^ ({12{i_vec[8]}}  & 12'hBE2)
                 ^ ({12{i_vec[7]}}  & 12'hDD1)
                 ^ ({12{i_vec[6]}}  & 12'h7CC)
                 ^ ({12{i_vec[5]}}  & 12'h53D)
                 ^ ({12{i_vec[4]}}  & 12'h2BE)
                 ^ ({12{i_vec[3]}}  & 12'h87B)
                 ^ ({12{i_vec[2]}}  & 12'hE74)
                 ^ ({12{i_vec[1]}}  & 12'hF1A)
                 ^ ({12{i_vec[0]}}  & 12'hEA9);

endmodule
