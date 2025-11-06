from django.core.management.base import BaseCommand
from cmms_api.models import Roles

class Command(BaseCommand):
    help = 'Verifica y muestra los roles existentes en la base de datos.'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- Iniciando diagnóstico de roles ---")
        self.stdout.write("Conectando a la base de datos configurada en settings.py...")
        
        try:
            all_roles = Roles.objects.all()
            
            if all_roles.exists():
                self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se encontraron {all_roles.count()} roles:'))
                for rol in all_roles:
                    self.stdout.write(f"  - ID: {rol.idrol}, Nombre: {rol.nombrerol}")
            else:
                self.stdout.write(self.style.ERROR('ERROR: No se encontró ningún rol.'))
                self.stdout.write("Causa probable: Django no está viendo los datos que insertaste.")
                self.stdout.write("Solución: Vuelve a ejecutar la consulta INSERT ... ON DUPLICATE KEY UPDATE y asegúrate de que se ejecute sin errores.")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERROR CRÍTICO AL CONECTAR A LA BASE DE DATOS: {e}'))
            self.stdout.write("Causa probable: Hay un error en la configuración 'DATABASES' de tu archivo settings.py (host, puerto, usuario, contraseña o nombre de la BD).")

        self.stdout.write("--- Diagnóstico finalizado ---")
