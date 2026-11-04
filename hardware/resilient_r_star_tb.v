// resilient_r_star_tb.v
// Testbench da Unidade de Co-processamento de Resiliência (RPU)
// Gera estímulos temporizados e monitora o gatilho homeostático.
//
// Autor: Euzébio Soares dos Santos (com base em "Linguagem segura.md")
// Data: 2026-11-04

`timescale 1ns / 1ps

module resilient_r_star_tb;

    // Sinais de estímulo (entradas do módulo de teste)
    reg clk;
    reg rst_n;
    reg [15:0] lambda_adapt;
    reg [15:0] lambda_damage;
    reg [15:0] alu_error_in;
    reg [15:0] landauer_entropy;

    // Sinais de monitoramento (saídas)
    wire [15:0] next_damage;
    wire tipping_point_trigger;

    // Instanciação da Unidade Sob Teste (UUT)
    resilient_r_star_block uut (
        .clk(clk),
        .rst_n(rst_n),
        .lambda_adapt(lambda_adapt),
        .lambda_damage(lambda_damage),
        .alu_error_in(alu_error_in),
        .landauer_entropy(landauer_entropy),
        .next_damage(next_damage),
        .tipping_point_trigger(tipping_point_trigger)
    );

    // Geração do clock (período 10 ns = 100 MHz)
    always begin
        #5 clk = ~clk;
    end

    // Bloco de estímulos sequenciais
    initial begin
        // Inicialização
        clk = 0;
        rst_n = 0;
        lambda_adapt = 16'h0100;    // 256 unidades de adaptação
        lambda_damage = 16'h0010;   // dano inicial baixo (16)
        alu_error_in = 16'h0000;
        landauer_entropy = 16'h0002;

        #20;
        rst_n = 1; // libera o circuito para operação
        $display("[SIMULAÇÃO] Circuito inicializado. Estado estável (R* > 1).");

        // CENÁRIO 1: operações de baixo erro
        #10;
        alu_error_in = 16'h0005;
        lambda_damage = next_damage;

        #10;
        alu_error_in = 16'h0008;
        lambda_damage = next_damage;

        // CENÁRIO 2: estresse de processamento (aproximação do tipping point)
        #10;
        $display("[SIMULAÇÃO] Injetando estresse entrópico na ALU...");
        alu_error_in = 16'h00A0;    // erro abrupto (160)
        lambda_damage = next_damage;

        // CENÁRIO 3: ativação do gatilho crítico (R* <= 1)
        #10;
        alu_error_in = 16'h0050;    // dano acumulado supera lambda_adapt (256)
        lambda_damage = next_damage;

        // CENÁRIO 4: recuperação homeostática por hardware
        #10;
        $display("[SIMULAÇÃO] Verificando atenuação automática pós-colapso.");
        alu_error_in = 16'h0001;    // retorna ao ruído mínimo
        lambda_damage = next_damage;

        #30;
        $display("[SIMULAÇÃO] Concluída com sucesso.");
        $finish;
    end

    // Monitoramento de variáveis no terminal
    initial begin
        $monitor("Tempo: %0tns | λ_adapt: %d | λ_damage: %d | Erro_ALU: %d | "
                 "Próx_Dano: %d | TRIGGER_R*: %b",
                 $time, lambda_adapt, lambda_damage, alu_error_in,
                 next_damage, tipping_point_trigger);
    end

endmodule
