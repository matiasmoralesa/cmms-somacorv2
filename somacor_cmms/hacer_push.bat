@echo off
echo ========================================
echo  Haciendo push al repositorio cmms-somacorv2
echo ========================================
echo.

cd /d "%~dp0"
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  ¡Push exitoso!
    echo ========================================
    echo.
    echo Tu repositorio esta disponible en:
    echo https://github.com/fjparrah/cmms-somacorv2
    echo.
) else (
    echo.
    echo ========================================
    echo  Error al hacer push
    echo ========================================
    echo.
    echo Verifica que:
    echo 1. El repositorio cmms-somacorv2 existe en GitHub
    echo 2. Tienes permisos para escribir en el repositorio
    echo 3. Estas autenticado correctamente
    echo.
)

pause

