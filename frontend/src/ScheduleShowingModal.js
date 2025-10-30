import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './auth';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const ScheduleShowingModal = ({ apartment, onClose }) => {
  const { isAuthenticated, user, loading } = useAuth();
  const [showingDate, setShowingDate] = useState('');
  const [showingTime, setShowingTime] = useState('');
  const [visitorName, setVisitorName] = useState('');
  const [visitorEmail, setVisitorEmail] = useState('');
  const [visitorPhone, setVisitorPhone] = useState('');
  const [specialNotes, setSpecialNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [showAuthPrompt, setShowAuthPrompt] = useState(false);

  // Pre-fill user information if authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      setVisitorName(user.name || user.full_name || '');
      setVisitorEmail(user.email || '');
    }
  }, [isAuthenticated, user]);

  // Time slots
  const timeSlots = ['9 AM', '12 PM', '3 PM', '6 PM'];

  // Get minimum date (tomorrow)
  const getMinDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  };

  // Get maximum date (3 months from now)
  const getMaxDate = () => {
    const maxDate = new Date();
    maxDate.setMonth(maxDate.getMonth() + 3);
    return maxDate.toISOString().split('T')[0];
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMessage('');
    setSubmitStatus(null);

    // Validation
    if (!showingDate || !showingTime || !visitorName || !visitorEmail || !visitorPhone) {
      setErrorMessage('Please fill in all required fields');
      setIsSubmitting(false);
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(visitorEmail)) {
      setErrorMessage('Please enter a valid email address');
      setIsSubmitting(false);
      return;
    }

    // Phone validation (basic)
    const phoneRegex = /^\+?[\d\s\-()]{10,}$/;
    if (!phoneRegex.test(visitorPhone)) {
      setErrorMessage('Please enter a valid phone number');
      setIsSubmitting(false);
      return;
    }

    try {
      const response = await axios.post(`${API}/showings/schedule`, {
        apartment_id: apartment.id,
        apartment_title: apartment.title,
        apartment_address: apartment.address || apartment.location,
        apartment_price: apartment.price,
        showing_date: showingDate,
        showing_time: showingTime,
        visitor_name: visitorName,
        visitor_email: visitorEmail,
        visitor_phone: visitorPhone,
        special_notes: specialNotes
      });

      if (response.data.success) {
        setSubmitStatus('success');
        // Close modal after 3 seconds
        setTimeout(() => {
          onClose();
        }, 3000);
      }
    } catch (error) {
      console.error('Error scheduling showing:', error);
      if (error.response?.data?.detail) {
        setErrorMessage(error.response.data.detail);
      } else {
        setErrorMessage('Failed to schedule showing. Please try again or contact us directly.');
      }
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-xl max-w-md w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-800">📅 Schedule Showing</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
            aria-label="Close modal"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Apartment Info */}
          <div className="bg-purple-50 p-4 rounded-lg mb-6">
            <h3 className="font-semibold text-gray-800 mb-2">{apartment.title}</h3>
            <p className="text-sm text-gray-600">{apartment.neighborhood || apartment.location}</p>
            <p className="text-lg font-bold text-purple-600 mt-2">
              ${apartment.price?.toLocaleString()}/month
            </p>
          </div>

          {!isAuthenticated ? (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">🔐</div>
              <h3 className="text-2xl font-bold text-gray-800 mb-4">Sign In Required</h3>
              <p className="text-gray-600 mb-6">
                Please sign in to schedule apartment showings. This helps us verify appointments and protect both tenants and landlords.
              </p>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
                <h4 className="font-semibold text-purple-800 mb-2">Why Sign In?</h4>
                <ul className="text-sm text-purple-700 space-y-1 text-left">
                  <li>• Verify your identity for confirmed appointments</li>
                  <li>• Track your scheduled showings</li>
                  <li>• Receive calendar invites and reminders</li>
                  <li>• Get priority booking confirmations</li>
                </ul>
              </div>
              <button
                onClick={() => {
                  onClose();
                  // Trigger auth modal (this will be handled by parent component)
                  window.dispatchEvent(new CustomEvent('openAuthModal'));
                }}
                className="w-full bg-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
              >
                Sign In to Schedule
              </button>
            </div>
          ) : submitStatus === 'success' ? (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">✅</div>
              <h3 className="text-2xl font-bold text-green-600 mb-2">Showing Scheduled!</h3>
              <p className="text-gray-600">
                Check your email for confirmation and calendar invite.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              {/* Date Selection */}
              <div className="mb-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Select Date *
                </label>
                <input
                  type="date"
                  value={showingDate}
                  onChange={(e) => setShowingDate(e.target.value)}
                  min={getMinDate()}
                  max={getMaxDate()}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Must be at least 24 hours in advance
                </p>
              </div>

              {/* Time Selection */}
              <div className="mb-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Select Time *
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {timeSlots.map((time) => (
                    <button
                      key={time}
                      type="button"
                      onClick={() => setShowingTime(time)}
                      className={`px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                        showingTime === time
                          ? 'bg-purple-600 text-white border-purple-600'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-purple-400'
                      }`}
                    >
                      {time}
                    </button>
                  ))}
                </div>
              </div>

              {/* Visitor Information */}
              <div className="mb-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Your Name *
                </label>
                <input
                  type="text"
                  value={visitorName}
                  onChange={(e) => setVisitorName(e.target.value)}
                  placeholder="John Doe"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Your Email *
                </label>
                <input
                  type="email"
                  value={visitorEmail}
                  onChange={(e) => setVisitorEmail(e.target.value)}
                  placeholder="john@example.com"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Your Phone *
                </label>
                <input
                  type="tel"
                  value={visitorPhone}
                  onChange={(e) => setVisitorPhone(e.target.value)}
                  placeholder="+1 (555) 123-4567"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Special Requests (Optional)
                </label>
                <textarea
                  value={specialNotes}
                  onChange={(e) => setSpecialNotes(e.target.value)}
                  placeholder="Any special requests or questions?"
                  rows="3"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Error Message */}
              {errorMessage && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-700 text-sm">{errorMessage}</p>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-colors ${
                  isSubmitting
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-purple-600 hover:bg-purple-700'
                }`}
              >
                {isSubmitting ? 'Scheduling...' : 'Schedule Showing'}
              </button>

              <p className="text-xs text-gray-500 text-center mt-4">
                By scheduling, you'll receive a confirmation email with a calendar invite
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ScheduleShowingModal;
