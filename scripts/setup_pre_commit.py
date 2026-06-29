import os
import sys

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git_hooks_dir = os.path.join(root_dir, ".git", "hooks")
    target_hook = os.path.join(git_hooks_dir, "pre-commit")

    if not os.path.exists(git_hooks_dir):
        print("Erro: Diretório .git/hooks não encontrado. Você está na raiz do repositório?")
        sys.exit(1)

    print(f"Instalando hook de pre-commit em {target_hook}...")
    
    # Criamos um script bash como wrapper. Isso garante compatibilidade no Windows (Git Bash)
    # e injeta o .venv no PATH para que o 'semgrep' e o 'antigravity' sejam encontrados
    # mesmo se o commit for feito via interface gráfica (VS Code, etc).
    hook_content = """#!/bin/sh
# Wrapper para pre-commit hook

# Adiciona o virtualenv ao PATH se existir, para encontrar o semgrep
if [ -d ".venv/Scripts" ]; then
    export PATH="$PWD/.venv/Scripts:$PATH"
elif [ -d ".venv/bin" ]; then
    export PATH="$PWD/.venv/bin:$PATH"
fi

# Executa o script python principal
python scripts/git_pre_commit.py
"""
    try:
        with open(target_hook, "w", encoding="utf-8") as f:
            f.write(hook_content)
            
        # Tenta dar permissão de execução
        os.chmod(target_hook, 0o755)
        print("✅ Pre-commit hook instalado com sucesso!")
        print("Certifique-se de que o 'semgrep' está instalado no seu ambiente (pip install semgrep).")
    except Exception as e:
        print(f"❌ Falha ao instalar o hook: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
