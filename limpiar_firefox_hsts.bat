@echo off
echo ========================================
echo Limpieza de HSTS en Firefox
echo ========================================
echo.
echo INSTRUCCIONES:
echo 1. Cierra TODAS las ventanas de Firefox
echo 2. Presiona cualquier tecla para continuar...
pause > nul

echo.
echo Abriendo Firefox para limpiar datos...
echo.
echo Pasos a seguir:
echo 1. Ve a: Configuracion ^> Privacidad y seguridad
echo 2. En "Cookies y datos del sitio", haz click en "Limpiar datos..."
echo 3. Marca ambas opciones y haz click en "Limpiar"
echo 4. O simplemente presiona Ctrl+Shift+Delete
echo 5. Selecciona "Todo" en el rango de tiempo
echo 6. Marca "Cache" y "Cookies"
echo 7. Haz click en "Limpiar ahora"
echo.

start firefox about:preferences#privacy

echo.
echo Presiona cualquier tecla cuando hayas terminado...
pause > nul

echo.
echo ========================================
echo Limpieza completada!
echo ========================================
echo.
echo Ahora accede a: http://localhost:5173
echo (Asegurate que sea HTTP, no HTTPS)
echo.
pause
