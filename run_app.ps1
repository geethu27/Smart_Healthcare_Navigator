# Launch Smart Healthcare Navigator in VS Code / PowerShell
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   Starting Smart Healthcare Navigator (Grounded RAG)   " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "URL: http://127.0.0.1:8000" -ForegroundColor Cyan
Start-Process "http://127.0.0.1:8000"
python server.py
