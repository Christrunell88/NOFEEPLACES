import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAnalytics } from '../hooks/useAdvancedAnalytics';

// Lead Magnet: NYC Apartment Hunter's Guide
export const ApartmentGuideLeadMagnet = ({ isOpen, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    budget_range: '',
    preferred_neighborhood: '',
    move_date: '',
    apartment_type: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});
  const { trackConversion, trackLeadGeneration } = useAnalytics();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Email is invalid';
    if (!formData.budget_range) newErrors.budget_range = 'Budget range is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsSubmitting(true);
    
    try {
      // Submit lead to backend
      const response = await fetch('/api/marketing/capture-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          source: 'apartment_guide_lead_magnet',
          utm_source: 'lead_magnet',
          utm_medium: 'popup',
          utm_campaign: 'apartment_guide'
        })
      });

      if (response.ok) {
        // Track conversion
        trackConversion('lead_magnet_conversion', {
          magnet_type: 'apartment_guide',
          value: 50
        });

        trackLeadGeneration({
          source: 'apartment_guide_lead_magnet',
          type: 'lead_magnet',
          estimatedValue: 50
        });

        onSuccess && onSuccess(formData);
        
        // Reset form
        setFormData({
          name: '', email: '', budget_range: '', preferred_neighborhood: '', 
          move_date: '', apartment_type: ''
        });
        
      } else {
        throw new Error('Failed to submit lead');
      }
    } catch (error) {
      console.error('Lead submission error:', error);
      setErrors({ submit: 'Something went wrong. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="relative">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white rounded-t-lg">
              <button
                onClick={onClose}
                className="absolute top-4 right-4 text-white hover:text-gray-200"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
              
              <div className="text-center">
                <div className="text-4xl mb-2">📚</div>
                <h2 className="text-xl font-bold mb-2">FREE NYC Apartment Guide</h2>
                <p className="text-blue-100 text-sm">
                  "The Ultimate No-Fee Apartment Hunter's Guide to NYC"
                </p>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-3">
                  🎯 What You'll Get Instantly:
                </h3>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>✅ 47-page comprehensive guide</li>
                  <li>✅ Secret neighborhoods with no-fee gems</li>
                  <li>✅ Broker fee negotiation scripts</li>
                  <li>✅ Application approval checklist</li>
                  <li>✅ NYC rental calendar & timing tips</li>
                  <li>✅ Bonus: Contact info for 50+ no-fee buildings</li>
                </ul>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <input
                    type="text"
                    name="name"
                    placeholder="Your Name *"
                    value={formData.name}
                    onChange={handleInputChange}
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${errors.name ? 'border-red-500' : 'border-gray-300'}`}
                  />
                  {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
                </div>

                <div>
                  <input
                    type="email"
                    name="email"
                    placeholder="Your Email Address *"
                    value={formData.email}
                    onChange={handleInputChange}
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${errors.email ? 'border-red-500' : 'border-gray-300'}`}
                  />
                  {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
                </div>

                <div>
                  <select
                    name="budget_range"
                    value={formData.budget_range}
                    onChange={handleInputChange}
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${errors.budget_range ? 'border-red-500' : 'border-gray-300'}`}
                  >
                    <option value="">Budget Range *</option>
                    <option value="under_2000">Under $2,000</option>
                    <option value="2000_3000">$2,000 - $3,000</option>
                    <option value="3000_4000">$3,000 - $4,000</option>
                    <option value="4000_5000">$4,000 - $5,000</option>
                    <option value="5000_plus">$5,000+</option>
                  </select>
                  {errors.budget_range && <p className="text-red-500 text-xs mt-1">{errors.budget_range}</p>}
                </div>

                <div>
                  <select
                    name="preferred_neighborhood"
                    value={formData.preferred_neighborhood}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Preferred Area (Optional)</option>
                    <option value="manhattan">Manhattan</option>
                    <option value="brooklyn">Brooklyn</option>
                    <option value="queens">Queens</option>
                    <option value="bronx">Bronx</option>
                    <option value="open_to_all">Open to All Areas</option>
                  </select>
                </div>

                <div>
                  <select
                    name="move_date"
                    value={formData.move_date}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Move-in Timeline (Optional)</option>
                    <option value="asap">ASAP</option>
                    <option value="1_month">Within 1 Month</option>
                    <option value="2_months">1-2 Months</option>
                    <option value="3_months">2-3 Months</option>
                    <option value="flexible">Flexible</option>
                  </select>
                </div>

                {errors.submit && (
                  <p className="text-red-500 text-sm text-center">{errors.submit}</p>
                )}

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Sending Guide...
                    </span>
                  ) : (
                    '📚 Get My FREE Guide Now!'
                  )}
                </button>

                <p className="text-xs text-gray-500 text-center">
                  📧 Instant download link sent to your email<br/>
                  🔒 We respect your privacy. Unsubscribe anytime.
                </p>
              </form>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

// Apartment Alert Signup Lead Magnet
export const ApartmentAlertSignup = ({ className = '', variant = 'inline' }) => {
  const [email, setEmail] = useState('');
  const [preferences, setPreferences] = useState({
    neighborhoods: [],
    budget_max: '',
    bedrooms: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const { trackConversion, trackLeadGeneration } = useAnalytics();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) return;

    setIsSubmitting(true);

    try {
      const response = await fetch('/api/marketing/capture-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          budget_range: preferences.budget_max,
          preferred_neighborhood: preferences.neighborhoods.join(', '),
          apartment_type: preferences.bedrooms,
          source: 'apartment_alerts',
          utm_source: 'apartment_alerts',
          utm_medium: 'signup_form'
        })
      });

      if (response.ok) {
        trackConversion('apartment_alerts_signup', { value: 25 });
        trackLeadGeneration({
          source: 'apartment_alerts',
          type: 'email_signup',
          estimatedValue: 25
        });

        setIsSuccess(true);
        setEmail('');
        setTimeout(() => setIsSuccess(false), 5000);
      }
    } catch (error) {
      console.error('Alert signup error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (variant === 'popup') {
    return (
      <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white p-6 rounded-lg shadow-lg">
        <div className="text-center mb-4">
          <div className="text-3xl mb-2">🚨</div>
          <h3 className="text-xl font-bold">Never Miss a No-Fee Apartment!</h3>
          <p className="text-orange-100 text-sm">Get instant alerts when new apartments match your criteria</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email for alerts..."
            className="w-full px-4 py-2 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-white focus:outline-none"
            required
          />

          <button
            type="submit"
            disabled={isSubmitting || isSuccess}
            className="w-full bg-white text-orange-600 py-2 px-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors disabled:opacity-50"
          >
            {isSuccess ? '✅ Alert Set Up!' : isSubmitting ? 'Setting Up...' : '🔔 Set Up Alerts'}
          </button>
        </form>

        <p className="text-xs text-orange-200 text-center mt-2">
          Free alerts • No spam • Unsubscribe anytime
        </p>
      </div>
    );
  }

  return (
    <div className={`bg-blue-50 border border-blue-200 rounded-lg p-4 ${className}`}>
      <div className="flex items-center mb-3">
        <div className="text-2xl mr-3">🔔</div>
        <div>
          <h4 className="font-semibold text-gray-900">Get Apartment Alerts</h4>
          <p className="text-sm text-gray-600">Be first to know about new listings</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Your email..."
          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          required
        />
        <button
          type="submit"
          disabled={isSubmitting || isSuccess}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          {isSuccess ? '✅' : isSubmitting ? '...' : 'Sign Up'}
        </button>
      </form>

      {isSuccess && (
        <p className="text-green-600 text-sm mt-2">✅ You're all set for apartment alerts!</p>
      )}
    </div>
  );
};

// Exit-Intent Lead Magnet
export const ExitIntentLeadMagnet = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isGuideOpen, setIsGuideOpen] = useState(false);
  const { trackUserEngagement } = useAnalytics();

  useEffect(() => {
    let mouseLeaveTimer;
    
    const handleMouseLeave = (e) => {
      if (e.clientY <= 0) {
        mouseLeaveTimer = setTimeout(() => {
          setIsVisible(true);
          trackUserEngagement('exit_intent_triggered');
        }, 1000);
      }
    };

    const handleMouseEnter = () => {
      if (mouseLeaveTimer) {
        clearTimeout(mouseLeaveTimer);
      }
    };

    document.addEventListener('mouseleave', handleMouseLeave);
    document.addEventListener('mouseenter', handleMouseEnter);

    return () => {
      document.removeEventListener('mouseleave', handleMouseLeave);
      document.removeEventListener('mouseenter', handleMouseEnter);
      if (mouseLeaveTimer) clearTimeout(mouseLeaveTimer);
    };
  }, [trackUserEngagement]);

  const handleClose = () => {
    setIsVisible(false);
  };

  const handleGetGuide = () => {
    setIsVisible(false);
    setIsGuideOpen(true);
  };

  if (!isVisible) return null;

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -50 }}
        className="fixed top-0 left-0 right-0 bg-red-600 text-white p-4 z-50 shadow-lg"
      >
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center">
            <div className="text-2xl mr-3">⚠️</div>
            <div>
              <div className="font-bold">Wait! Don't leave empty-handed!</div>
              <div className="text-sm text-red-100">
                Get our FREE guide with 50+ no-fee apartment contacts before you go
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={handleGetGuide}
              className="bg-white text-red-600 px-6 py-2 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              📚 Get FREE Guide
            </button>
            <button
              onClick={handleClose}
              className="text-white hover:text-red-200 text-xl"
            >
              ×
            </button>
          </div>
        </div>
      </motion.div>

      <ApartmentGuideLeadMagnet
        isOpen={isGuideOpen}
        onClose={() => setIsGuideOpen(false)}
        onSuccess={handleClose}
      />
    </>
  );
};

// Lead Magnet Success Component
export const LeadMagnetSuccess = ({ isOpen, onClose, downloadUrl, magnet_type }) => {
  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 text-center"
      >
        <div className="text-6xl mb-4">🎉</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Success!</h2>
        <p className="text-gray-600 mb-6">
          Your NYC Apartment Guide is being sent to your email right now!
        </p>

        <div className="space-y-3">
          {downloadUrl && (
            <a
              href={downloadUrl}
              className="block bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              📥 Download Guide Now
            </a>
          )}

          <a
            href="tel:646-408-8048"
            className="block bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 transition-colors"
          >
            📞 Call for Personal Help: (646) 408-8048
          </a>

          <button
            onClick={onClose}
            className="block w-full text-gray-500 hover:text-gray-700 py-2"
          >
            Continue Browsing Apartments
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};