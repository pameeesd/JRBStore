@echo off
echo ===================================================
echo   Iniciando Servidor Web JRBStore (Django)
echo ===================================================
echo.
echo La pagina web se abrira automaticamente en tu navegador...
echo Para detener el servidor, cierra esta ventana.
echo.
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8000/"
python src/manage.py runserver 127.0.0.1:8000
pause
