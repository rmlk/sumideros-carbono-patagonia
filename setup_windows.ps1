# Ejecutar desde la carpeta del proyecto en PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Write-Host "Entorno listo. Inicia con: .\.venv\Scripts\python.exe app.py" -ForegroundColor Green
