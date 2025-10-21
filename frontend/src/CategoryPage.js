import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { Header, ApartmentCard } from './components';
import { useAuth } from './auth';
import { CategoryMetaTags } from './MetaTags';

const API = process.env.REACT_APP_BACKEND_URL || '';

const CATEGORY_CONFIG = {
  'best-value': {
    title: 'Best Value Apartments',
    emoji: '⭐',
    description: 'Top-rated apartments offering exceptional value based on price per square foot, premium amenities, and desirable neighborhoods. Only the top 20% make the cut.',
    priceRange: 'All Price Ranges',
    color: 'purple',
    seoTitle: 'Best Value No-Fee Apartments NYC | Top Deals | NoFeePlaces',
    seoDescription: 'Discover NYC\'s best value apartments - luxury amenities at great prices. Hand-picked top 20% based on price/sqft, location, and features. No broker fees.',
    features: [
      'Top 20% value score',
      'Luxury amenities included',
      'Best price per square foot',
      'Prime locations & neighborhoods'
    ]
  },
  budget: {
    title: 'Budget Apartments',
    emoji: '💰',
    description: 'Affordable no-fee apartments under $4,500/month. Perfect for budget-conscious renters looking for quality apartments without breaking the bank.',
    priceRange: 'Under $4,500/mo',
    color: 'green',
    seoTitle: 'Budget No-Fee Apartments NYC | Under $4,500/mo | NoFeePlaces',
    seoDescription: 'Find affordable NYC apartments under $4,500/month with zero broker fees. 129+ verified budget-friendly rentals in Manhattan, Brooklyn, Queens. Save $3,000+ on fees.',
    features: [
      'All under $4,500/month',
      'Zero broker fees',
      'Quality verified listings',
      'Budget-friendly neighborhoods'
    ]
  },
  smart: {
    title: 'Smart Value Apartments',
    emoji: '🎯',
    description: 'Best value apartments from $4,500-$6,500/month. Great quality at fair prices - the smart choice for professionals.',
    priceRange: '$4,500 - $6,500/mo',
    color: 'blue',
    seoTitle: 'Smart Value No-Fee Apartments NYC | $4,500-$6,500 | NoFeePlaces',
    seoDescription: 'Best value NYC apartments $4,500-$6,500/month with no broker fees. 69+ quality rentals in prime locations. Smart living at fair prices.',
    features: [
      'Sweet spot pricing $4,500-$6,500',
      'Best value for quality',
      'Modern amenities included',
      'Prime NYC locations'
    ]
  },
  luxury: {
    title: "Sky's the Limit Apartments",
    emoji: '✨',
    description: 'Premium luxury apartments over $6,500/month. Top-tier amenities, prime locations, and exceptional quality for those who want the best.',
    priceRange: 'Over $6,500/mo',
    color: 'amber',
    seoTitle: "Luxury No-Fee Apartments NYC | Sky's the Limit | NoFeePlaces",
    seoDescription: 'Premium luxury NYC apartments over $6,500/month with no broker fees. 22+ high-end rentals with top amenities, doorman, and prime locations.',
    features: [
      'Premium luxury $6,500+',
      'Top-tier amenities',
      'Prime Manhattan locations',
      'White-glove service'
    ]
  }
};

export const CategoryPage = () => {
  const { category } = useParams();
  const config = CATEGORY_CONFIG[category];
  const { isAuthenticated } = useAuth();
  
  const [apartments, setApartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, avgPrice: 0 });

  useEffect(() => {
    if (!config) return;
    
    // Set page title and meta description for SEO
    document.title = config.seoTitle;
    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc) {
      metaDesc.setAttribute('content', config.seoDescription);
    }
    
    fetchCategoryApartments();
  }, [category]);

  const fetchCategoryApartments = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/api/apartments/category/${category}`);
      setApartments(response.data.apartments || []);
      setStats(response.data.stats || { total: 0, avgPrice: 0 });
    } catch (error) {
      console.error('Error fetching category apartments:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!config) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">Category Not Found</h1>
          <Link to="/" className="text-mint-400 hover:text-mint-300">Go Home</Link>
        </div>
      </div>
    );
  }

  const colorClasses = {
    purple: {
      bg: 'bg-purple-50',
      border: 'border-purple-200',
      text: 'text-purple-800',
      badge: 'bg-purple-100 text-purple-800',
      button: 'bg-purple-600 hover:bg-purple-700'
    },
    green: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-800',
      badge: 'bg-green-100 text-green-800',
      button: 'bg-green-600 hover:bg-green-700'
    },
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-800',
      badge: 'bg-blue-100 text-blue-800',
      button: 'bg-blue-600 hover:bg-blue-700'
    },
    amber: {
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      text: 'text-amber-800',
      badge: 'bg-amber-100 text-amber-800',
      button: 'bg-amber-600 hover:bg-amber-700'
    }
  };

  const colors = colorClasses[config.color];

  return (
    <div className="min-h-screen bg-gray-900">
      <Header />
      
      {/* Hero Section */}
      <div className={`${colors.bg} border-b-4 ${colors.border} py-12`}>
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <div className="text-6xl mb-4">{config.emoji}</div>
            <h1 className={`text-4xl md:text-5xl font-bold ${colors.text} mb-4`}>
              {config.title}
            </h1>
            <p className="text-xl text-gray-700 mb-6">
              {config.description}
            </p>
            <div className={`inline-block ${colors.badge} px-6 py-2 rounded-full text-lg font-semibold mb-8`}>
              {config.priceRange}
            </div>
            
            {/* Stats */}
            <div className="flex justify-center gap-8 mb-8">
              <div className="text-center">
                <div className={`text-3xl font-bold ${colors.text}`}>{stats.total}</div>
                <div className="text-gray-600">Apartments</div>
              </div>
              <div className="text-center">
                <div className={`text-3xl font-bold ${colors.text}`}>${stats.avgPrice?.toLocaleString()}</div>
                <div className="text-gray-600">Avg Price/mo</div>
              </div>
              <div className="text-center">
                <div className={`text-3xl font-bold ${colors.text}`}>$0</div>
                <div className="text-gray-600">Broker Fees</div>
              </div>
            </div>

            {/* Features */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
              {config.features.map((feature, index) => (
                <div key={index} className="bg-white rounded-lg p-3 shadow-sm">
                  <p className="text-sm text-gray-700 font-medium">✓ {feature}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Breadcrumb */}
      <div className="container mx-auto px-4 py-4">
        <nav className="text-sm">
          <Link to="/" className="text-mint-400 hover:text-mint-300">Home</Link>
          <span className="text-gray-500 mx-2">/</span>
          <span className="text-gray-300">{config.title}</span>
        </nav>
      </div>

      {/* Apartments Grid */}
      <div className="container mx-auto px-4 py-8">
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-mint-500"></div>
          </div>
        ) : apartments.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-gray-400 text-xl">No apartments found in this category</p>
          </div>
        ) : (
          <>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-white">
                {stats.total} {config.title} Available
              </h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {apartments.map((apartment) => (
                <ApartmentCard
                  key={apartment.id}
                  apartment={apartment}
                  isAuthenticated={isAuthenticated}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {/* CTA Section */}
      <div className={`${colors.bg} border-t-4 ${colors.border} py-12 mt-12`}>
        <div className="container mx-auto px-4 text-center">
          <h2 className={`text-3xl font-bold ${colors.text} mb-4`}>
            Ready to Find Your Perfect {category === 'budget' ? 'Budget-Friendly' : category === 'smart' ? 'Smart Value' : 'Luxury'} Apartment?
          </h2>
          <p className="text-gray-700 mb-6 max-w-2xl mx-auto">
            Browse all {stats.total} no-fee apartments in this category or explore our other price ranges.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/"
              className={`${colors.button} text-white px-8 py-3 rounded-lg font-semibold transition-colors`}
            >
              Browse All Apartments
            </Link>
            {category !== 'budget' && (
              <Link
                to="/apartments/budget"
                className="bg-gray-600 hover:bg-gray-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
              >
                💰 View Budget Options
              </Link>
            )}
            {category !== 'smart' && (
              <Link
                to="/apartments/smart"
                className="bg-gray-600 hover:bg-gray-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
              >
                🎯 View Smart Value
              </Link>
            )}
            {category !== 'luxury' && (
              <Link
                to="/apartments/luxury"
                className="bg-gray-600 hover:bg-gray-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
              >
                ✨ View Luxury
              </Link>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CategoryPage;
