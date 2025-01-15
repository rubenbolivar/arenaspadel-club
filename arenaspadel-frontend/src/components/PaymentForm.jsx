import React, { useState } from 'react';
import { PAYMENT_TYPES } from '../utils/constants';

const PaymentForm = ({ onSubmit, amount, disabled }) => {
    const [formData, setFormData] = useState({
        paymentType: '',
        email: '',
        name: '',
        phone: '',
        reference: ''
    });
    const [errors, setErrors] = useState({});

    const validateForm = () => {
        const newErrors = {};
        
        if (!formData.paymentType) {
            newErrors.paymentType = 'Seleccione un método de pago';
        }
        if (!formData.email) {
            newErrors.email = 'El email es requerido';
        }
        if (!formData.name) {
            newErrors.name = 'El nombre es requerido';
        }
        if (!formData.phone) {
            newErrors.phone = 'El teléfono es requerido';
        }
        if (formData.paymentType !== PAYMENT_TYPES.STRIPE && !formData.reference) {
            newErrors.reference = 'El número de referencia es requerido';
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
    };

    return (
        <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold mb-6 text-center">Formulario de Pago</h2>
            
            <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                    Método de Pago
                </label>
                <select 
                    name="paymentType"
                    className={`w-full p-2 border rounded ${errors.paymentType ? 'border-red-500' : ''}`}
                    value={formData.paymentType}
                    onChange={handleChange}
                    disabled={disabled}
                >
                    <option value="">Seleccione un método</option>
                    <option value={PAYMENT_TYPES.STRIPE}>Tarjeta de Crédito</option>
                    <option value={PAYMENT_TYPES.ZELLE}>Zelle</option>
                    <option value={PAYMENT_TYPES.PAGO_MOVIL}>Pago Móvil</option>
                </select>
                {errors.paymentType && <p className="text-red-500 text-xs mt-1">{errors.paymentType}</p>}
            </div>

            <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                    Nombre Completo
                </label>
                <input 
                    type="text"
                    name="name"
                    className={`w-full p-2 border rounded ${errors.name ? 'border-red-500' : ''}`}
                    value={formData.name}
                    onChange={handleChange}
                    disabled={disabled}
                />
                {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
            </div>

            <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                    Email
                </label>
                <input 
                    type="email"
                    name="email"
                    className={`w-full p-2 border rounded ${errors.email ? 'border-red-500' : ''}`}
                    value={formData.email}
                    onChange={handleChange}
                    disabled={disabled}
                />
                {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
            </div>

            <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                    Teléfono
                </label>
                <input 
                    type="tel"
                    name="phone"
                    className={`w-full p-2 border rounded ${errors.phone ? 'border-red-500' : ''}`}
                    value={formData.phone}
                    onChange={handleChange}
                    disabled={disabled}
                />
                {errors.phone && <p className="text-red-500 text-xs mt-1">{errors.phone}</p>}
            </div>

            {formData.paymentType && formData.paymentType !== PAYMENT_TYPES.STRIPE && (
                <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2">
                        Número de Referencia
                    </label>
                    <input 
                        type="text"
                        name="reference"
                        className={`w-full p-2 border rounded ${errors.reference ? 'border-red-500' : ''}`}
                        value={formData.reference}
                        onChange={handleChange}
                        disabled={disabled}
                    />
                    {errors.reference && <p className="text-red-500 text-xs mt-1">{errors.reference}</p>}
                </div>
            )}

            <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                    Monto a Pagar
                </label>
                <input 
                    type="text"
                    className="w-full p-2 border rounded bg-gray-100"
                    value={`$${amount}`}
                    disabled
                />
            </div>

            <button 
                type="submit"
                className={`w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 
                    ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                disabled={disabled}
            >
                {disabled ? 'Procesando...' : 'Proceder al Pago'}
            </button>
        </form>
    );
};

export default PaymentForm; 