import { useState } from 'react';
import api from '../services/api';
import { API_ROUTES } from '../utils/constants';

export const usePayment = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const processPayment = async (paymentData) => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await api.post(API_ROUTES.PROCESS_PAYMENT, paymentData);
            
            if (response.data.success) {
                setSuccess(true);
                return response.data;
            }
        } catch (err) {
            const errorMessage = err.response?.data?.message || 'Error procesando el pago';
            setError(errorMessage);
            throw new Error(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const resetPaymentState = () => {
        setLoading(false);
        setError(null);
        setSuccess(false);
    };

    return {
        loading,
        error,
        success,
        processPayment,
        resetPaymentState
    };
}; 