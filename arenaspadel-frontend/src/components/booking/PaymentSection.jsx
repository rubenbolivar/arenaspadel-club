import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { paymentService } from '../../services/paymentService';

const PAYMENT_METHODS = {
    ZELLE: {
        id: 'ZELLE',
        name: 'Zelle',
        icon: '💳',
        fields: ['email', 'reference']
    },
    PAGO_MOVIL: {
        id: 'PAGO_MOVIL',
        name: 'Pago Móvil',
        icon: '📱',
        fields: ['phone', 'bank', 'reference']
    }
};

const PaymentSection = ({ bookingData, onPaymentComplete }) => {
    const [selectedMethod, setSelectedMethod] = useState(null);
    const [paymentData, setPaymentData] = useState({
        email: '',
        phone: '',
        bank: '',
        reference: '',
        proofImage: null
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handlePaymentSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const formData = new FormData();
            Object.keys(paymentData).forEach(key => {
                if (paymentData[key]) {
                    formData.append(key, paymentData[key]);
                }
            });
            formData.append('payment_type', selectedMethod.id);
            formData.append('reservation_id', bookingData.reservationId);

            const response = await paymentService.processPayment(formData);
            onPaymentComplete(response.data);
        } catch (err) {
            setError(err.response?.data?.message || 'Error procesando el pago');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-md mx-auto py-8">
            <h2 className="text-3xl font-bold text-secondary mb-8 text-center">
                Método de Pago
            </h2>

            {/* Resumen del Monto */}
            <div className="bg-white p-6 rounded-lg shadow-md mb-8">
                <div className="text-center">
                    <span className="text-primary-light">Total a pagar</span>
                    <div className="text-4xl font-bold text-secondary mt-2">
                        ${bookingData.court.price_per_hour}
                    </div>
                </div>
            </div>

            {/* Selección de Método de Pago */}
            <div className="grid grid-cols-2 gap-4 mb-8">
                {Object.values(PAYMENT_METHODS).map((method) => (
                    <motion.button
                        key={method.id}
                        whileHover={{ scale: 1.03 }}
                        whileTap={{ scale: 0.97 }}
                        className={`p-4 rounded-lg text-center transition-colors
                            ${selectedMethod?.id === method.id 
                                ? 'bg-secondary text-white' 
                                : 'bg-white border-2 border-primary-light hover:border-primary'}`}
                        onClick={() => setSelectedMethod(method)}
                    >
                        <div className="text-2xl mb-2">{method.icon}</div>
                        <div className="font-medium">{method.name}</div>
                    </motion.button>
                ))}
            </div>

            {/* Formulario de Pago */}
            {selectedMethod && (
                <motion.form
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    onSubmit={handlePaymentSubmit}
                    className="space-y-6"
                >
                    {selectedMethod.fields.includes('email') && (
                        <div>
                            <label className="block text-secondary font-medium mb-2">
                                Email de Zelle
                            </label>
                            <input
                                type="email"
                                value={paymentData.email}
                                onChange={(e) => setPaymentData(prev => ({
                                    ...prev,
                                    email: e.target.value
                                }))}
                                className="w-full px-4 py-3 rounded-lg border-2 border-primary-light focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                                placeholder="email@ejemplo.com"
                                required
                            />
                        </div>
                    )}

                    {selectedMethod.fields.includes('phone') && (
                        <div>
                            <label className="block text-secondary font-medium mb-2">
                                Teléfono
                            </label>
                            <input
                                type="tel"
                                value={paymentData.phone}
                                onChange={(e) => setPaymentData(prev => ({
                                    ...prev,
                                    phone: e.target.value
                                }))}
                                className="w-full px-4 py-3 rounded-lg border-2 border-primary-light focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                                placeholder="+58 414 1234567"
                                required
                            />
                        </div>
                    )}

                    {selectedMethod.fields.includes('bank') && (
                        <div>
                            <label className="block text-secondary font-medium mb-2">
                                Banco
                            </label>
                            <select
                                value={paymentData.bank}
                                onChange={(e) => setPaymentData(prev => ({
                                    ...prev,
                                    bank: e.target.value
                                }))}
                                className="w-full px-4 py-3 rounded-lg border-2 border-primary-light focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                                required
                            >
                                <option value="">Seleccionar banco</option>
                                <option value="BANCO1">Banco 1</option>
                                <option value="BANCO2">Banco 2</option>
                                <option value="BANCO3">Banco 3</option>
                            </select>
                        </div>
                    )}

                    <div>
                        <label className="block text-secondary font-medium mb-2">
                            Número de Referencia
                        </label>
                        <input
                            type="text"
                            value={paymentData.reference}
                            onChange={(e) => setPaymentData(prev => ({
                                ...prev,
                                reference: e.target.value
                            }))}
                            className="w-full px-4 py-3 rounded-lg border-2 border-primary-light focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                            placeholder="Número de referencia"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-secondary font-medium mb-2">
                            Comprobante de Pago
                        </label>
                        <input
                            type="file"
                            accept="image/*"
                            onChange={(e) => setPaymentData(prev => ({
                                ...prev,
                                proofImage: e.target.files[0]
                            }))}
                            className="w-full"
                            required
                        />
                    </div>

                    {error && (
                        <div className="text-red-500 text-center p-4 bg-red-50 rounded-lg">
                            {error}
                        </div>
                    )}

                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        type="submit"
                        disabled={loading}
                        className={`w-full bg-secondary hover:bg-secondary-light text-white font-medium 
                            py-3 px-4 rounded-lg transition-colors duration-200
                            ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                        {loading ? 'Procesando...' : 'Confirmar Pago'}
                    </motion.button>
                </motion.form>
            )}
        </div>
    );
};

export default PaymentSection; 