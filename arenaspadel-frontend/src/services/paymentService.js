import api from './api';

export const paymentService = {
    processPayment: (formData) => 
        api.post('/payments', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
}; 