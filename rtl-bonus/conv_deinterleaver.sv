// Deinterleaver convolucional: la rama i es 
// shift register de (LAMBDA-1-i)*J bits, la última no tiene retardo.
// Sumando las dos partes, todas las ramas quedan con el mismo retardo.

module conv_deinterleaver #(
    parameter LAMBDA = 24,
    parameter J      = 1
) (
    input  wire i_clk,
    input  wire i_rst,
    input  wire i_bit,
    output reg  o_bit
);

    logic [$clog2(LAMBDA)-1:0] rama;
    wire  salida [0:LAMBDA-1];

    genvar i;
    generate
        for (i = 0; i < LAMBDA; i = i + 1) begin : ramas
            if ((LAMBDA - 1 - i) * J == 0) begin
                assign salida[i] = i_bit;
            end else begin
                logic [(LAMBDA-1-i)*J-1:0] sr;

                always_ff @(posedge i_clk) begin
                    if (i_rst)
                        sr <= 0;
                    else if (rama == i)
                        sr <= {sr, i_bit};   // entra i_bit y se pierde el bit de arriba
                end

                assign salida[i] = sr[(LAMBDA-1-i)*J-1];
            end
        end
    endgenerate

    always_ff @(posedge i_clk) begin
        if (i_rst) begin
            rama  <= 0;
            o_bit <= 0;
        end else begin
            o_bit <= salida[rama];
            rama  <= (rama == LAMBDA - 1) ? 0 : rama + 1;
        end
    end

endmodule
