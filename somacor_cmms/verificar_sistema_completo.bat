@echo off
setlocal enabledelayedexpansion

echo ================================================
echo    VERIFICACION COMPLETA DEL SISTEMA CMMS
echo ================================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)

echo [OK] Python detectado correctamente
echo.

REM Navegar al directorio del backend
cd somacor_cmms\backend

REM Crear directorio de logs si no existe
if not exist "logs" mkdir "logs"

echo ================================================
echo    PASO 1: INSTALACION DE DEPENDENCIAS
echo ================================================
echo.

python install_dependencies.py
if errorlevel 1 (
    echo.
    echo [ERROR] Error en la instalacion de dependencias
    pause
    exit /b 1
)

echo.
echo ================================================
echo    PASO 2: VERIFICACION DE CONEXIONES
echo ================================================
echo.

REM Verificar si el servidor está corriendo
echo [*] Verificando si el servidor Django esta corriendo...
curl -s http://localhost:8000 >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARN] El servidor Django no esta corriendo en http://localhost:8000
    echo.
    echo ¿Deseas iniciar el servidor ahora? (S/N)
    set /p start_server="> "
    
    if /i "!start_server!"=="S" (
        echo.
        echo [*] Iniciando servidor Django...
        start "Django Backend" cmd /k "python manage.py runserver 0.0.0.0:8000"
        echo.
        echo [*] Esperando a que el servidor se inicie...
        timeout /t 5 /nobreak >nul
    ) else (
        echo.
        echo [INFO] Por favor, inicia el servidor manualmente y ejecuta este script nuevamente.
        echo Comando: cd somacor_cmms\backend ^&^& python manage.py runserver
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Servidor Django detectado
echo.

REM Ejecutar verificación completa de conexiones
echo [*] Ejecutando verificacion completa de conexiones...
echo.
python test_connections_enhanced.py
if errorlevel 1 (
    echo.
    echo [WARN] Algunas verificaciones fallaron
    echo [INFO] Revisa los logs en: somacor_cmms\backend\logs\
) else (
    echo.
    echo [OK] Todas las verificaciones pasaron exitosamente
)

echo.
echo ================================================
echo    PASO 3: VERIFICACION DE FORMULARIOS
echo ================================================
echo.

python test_forms_connection.py
if errorlevel 1 (
    echo.
    echo [WARN] Algunas verificaciones de formularios fallaron
) else (
    echo.
    echo [OK] Todas las verificaciones de formularios pasaron exitosamente
)

echo.
echo ================================================
echo    PASO 4: GENERACION DE REPORTES
echo ================================================
echo.

if exist "logs\dashboard_*.html" (
    echo [OK] Dashboard HTML generado
    echo [INFO] Abre el archivo en: somacor_cmms\backend\logs\
    echo.
    
    REM Buscar el archivo más reciente
    for /f "delims=" %%i in ('dir /b /o-d logs\dashboard_*.html 2^>nul') do (
        set latest_dashboard=logs\%%i
        goto :found_dashboard
    )
    :found_dashboard
    
    if defined latest_dashboard (
        echo [*] ¿Deseas abrir el dashboard en el navegador? (S/N)
        set /p open_dashboard="> "
        
        if /i "!open_dashboard!"=="S" (
            start "" "!latest_dashboard!"
        )
    )
) else (
    echo [WARN] No se genero el dashboard HTML
)

echo.
echo ================================================
echo    VERIFICACION COMPLETADA
echo ================================================
echo.
echo [OK] Verificacion completa del sistema finalizada
echo.
echo [INFO] Archivos generados:
echo    - Logs: somacor_cmms\backend\logs\
echo    - Dashboard HTML: somacor_cmms\backend\logs\dashboard_*.html
echo    - Resultados JSON: somacor_cmms\backend\logs\results_*.json
echo.
echo [INFO] Para verificar nuevamente, ejecuta este script
echo.
pause

