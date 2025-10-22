import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { Header, ApartmentCard } from './components';
import { useAuth } from './auth';
import { BoroughMetaTags } from './CanonicalMeta';

const API = process.env.REACT_APP_BACKEND_URL || '';

const BoroughPage = () => {
  const { borough } = useParams();
  const [apartments, setApartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, avgPrice: 0 });
  const { isAuthenticated, user, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  useEffect(() => {
    fetchBoroughApartments();
  }, [borough]);

  const fetchBoroughApartments = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/api/apartments`, {
        params: {
          borough: borough.charAt(0).toUpperCase() + borough.slice(1),
          limit: 100
        }
      });

      const data = response.data;
      setApartments(data.apartments || []);
      setStats({
        total: data.total || 0,
        avgPrice: data.apartments?.length > 0 
          ? Math.round(data.apartments.reduce((sum, apt) => sum + apt.price, 0) / data.apartments.length)
          : 0
      });
    } catch (error) {
      console.error('Error fetching borough apartments:', error);
      setApartments([]);
    } finally {
      setLoading(false);
    }
  };

  const boroughInfo = {
    manhattan: {
      name: 'Manhattan',
      emoji: '🏙️',
      description: 'Discover luxury and convenience in the heart of NYC',
      color: 'blue'
    },
    brooklyn: {
      name: 'Brooklyn',
      emoji: '🌉',
      description: 'Vibrant neighborhoods with artistic flair and brownstone charm',
      color: 'orange'
    },
    queens: {
      name: 'Queens',
      emoji: '🏘️',
      description: 'Diverse communities with great value and accessibility',
      color: 'green'
    },
    bronx: {
      name: 'Bronx',
      emoji: '🏡',
      description: 'Affordable living with cultural richness and green spaces',
      color: 'purple'
    }
  };

  const info = boroughInfo[borough.toLowerCase()] || boroughInfo.manhattan;

  const colorClasses = {
    blue: 'bg-blue-600 border-blue-400',
    orange: 'bg-orange-600 border-orange-400',
    green: 'bg-green-600 border-green-400',
    purple: 'bg-purple-600 border-purple-400'
  };

  return (
    <div className="min-h-screen bg-gray-900">
      {/* SEO Meta Tags & Structured Data */}
      <BoroughMetaTags borough={info.name} apartmentCount={stats.total} />
      
      <Header 
        isAuthenticated={isAuthenticated}
        user={user}
        logout={logout}
        setShowAuthModal={setShowAuthModal}
      />

      {/* Hero Section */}
      <div className={`${colorClasses[info.color]} py-12 border-b-4`}>
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center text-white">
            <div className="text-6xl mb-4">{info.emoji}</div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              No-Fee Apartments in {info.name}
            </h1>
            <p className="text-xl text-white/90 mb-6">
              {info.description}
            </p>
            <div className="flex justify-center gap-8 text-lg">
              <div>
                <span className="font-bold text-3xl">{stats.total}</span>
                <div className="text-white/80">Apartments</div>
              </div>
              {stats.avgPrice > 0 && (
                <div>
                  <span className="font-bold text-3xl">${stats.avgPrice.toLocaleString()}</span>
                  <div className="text-white/80">Avg. Price</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Breadcrumb */}
      <div className="bg-gray-800 py-3 border-b border-gray-700">
        <div className="container mx-auto px-4">
          <div className="flex items-center text-sm text-gray-400">
            <Link to="/" className="hover:text-white">Home</Link>
            <span className="mx-2">/</span>
            <span className="text-white">{info.name}</span>
          </div>
        </div>
      </div>

      {/* Apartments Listing */}
      <div className="container mx-auto px-4 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
            <p className="text-white mt-4">Loading {info.name} apartments...</p>
          </div>
        ) : apartments.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-white text-xl">No apartments found in {info.name} at the moment.</p>
            <Link to="/" className="text-blue-400 hover:underline mt-4 inline-block">
              Browse all apartments
            </Link>
          </div>
        ) : (
          <>
            <div className="text-white mb-6">
              <h2 className="text-2xl font-bold">
                {stats.total} No-Fee Apartments in {info.name}
              </h2>
              <p className="text-gray-400 mt-2">
                Browse apartments with zero broker fees
              </p>
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
      <div className="bg-gray-800 py-12 mt-12">
        <div className="container mx-auto px-4 text-center">
          <h3 className="text-2xl font-bold text-white mb-4">
            Explore More Apartments in Other NYC Boroughs
          </h3>
          <p className="text-gray-300 mb-6">
            Browse apartments in Manhattan, Brooklyn, Queens, and more
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            {Object.keys(boroughInfo)
              .filter(b => b !== borough.toLowerCase())
              .map(b => (
                <Link
                  key={b}
                  to={`/${b}`}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  {boroughInfo[b].emoji} {boroughInfo[b].name}
                </Link>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BoroughPage;
