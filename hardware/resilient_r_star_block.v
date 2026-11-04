// resilient_r_star_block.v
// Unidade de Co-processamento de Resiliência (RPU)
// Calcula o índice de resiliência R* = λ_adapt / λ_damage por comparação
// de magnitude (evita divisão em silício) e dispara tipping_point_trigger
// quando R* <= 1, ativando mitigação homeostática por hardware.
//
// Autor: Euzébio Soares dos Santos (com base em "Linguagem segura.md")
// Data: 2026-11-04

`timescale 1ns / 1ps

module resilient_r_star_block (
    input wire clk,                  // Clock do sistema
    input wire rst_n,                // Reset ativo em nível baixo
    input wire [15:0] lambda_adapt,  // Capacidade de adaptação atual (16 bits)
    input wire [15:0] lambda_damage, // Dano acumulado atual (16 bits)
    input wire [15:0] alu_error_in,  // Injeção de erro gerada pela ALU
    input wire [15:0] landauer_entropy, // Constante de Landauer injetada na operação

    output reg [15:0] next_damage,          // Próximo estado do dano
    output reg tipping_point_trigger        // Flag: 1 se R* <= 1
);

    // Fio com 1 bit extra para evitar overflow no somador de dano
    wire [16:0] internal_damage_sum;
    wire is_critical;

    // 1. Camada combinacional: soma de entropia e dano
    // next_damage = lambda_damage + alu_error_in + landauer_entropy
    assign internal_damage_sum = lambda_damage + alu_error_in + landauer_entropy;

    // 2. Comparador de limiar crítico (substitui a divisão de R*)
    // Se lambda_adapt <= next_damage (truncado a 16 bits), então R* <= 1.0
    assign is_critical = (lambda_adapt <= internal_damage_sum[15:0]) ? 1'b1 : 1'b0;

    // 3. Camada sequencial: atualização na borda de subida do clock
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            next_damage           <= 16'h0001; // dano mínimo (evita divisão por zero)
            tipping_point_trigger <= 1'b0;
        end else begin
            if (is_critical) begin
                tipping_point_trigger <= 1'b1;
                // Mitigação física homeostática: shift right por 2 bits
                // (simula a função psi(w) de atenuação do dano)
                next_damage <= internal_damage_sum[15:0] >> 2;
            end else begin
                tipping_point_trigger <= 1'b0;
                next_damage <= internal_damage_sum[15:0];
            end
        end
    end

endmodule
