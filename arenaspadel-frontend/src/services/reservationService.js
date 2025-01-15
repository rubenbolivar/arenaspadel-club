import api from './api';

export const reservationService = {
    getCourts: () => api.get('/courts'),
    
    checkAvailability: (courtId, date) => 
        api.get(`/courts/${courtId}/availability`, { params: { date } }),
    
    createReservation: (data) => api.post('/reservations', data)
}; 