# cmms_api/management/commands/generar_agenda_preventiva.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from cmms_api.models import (
    PlanesMantenimiento, DetallesPlanMantenimiento, 
    Equipos, Agendas, TiposEquipo
)
import datetime

class Command(BaseCommand):
    help = 'Genera agenda de mantenimiento preventivo basada en planes y horometros de equipos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo-equipo',
            type=int,
            help='ID del tipo de equipo para generar agenda específica'
        )
        parser.add_argument(
            '--dias-adelante',
            type=int,
            default=30,
            help='Días hacia adelante para proyectar mantenimientos (default: 30)'
        )
        parser.add_argument(
            '--horas-diarias',
            type=int,
            default=8,
            help='Horas de operación diarias estimadas (default: 8)'
        )

    def handle(self, *args, **options):
        tipo_equipo_id = options['tipo_equipo']
        dias_adelante = options['dias_adelante']
        horas_diarias = options['horas_diarias']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Generando agenda preventiva para los próximos {dias_adelante} días...'
            )
        )

        # Filtrar equipos por tipo si se especifica
        equipos_query = Equipos.objects.filter(activo=True)
        if tipo_equipo_id:
            equipos_query = equipos_query.filter(idtipoequipo_id=tipo_equipo_id)

        eventos_creados = 0
        usuario_sistema = User.objects.first()  # Usuario por defecto para crear eventos

        for equipo in equipos_query:
            self.stdout.write(f'Procesando equipo: {equipo.nombreequipo}')
            
            # Obtener planes de mantenimiento para este tipo de equipo
            planes = PlanesMantenimiento.objects.filter(
                idtipoequipo=equipo.idtipoequipo,
                activo=True
            )

            for plan in planes:
                detalles = DetallesPlanMantenimiento.objects.filter(
                    idplanmantenimiento=plan,
                    activo=True
                ).order_by('intervalohorasoperacion')

                for detalle in detalles:
                    # Calcular próximas fechas de mantenimiento
                    eventos_generados = self._generar_eventos_para_detalle(
                        equipo, plan, detalle, dias_adelante, horas_diarias, usuario_sistema
                    )
                    eventos_creados += eventos_generados

        self.stdout.write(
            self.style.SUCCESS(
                f'Agenda generada exitosamente. {eventos_creados} eventos creados.'
            )
        )

    def _generar_eventos_para_detalle(self, equipo, plan, detalle, dias_adelante, horas_diarias, usuario):
        """
        Genera eventos de agenda para un detalle específico del plan de mantenimiento
        """
        eventos_creados = 0
        horometro_actual = equipo.horometroactual
        intervalo = detalle.intervalohorasoperacion
        
        # Calcular el próximo mantenimiento
        horas_desde_ultimo = horometro_actual % intervalo
        horas_hasta_proximo = intervalo - horas_desde_ultimo
        
        # Si ya es tiempo de mantenimiento
        if horas_hasta_proximo == intervalo:
            horas_hasta_proximo = 0

        fecha_actual = timezone.now().date()
        fecha_limite = fecha_actual + datetime.timedelta(days=dias_adelante)

        # Generar eventos dentro del período especificado
        while True:
            # Calcular fecha estimada del mantenimiento
            dias_estimados = horas_hasta_proximo / horas_diarias
            fecha_mantenimiento = fecha_actual + datetime.timedelta(days=int(dias_estimados))
            
            if fecha_mantenimiento > fecha_limite:
                break

            # Verificar si ya existe un evento similar en esa fecha
            evento_existente = Agendas.objects.filter(
                idequipo=equipo,
                idplanmantenimiento=plan,
                fechahorainicio__date=fecha_mantenimiento,
                tituloevento__icontains=detalle.idtareaestandar.nombretarea
            ).exists()

            if not evento_existente:
                # Crear evento de agenda
                hora_inicio = datetime.time(8, 0)  # 8:00 AM por defecto
                fecha_hora_inicio = datetime.datetime.combine(fecha_mantenimiento, hora_inicio)
                fecha_hora_fin = fecha_hora_inicio + datetime.timedelta(
                    minutes=detalle.idtareaestandar.tiempoestimadominutos or 60
                )

                Agendas.objects.create(
                    tituloevento=f"Mantenimiento {detalle.idtareaestandar.nombretarea} - {equipo.nombreequipo}",
                    fechahorainicio=fecha_hora_inicio,
                    fechahorafin=fecha_hora_fin,
                    descripcionevento=(
                        f"Mantenimiento preventivo programado cada {intervalo} horas. "
                        f"Horometro estimado: {horometro_actual + horas_hasta_proximo}h"
                    ),
                    tipoevento="Mantenimiento Preventivo",
                    colorevento="#28a745" if not detalle.escritic else "#dc3545",
                    idequipo=equipo,
                    idplanmantenimiento=plan,
                    idusuariocreador=usuario
                )
                eventos_creados += 1

            # Preparar para el siguiente mantenimiento
            horas_hasta_proximo += intervalo
            horometro_actual += intervalo

        return eventos_creados

