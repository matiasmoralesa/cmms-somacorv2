import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Calendar, momentLocalizer, Views, type Event } from 'react-big-calendar';
import moment from 'moment';
import 'moment/locale/es';
import Modal from '../components/ui/Modal'; 
import { PlusCircle, ChevronLeft, ChevronRight, Trash2, Edit } from 'lucide-react';

// --- CONFIGURACIÓN Y DATOS INICIALES ---
moment.locale('es');
const localizer = momentLocalizer(moment);

interface MyEvent extends Event {
    id: number;
    type: string;
    notes?: string;
    title: string;
    start: Date;
    end: Date;
}

interface ApiEvent {
    id: number;
    title: string;
    start: string;
    end: string;
    type: string;
    notes?: string;
}

const initialEvents: MyEvent[] = [
    { id: 1, title: 'Mantenimiento Preventivo - Cargador Frontal 966 GC', start: new Date(2025, 5, 12, 9, 0, 0), end: new Date(2025, 5, 12, 11, 0, 0), type: 'preventivo', notes: 'Revisión de motor y cambio de aceite.' },
    { id: 2, title: 'Reparación Correctiva - Retroexcavadora 3157TR', start: new Date(2025, 5, 15, 14, 0, 0), end: new Date(2025, 5, 15, 17, 30, 0), type: 'correctivo', notes: 'Falla en el sistema hidráulico.' },
    { id: 3, title: 'Inspección Semanal - Camión Minero 797F', start: new Date(2025, 5, 17, 8, 0, 0), end: new Date(2025, 5, 17, 9, 0, 0), type: 'inspeccion', notes: 'Verificar niveles y estado de neumáticos.' },
];

// --- COMPONENTES PERSONALIZADOS DEL CALENDARIO (sin cambios) ---
const CustomEventComponent: React.FC<{ event: MyEvent }> = ({ event }) => {
    const eventTypeClasses: { [key: string]: string } = {
        preventivo: 'bg-blue-500 hover:bg-blue-600',
        correctivo: 'bg-orange-500 hover:bg-orange-600',
        inspeccion: 'bg-teal-500 hover:bg-teal-600',
        general: 'bg-gray-500 hover:bg-gray-600',
    };
    const baseClasses = 'p-1 text-white rounded-lg text-xs truncate transition-colors h-full flex items-center';
    const eventClasses = `${baseClasses} ${eventTypeClasses[event.type] || eventTypeClasses.general}`;
    return <div className={eventClasses}><span>{event.title}</span></div>;
};

interface CustomToolbarProps {
    label: string;
    onNavigate: (action: string) => void;
}

const CustomToolbar: React.FC<CustomToolbarProps> = ({ label, onNavigate }) => (
    <div className="rbc-toolbar mb-4">
        <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
                 <button onClick={() => onNavigate("TODAY")} className="px-4 py-2 text-sm font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700">Hoy</button>
                 <button onClick={() => onNavigate("PREV")} className="p-2 text-gray-600 bg-gray-200 rounded-full hover:bg-gray-300"><ChevronLeft size={20} /></button>
                 <button onClick={() => onNavigate("NEXT")} className="p-2 text-gray-600 bg-gray-200 rounded-full hover:bg-gray-300"><ChevronRight size={20} /></button>
            </div>
            <h2 className="text-xl font-bold text-gray-700 capitalize">{label}</h2>
            <div className="w-40"></div>
        </div>
    </div>
);

interface EventFormProps {
    event?: MyEvent;
    slot?: { start: Date; end: Date; };
    onSave: (eventData: MyEvent) => void;
    onCancel: () => void;
}

const EventForm: React.FC<EventFormProps> = ({ event, slot, onSave, onCancel }) => {
    const [title, setTitle] = useState<string>("");
    const [start, setStart] = useState<string>("");
    const [end, setEnd] = useState<string>("");
    const [type, setType] = useState<string>("general");

    useEffect(() => {
        const initialStart = event?.start || slot?.start;
        const initialEnd = event?.end || slot?.end;
        
        setTitle(event?.title || "");
        setStart(moment(initialStart).format("YYYY-MM-DDTHH:mm"));
        setEnd(moment(initialEnd).format("YYYY-MM-DDTHH:mm"));
        setType(event?.type || "general");
    }, [event, slot]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const eventData: MyEvent = {
            id: event?.id || 0,
            title,
            start: new Date(start),
            end: new Date(end),
            type,
        };
        onSave(eventData);
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-gray-700">Título del Evento</label>
                <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md" required />
            </div>
             <div>
                <label className="block text-sm font-medium text-gray-700">Tipo de Evento</label>
                <select value={type} onChange={(e) => setType(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md">
                    <option value="general">General</option>
                    <option value="preventivo">Preventivo</option>
                    <option value="correctivo">Correctivo</option>
                    <option value="inspeccion">Inspección</option>
                </select>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Inicio</label>
                    <input type="datetime-local" value={start} onChange={(e) => setStart(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md" required />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Fin</label>
                    <input type="datetime-local" value={end} onChange={(e) => setEnd(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md" required />
                </div>
            </div>
            <div className="flex justify-end pt-4 space-x-3">
                <button type="button" onClick={onCancel} className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300">Cancelar</button>
                <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">Guardar Evento</button>
            </div>
        </form>
    );
};


// --- VISTA PRINCIPAL DEL CALENDARIO ---
const CalendarView = () => {
    const [events, setEvents] = useState(initialEvents);
    const [modalState, setModalState] = useState({ isOpen: false, mode: null, data: null });

    const handleSelectSlot = useCallback((slotInfo) => {
        if (slotInfo.action === 'click' && slotInfo.slots.length <= 1) return;
        setModalState({ isOpen: true, mode: 'create', data: { slot: slotInfo } });
    }, []);

    const handleSelectEvent = useCallback((event) => {
        setModalState({ isOpen: true, mode: 'view', data: { event } });
    }, []);
    
    const handleSaveEvent = useCallback((eventData) => {
        if (modalState.mode === 'create') {
            // Crear nuevo evento
            setEvents(prev => [...prev, { ...eventData, id: prev.length + 1 }]);
        } else if (modalState.mode === 'edit') {
            // Actualizar evento existente
            setEvents(prev => prev.map(e => e.id === eventData.id ? eventData : e));
        }
        setModalState({ isOpen: false, mode: null, data: null });
    }, [modalState.mode]);
    
    const handleDeleteEvent = useCallback((eventId) => {
        if (window.confirm("¿Está seguro de que desea eliminar este evento?")) {
            setEvents(prev => prev.filter(e => e.id !== eventId));
            setModalState({ isOpen: false, mode: null, data: null });
        }
    }, []);

    const components = useMemo(() => ({ event: CustomEventComponent, toolbar: CustomToolbar }), []);

    const renderModalContent = () => {
        const { mode, data } = modalState;
        if (mode === 'create' || mode === 'edit') {
            return <EventForm event={data?.event} slot={data?.slot} onSave={handleSaveEvent} onCancel={() => setModalState({ isOpen: false, mode: null, data: null })} />;
        }
        if (mode === 'view' && data?.event) {
            return (
                <div className="space-y-4">
                    <p><strong className="text-gray-600">Tipo:</strong> <span className="capitalize">{data.event.type}</span></p>
                    <p><strong className="text-gray-600">Desde:</strong> {moment(data.event.start).format('DD/MM/YYYY HH:mm')}</p>
                    <p><strong className="text-gray-600">Hasta:</strong> {moment(data.event.end).format('DD/MM/YYYY HH:mm')}</p>
                    {data.event.notes && <p><strong className="text-gray-600">Notas:</strong> {data.event.notes}</p>}
                    <div className="flex justify-end pt-4 space-x-3">
                        <button onClick={() => handleDeleteEvent(data.event.id)} className="bg-red-500 text-white px-4 py-2 rounded-lg flex items-center hover:bg-red-600"><Trash2 size={16} className="mr-2"/>Eliminar</button>
                        <button onClick={() => setModalState({ ...modalState, mode: 'edit' })} className="bg-indigo-500 text-white px-4 py-2 rounded-lg flex items-center hover:bg-indigo-600"><Edit size={16} className="mr-2"/>Editar</button>
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-gray-800">Calendario de Mantenimiento</h1>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-md h-[75vh]">
                <Calendar
                    localizer={localizer}
                    events={events}
                    components={components}
                    onSelectSlot={handleSelectSlot}
                    onSelectEvent={handleSelectEvent}
                    selectable
                    defaultView={Views.MONTH}
                    messages={{ /* ... sin cambios ... */ }}
                />
            </div>
            <Modal 
                isOpen={modalState.isOpen} 
                onClose={() => setModalState({ isOpen: false, mode: null, data: null })} 
                title={
                    modalState.mode === 'create' ? 'Crear Nuevo Evento' :
                    modalState.mode === 'edit' ? `Editar: ${modalState.data?.event?.title}` :
                    modalState.data?.event?.title || 'Detalles del Evento'
                }
            >
                {renderModalContent()}
            </Modal>
        </div>
    );
};

export default CalendarView;