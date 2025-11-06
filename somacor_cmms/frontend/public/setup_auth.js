/**
 * Script de configuración de autenticación para Somacor CMMS
 * 
 * INSTRUCCIONES:
 * 1. Abre la consola del navegador (F12)
 * 2. Copia y pega este código completo
 * 3. Presiona Enter
 * 4. Sigue las instrucciones en pantalla
 */

(function() {
    console.clear();
    console.log('%c🔐 CONFIGURACIÓN DE AUTENTICACIÓN - SOMACOR CMMS', 'color: #667eea; font-size: 20px; font-weight: bold;');
    console.log('%c==============================================', 'color: #667eea; font-size: 14px;');
    console.log('');
    
    // Verificar si ya hay un token
    const existingToken = localStorage.getItem('authToken');
    if (existingToken) {
        console.log('%c✅ Ya tienes un token configurado', 'color: #28a745; font-size: 14px; font-weight: bold;');
        console.log('%cToken actual: ' + existingToken.substring(0, 20) + '...', 'color: #666; font-size: 12px;');
        console.log('');
        
        const update = confirm('¿Deseas actualizar el token?');
        if (!update) {
            console.log('%c✋ Token no actualizado. Recarga la página para continuar.', 'color: #ffc107; font-size: 12px;');
            return;
        }
    }
    
    // Solicitar el token
    console.log('%c📋 Ingresa tu token de autenticación:', 'color: #333; font-size: 14px; font-weight: bold;');
    console.log('%c(Puedes obtenerlo ejecutando: cd somacor_cmms\\backend && python create_token.py)', 'color: #666; font-size: 11px; font-style: italic;');
    console.log('');
    
    const token = prompt('🔑 Ingresa tu token de autenticación:');
    
    if (!token || token.trim() === '') {
        console.log('%c❌ No se ingresó ningún token. Operación cancelada.', 'color: #dc3545; font-size: 14px; font-weight: bold;');
        return;
    }
    
    // Guardar el token
    localStorage.setItem('authToken', token.trim());
    
    console.log('');
    console.log('%c✅ Token guardado exitosamente!', 'color: #28a745; font-size: 16px; font-weight: bold;');
    console.log('');
    console.log('%c🔄 Recargando la página...', 'color: #17a2b8; font-size: 14px;');
    console.log('');
    
    // Recargar la página después de 1 segundo
    setTimeout(() => {
        window.location.reload();
    }, 1000);
    
    return 'Token configurado exitosamente. La página se recargará en 1 segundo...';
})();

