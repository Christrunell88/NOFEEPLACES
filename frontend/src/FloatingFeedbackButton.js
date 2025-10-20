import React, { useState } from 'react';
import FeedbackModal from './FeedbackModal';

const FloatingFeedbackButton = () => {
  const [showModal, setShowModal] = useState(false);

  const handleButtonClick = () => {
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
  };

  return (
    <>
      {/* Floating Feedback Button */}
      <button
        onClick={handleButtonClick}
        className="fixed bottom-24 right-6 bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full shadow-lg hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-opacity-75 transition-all duration-300 z-40 flex items-center justify-center group"
        style={{ 
          // Position above chatbot button
          marginBottom: '20px',
          marginRight: '20px',
          minWidth: '48px',
          minHeight: '48px'
        }}
        title="Send Feedback"
        aria-label="Open feedback form to report bugs or suggest improvements"
      >
        {/* Icon and Text */}
        <div className="flex items-center">
          {/* Message Icon */}
          <svg 
            className="w-6 h-6" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" 
            />
          </svg>
          
          {/* Feedback Text (hidden on mobile, shown on hover/larger screens) */}
          <span className="ml-2 font-medium text-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300 hidden sm:inline-block">
            Feedback
          </span>
        </div>

        {/* Pulse Animation */}
        <div className="absolute inset-0 rounded-full bg-blue-400 animate-ping opacity-20"></div>
      </button>

      {/* Feedback Modal */}
      <FeedbackModal 
        isOpen={showModal} 
        onClose={handleCloseModal} 
      />
    </>
  );
};

export default FloatingFeedbackButton;