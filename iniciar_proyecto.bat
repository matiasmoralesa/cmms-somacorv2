@echo off
echo ========================================
echo   INICIANDO CMMS SOMACOR V2
echo ========================================
echo.

echo [1/4] Verificando entorno virtual...
if not exist "somacor_cmms\backend\venv" (
    echo Creando entorno virtual...
    python -m venv somacor_cmms\backend\venv
    echo Entorno virtual creado!
)

echo.
echo [2/4] Verificando migraciones...
somacor_cmms\backend\venv\Scripts\python.exe somacor_cmms\backend\manage.py migrate --noinput

echo.
echo [3/4] Iniciando Backend Django...
echo Backend corriendo en: http://localhost:8000
echo.
start "CMMS Backend" cmd /k "somacor_cmms\backend\venv\Scripts\python.exe somacor_cmms\backend\manage.py runserver 0.0.0.0:8000"

timeout /t 5 /nobreak >nul

echo.
echo [4/4] Iniciando Frontend React...
echo Frontend corriendo en: http://localhost:5173
echo.
start "CMMS Frontend" cmd /k "cd somacor_cmms\frontend && npm run dev"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   SISTEMA INICIADO CORRECTAMENTE
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo Admin:    http://localhost:8000/admin
echo Health:   http://localhost:8000/health/
echo.
echo Presiona cualquier tecla para abrir el navegador...
pause >nul

start http://localhost:5173

echo.
echo Para detener los servicios, cierra las ventanas de Backend y Frontend
echo.
