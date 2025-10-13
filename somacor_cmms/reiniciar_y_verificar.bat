@echo off
setlocal enabledelayedexpansion

echo ================================================
echo    REINICIO Y VERIFICACION DEL SISTEMA
echo ================================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado
    pause
    exit /b 1
)

echo [OK] Python detectado
echo.

REM Navegar al directorio del backend
cd somacor_cmms\backend

REM Verificar si el servidor está corriendo
echo [*] Verificando si el servidor esta corriendo...
curl -s http://localhost:8000 >nul 2>&1
if not errorlevel 1 (
    echo [WARN] El servidor ya esta corriendo
    echo [*] Deteniendo servidor actual...
    taskkill /F /IM python.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo [*] Iniciando servidor Django...
start "Django Backend" cmd /k "python manage.py runserver 0.0.0.0:8000"

echo [*] Esperando a que el servidor se inicie...
timeout /t 5 /nobreak >nul

echo.
echo ================================================
echo    VERIFICANDO ENDPOINTS DE FORMULARIOS
echo ================================================
echo.

python test_forms_backend.py
if errorlevel 1 (
    echo.
    echo [ERROR] Algunos endpoints tienen problemas
    echo [INFO] Revisa los errores arriba
    pause
    exit /b 1
)

echo.
echo ================================================
echo    VERIFICACION COMPLETADA
echo ================================================
echo.
echo [OK] El servidor esta corriendo y los endpoints funcionan
echo.
echo [INFO] Servidor Django: http://localhost:8000
echo [INFO] Frontend: http://localhost:5173
echo.
echo [INFO] Siguiente paso:
echo    1. Inicia el frontend: cd somacor_cmms\frontend ^&^& npm run dev
echo    2. Abre http://localhost:5173
echo    3. Prueba crear un nuevo equipo u orden de trabajo
echo    4. Verifica en la consola del navegador (F12) que los datos se carguen
echo.
pause

