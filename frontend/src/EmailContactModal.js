import React, { useState } from 'react';
import axios from 'axios';

const EmailContactModal = ({ isOpen, onClose, apartmentDetails, recipientEmail = 'placesfirm@gmail.com' }) => {
  const [formData, setFormData] = useState({
    senderName: '',
    senderEmail: '',
    senderPhone: '',
    message: '',
    subject: apartmentDetails ? `Interest in ${apartmentDetails.title}` : 'Inquiry from NoFeePlaces.com'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setStatus({ type: '', message: '' });

    try {
      const API_URL = process.env.REACT_APP_BACKEND_URL || 'https://rentalnobroker.preview.emergentagent.com';
      
      // Prepare email data
      const emailData = {
        to: recipientEmail,
        subject: formData.subject,
        sender_name: formData.senderName,
        sender_email: formData.senderEmail,
        sender_phone: formData.senderPhone,
        message: formData.message,
        apartment_details: apartmentDetails
      };

      const response = await axios.post(`${API_URL}/api/send-contact-email`, emailData);

      setStatus({ 
        type: 'success', 
        message: 'Your message has been sent successfully! We\'ll get back to you soon.' 
      });

      // Reset form after successful submission
      setTimeout(() => {
        setFormData({
          senderName: '',
          senderEmail: '',
          senderPhone: '',
          message: '',
          subject: apartmentDetails ? `Interest in ${apartmentDetails.title}` : 'Inquiry from NoFeePlaces.com'
        });
        onClose();
      }, 2000);

    } catch (error) {
      console.error('Error sending email:', error);
      setStatus({ 
        type: 'error', 
        message: error.response?.data?.detail || 'Failed to send message. Please try again.' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            Send Message
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        {apartmentDetails && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-2">About this listing:</h3>
            <p className="text-sm text-gray-600">{apartmentDetails.title}</p>
            {apartmentDetails.neighborhood && (
              <p className="text-sm text-gray-500">{apartmentDetails.neighborhood}</p>
            )}
            {apartmentDetails.price && (
              <p className="text-sm font-medium text-green-600">${apartmentDetails.price}/month</p>
            )}
          </div>
        )}

        {status.message && (
          <div className={`mb-4 p-3 rounded-lg text-sm ${
            status.type === 'success' 
              ? 'bg-green-50 border border-green-200 text-green-700' 
              : 'bg-red-50 border border-red-200 text-red-700'
          }`}>
            {status.message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Name *
            </label>
            <input
              type="text"
              name="senderName"
              required
              value={formData.senderName}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your full name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Email *
            </label>
            <input
              type="email"
              name="senderEmail"
              required
              value={formData.senderEmail}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="your.email@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Phone Number
            </label>
            <input
              type="tel"
              name="senderPhone"
              value={formData.senderPhone}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="(555) 123-4567"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subject
            </label>
            <input
              type="text"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Message *
            </label>
            <textarea
              name="message"
              required
              rows="4"
              value={formData.message}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder={apartmentDetails 
                ? `Hi, I'm interested in this apartment listing. Please provide more details about availability, viewing schedule, and any additional information.`
                : "Please enter your message here..."
              }
            />
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-600 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Sending...' : 'Send Message'}
            </button>
          </div>
        </form>

        <div className="mt-4 text-xs text-gray-500 text-center">
          <p>
            Message will be sent to {recipientEmail}
          </p>
        </div>
      </div>
    </div>
  );
};

export default EmailContactModal;