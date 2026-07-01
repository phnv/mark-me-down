@echo off
echo ============================================================
echo  mark-me-down A2A Server
echo  Running on http://localhost:8001
echo  AgentCard: http://localhost:8001/.well-known/agent-card.json
echo ============================================================
echo.
.venv\Scripts\uvicorn.exe agents.v2.a2a_server:app --host 0.0.0.0 --port 8001 --reload
