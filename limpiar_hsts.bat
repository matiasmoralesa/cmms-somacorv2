@echo off
echo ========================================
echo Limpieza de HSTS para desarrollo local
echo ========================================
echo.
echo INSTRUCCIONES:
echo 1. Cierra TODAS las ventanas de Chrome/Edge
echo 2. Presiona cualquier tecla para continuar...
pause > nul

echo.
echo Abriendo Chrome para limpiar HSTS...
echo.
echo Pasos a seguir:
echo 1. En la pagina que se abre, busca "Delete domain security policies"
echo 2. Escribe "localhost" y haz click en "Delete"
echo 3. Escribe "127.0.0.1" y haz click en "Delete"
echo 4. Cierra Chrome completamente
echo.

start chrome chrome://net-internals/#hsts

echo.
echo Presiona cualquier tecla cuando hayas terminado...
pause > nul

echo.
echo Limpiando cache de DNS...
ipconfig /flushdns

echo.
echo ========================================
echo Limpieza completada!
echo ========================================
echo.
echo Ahora puedes abrir Chrome y acceder a:
echo http://localhost:5173
echo.
pause
