@echo off
echo ================================================
echo    INICIANDO SERVIDORES CMMS OPTIMIZADOS
echo ================================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

REM Verificar si Node.js está instalado
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js no está instalado o no está en el PATH
    pause
    exit /b 1
)

echo ✅ Python y Node.js detectados correctamente
echo.

REM Crear directorio de logs si no existe
if not exist "somacor_cmms\backend\logs" mkdir "somacor_cmms\backend\logs"

echo 🚀 Iniciando Backend Django...
echo.
cd somacor_cmms\backend

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
)

REM Instalar dependencias si es necesario
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Instalando dependencias de Python...
    pip install -r requirements.txt
)

REM Migrar base de datos si es necesario
echo Verificando migraciones...
python manage.py migrate --run-syncdb

REM Crear superusuario si no existe
echo Verificando superusuario...
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"

REM Crear token de autenticación
echo.
echo Generando token de autenticación...
python create_token.py

echo.
echo 🔧 Configuraciones de rendimiento aplicadas:
echo    - CORS optimizado
echo    - Timeouts configurados (10s)
echo    - Cache habilitado (30s)
echo    - Paginación optimizada (100 items)
echo    - Consultas optimizadas con select_related
echo.

REM Iniciar servidor Django en segundo plano
echo Iniciando servidor Django en puerto 8000...
start "Django Backend" cmd /k "python manage.py runserver 0.0.0.0:8000 --noreload"

REM Esperar un poco para que Django se inicie
timeout /t 3 /nobreak >nul

echo.
echo 🌐 Iniciando Frontend React...
echo.
cd ..\frontend

REM Instalar dependencias si es necesario
if not exist "node_modules" (
    echo Instalando dependencias de Node.js...
    npm install
)

echo Iniciando servidor de desarrollo React en puerto 5173...
start "React Frontend" cmd /k "npm run dev"

echo.
echo ⏱️  Esperando a que los servidores se inicien...
timeout /t 5 /nobreak >nul

echo.
echo ================================================
echo    SERVIDORES INICIADOS EXITOSAMENTE
echo ================================================
echo.
echo 🌐 Frontend: http://localhost:5173
echo 🔧 Backend:  http://localhost:8000
echo 👤 Admin:    http://localhost:8000/admin (admin/admin123)
echo 📊 API:      http://localhost:8000/api/
echo.
echo ================================================
echo    CONFIGURACIÓN DE AUTENTICACIÓN
echo ================================================
echo.
echo 🔑 IMPORTANTE: Para usar el sistema, debes configurar tu token:
echo.
echo    Opción 1 - Usar la página de configuración:
echo    Abre en tu navegador: http://localhost:5173/set_token.html
echo.
echo    Opción 2 - Desde la consola del navegador:
echo    1. Abre http://localhost:5173
echo    2. Presiona F12 para abrir las herramientas de desarrollador
echo    3. Ve a la pestaña "Console"
echo    4. Ejecuta: localStorage.setItem('authToken', 'TU_TOKEN_AQUI');
echo    5. Recarga la página (F5)
echo.
echo    El token fue mostrado arriba cuando se inició el backend.
echo.
echo ================================================
echo    COMANDOS ÚTILES
echo ================================================
echo.
echo 💡 Para probar el rendimiento, ejecuta:
echo    cd somacor_cmms\backend
echo    python test_api_performance.py
echo.
echo 🔍 Para diagnosticar problemas de carga, ejecuta:
echo    cd somacor_cmms\backend
echo    python debug_api.py
echo.
echo 📊 Para ver logs en tiempo real, ejecuta:
echo    python view_logs.py
echo.
echo 🔑 Para regenerar el token de autenticación:
echo    cd somacor_cmms\backend
echo    python create_token.py
echo.
echo 🛑 Para detener los servidores, cierra las ventanas de cmd
echo.
pause
