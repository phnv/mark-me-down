import os
import sys
import shutil

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git_hooks_dir = os.path.join(root_dir, ".git", "hooks")
    source_hook = os.path.join(root_dir, "scripts", "git_pre_commit.py")
    target_hook = os.path.join(git_hooks_dir, "pre-commit")

    if not os.path.exists(git_hooks_dir):
        print("Erro: Diretório .git/hooks não encontrado. Você está na raiz do repositório?")
        sys.exit(1)

    if not os.path.exists(source_hook):
        print(f"Erro: Script fonte {source_hook} não encontrado.")
        sys.exit(1)

    print(f"Instalando hook de pre-commit em {target_hook}...")
    
    try:
        shutil.copyfile(source_hook, target_hook)
        # Tenta dar permissão de execução (mais relevante para Unix/WSL/Git Bash)
        os.chmod(target_hook, 0o755)
        print("✅ Pre-commit hook instalado com sucesso!")
        print("Certifique-se de que o 'semgrep' está instalado globalmente ou no seu ambiente (pip install semgrep).")
    except Exception as e:
        print(f"❌ Falha ao instalar o hook: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
