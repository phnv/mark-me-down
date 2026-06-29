# Developer Guide

Bem-vindo ao guia de desenvolvimento do **Mark-me-down**!

## Ecossistema Antigravity 2.0

Este projeto utiliza o **Google Antigravity 2.0** como _coding agent_ integrado. A infraestrutura nativa do Antigravity nos ajuda a manter a documentação e os testes sempre atualizados, delegando trabalho massante para o subagente em background.

## Automação de Pre-commit (Semgrep + Antigravity)

Temos um fluxo de _pre-commit_ que atua como nosso guarda-redes e executor inteligente:

1. **O Guarda-Redes (Semgrep):**
   - Ao rodar `git commit`, um script local (o _git hook_) intercepta a chamada.
   - Ele executa o `semgrep` nos arquivos em _stage_.
   - Se detectar mudanças estruturais em código Python (ex: novas `class`, novas assinaturas de `def`), ele **pausa (aborta)** o seu commit atual.

2. **O Executor Inteligente (Antigravity em Background):**
   - Caso o Semgrep aponte uma alteração estrutural, o hook invoca silenciosamente a CLI do Antigravity (`antigravity run --bg`).
   - O subagente do Antigravity analisa o `git diff` e se encarrega de:
     - Atualizar/escrever os arquivos correspondentes na pasta `docs/`.
     - Atualizar/escrever os testes correspondentes na pasta `tests/`.
     - Rodar a suíte `pytest`.
   - Se tudo passar, ele automaticamente roda `git add` e cria o commit para você com uma mensagem de _auto-update_.

### Como Instalar o Pre-commit Hook

Se você acabou de clonar o repositório, garanta que seu ambiente possui o `semgrep` instalado e execute o script de instalação do hook:

```bash
pip install semgrep
python scripts/setup_pre_commit.py
```

Isso fará o vínculo do script `scripts/git_pre_commit.py` para o local correto no Git (`.git/hooks/pre-commit`). A partir de agora, o Antigravity trabalhará por você.
