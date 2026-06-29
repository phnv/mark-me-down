#!/usr/bin/env python
import sys
import subprocess
import json
import os

def main():
    # 1. Obter arquivos .py em stage
    try:
        staged_files = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            text=True,
            encoding="utf-8"
        ).splitlines()
    except subprocess.CalledProcessError:
        sys.exit(0)
        
    py_files = [f for f in staged_files if f.endswith(".py")]
    
    if not py_files:
        sys.exit(0)
        
    # 2. Rodar Semgrep
    try:
        semgrep_cmd = ["semgrep", "--config", ".semgrep.yaml", "--json"] + py_files
        result = subprocess.run(semgrep_cmd, capture_output=True, text=True, encoding="utf-8")
        
        # Faz parse do JSON resultante do Semgrep
        output = json.loads(result.stdout)
        results = output.get("results", [])
    except Exception as e:
        print(f"Aviso: Falha ao rodar ou parsear a saída do Semgrep: {e}")
        # Retorna 0 para não bloquear commits se o semgrep não estiver instalado
        sys.exit(0)
        
    if results:
        print("==========================================================")
        print("🚀 Antigravity 2.0: Mudança estrutural detectada pelo Semgrep.")
        print("O commit atual será pausado.")
        print("Delegando a atualização de specs e testes para o subagente Antigravity em background...")
        print("==========================================================")
        
        prompt = (
            "Como subagente de background do hook pre-commit: "
            "1. Analise as mudanças no stage (git diff --cached). "
            "2. Atualize os documentos na pasta docs/ se fatos arquiteturais mudaram. "
            "3. Atualize ou crie testes na pasta tests/ de acordo com os novos contratos. "
            "4. Execute 'pytest' localmente. "
            "5. Se os testes passarem, execute 'git add docs/ tests/' e crie um commit com "
            "a mensagem 'chore: auto-update tests and docs via Antigravity'."
        )
        
        try:
            # Chama a CLI nativa do Antigravity em modo background
            subprocess.run(["antigravity", "run", "--bg", prompt])
        except FileNotFoundError:
            print("Erro: A CLI 'antigravity' não foi encontrada no PATH.")
            print("Certifique-se de que o ecossistema Antigravity 2.0 está instalado e acessível.")
            
        # Aborta o commit atual (exit 1) para dar tempo ao agente de corrigir o código em background
        sys.exit(1)
    else:
        # Commit permitido sem mudanças estruturais
        sys.exit(0)

if __name__ == "__main__":
    main()
