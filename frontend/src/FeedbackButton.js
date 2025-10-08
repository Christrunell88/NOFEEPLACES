import React, { useState } from 'react';
import FeedbackModal from './FeedbackModal';

const FeedbackButton = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleOpenModal = (type = 'bug') => {
    setIsModalOpen(true);
    setIsExpanded(false);
  };

  return (
    <>
      {/* Floating Feedback Button */}
      <div className="fixed bottom-4 right-4 z-40">
        {/* Expanded Menu */}
        {isExpanded && (
          <div className="mb-2 bg-white rounded-lg shadow-lg border border-gray-200 p-2 min-w-[200px]">
            <div className="text-xs font-medium text-gray-600 mb-2 px-2">Quick Feedback:</div>
            
            <button
              onClick={() => handleOpenModal('bug')}
              className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-red-50 rounded flex items-center gap-2"
            >
              🐛 Report a Bug
            </button>
            
            <button
              onClick={() => handleOpenModal('feature')}
              className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-blue-50 rounded flex items-center gap-2"
            >
              💡 Suggest Feature
            </button>
            
            <button
              onClick={() => handleOpenModal('improvement')}
              className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-green-50 rounded flex items-center gap-2"
            >
              🔧 Improvement
            </button>
            
            <button
              onClick={() => handleOpenModal('compliment')}
              className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-yellow-50 rounded flex items-center gap-2"
            >
              👏 Leave Praise
            </button>
            
            <button
              onClick={() => handleOpenModal('other')}
              className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded flex items-center gap-2"
            >
              💬 General Feedback
            </button>
          </div>
        )}

        {/* Main Feedback Button */}
        <div className="relative group">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="bg-blue-500 hover:bg-blue-600 text-white rounded-full p-3 shadow-lg transition-all duration-300 hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-200"
            title="Share Feedback"
          >
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
          </button>
          
          {/* Tooltip */}
          {!isExpanded && (
            <div className="absolute right-full mr-3 top-1/2 transform -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
              <div className="bg-gray-800 text-white text-xs rounded py-1 px-2 whitespace-nowrap">
                Share Feedback
                <div className="absolute left-full top-1/2 transform -translate-y-1/2 border-4 border-transparent border-l-gray-800"></div>
              </div>
            </div>
          )}
        </div>

        {/* Pulse Animation for First-Time Users */}
        <div className="absolute inset-0 rounded-full bg-blue-400 animate-ping opacity-20"></div>
      </div>

      {/* Click Outside Handler */}
      {isExpanded && (
        <div 
          className="fixed inset-0 z-30" 
          onClick={() => setIsExpanded(false)}
        ></div>
      )}

      {/* Feedback Modal */}
      <FeedbackModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
      />
    </>
  );
};

export default FeedbackButton;