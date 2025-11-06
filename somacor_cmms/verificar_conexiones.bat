@echo off
echo ================================================
echo    VERIFICACION DE CONEXIONES CMMS
echo ================================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

echo ✅ Python detectado correctamente
echo.

REM Navegar al directorio del backend
cd somacor_cmms\backend

REM Verificar si el servidor está corriendo
echo 🔍 Verificando si el servidor Django está corriendo...
curl -s http://localhost:8000 >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  El servidor Django no está corriendo en http://localhost:8000
    echo.
    echo ¿Deseas iniciar el servidor ahora? (S/N)
    set /p start_server="> "
    
    if /i "%start_server%"=="S" (
        echo.
        echo 🚀 Iniciando servidor Django...
        start "Django Backend" cmd /k "python manage.py runserver 0.0.0.0:8000"
        echo.
        echo ⏱️  Esperando a que el servidor se inicie...
        timeout /t 5 /nobreak >nul
    ) else (
        echo.
        echo Por favor, inicia el servidor manualmente y ejecuta este script nuevamente.
        echo Comando: cd somacor_cmms\backend ^&^& python manage.py runserver
        pause
        exit /b 1
    )
)

echo.
echo ================================================
echo    EJECUTANDO VERIFICACIONES
echo ================================================
echo.

REM Ejecutar verificación completa de conexiones
echo 📡 Verificando conexiones generales...
echo.
python test_connections.py
if errorlevel 1 (
    echo.
    echo ❌ Error en la verificación de conexiones
    pause
    exit /b 1
)

echo.
echo ================================================
echo    VERIFICANDO FORMULARIOS
echo ================================================
echo.

REM Ejecutar verificación de formularios
echo 📝 Verificando formularios...
echo.
python test_forms_connection.py
if errorlevel 1 (
    echo.
    echo ❌ Error en la verificación de formularios
    pause
    exit /b 1
)

echo.
echo ================================================
echo    VERIFICACION COMPLETADA
echo ================================================
echo.
echo ✅ Todas las verificaciones se completaron exitosamente
echo.
echo 📊 Resumen:
echo    - Conexiones verificadas
echo    - Endpoints probados
echo    - Formularios verificados
echo    - Datos validados
echo.
echo 💡 Si encontraste algún problema, revisa los logs arriba
echo.
pause

