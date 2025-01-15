import React, { useState } from 'react';
import { motion } from 'framer-motion';

const UserDetails = ({ onSubmit }) => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
        isNewUser: true
    });

    const [errors, setErrors] = useState({});

    const validateForm = () => {
        const newErrors = {};
        if (!formData.name.trim()) newErrors.name = 'El nombre es requerido';
        if (!formData.email.trim()) {
            newErrors.email = 'El email es requerido';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Email inválido';
        }
        if (!formData.phone.trim()) {
            newErrors.phone = 'El teléfono es requerido';
        } else if (!/^\+?[0-9]{10,12}$/.test(formData.phone.replace(/\s/g, ''))) {
            newErrors.phone = 'Teléfono inválido';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (validateForm()) {
            onSubmit(formData);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        // Limpiar error del campo cuando el usuario empieza a escribir
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-md mx-auto py-8"
        >
            <h2 className="text-3xl font-bold text-secondary mb-8 text-center">
                Tus datos
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label className="block text-secondary font-medium mb-2">
                        Nombre completo
                    </label>
                    <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        className={`w-full px-4 py-3 rounded-lg border-2 focus:outline-none focus:ring-2 
                            ${errors.name 
                                ? 'border-red-500 focus:ring-red-200' 
                                : 'border-primary-light focus:ring-primary/20 focus:border-primary'}`}
                        placeholder="Ej: Juan Pérez"
                    />
                    {errors.name && (
                        <p className="text-red-500 text-sm mt-1">{errors.name}</p>
                    )}
                </div>

                <div>
                    <label className="block text-secondary font-medium mb-2">
                        Email
                    </label>
                    <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        className={`w-full px-4 py-3 rounded-lg border-2 focus:outline-none focus:ring-2 
                            ${errors.email 
                                ? 'border-red-500 focus:ring-red-200' 
                                : 'border-primary-light focus:ring-primary/20 focus:border-primary'}`}
                        placeholder="Ej: juan@email.com"
                    />
                    {errors.email && (
                        <p className="text-red-500 text-sm mt-1">{errors.email}</p>
                    )}
                </div>

                <div>
                    <label className="block text-secondary font-medium mb-2">
                        Teléfono
                    </label>
                    <input
                        type="tel"
                        name="phone"
                        value={formData.phone}
                        onChange={handleChange}
                        className={`w-full px-4 py-3 rounded-lg border-2 focus:outline-none focus:ring-2 
                            ${errors.phone 
                                ? 'border-red-500 focus:ring-red-200' 
                                : 'border-primary-light focus:ring-primary/20 focus:border-primary'}`}
                        placeholder="Ej: +58 414 1234567"
                    />
                    {errors.phone && (
                        <p className="text-red-500 text-sm mt-1">{errors.phone}</p>
                    )}
                </div>

                <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    type="submit"
                    className="w-full bg-secondary hover:bg-secondary-light text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200"
                >
                    Continuar
                </motion.button>
            </form>
        </motion.div>
    );
};

export default UserDetails; 