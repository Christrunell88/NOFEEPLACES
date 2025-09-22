import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from './auth';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Hero Component with Image Carousel
export const Hero = () => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const heroImages = [
    'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=1200&h=600&fit=crop',
    'https://images.unsplash.com/photo-1559767949-0faa5c7e9992?w=1200&h=600&fit=crop'
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prev) => (prev + 1) % heroImages.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const scrollToListings = () => {
    window.scrollTo({ top: 1200, behavior: 'smooth' });
  };

  return (
    <section className="relative h-96 overflow-hidden">
      {/* Background Image Carousel */}
      <div className="absolute inset-0">
        {heroImages.map((image, index) => (
          <div
            key={index}
            className={`absolute inset-0 transition-opacity duration-1000 ${
              index === currentImageIndex ? 'opacity-100' : 'opacity-0'
            }`}
          >
            <img
              src={image}
              alt={`NYC Apartment ${index + 1}`}
              className="w-full h-full object-cover"
            />
          </div>
        ))}
      </div>
      
      {/* Dark Overlay */}
      <div className="absolute inset-0 bg-black bg-opacity-50"></div>
      
      {/* Content */}
      <div className="relative z-10 flex items-center justify-center h-full">
        <div className="text-center text-white px-4">
          <h1 className="text-4xl md:text-6xl font-bold mb-4">
            No Fee <span className="text-yellow-400">NYC</span> Apartments
          </h1>
          <p className="text-xl mb-8">Save $3,000+ on broker fees</p>
          <button 
            onClick={scrollToListings}
            className="bg-yellow-500 text-black px-8 py-3 rounded-lg font-semibold hover:bg-yellow-400 transition-all transform hover:scale-105 shadow-lg"
          >
            🏠 Browse Apartments
          </button>
        </div>
      </div>
      
      {/* Image Indicators */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
        {heroImages.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentImageIndex(index)}
            className={`w-3 h-3 rounded-full transition-colors ${
              index === currentImageIndex ? 'bg-yellow-400' : 'bg-white bg-opacity-50'
            }`}
          />
        ))}
      </div>
    </section>
  );
};

// SEO Content Section - More App-like, Less Text
export const SEOContentSection = () => {
  return (
    <section className="py-8 bg-gradient-to-r from-purple-50 to-pink-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-center space-x-8 text-center">
          <div className="flex flex-col items-center">
            <div className="text-3xl mb-2">🏠</div>
            <div className="text-2xl font-bold text-purple-600">316+</div>
            <div className="text-sm text-gray-600">Apartments</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-3xl mb-2">💰</div>
            <div className="text-2xl font-bold text-green-600">$0</div>
            <div className="text-sm text-gray-600">Broker Fees</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-3xl mb-2">⚡</div>
            <div className="text-2xl font-bold text-orange-600">24/7</div>
            <div className="text-sm text-gray-600">Access</div>
          </div>
        </div>
      </div>
    </section>
  );
};

// Advanced Search Filters
export const AdvancedSearchFilters = ({ filters, onFilterChange, apartmentCount }) => {
  return (
    <div className="bg-white shadow-lg py-6">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Min Price
            </label>
            <input
              type="number"
              placeholder="Min price"
              value={filters.min_price}
              onChange={(e) => onFilterChange('min_price', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Price
            </label>
            <input
              type="number"
              placeholder="Max price"
              value={filters.max_price}
              onChange={(e) => onFilterChange('max_price', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Bedrooms
            </label>
            <select
              value={filters.bedrooms}
              onChange={(e) => onFilterChange('bedrooms', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Any</option>
              <option value="0">Studio</option>
              <option value="1">1 BR</option>
              <option value="2">2 BR</option>
              <option value="3">3 BR</option>
              <option value="4">4+ BR</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search
            </label>
            <input
              type="text"
              placeholder="Search apartments..."
              value={filters.search_term}
              onChange={(e) => onFilterChange('search_term', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>
        </div>
        
        <div className="mt-4 text-center">
          <p className="text-gray-600">
            Found {apartmentCount} no fee apartments
          </p>
        </div>
      </div>
    </div>
  );
};

// Map View Component
export const MapView = ({ apartments }) => {
  return (
    <div className="h-96 bg-gray-200 rounded-lg flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl mb-4">🗺️</div>
        <h3 className="text-xl font-semibold text-gray-700 mb-2">Map View</h3>
        <p className="text-gray-600">
          Showing {apartments.length} apartments on map
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Interactive map coming soon
        </p>
      </div>
    </div>
  );
};

// Footer Component
export const Footer = () => {
  return (
    <footer className="bg-black text-white py-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-yellow-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">🏢</span>
              </div>
              <div>
                <div className="font-bold text-lg">
                  No Fee <span className="text-yellow-400">Places</span>
                </div>
              </div>
            </div>
            <p className="text-gray-400">
              Find your perfect NYC apartment without broker fees.
            </p>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li><Link to="/" className="text-gray-400 hover:text-white">Home</Link></li>
              <li><Link to="/apartments" className="text-gray-400 hover:text-white">Apartments</Link></li>
              <li><Link to="/blog" className="text-gray-400 hover:text-white">Blog</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Neighborhoods</h3>
            <ul className="space-y-2">
              <li><span className="text-gray-400">Manhattan</span></li>
              <li><span className="text-gray-400">Brooklyn</span></li>
              <li><span className="text-gray-400">Queens</span></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Contact</h3>
            <ul className="space-y-2">
              <li><span className="text-gray-400">support@nofeeplaces.com</span></li>
              <li><span className="text-gray-400">(646) 408-8048</span></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center">
          <p className="text-gray-400">
            © 2025 NoFeePlaces.com. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

// Loading Spinner
export const LoadingSpinner = () => {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
    </div>
  );
};

// Auth Modal
export const AuthModal = ({ onClose }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    fullName: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        const result = await login(formData.email, formData.password);
        if (result.success) {
          onClose();
        } else {
          setError(result.error);
        }
      } else {
        const result = await register(formData.email, formData.password, formData.fullName);
        if (result.success) {
          onClose();
        } else {
          setError(result.error);
        }
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">
            {isLogin ? 'Sign In' : 'Sign Up'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <input
                type="text"
                required
                value={formData.fullName}
                onChange={(e) => setFormData(prev => ({ ...prev, fullName: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              />
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              required
              value={formData.password}
              onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Sign Up')}
          </button>
        </form>

        <div className="mt-4 text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-purple-600 hover:text-purple-800"
          >
            {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
          </button>
        </div>

        <div className="mt-4 text-center">
          <div className="text-sm text-gray-600 mb-2">Or continue with</div>
          <button
            onClick={() => window.location.href = `${BACKEND_URL}/api/auth/google/login`}
            className="w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors"
          >
            Continue with Google
          </button>
        </div>
      </div>
    </div>
  );
};

// Placeholder components for the remaining missing components
export const UserDashboard = ({ user }) => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold mb-6">Welcome, {user?.full_name || 'User'}!</h1>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Your Favorites</h2>
        <p className="text-gray-600">View your saved apartments</p>
      </div>
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Saved Searches</h2>
        <p className="text-gray-600">Manage your search preferences</p>
      </div>
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <p className="text-gray-600">Track your apartment views</p>
      </div>
    </div>
  </div>
);

export const SavedSearches = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold mb-6">Saved Searches</h1>
    <div className="bg-white rounded-lg shadow-lg p-6">
      <p className="text-gray-600">Your saved searches will appear here.</p>
    </div>
  </div>
);

export const AdminAppointments = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold mb-6">Admin Appointments</h1>
    <div className="bg-white rounded-lg shadow-lg p-6">
      <p className="text-gray-600">Appointment management dashboard.</p>
    </div>
  </div>
);

export const AIChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 bg-purple-600 text-white rounded-full w-12 h-12 flex items-center justify-center hover:bg-purple-700 transition-colors z-40"
      >
        💬
      </button>
      
      {isOpen && (
        <div className="fixed bottom-20 right-4 bg-white rounded-lg shadow-xl w-80 h-96 z-50 border">
          <div className="bg-purple-600 text-white p-4 rounded-t-lg">
            <div className="flex justify-between items-center">
              <h3 className="font-semibold">AI Assistant</h3>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white hover:text-gray-200"
              >
                ×
              </button>
            </div>
          </div>
          <div className="p-4 h-80 flex items-center justify-center">
            <p className="text-gray-600 text-center">
              AI chatbot coming soon! <br />
              Get help finding your perfect apartment.
            </p>
          </div>
        </div>
      )}
    </>
  );
};

export const FavoritesPage = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold mb-6">Your Favorites</h1>
    <div className="bg-white rounded-lg shadow-lg p-6">
      <p className="text-gray-600">Your favorite apartments will appear here.</p>
    </div>
  </div>
);

export const ApartmentComparison = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold mb-6">Compare Apartments</h1>
    <div className="bg-white rounded-lg shadow-lg p-6">
      <p className="text-gray-600">Compare selected apartments side by side.</p>
    </div>
  </div>
);

export const ToastProvider = ({ children }) => {
  return <div>{children}</div>;
};

export const ErrorBoundary = ({ children }) => {
  return <div>{children}</div>;
};

export const CompleteGuideNoFeeApartments = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-4xl font-bold mb-6">Complete Guide to No Fee Apartments in NYC</h1>
    <div className="prose max-w-none">
      <p className="text-lg text-gray-600 mb-6">
        Your comprehensive guide to finding and securing no fee apartments in New York City.
      </p>
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-semibold mb-4">What are No Fee Apartments?</h2>
        <p className="text-gray-600 mb-4">
          No fee apartments are rental properties where the landlord or building owner pays the broker commission instead of the tenant.
        </p>
        <h2 className="text-2xl font-semibold mb-4">Benefits of No Fee Apartments</h2>
        <ul className="list-disc list-inside text-gray-600 space-y-2">
          <li>Save thousands of dollars in broker fees</li>
          <li>Lower upfront costs when moving</li>
          <li>More money available for security deposits and moving expenses</li>
        </ul>
      </div>
    </div>
  </div>
);

export const BlogList = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBlogPosts();
  }, []);

  const fetchBlogPosts = async () => {
    try {
      const response = await axios.get(`${API}/blog`);
      setPosts(response.data.posts || []);
    } catch (error) {
      console.error('Failed to fetch blog posts:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-center">NYC Apartment Blog</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {posts.map(post => (
          <Link
            key={post.id}
            to={`/blog/${post.slug}`}
            className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
          >
            {post.featured_image && (
              <img
                src={post.featured_image}
                alt={post.title}
                className="w-full h-48 object-cover"
              />
            )}
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-2 hover:text-purple-600">
                {post.title}
              </h2>
              <p className="text-gray-600 mb-4 line-clamp-3">
                {post.excerpt}
              </p>
              <div className="text-sm text-gray-500">
                {new Date(post.created_at).toLocaleDateString()}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export const BlogPost = ({ slug }) => {
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const { slug: routeSlug } = useParams();
  
  // Use slug from props or route params
  const actualSlug = slug || routeSlug;

  useEffect(() => {
    if (actualSlug) {
      fetchBlogPost();
    }
  }, [actualSlug]);

  const fetchBlogPost = async () => {
    try {
      const response = await axios.get(`${API}/blog/${actualSlug}`);
      setPost(response.data);
    } catch (error) {
      console.error('Failed to fetch blog post:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!post) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Post Not Found</h1>
        <p className="text-gray-600">The blog post you're looking for doesn't exist.</p>
      </div>
    );
  }

  return (
    <article className="container mx-auto px-4 py-8 max-w-4xl">
      {post.featured_image && (
        <img
          src={post.featured_image}
          alt={post.title}
          className="w-full h-64 object-cover rounded-lg mb-8"
        />
      )}
      
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">{post.title}</h1>
        <div className="flex items-center space-x-4 text-gray-600">
          <span>By {post.author}</span>
          <span>•</span>
          <span>{new Date(post.created_at).toLocaleDateString()}</span>
          <span>•</span>
          <span>{post.category}</span>
        </div>
      </header>

      <div 
        className="prose max-w-none"
        dangerouslySetInnerHTML={{ __html: post.content }}
      />
    </article>
  );
};

// Email Contact Modal
export const EmailContactModal = ({ apartment, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    message: `Hi, I'm interested in the apartment at ${apartment.address || apartment.location}. Please provide more information about availability and scheduling a viewing.`
  });
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSending(true);
    
    try {
      // Simulate sending email
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSent(true);
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setSending(false);
    }
  };

  if (sent) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg max-w-md w-full p-6 text-center">
          <div className="text-green-600 text-4xl mb-4">✓</div>
          <h2 className="text-2xl font-bold mb-2">Message Sent!</h2>
          <p className="text-gray-600">We'll get back to you soon.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Contact About This Apartment</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Name
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Phone (optional)
            </label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Message
            </label>
            <textarea
              required
              rows="4"
              value={formData.message}
              onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <button
            type="submit"
            disabled={sending}
            className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
          >
            {sending ? 'Sending...' : 'Send Message'}
          </button>
        </form>
      </div>
    </div>
  );
};