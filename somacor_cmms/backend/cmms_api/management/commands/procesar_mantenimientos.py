# cmms_api/management/commands/procesar_mantenimientos.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from cmms_api.models import (
    OrdenesTrabajo, ActividadesOrdenTrabajo, Equipos, 
    EstadosOrdenTrabajo, TiposMantenimientoOT, Agendas
)
import datetime

class Command(BaseCommand):
    help = 'Procesa mantenimientos vencidos y crea órdenes de trabajo automáticamente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto-crear-ot',
            action='store_true',
            help='Crear automáticamente OTs para mantenimientos vencidos'
        )
        parser.add_argument(
            '--dias-anticipacion',
            type=int,
            default=3,
            help='Días de anticipación para crear OTs (default: 3)'
        )

    def handle(self, *args, **options):
        auto_crear = options['auto_crear_ot']
        dias_anticipacion = options['dias_anticipacion']
        
        self.stdout.write('Procesando mantenimientos...')
        
        # Buscar eventos de agenda próximos a vencer
        fecha_limite = timezone.now().date() + datetime.timedelta(days=dias_anticipacion)
        
        eventos_proximos = Agendas.objects.filter(
            fechahorainicio__date__lte=fecha_limite,
            fechahorainicio__date__gte=timezone.now().date(),
            tipoevento='Mantenimiento Preventivo',
            idordentrabajo__isnull=True  # Sin OT asociada
        ).select_related('idequipo', 'idplanmantenimiento')

        self.stdout.write(f'Encontrados {eventos_proximos.count()} mantenimientos próximos')

        ots_creadas = 0
        for evento in eventos_proximos:
            if auto_crear:
                ot_creada = self._crear_ot_desde_evento(evento)
                if ot_creada:
                    ots_creadas += 1
            else:
                self.stdout.write(
                    f'Mantenimiento próximo: {evento.tituloevento} - '
                    f'{evento.fechahorainicio.date()} - {evento.idequipo.nombreequipo}'
                )

        if auto_crear:
            self.stdout.write(
                self.style.SUCCESS(f'{ots_creadas} órdenes de trabajo creadas automáticamente')
            )
        
        # Procesar OTs vencidas
        self._procesar_ots_vencidas()

    def _crear_ot_desde_evento(self, evento):
        """
        Crea una orden de trabajo desde un evento de agenda
        """
        try:
            with transaction.atomic():
                # Obtener estados y tipos necesarios
                estado_abierta = EstadosOrdenTrabajo.objects.get_or_create(
                    nombreestadoot='Abierta',
                    defaults={'descripcion': 'OT recién creada'}
                )[0]
                
                tipo_preventivo = TiposMantenimientoOT.objects.get_or_create(
                    nombretipomantenimientoot='Preventivo',
                    defaults={'descripcion': 'Mantenimiento planificado'}
                )[0]
                
                # Usuario sistema para crear la OT
                usuario_sistema = User.objects.first()
                
                # Crear la orden de trabajo
                ot = OrdenesTrabajo.objects.create(
                    numeroot=f"OT-AUTO-{evento.idequipo.codigointerno or evento.idequipo.idequipo}-{timezone.now().strftime('%Y%m%d%H%M')}",
                    idequipo=evento.idequipo,
                    idplanorigen=evento.idplanmantenimiento,
                    idtipomantenimientoot=tipo_preventivo,
                    idestadoot=estado_abierta,
                    horometro=evento.idequipo.horometroactual,
                    idsolicitante=usuario_sistema,
                    fechaemision=timezone.now().date(),
                    fechaejecucion=evento.fechahorainicio.date(),
                    descripcionproblemareportado=f"Mantenimiento preventivo programado: {evento.tituloevento}"
                )
                
                # Asociar el evento con la OT
                evento.idordentrabajo = ot
                evento.save()
                
                # Crear actividad genérica
                ActividadesOrdenTrabajo.objects.create(
                    idordentrabajo=ot,
                    descripcionactividad=evento.descripcionevento or evento.tituloevento,
                    tiempoestimadominutos=int((evento.fechahorafin - evento.fechahorainicio).total_seconds() / 60)
                )
                
                self.stdout.write(f'OT creada: {ot.numeroot} para {evento.idequipo.nombreequipo}')
                return True
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creando OT para evento {evento.idagenda}: {str(e)}')
            )
            return False

    def _procesar_ots_vencidas(self):
        """
        Procesa órdenes de trabajo vencidas y actualiza estados
        """
        fecha_actual = timezone.now().date()
        
        # Buscar OTs vencidas (fecha de ejecución pasada y aún abiertas)
        ots_vencidas = OrdenesTrabajo.objects.filter(
            fechaejecucion__lt=fecha_actual,
            idestadoot__nombreestadoot__in=['Abierta', 'Asignada']
        ).select_related('idequipo', 'idestadoot')

        if ots_vencidas.exists():
            self.stdout.write(f'Encontradas {ots_vencidas.count()} OTs vencidas:')
            
            for ot in ots_vencidas:
                dias_vencida = (fecha_actual - ot.fechaejecucion).days
                self.stdout.write(
                    f'  - {ot.numeroot} ({ot.idequipo.nombreequipo}) - '
                    f'Vencida hace {dias_vencida} días'
                )
        else:
            self.stdout.write('No se encontraron OTs vencidas')

