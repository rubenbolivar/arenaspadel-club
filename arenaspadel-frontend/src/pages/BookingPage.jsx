import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import CourtSelection from '../components/booking/CourtSelection';
import TimeSelection from '../components/booking/TimeSelection';
import UserDetails from '../components/booking/UserDetails';
import PaymentSection from '../components/booking/PaymentSection';
import BookingSummary from '../components/booking/BookingSummary';

const BookingPage = () => {
    const [step, setStep] = useState(1);
    const [bookingData, setBookingData] = useState({
        court: null,
        date: null,
        timeSlot: null,
        userDetails: null,
        paymentMethod: null
    });

    const updateBookingData = (key, value) => {
        setBookingData(prev => ({
            ...prev,
            [key]: value
        }));
        // Avanzar automáticamente al siguiente paso
        if (key !== 'paymentMethod') {
            setStep(prev => prev + 1);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Progress Bar */}
            <div className="fixed top-0 left-0 right-0 h-1 bg-gray-200">
                <motion.div 
                    className="h-full bg-blue-500"
                    initial={{ width: "0%" }}
                    animate={{ width: `${(step / 4) * 100}%` }}
                />
            </div>

            <div className="container mx-auto px-4 py-8">
                <AnimatePresence mode="wait">
                    {step === 1 && (
                        <motion.div
                            key="court-selection"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                        >
                            <CourtSelection 
                                onSelect={(court) => updateBookingData('court', court)}
                            />
                        </motion.div>
                    )}

                    {step === 2 && (
                        <motion.div
                            key="time-selection"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                        >
                            <TimeSelection 
                                courtId={bookingData.court.id}
                                onSelect={(timeData) => {
                                    updateBookingData('date', timeData.date);
                                    updateBookingData('timeSlot', timeData.slot);
                                }}
                            />
                        </motion.div>
                    )}

                    {step === 3 && (
                        <motion.div
                            key="user-details"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                        >
                            <UserDetails 
                                onSubmit={(details) => updateBookingData('userDetails', details)}
                            />
                        </motion.div>
                    )}

                    {step === 4 && (
                        <motion.div
                            key="payment"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                        >
                            <PaymentSection 
                                bookingData={bookingData}
                                onPaymentComplete={() => setStep(5)}
                            />
                        </motion.div>
                    )}

                    {step === 5 && (
                        <motion.div
                            key="summary"
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                        >
                            <BookingSummary bookingData={bookingData} />
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Floating Summary Card */}
                {step > 1 && step < 5 && (
                    <motion.div 
                        className="fixed bottom-4 right-4 bg-white p-4 rounded-lg shadow-lg"
                        initial={{ y: 100, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                    >
                        <BookingSummary 
                            bookingData={bookingData} 
                            compact={true}
                        />
                    </motion.div>
                )}
            </div>
        </div>
    );
};

export default BookingPage; 