# Documento de Continuidade – OTRA – Redes Adaptativas por Fluxo de Energia

Este documento descreve os próximos passos recomendados para o desenvolvimento, manutenção e expansão do projeto **OTRA**. Ele organiza o trabalho em três áreas principais: **Lean (compilação formal)**, **Pacote PyPI (publicação)** e **Suite pytest (expansão de testes)**.

---

## 1. Compilar o Lean (formal verification)

### 1.1. Requisitos já cumpridos
- **Lean 4.15.0** instalado via ELAN (`C:\Users\Euzebio\.elan\toolchains\leanprover--lean4---v4.15.0\bin\lean.exe`).
- **Mathlib 4** clonado em `C:\Users\Euzebio\.lean\mathlib4`.
- **`lakefile.toml`** ajustado para apontar para a pasta do Mathlib (ver `lakefile.toml` do repositório).

### 1.2. Como compilar (Opção A – `leanproject`)

1. **Instalar o `leanproject`** (caso ainda não tenha):
   ```powershell
   # Baixar o zip da release v4.2.4 do ELAN (contém lean‑project.exe)
   iwr -Uri https://github.com/leanprover/elan/releases/download/v4.2.4/elan-x86_64-pc-windows-msvc.zip -OutFile C:\Downloads\elan‑v4.2.4‑windows‑msvc.zip
   # Extrair para a pasta bin do ELAN
   Expand-Archive -Path C:\Downloads\elan‑v4.2.4‑windows‑msvc.zip -DestinationPath C:\Users\Euzebio\.elan\bin
   # Garantir que a pasta bin está no PATH (por sessão)
   $env:PATH = 'C:\Users\Euzebio\.elan\bin;' + $env:PATH
   ```
2. **Inicializar o projeto com Mathlib**:
   ```powershell
   Set-Location "D:\Redes adaptativas\repositorio-github\redes-adaptativas-fluxo-energetico\lean_project"
   leanproject init --mathlib .
   ```
3. **Compilar**:
   ```powershell
   lean build          # ou `leanproject build`
   ```
   Se tudo correr bem, aparecerá `Build completed successfully.`.

### 1.3. Como compilar (Opção B – apenas `lean.exe` + `LEAN_PATH`)

Caso não queira instalar `leanproject`, basta apontar o compilador:

```powershell
$env:LEAN_PATH = \
    "C:\Users\Euzebio\.elan\toolchains\leanprover--lean4---v4.15.0\lib\lean;" + \
    "C:\Users\Euzebio\.lean\mathlib4"

& "C:\Users\Euzebio\.elan\toolchains\leanprover--lean4---v4.15.0\bin\lean.exe" _entry.lean
```
*Nota:* esta abordagem não gera os ficheiros `.olean`/`.ilean` automaticamente e pode exigir ajustes manuais de `import` caso o Lean encontre módulos em falta. Use‑a para testes rápidos.

### 1.3. Rotina de manutenção
- Sempre que atualizar o Lean (via `elan self update`), verifique se o `lakefile.toml` ainda referencia o Mathlib correto.
- Após alterações em `_entry.lean`, rode `lean build` para garantir que não hajam “unknown module prefix ‘Mathlib’”.

---

## 2. Publicar o pacote PyPI

### 2.1. Estado atual
- `python -m build` já foi executado e gerou:
  - `dist/otra-0.1.0.tar.gz`
  - `dist/otra-0.1.0‑py3‑none‑any.whl`
- O `pyproject.toml` está configurado com nome `otra`, versão `0.1.0`, dependências (`numpy`, `scipy`, `matplotlib`) e entry‑point `otra = "codigo.otra_unified:main"`.

### 2.2. Passos para upload

```powershell
# 1. (Opcional) Criar / ativar ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar o twine (se ainda não tiver)
pip install twine

# 3. Fazer o upload
twine upload dist/*
```
- Serão solicitados **nome de utilizador** e **token** da conta PyPI. Recomenda‑se usar um token de gravação (settings → APIs → Token de gravação) e guardá‑lo na variável de ambiente `TWINE_PASSWORD` (ou deixar o `twine` pedir interativamente).

### 2.3. Após o upload
- O pacote ficará disponível em `https://pypi.org/project/otra/`.
- Os utilizadores podem instalá‑lo com:
  ```powershell
  pip install outra==0.1.0
  ```
- O entry‑point `otra` permite rodar o script unificado diretamente:
  ```powershell
  outra A B fold   # executa os teoremas A, B e fold
  ```

### 2.4. Rotina de manutenção
- Sempre que adicionar nova funcionalidade ao `codigo/otra_unified.py`, atualize a versão em `pyproject.toml` (ex.: `version = "0.2.0"`).
- Execute `python -m build` novamente e faça upload novamente para refletir as mudanças.

---

## 3. Expandir a suite pytest

### 3.1. Estrutura atual
- 6 testes originais (`test_theorem_A.py` … `test_theorem_F.py`).
- 1 novo teste `test_theorem_C.py` (adicionado recentemente) que valida o rótulo **C** do script `otra_unified.py`.
- Todos os 7 testes passam (`python -m pytest tests/`).

### 3.2. Como adicionar um novo teste

1. **Criar o ficheiro** `tests/test_XXX.py` com a seguinte estrutura (copiar de `test_theorem_C.py`):

   ```python
   """
   Test for Theorem XXX.
   Runs the unified script with test 'X' and verifies the generated results.
   """
   import subprocess, json, pathlib, sys

   ROOT = pathlib.Path(__file__).resolve().parent.parent
   CODE_DIR = ROOT / "codigo"
   RES_FILE = CODE_DIR / "results.json"
   SCRIPT = CODE_DIR / "otra_unified.py"

   def test_theorem_XXX():
       # Run the unified script with the desired label
       proc = subprocess.run(
           [sys.executable, str(SCRIPT), "X"],
           cwd=str(CODE_DIR),
           capture_output=True,
           text=True,
       )
       assert proc.returncode == 0, f"Script failed:\nstdout={proc.stdout}\nstderr={proc.stderr}"

       # Check that results.json was created
       assert RES_FILE.exists(), "results.json not generated"

       with open(RES_FILE, "r", encoding="utf-8") as f:
           data = json.load(f)

       # Assert the presence of the expected key, e.g. "theorem_X"
       assert "theorem_X" in data, "theorem_X missing from results.json"

       print("test_theorem_XXX PASSED")
   ```

2. **Adicionar a função ao dicionário `fn`** em `codigo/otra_unified.py` (bloco `if __name__ == "__main__":`):
   ```python
   fn = dict(
       A=test_theorem_A,
       B=test_theorem_B,
       pitch=test_pitchfork,
       chain=test_chain_transcritical,
       fold=test_fold,
       frac=test_fractional,
       C=test_theorem_C,      # já existe
       XXX=test_theorem_XXX, # <-- novo
   )
   ```
3. **Rodar o novo teste**:
   ```powershell
   python -m pytest tests/test_XXX.py -v
   ```
4. **Confirmar que o `results.json` contém o bloco esperado** (ex.: `"theorem_XXX": …`).

### 3.3. Sugestões de novos testes (ideias)

| Teste | Descrição |
|-------|-----------|
| `test_theorem_D` | Validar comportamento de γ < 1 (extinção de arestas em tempo finito). |
| `test_stability_hessian` | Verificar que o espectro do Hessiano do funcional `F` satisfaz as condições de convexidade para γ > 1. |
| `test_fractional_step` | Testar integração com passo fracionário (Caputo) por diferentes ordens α e comparar com a solução numérica `net.run`. |
| `test_parameter_sweep` | Parametriar `k`, `γ`, `c` em grade e gerar um heat‑map do minimizador `g*`. |
| `test_mpi_parallel` | Executar a simulação em múltiplos núcleos (usando `multiprocessing`) e verificar consistência dos resultados. |

### 3.4. Rotina de CI (opcional)

Criar `.github/workflows/ci.yml` para que, a cada push, o suite pytest seja executado e o pacote seja buildado:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install numpy scipy matplotlib pytest
      - name: Run tests
        run: python -m pytest tests/ -v
  build:
    needs: test
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Build package
        run: python -m build
      - name: Upload to PyPI (conditional)
        if: github.event_name == 'push'
        run: twine upload dist/*
        env:
          TWINE_USERNAME: ${{ secrets.PYPI_USER }}
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

---

## 4. Checklist rápido (o que fazer agora)

| ✅ | Item |
|---|------|
| ✅ | **Lean** compilado (opção A ou B). |
| ✅ | **Pacote Python** `otra` buildado e pronto para `twine upload`. |
| ✅ | **Suite pytest** com 7 testes (todos verdes). |
| ✅ | **README.md** criado com descrição completa, propósito e sugestões de aplicação. |
| ✅ | **CONTINUITY.md** criado com orientações detalhadas para Lean, PyPI e pytest. |
| ⏳ | **Subir ao GitHub** (ver passo‑a‑passo abaixo). |
| ⏳ | **Publicar no PyPI** (executar `twine upload dist/*`). |
| ⏳ | **Adicionar mais testes** ou funcionalidades conforme necessidade. |

---

## 5. Como publicar no GitHub (passo‑a‑passo)

```powershell
# 1. (Se ainda não tiver) criar uma conta GitHub e um repositório vazio chamado "otra"
#    https://github.com/new   -> name: "otra", private ou public conforme desejar.

# 2. Clonar o repositório localmente (apenas para ter o histórico)
git clone https://github.com/seu_usuario/otra.git
cd outra

# 3. Copiar os ficheiros que criamos (README, CONTINUITY, .gitignore, etc.)
#    (já estão na pasta atual, caso tenham sido clonados do zip do repositório).

# 4. Adicionar, commitar e push
git add -A
git commit -m "Initial commit: OTRA project with Lean, PyPI and pytest suite"
git branch -M main
git push -u origin main

# 5. (Opcional) Marcar issues ou pull requests para futuras melhorias.
```

Após o push, o repositório estará disponível em https://github.com/seu_usuario/otra e conterá:

- `README.md` – descrição detalhada, propósito e sugestões de aplicação.
- `CONTINUITY.md` – roteiro de desenvolvimento (Lean, PyPI, pytest).
- `pyproject.toml` – configuração do pacote Python.
- `codigo/otra_unified.py` – núcleo numérico.
- `tests/` – suite de testes (7 testes atuais).
- `lean_project/` – esqueleto Lean ( `_entry.lean`, `lakefile.toml`, `Mathlib` já clonado).
- `.gitignore` – para ignorar `__pycache__`, `.lean`, `dist/`, `results.json`, etc.

---

## 6. Próximas reuniões / marcos sugeridos

| Marco | Data alvo | O que entregar |
|-------|-----------|----------------|
| **M1 – Lean compilado** | + 1 semana | `lean build` bem‑sucedido; `results.json` gerado. |
| **M2 – PyPI publicação** | + 2 semanas | Pacote `otra` indexado em https://pypi.org/project/otra/. |
| **M3 – Suite pytest expandida** | + 3 semanas | Pelo menos mais 2 testes novos (`test_theorem_D`, `test_stability_hessian`). |
| **M4 – Documentação adicional** | + 4 semanas | Exemplos de uso em notebooks, guias de parámetros, diagrama de fluxo da simulação. |

---

*Fim do documento de continuidade. Qualquer dúvida ou necessidade de ajuste, basta abrir uma issue no GitHub ou contactar o mantenedor do projeto.*