@echo off
echo ================================================
echo    PRUEBA RAPIDA DE CONEXIONES
echo ================================================
echo.

cd somacor_cmms\backend
python quick_test.py

if errorlevel 1 (
    echo.
    echo ❌ Se encontraron problemas
    echo.
    echo 💡 Ejecuta la verificacion completa:
    echo    cd somacor_cmms
    echo    verificar_conexiones.bat
    echo.
) else (
    echo.
    echo ✅ Todo parece estar funcionando correctamente
    echo.
)

pause

