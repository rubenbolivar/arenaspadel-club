import React, { useState } from 'react';
import PaymentForm from '../components/PaymentForm';
import api from '../services/api';
import { API_ROUTES } from '../utils/constants';

const PaymentPage = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const handlePayment = async (paymentData) => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await api.post(API_ROUTES.PROCESS_PAYMENT, paymentData);
            
            if (response.data.success) {
                setSuccess(true);
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Error procesando el pago');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {error}
                </div>
            )}
            
            {success ? (
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                    ¡Pago procesado exitosamente!
                </div>
            ) : (
                <PaymentForm 
                    onSubmit={handlePayment}
                    amount={100}
                    disabled={loading}
                />
            )}
        </div>
    );
};

export default PaymentPage; 