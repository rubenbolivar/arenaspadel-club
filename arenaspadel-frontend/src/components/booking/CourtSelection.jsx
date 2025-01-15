import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { reservationService } from '../../services/reservationService';

const CourtSelection = ({ onSelect }) => {
    const [courts, setCourts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCourts = async () => {
            try {
                const response = await reservationService.getCourts();
                setCourts(response.data);
            } catch (err) {
                setError('Error al cargar las canchas');
            } finally {
                setLoading(false);
            }
        };

        fetchCourts();
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-red-500 text-center p-4">
                {error}
            </div>
        );
    }

    return (
        <div className="py-8">
            <h2 className="text-3xl font-bold text-secondary mb-8 text-center">
                Selecciona tu cancha
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {courts.map(court => (
                    <motion.div
                        key={court.id}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="bg-white rounded-xl shadow-lg overflow-hidden cursor-pointer"
                        onClick={() => onSelect(court)}
                    >
                        {court.image ? (
                            <img 
                                src={court.image} 
                                alt={court.name}
                                className="w-full h-48 object-cover"
                            />
                        ) : (
                            <div className="w-full h-48 bg-primary-light flex items-center justify-center">
                                <span className="text-white text-lg">
                                    {court.name}
                                </span>
                            </div>
                        )}
                        
                        <div className="p-6">
                            <h3 className="text-xl font-semibold text-secondary mb-2">
                                {court.name}
                            </h3>
                            
                            <div className="flex justify-between items-center">
                                <span className="text-primary font-bold text-2xl">
                                    ${court.price_per_hour}/hora
                                </span>
                                
                                <span className="text-primary-light text-sm">
                                    {court.opening_time} - {court.closing_time}
                                </span>
                            </div>
                            
                            <button 
                                className="mt-4 w-full bg-secondary hover:bg-secondary-light text-white py-3 px-4 rounded-lg transition-colors duration-200"
                            >
                                Seleccionar
                            </button>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};

export default CourtSelection; 