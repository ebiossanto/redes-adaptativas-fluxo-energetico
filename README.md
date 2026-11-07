# OTRA – Redes Adaptativas por Fluxo de Energia

## Visão geral

**OTRA** (Open-source Tool for Adaptive REsources) é um pacote Python de reprodução numérica do modelo unificado Onsager‑Prigogine‑Odum para redes de fluxo de energia. O projeto combina:

* **Modelagem em Lean 4** – uma especificação formal do modelo de rede (`lean_project/_entry.lean`) que define a estrutura `Net`, o funcional de Lyapunov `F`, e vários lemmas e teoremas de convexidade e convergência global.
* **Implementação numérica em Python** – o módulo `codigo/otra_unified.py` resolve as equações diferenciais ordinárias (via `scipy.integrate.solve_ivp`), calcula o minimizador do funcional (`L‑BFGS‑B`), e inclui seis grupos de testes (Teoremas A‑F) que verificam propriedades de estabilidade, pitchfork, transcritica, dobrou fracionária, entre outros.
* **Suite de testes pytest** – seis testes originais (`test_theorem_A.py` … `test_theorem_F.py`) mais um novo `test_theorem_C.py` que validam a geração do ficheiro `results.json` e os resultados esperados.

## O que o projeto faz

1. **Simulação dinâmica** – integra a lei de adaptação  
   \[
   \tau\,\frac{dg_e}{dt}=g_e\bigl(d\phi_e^2 - c - k\,g_e^{\gamma-1}\bigr)
   \]
   para diferentes modos de fonte (Neumann, Dirichlet, Thevenin) e expoentes de custo \(\gamma\).

2. **Análise de teoremas** – verifica teoremas de Lyapunov, convexidade, espectro do Hessiano, bifurcações pitchfork, transcritica, dobrou e memória fracionária (Caputo).

3. **Geração de figuras e dados** – produz fichas PNG/SVG (ex.: `fig1_lyapunov.png`) e um ficheiro `results.json` com métricas consolidadas (erros, minimizadores, espectros, etc.).

4. **Pacote PyPI** – o `pyproject.toml` define o nome `otra`, versão `0.1.0`, dependências (`numpy`, `scipy`, `matplotlib`) e um entry‑point de linha de comando `otra = "codigo.otra_unified:main"`.

## Para que serve

* **Pesquisa em redes complexas** – testes de hipóteses sobre estabilidade, convexidade e bifurcações em sistemas de fluxo de energia.
* **Educação** – material didático para cursos de modelação matemática, teoria de controle e redes complexas.
* **Protótipo de software** – base para desenvolvimentos comercciais ou acadêmicos que necessitem de simulação de redes adaptativas com parâmetros de custo variáveis.

## Sugestões de aplicação

| Área | Como usar o OTRA |
|------|------------------|
| **Modelação de redes elétricas de micro‑geração** | Ajustar parâmetros `k`, `γ`, `c` para representar custos de manutenção de cada aresta e estudar a estabilidade da rede bajo diferentes fontes (Thevenin, Neumann, Dirichlet). |
| **Estudos de eficiência energética** | Usar a funcional `F(g)` como índice de “custo total” e executar o minimizador `L‑BFGS‑B` para encontrar a configuração de condutâncias que minimiza o custoglobal. |
| **Pós‑graduação / cursos** | Os testes `test_theorem_*` já vêm com scripts e figuras; basta rodar `python -m pytest tests/` para obter resultados imediatos. |
| **Prototipagem de controladores adaptativos** | O script `outra_unified.py` aceita parâmetros via linha de comando (`python outra_unified.py A B fold`), permitindo integração em pipelines de otimização. |
| **Integração com frameworks de Machine Learning** | Os dados gerados (`results.json`, figuras) podem ser importados em notebooks Python para análise de séries temporais ou treinamento de modelos preditivos. |

## Como começar

```powershell
# 1. Clonar o repositório
git clone https://github.com/seu_usuario/otra.git
cd outra

# 2. Criar um ambiente virtual (recomendado)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Instalar dependências
pip install -r requirements.txt   # ou: pip install numpy scipy matplotlib

# 3. (Opcional) Build do pacote PyPI
python -m build                     # gera dist/otra-0.1.0.tar.gz e .whl
twine upload dist/*                 # upload para https://pypi.org

# 4. Rodar os testes pytest
python -m pytest tests/            # deve mostrar 7 passed (6 originais + test_theorem_C)

# 5. Simular um cenário simples
python outra_unified.py A           # Teorema A (Lyapunov / convergência global)
```

## Licença

Este projeto está licenciado sob a **MIT License** – veja o ficheiro `LICENSE` para mais detalhes.

---
*Projeto desenvolvido por Euzebio, 2026. Contribuições e issues são bem-vindos no GitHub.*