/**
 * Landlord Portal Components for NoFeePlaces.com
 * Handles registration, listing management, and payment processing
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

// Pricing Plans Component
export const LandlordPricing = () => {
  const [pricingData, setPricingData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPricingPlans();
  }, []);

  const fetchPricingPlans = async () => {
    try {
      const response = await axios.get(`${API}/api/landlord/pricing`);
      setPricingData(response.data);
    } catch (error) {
      console.error('Error fetching pricing:', error);
    }
  };

  if (!pricingData) return <div>Loading pricing...</div>;

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            List Your No-Fee Apartments
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Join NYC's premier no-fee apartment platform. Get qualified tenant inquiries with transparent pricing and no hidden fees.
          </p>
          <div className="mt-6 bg-green-100 border border-green-400 rounded-lg p-4 inline-block">
            <span className="text-green-800 font-semibold">🎉 14-Day Free Trial - No Credit Card Required!</span>
          </div>
        </div>

        {/* Small Landlords Section */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-center mb-8">For Small Landlords (1-10 Units)</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {['basic', 'featured', 'premium'].map((planKey) => {
              const plan = pricingData.plans[planKey];
              return (
                <div key={planKey} className={`bg-white rounded-lg shadow-lg p-8 ${planKey === 'featured' ? 'ring-2 ring-purple-500 transform scale-105' : ''}`}>
                  {planKey === 'featured' && (
                    <div className="bg-purple-500 text-white text-center py-2 px-4 rounded-lg mb-4 font-semibold">
                      MOST POPULAR
                    </div>
                  )}
                  <h3 className="text-2xl font-bold text-center mb-4">{plan.name}</h3>
                  <div className="text-center mb-6">
                    <span className="text-4xl font-bold text-purple-600">${plan.price}</span>
                    <span className="text-gray-600">/apartment/month</span>
                  </div>
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-green-500 mr-2">✓</span>
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <button
                    onClick={() => navigate(`/landlord/register?plan=${planKey}`)}
                    className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
                      planKey === 'featured'
                        ? 'bg-purple-600 text-white hover:bg-purple-700'
                        : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                    }`}
                  >
                    Start Free Trial
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Large Property Managers Section */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-center mb-8">For Large Property Managers (10+ Units)</h2>
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {['portfolio', 'enterprise'].map((planKey) => {
              const plan = pricingData.plans[planKey];
              return (
                <div key={planKey} className="bg-white rounded-lg shadow-lg p-8">
                  <h3 className="text-2xl font-bold text-center mb-4">{plan.name}</h3>
                  <div className="text-center mb-6">
                    <span className="text-4xl font-bold text-purple-600">${plan.price}</span>
                    <span className="text-gray-600">/month</span>
                    <div className="text-sm text-green-600 font-semibold">Unlimited Listings</div>
                  </div>
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-green-500 mr-2">✓</span>
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <button
                    onClick={() => navigate(`/landlord/register?plan=${planKey}`)}
                    className="w-full py-3 px-4 rounded-lg font-semibold bg-purple-600 text-white hover:bg-purple-700 transition-colors"
                  >
                    Start Free Trial
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Benefits Section */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-center mb-8">Why Choose NoFeePlaces.com?</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="font-semibold mb-2">Qualified Tenants</h3>
              <p className="text-gray-600">Attract renters specifically looking for no-fee apartments</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">💰</div>
              <h3 className="font-semibold mb-2">No Commission</h3>
              <p className="text-gray-600">Keep 100% of your rent - we don't take a cut</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">📈</div>
              <h3 className="font-semibold mb-2">Analytics</h3>
              <p className="text-gray-600">Track listing performance and optimize your rentals</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Registration Component
export const LandlordRegistration = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    phone: '',
    company_name: '',
    license_number: '',
    property_count: 1,
    plan: new URLSearchParams(window.location.search).get('plan') || 'basic'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const registrationData = {
        ...formData,
        trial_requested: true
      };

      const response = await axios.post(`${API}/api/landlord/register`, registrationData);
      
      // Redirect to dashboard
      navigate(`/landlord/dashboard/${response.data.landlord_id}`);
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'property_count' ? parseInt(value) : value
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-2xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-center mb-8">Landlord Registration</h1>
          
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-green-800">🎉 14-Day Free Trial Included</h3>
            <p className="text-green-700 text-sm">No payment required. Start listing apartments immediately!</p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address *
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name or Company Name *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Property Management Company (Optional)
              </label>
              <input
                type="text"
                name="company_name"
                value={formData.company_name}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Real Estate License Number (Optional)
              </label>
              <input
                type="text"
                name="license_number"
                value={formData.license_number}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Properties You Manage *
              </label>
              <select
                name="property_count"
                value={formData.property_count}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
              >
                <option value={1}>1</option>
                <option value={2}>2-5</option>
                <option value={6}>6-10</option>
                <option value={15}>11-25</option>
                <option value={50}>25+</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Selected Plan
              </label>
              <select
                name="plan"
                value={formData.plan}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
              >
                <option value="basic">Basic - $19.99/apartment</option>
                <option value="featured">Featured - $69/apartment</option>
                <option value="premium">Premium - $99/apartment</option>
                <option value="portfolio">Portfolio - $99/month unlimited</option>
                <option value="enterprise">Enterprise - $299/month unlimited</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
            >
              {loading ? 'Creating Account...' : 'Start Free Trial'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-600 mt-6">
            Already have an account? <a href="/landlord/login" className="text-purple-600 hover:underline">Sign in</a>
          </p>
        </div>
      </div>
    </div>
  );
};

// Dashboard Component
export const LandlordDashboard = () => {
  const { landlordId } = useParams();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (landlordId) {
      fetchDashboardData();
    }
  }, [landlordId]);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/api/landlord/dashboard/${landlordId}`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading dashboard...</div>;
  if (!dashboardData) return <div>Dashboard not found</div>;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h1 className="text-3xl font-bold">Landlord Dashboard</h1>
          <p className="text-gray-600">Welcome back, {dashboardData.profile.name}!</p>
          
          {dashboardData.subscription_status === 'trial' && (
            <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h3 className="font-semibold text-yellow-800">Free Trial Active</h3>
              <p className="text-yellow-700">
                {dashboardData.days_remaining} days remaining. 
                <button className="ml-2 text-yellow-800 underline hover:no-underline">
                  Upgrade now
                </button>
              </p>
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Active Listings</h3>
            <p className="text-3xl font-bold text-purple-600">{dashboardData.active_listings}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Total Inquiries</h3>
            <p className="text-3xl font-bold text-green-600">{dashboardData.total_inquiries}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">This Month</h3>
            <p className="text-3xl font-bold text-blue-600">{dashboardData.this_month_inquiries}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Plan</h3>
            <p className="text-xl font-bold capitalize">{dashboardData.profile.subscription_plan}</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
            <div className="space-y-4">
              <button className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 transition-colors">
                + Add New Listing
              </button>
              <button className="w-full bg-gray-200 text-gray-800 py-3 px-4 rounded-lg hover:bg-gray-300 transition-colors">
                View All Listings
              </button>
              <button className="w-full bg-gray-200 text-gray-800 py-3 px-4 rounded-lg hover:bg-gray-300 transition-colors">
                Manage Account
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
            <div className="text-gray-600">
              <p>No recent activity</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Payment Success Component
export const PaymentSuccess = () => {
  const navigate = useNavigate();
  const [sessionId, setSessionId] = useState('');
  const [paymentStatus, setPaymentStatus] = useState('checking');

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const session_id = urlParams.get('session_id');
    
    if (session_id) {
      setSessionId(session_id);
      pollPaymentStatus(session_id);
    }
  }, []);

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    
    if (attempts >= maxAttempts) {
      setPaymentStatus('timeout');
      return;
    }

    try {
      const response = await axios.get(`${API}/api/landlord/payment/status/${sessionId}`);
      
      if (response.data.payment_status === 'paid') {
        setPaymentStatus('success');
        return;
      } else if (response.data.status === 'expired') {
        setPaymentStatus('expired');
        return;
      }

      // Continue polling
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), 2000);
    } catch (error) {
      console.error('Error checking payment status:', error);
      setPaymentStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
        {paymentStatus === 'checking' && (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold mb-2">Processing Payment...</h2>
            <p className="text-gray-600">Please wait while we confirm your payment.</p>
          </>
        )}

        {paymentStatus === 'success' && (
          <>
            <div className="text-green-500 text-6xl mb-4">✅</div>
            <h2 className="text-2xl font-bold mb-2">Payment Successful!</h2>
            <p className="text-gray-600 mb-6">Your subscription has been activated. You can now start listing apartments.</p>
            <button
              onClick={() => navigate('/landlord/dashboard')}
              className="bg-purple-600 text-white py-3 px-6 rounded-lg hover:bg-purple-700 transition-colors"
            >
              Go to Dashboard
            </button>
          </>
        )}

        {paymentStatus === 'error' && (
          <>
            <div className="text-red-500 text-6xl mb-4">❌</div>
            <h2 className="text-2xl font-bold mb-2">Payment Error</h2>
            <p className="text-gray-600 mb-6">There was an issue processing your payment. Please try again.</p>
            <button
              onClick={() => navigate('/landlord/pricing')}
              className="bg-purple-600 text-white py-3 px-6 rounded-lg hover:bg-purple-700 transition-colors"
            >
              Try Again
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default {
  LandlordPricing,
  LandlordRegistration,
  LandlordDashboard,
  PaymentSuccess
};