import React, { useState, useEffect } from 'react';
import { useAuth } from './auth';

const FeedbackModal = ({ isOpen, onClose }) => {
  const { isAuthenticated, user, loading } = useAuth();
  const [feedbackData, setFeedbackData] = useState({
    type: 'bug',
    title: '',
    description: '',
    email: '',
    page: window.location.pathname,
    userAgent: navigator.userAgent,
    priority: 'medium'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);

  // Pre-fill email if authenticated
  useEffect(() => {
    if (isAuthenticated && user && user.email) {
      setFeedbackData(prev => ({
        ...prev,
        email: user.email
      }));
    }
  }, [isAuthenticated, user]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFeedbackData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus(null);

    try {
      const API_URL = process.env.REACT_APP_BACKEND_URL;
      
      const submitData = {
        ...feedbackData,
        timestamp: new Date().toISOString(),
        url: window.location.href
      };
      
      console.log('Submitting feedback data:', submitData);
      console.log('API URL:', `${API_URL}/api/feedback/submit`);
      
      const response = await fetch(`${API_URL}/api/feedback/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData)
      });

      if (response.ok) {
        setSubmitStatus('success');
        setFeedbackData({
          type: 'bug',
          title: '',
          description: '',
          email: '',
          page: window.location.pathname,
          userAgent: navigator.userAgent,
          priority: 'medium'
        });
        
        // Auto-close after success
        setTimeout(() => {
          onClose();
          setSubmitStatus(null);
        }, 2000);
      } else {
        const errorText = await response.text();
        console.error('Feedback submission failed:', response.status, errorText);
        throw new Error(`Failed to submit feedback: ${response.status} ${errorText}`);
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-800">💬 Share Feedback</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-xl font-bold"
              aria-label="Close feedback modal"
            >
              ×
            </button>
          </div>

          {/* Authentication Gate */}
          {!isAuthenticated ? (
            <div className="text-center py-6">
              <div className="text-6xl mb-4">🔐</div>
              <h3 className="text-xl font-bold text-gray-800 mb-3">Sign In Required</h3>
              <p className="text-gray-600 mb-6">
                Please sign in to leave feedback. This helps us track and respond to your suggestions more effectively.
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h4 className="font-semibold text-blue-800 mb-2">Why Sign In?</h4>
                <ul className="text-sm text-blue-700 space-y-1 text-left">
                  <li>• Get updates on your feedback</li>
                  <li>• Track your reported issues</li>
                  <li>• Receive priority support</li>
                  <li>• Build your contribution history</li>
                </ul>
              </div>
              <button
                onClick={() => {
                  onClose();
                  window.dispatchEvent(new CustomEvent('openAuthModal'));
                }}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Sign In to Leave Feedback
              </button>
            </div>
          ) : (
            <>
              {/* Success Message */}
              {submitStatus === 'success' && (
                <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
                  ✅ Thank you! Your feedback has been submitted successfully.
                </div>
              )}

              {/* Error Message */}
              {submitStatus === 'error' && (
                <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                  ❌ Sorry, there was an error submitting your feedback. Please try again.
                </div>
              )}

              {/* Feedback Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
            {/* Feedback Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                What type of feedback is this?
              </label>
              <select
                name="type"
                value={feedbackData.type}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value="bug">🐛 Bug Report</option>
                <option value="feature">💡 Feature Request</option>
                <option value="improvement">🔧 Improvement Suggestion</option>
                <option value="compliment">👏 Compliment</option>
                <option value="other">❓ Other</option>
              </select>
            </div>

            {/* Priority */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority Level
              </label>
              <select
                name="priority"
                value={feedbackData.priority}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="low">🟢 Low - Minor issue</option>
                <option value="medium">🟡 Medium - Moderate issue</option>
                <option value="high">🟠 High - Important issue</option>
                <option value="urgent">🔴 Urgent - Critical issue</option>
              </select>
            </div>

            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Brief Summary *
              </label>
              <input
                type="text"
                name="title"
                value={feedbackData.title}
                onChange={handleInputChange}
                placeholder="e.g., Search results not loading"
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Detailed Description *
              </label>
              <textarea
                name="description"
                value={feedbackData.description}
                onChange={handleInputChange}
                rows={4}
                placeholder={
                  feedbackData.type === 'bug' 
                    ? "Please describe what happened, what you expected, and steps to reproduce..."
                    : feedbackData.type === 'feature'
                    ? "Describe the feature you'd like to see and how it would help..."
                    : "Please provide details about your feedback..."
                }
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            {/* Email (Optional) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email (Optional)
              </label>
              <input
                type="email"
                name="email"
                value={feedbackData.email}
                onChange={handleInputChange}
                placeholder="your@email.com (if you'd like a response)"
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Current Page Info */}
            <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
              <strong>Page:</strong> {feedbackData.page}<br/>
              <strong>Browser:</strong> {navigator.userAgent.split(' ')[0]}
            </div>

            {/* Submit Button */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting || !feedbackData.title || !feedbackData.description}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
              </button>
            </div>
          </form>
          </>
          )}

          {/* Footer */}
          <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500 text-center">
            Your feedback helps us improve NoFeePlaces.com for everyone! 🏠
          </div>
        </div>
      </div>
    </div>
  );
};

export default FeedbackModal;