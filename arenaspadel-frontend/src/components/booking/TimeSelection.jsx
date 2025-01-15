import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { reservationService } from '../../services/reservationService';
import { format, addDays } from 'date-fns';
import { es } from 'date-fns/locale';

const TimeSelection = ({ courtId, onSelect }) => {
    const [selectedDate, setSelectedDate] = useState(new Date());
    const [availableSlots, setAvailableSlots] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Generar próximos 7 días
    const nextDays = Array.from({ length: 7 }, (_, i) => addDays(new Date(), i));

    useEffect(() => {
        const fetchAvailability = async () => {
            setLoading(true);
            try {
                const formattedDate = format(selectedDate, 'yyyy-MM-dd');
                const response = await reservationService.checkAvailability(
                    courtId, 
                    formattedDate
                );
                setAvailableSlots(response.data.available_slots);
            } catch (err) {
                setError('Error al cargar los horarios disponibles');
            } finally {
                setLoading(false);
            }
        };

        fetchAvailability();
    }, [courtId, selectedDate]);

    return (
        <div className="py-8">
            <h2 className="text-3xl font-bold text-secondary mb-8 text-center">
                Selecciona fecha y hora
            </h2>

            {/* Selector de Fecha */}
            <div className="flex overflow-x-auto pb-4 mb-8 gap-2">
                {nextDays.map((date) => (
                    <motion.button
                        key={date.toISOString()}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`
                            flex-shrink-0 p-4 rounded-lg text-center min-w-[120px]
                            ${selectedDate.toDateString() === date.toDateString()
                                ? 'bg-secondary text-white'
                                : 'bg-white border-2 border-primary-light text-secondary hover:border-primary'}
                        `}
                        onClick={() => setSelectedDate(date)}
                    >
                        <div className="font-bold">
                            {format(date, 'EEEE', { locale: es })}
                        </div>
                        <div className="text-sm">
                            {format(date, 'd MMM', { locale: es })}
                        </div>
                    </motion.button>
                ))}
            </div>

            {/* Horarios Disponibles */}
            {loading ? (
                <div className="flex justify-center items-center h-48">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                </div>
            ) : error ? (
                <div className="text-red-500 text-center p-4">{error}</div>
            ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {availableSlots.map((slot) => (
                        <motion.button
                            key={`${slot.start_time}-${slot.end_time}`}
                            whileHover={{ scale: 1.03 }}
                            whileTap={{ scale: 0.97 }}
                            className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow"
                            onClick={() => onSelect({
                                date: selectedDate,
                                slot: slot
                            })}
                        >
                            <div className="text-secondary font-semibold">
                                {slot.start_time}
                            </div>
                            <div className="text-primary-light text-sm">
                                1 hora
                            </div>
                        </motion.button>
                    ))}
                </div>
            )}

            {availableSlots.length === 0 && !loading && !error && (
                <div className="text-center p-8 bg-primary-light/10 rounded-lg">
                    <p className="text-secondary">
                        No hay horarios disponibles para esta fecha
                    </p>
                    <p className="text-primary-light text-sm mt-2">
                        Por favor, selecciona otro día
                    </p>
                </div>
            )}
        </div>
    );
};

export default TimeSelection; 