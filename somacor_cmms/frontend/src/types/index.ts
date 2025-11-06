// src/types/index.ts
// Tipos TypeScript actualizados para coincidir con el backend

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  usuarios?: {
    idrol: number;
    nombrerol: string;
    idespecialidad: number | null;
    telefono: string | null;
    cargo: string | null;
  };
}

export interface TipoEquipo {
  idtipoequipo: number;
  nombretipo: string;
  descripciontipo?: string;
}

export interface EstadoEquipo {
  idestadoequipo: number;
  nombreestado: string;
}

export interface Faena {
  idfaena: number;
  nombrefaena: string;
  ubicacion?: string;
}

export interface Equipo {
  idequipo: number;
  codigointerno: string;
  nombreequipo: string;
  marca: string;
  modelo: string;
  anio?: number;
  patente?: string;
  horometroactual: number;
  activo: boolean;
  idtipoequipo: number;
  idfaenaactual: number;
  idestadoactual: number;
  // Datos relacionados
  tipo_equipo?: TipoEquipo;
  faena_actual?: Faena;
  estado_actual?: EstadoEquipo;
}

export interface TipoTarea {
  idtipotarea: number;
  descripcion: string;
}

export interface TareaEstandar {
  idtareaestandar: number;
  nombretarea: string;
  descripciontarea: string;
  tiempoestimadominutos: number;
  idtipotarea: number;
  tipo_tarea?: TipoTarea;
}

export interface PlanMantenimiento {
  idplanmantenimiento: number;
  nombreplan: string;
  descripcionplan?: string;
  idtipoequipo: number;
  activo: boolean;
  fechacreacion: string;
  // Datos relacionados
  tipo_equipo?: TipoEquipo;
  detalles?: DetallePlanMantenimiento[];
}

export interface DetallePlanMantenimiento {
  iddetalleplan: number;
  idplanmantenimiento: number;
  idtareaestandar: number;
  intervalohorasoperacion: number;
  activo: boolean;
  escritic: boolean;
  // Datos relacionados
  plan_mantenimiento?: PlanMantenimiento;
  tarea_estandar?: TareaEstandar;
}

export interface TipoMantenimientoOT {
  idtipomantenimientoot: number;
  nombretipomantenimientoot: string;
  descripcion?: string;
}

export interface EstadoOrdenTrabajo {
  idestadoordentrabajo: number;
  nombreestado: string;
  descripcion?: string;
}

export interface OrdenTrabajo {
  idordentrabajo: number;
  numeroot: string;
  fechacreacion: string;
  fechaejecucion?: string;
  fechacompletado?: string;
  fechareportefalla?: string;
  descripcionproblemareportado?: string;
  observacionesfinales?: string;
  prioridad: 'Baja' | 'Media' | 'Alta' | 'Crítica';
  tiempototalminutos?: number;
  horometro?: number;
  idequipo: number;
  idtecnicoasignado?: number;
  idsolicitante: number;
  idestadoordentrabajo: number;
  idtipomantenimientoot: number;
  idplanorigen?: number;
  // Datos relacionados
  equipo?: Equipo;
  tecnico_asignado?: User;
  solicitante?: User;
  estado_orden_trabajo?: EstadoOrdenTrabajo;
  tipo_mantenimiento_ot?: TipoMantenimientoOT;
  plan_origen?: PlanMantenimiento;
  actividades?: ActividadOrdenTrabajo[];
}

export interface ActividadOrdenTrabajo {
  idactividadot: number;
  idordentrabajo: number;
  idtareaestandar: number;
  descripcionactividad: string;
  secuencia: number;
  fechainicioactividad?: string;
  fechafinactividad?: string;
  tiempoestimadominutos: number;
  tiemporealminutos?: number;
  observacionesactividad?: string;
  resultadoinspeccion?: string;
  medicionvalor?: number;
  unidadmedicion?: string;
  idtecnicoejecutor?: number;
  // Datos relacionados
  orden_trabajo?: OrdenTrabajo;
  tarea_estandar?: TareaEstandar;
  tecnico_ejecutor?: User;
}

export interface Agenda {
  idagenda: number;
  titulo: string;
  descripcion?: string;
  fechainicio: string;
  fechafin: string;
  esdiacompleto: boolean;
  colorevento: string;
  recursivo: boolean;
  reglarecursividad?: string;
  fechacreacionevento: string;
  idequipo?: number;
  idplanmantenimiento?: number;
  idusuarioasignado?: number;
  idusuariocreador: number;
  // Datos relacionados
  equipo?: Equipo;
  plan_mantenimiento?: PlanMantenimiento;
  usuario_asignado?: User;
  usuario_creador?: User;
}

// Tipos para Checklist
export interface ChecklistTemplate {
  id: number;
  nombre: string;
  descripcion?: string;
  activo: boolean;
  tipo_equipo: number;
  // Datos relacionados
  tipo_equipo_info?: TipoEquipo;
  categorias?: ChecklistCategory[];
}

export interface ChecklistCategory {
  id: number;
  nombre: string;
  descripcion?: string;
  orden: number;
  template: number;
  // Datos relacionados
  items?: ChecklistItem[];
}

export interface ChecklistItem {
  id: number;
  nombre: string;
  descripcion?: string;
  es_critico: boolean;
  orden: number;
  categoria: number;
  // Datos relacionados
  categoria_info?: ChecklistCategory;
}

export interface ChecklistInstance {
  id: number;
  fecha_inspeccion: string;
  horometro_inspeccion?: number;
  lugar_inspeccion?: string;
  observaciones_generales?: string;
  completado: boolean;
  fecha_completado?: string;
  template: number;
  equipo: number;
  operador: number;
  // Datos relacionados
  template_info?: ChecklistTemplate;
  equipo_info?: Equipo;
  operador_info?: User;
  respuestas?: ChecklistAnswer[];
}

export interface ChecklistAnswer {
  id: number;
  estado: 'bueno' | 'malo' | 'na';
  observacion_item?: string;
  instance: number;
  item: number;
  // Datos relacionados
  instance_info?: ChecklistInstance;
  item_info?: ChecklistItem;
}

// Tipos para respuestas de API
export interface ApiResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
}

export interface DashboardStats {
  estadisticas_generales: {
    total_equipos: number;
    equipos_operativos: number;
    ots_abiertas: number;
    ots_vencidas: number;
    mantenimientos_proximos: number;
  };
  equipos_por_estado: Array<{
    nombreestado: string;
    cantidad: number;
  }>;
  ots_por_tipo: Array<{
    nombretipomantenimientoot: string;
    cantidad: number;
  }>;
  equipos_criticos?: Equipo[];
  mantenimientos_proximos?: Array<{
    equipo: string;
    fecha_programada: string;
    tipo_mantenimiento: string;
  }>;
}

export interface ChecklistCompletionResponse {
  checklist: {
    id_instance: number;
    template_nombre: string;
    equipo_nombre: string;
    operador_nombre: string;
    fecha_inspeccion: string;
    horometro_inspeccion?: number;
  };
  alertas: {
    elementos_criticos_malos: Array<{
      item: string;
      categoria: string;
      observacion?: string;
    }>;
    requiere_atencion_inmediata: boolean;
    ot_creada?: {
      numero_ot: string;
      mensaje: string;
    };
  };
}

// Tipos para formularios
export interface ChecklistFormData {
  template: number;
  equipo: number;
  operador: number;
  fecha_inspeccion: string;
  horometro_inspeccion?: number;
  lugar_inspeccion?: string;
  observaciones_generales?: string;
  answers: Array<{
    item: number;
    estado: 'bueno' | 'malo' | 'na';
    observacion_item?: string;
  }>;
}

export interface OrdenTrabajoFormData {
  idequipo: number;
  idplanorigen?: number;
  horometro?: number;
  idtecnicoasignado?: number;
  idsolicitante: number;
  fechaejecucion?: string;
  descripcionproblemareportado?: string;
  prioridad?: 'Baja' | 'Media' | 'Alta' | 'Crítica';
}

