import React from 'react';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const BookingSummary = ({ bookingData, compact = false }) => {
    const { court, date, timeSlot, userDetails } = bookingData;

    if (!court) return null;

    return (
        <motion.div
            initial={compact ? {} : { opacity: 0, scale: 0.95 }}
            animate={compact ? {} : { opacity: 1, scale: 1 }}
            className={`bg-white rounded-lg shadow-lg ${compact ? 'p-4' : 'p-8'}`}
        >
            {!compact && (
                <div className="text-center mb-8">
                    <div className="text-5xl mb-4">🎾</div>
                    <h2 className="text-3xl font-bold text-secondary">
                        ¡Reserva Confirmada!
                    </h2>
                </div>
            )}

            <div className={`space-y-4 ${compact ? 'text-sm' : ''}`}>
                {/* Detalles de la Cancha */}
                <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 w-12 h-12 bg-primary-light rounded-full flex items-center justify-center">
                        🏸
                    </div>
                    <div>
                        <h3 className="font-medium text-secondary">
                            {court.name}
                        </h3>
                        <p className="text-primary">
                            ${court.price_per_hour}/hora
                        </p>
                    </div>
                </div>

                {/* Fecha y Hora */}
                {date && timeSlot && (
                    <div className="flex items-start space-x-4">
                        <div className="flex-shrink-0 w-12 h-12 bg-primary-light rounded-full flex items-center justify-center">
                            📅
                        </div>
                        <div>
                            <h3 className="font-medium text-secondary">
                                {format(date, "EEEE d 'de' MMMM", { locale: es })}
                            </h3>
                            <p className="text-primary">
                                {timeSlot.start_time} - {timeSlot.end_time}
                            </p>
                        </div>
                    </div>
                )}

                {/* Datos del Usuario */}
                {userDetails && !compact && (
                    <div className="flex items-start space-x-4">
                        <div className="flex-shrink-0 w-12 h-12 bg-primary-light rounded-full flex items-center justify-center">
                            👤
                        </div>
                        <div>
                            <h3 className="font-medium text-secondary">
                                {userDetails.name}
                            </h3>
                            <p className="text-primary">
                                {userDetails.email}
                            </p>
                            <p className="text-primary-light">
                                {userDetails.phone}
                            </p>
                        </div>
                    </div>
                )}

                {/* Línea divisoria */}
                <div className="border-t border-primary-light my-4"></div>

                {/* Total */}
                <div className="flex justify-between items-center">
                    <span className="font-medium text-secondary">Total</span>
                    <span className="text-xl font-bold text-secondary">
                        ${court.price_per_hour}
                    </span>
                </div>
            </div>

            {!compact && (
                <div className="mt-8 text-center">
                    <p className="text-primary-light">
                        Recibirás un correo con los detalles de tu reserva
                    </p>
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => window.location.href = '/'}
                        className="mt-4 bg-secondary hover:bg-secondary-light text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200"
                    >
                        Volver al Inicio
                    </motion.button>
                </div>
            )}
        </motion.div>
    );
};

export default BookingSummary; 