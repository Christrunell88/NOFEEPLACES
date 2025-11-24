import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './RobustAuth';
import { ApartmentDetailsModal } from './components';
import { EmailContactModal } from './missing-components';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Tenant Browse Page - Browse apartments listed by tenants
export const TenantBrowsePage = () => {
  const { isAuthenticated } = useAuth();
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedListing, setSelectedListing] = useState(null);
  const [showContactModal, setShowContactModal] = useState(false);
  const [contactListing, setContactListing] = useState(null);
  const [filters, setFilters] = useState({
    listing_type: 'all',
    borough: 'all',
    min_price: '',
    max_price: '',
    bedrooms: 'all'
  });

  const listingTypes = [
    { value: 'all', label: 'All Types' },
    { value: 'sublet', label: 'Sublets' },
    { value: 'roommate', label: 'Roommate Wanted' },
    { value: 'lease_transfer', label: 'Lease Transfers' }
  ];

  const boroughs = [
    { value: 'all', label: 'All Boroughs' },
    { value: 'Manhattan', label: 'Manhattan' },
    { value: 'Brooklyn', label: 'Brooklyn' },
    { value: 'Queens', label: 'Queens' },
    { value: 'Bronx', label: 'Bronx' },
    { value: 'Staten Island', label: 'Staten Island' }
  ];

  useEffect(() => {
    fetchTenantListings();
  }, [filters]);

  const fetchTenantListings = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/tenant/listings/approved`);
      
      if (response.data.success) {
        let filteredListings = response.data.listings;
        
        // Apply filters
        if (filters.listing_type !== 'all') {
          filteredListings = filteredListings.filter(listing => 
            listing.listing_type === filters.listing_type
          );
        }
        
        if (filters.borough !== 'all') {
          filteredListings = filteredListings.filter(listing => 
            listing.borough === filters.borough
          );
        }
        
        if (filters.min_price) {
          filteredListings = filteredListings.filter(listing => 
            parseFloat(listing.rent_price) >= parseFloat(filters.min_price)
          );
        }
        
        if (filters.max_price) {
          filteredListings = filteredListings.filter(listing => 
            parseFloat(listing.rent_price) <= parseFloat(filters.max_price)
          );
        }
        
        if (filters.bedrooms !== 'all') {
          filteredListings = filteredListings.filter(listing => 
            listing.bedrooms === filters.bedrooms
          );
        }
        
        setListings(filteredListings);
      }
    } catch (error) {
      console.error('Error fetching tenant listings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  const getListingTypeColor = (type) => {
    switch (type) {
      case 'sublet': return 'bg-blue-100 text-blue-800';
      case 'roommate': return 'bg-green-100 text-green-800';
      case 'lease_transfer': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getListingTypeIcon = (type) => {
    switch (type) {
      case 'sublet': return '🏠';
      case 'roommate': return '👥';
      case 'lease_transfer': return '📝';
      default: return '🏡';
    }
  };

  const convertToApartmentFormat = (listing) => {
    return {
      id: listing.id,
      title: listing.title,
      description: listing.description,
      price: parseFloat(listing.rent_price),
      location: `${listing.neighborhood}, ${listing.borough}`,
      neighborhood: listing.neighborhood,
      bedrooms: parseInt(listing.bedrooms) || 0,
      bathrooms: parseFloat(listing.bathrooms) || 1,
      sqft: parseInt(listing.sqft) || 800,
      amenities: listing.amenities || [],
      images: listing.images || [],
      contact_email: "placesfirm@gmail.com",
      contact_phone: "+1-646-408-8048",
      available: true,
      address: isAuthenticated ? listing.address : `${listing.neighborhood}, ${listing.borough}`,
      lease_terms: listing.lease_terms || 'Flexible',
      pet_policy: listing.pets_allowed ? 'Pets allowed' : 'No pets',
      utilities: listing.utilities_included ? 'Utilities included' : 'Utilities separate',
      move_in_date: listing.available_date,
      deposit: listing.deposit_required || 'Contact for details',
      broker_fee: 'No fee',
      listing_type: listing.listing_type,
      furnished: listing.furnished,
      short_term_ok: listing.short_term_ok,
      original_tenant: {
        name: listing.contact_name,
        email: listing.contact_email,
        phone: listing.contact_phone
      }
    };
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-4">
              🏠 Tenant Listings
            </h1>
            <p className="text-xl text-orange-100 mb-6">
              Find sublets, roommates, and lease transfers directly from NYC tenants
            </p>
            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <div className="bg-white bg-opacity-20 px-4 py-2 rounded-full">
                <span className="font-semibold">{listings.length}</span> Active Listings
              </div>
              <div className="bg-white bg-opacity-20 px-4 py-2 rounded-full">
                💯 Zero Broker Fees
              </div>
              <div className="bg-white bg-opacity-20 px-4 py-2 rounded-full">
                ⚡ Direct Contact
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Filters */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Filter Listings</h2>
          
          <div className="grid md:grid-cols-3 lg:grid-cols-5 gap-4">
            {/* Listing Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Listing Type
              </label>
              <select
                value={filters.listing_type}
                onChange={(e) => handleFilterChange('listing_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                {listingTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Borough */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Borough
              </label>
              <select
                value={filters.borough}
                onChange={(e) => handleFilterChange('borough', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                {boroughs.map(borough => (
                  <option key={borough.value} value={borough.value}>
                    {borough.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Min Price */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min Price
              </label>
              <input
                type="number"
                value={filters.min_price}
                onChange={(e) => handleFilterChange('min_price', e.target.value)}
                placeholder="$1,500"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            {/* Max Price */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Price
              </label>
              <input
                type="number"
                value={filters.max_price}
                onChange={(e) => handleFilterChange('max_price', e.target.value)}
                placeholder="$5,000"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            {/* Bedrooms */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Bedrooms
              </label>
              <select
                value={filters.bedrooms}
                onChange={(e) => handleFilterChange('bedrooms', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                <option value="all">All</option>
                <option value="0">Studio</option>
                <option value="1">1 BR</option>
                <option value="2">2 BR</option>
                <option value="3">3 BR</option>
                <option value="4+">4+ BR</option>
              </select>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
          </div>
        )}

        {/* Listings Grid */}
        {!loading && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {listings.map((listing) => (
              <div key={listing.id} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                {/* Image */}
                <div className="relative h-48 bg-gray-200">
                  <img
                    src={listing.images?.[0] || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=600&fit=crop'}
                    alt={listing.title}
                    className="w-full h-full object-cover"
                  />
                  
                  {/* Listing Type Badge */}
                  <div className={`absolute top-3 left-3 px-3 py-1 rounded-full text-xs font-semibold ${getListingTypeColor(listing.listing_type)}`}>
                    {getListingTypeIcon(listing.listing_type)} {listing.listing_type.replace('_', ' ').toUpperCase()}
                  </div>
                  
                  {/* Price */}
                  <div className="absolute top-3 right-3 bg-black bg-opacity-70 text-white px-3 py-1 rounded-full text-sm font-bold">
                    ${parseFloat(listing.rent_price).toLocaleString()}/mo
                  </div>
                </div>

                {/* Content */}
                <div className="p-5">
                  <h3 className="font-semibold text-lg text-gray-800 mb-2 line-clamp-2">
                    {listing.title}
                  </h3>
                  
                  <p className="text-gray-600 text-sm mb-3">
                    📍 {listing.neighborhood}, {listing.borough}
                  </p>

                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                    <span>{listing.bedrooms === '0' ? 'Studio' : `${listing.bedrooms} bed`}</span>
                    <span>{parseInt(listing.bathrooms)} bath</span>
                    {listing.sqft && <span>{listing.sqft} sqft</span>}
                  </div>

                  {/* Key Features */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {listing.furnished && (
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                        Furnished
                      </span>
                    )}
                    {listing.utilities_included && (
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                        Utilities Included
                      </span>
                    )}
                    {listing.pets_allowed && (
                      <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs">
                        Pet Friendly
                      </span>
                    )}
                  </div>

                  {/* Available Date */}
                  <p className="text-sm text-gray-600 mb-4">
                    📅 Available: {new Date(listing.available_date).toLocaleDateString()}
                  </p>

                  {/* Action Buttons */}
                  <div className="space-y-2">
                    <button
                      onClick={() => setSelectedListing(convertToApartmentFormat(listing))}
                      className="w-full bg-orange-600 text-white py-2 px-4 rounded-lg hover:bg-orange-700 transition-colors font-semibold"
                    >
                      View Details
                    </button>
                    <button
                      onClick={() => {
                        setContactListing(convertToApartmentFormat(listing));
                        setShowContactModal(true);
                      }}
                      className="w-full bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-colors font-semibold"
                    >
                      📧 Contact
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* No Results */}
        {!loading && listings.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-2xl font-bold text-gray-800 mb-2">No Listings Found</h3>
            <p className="text-gray-600 mb-4">
              Try adjusting your filters or check back later for new tenant listings.
            </p>
            <button
              onClick={() => setFilters({
                listing_type: 'all',
                borough: 'all',
                min_price: '',
                max_price: '',
                bedrooms: 'all'
              })}
              className="bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>

      {/* Apartment Details Modal */}
      {selectedListing && (
        <ApartmentDetailsModal 
          apartment={selectedListing}
          onClose={() => setSelectedListing(null)}
        />
      )}

      {/* Email Contact Modal */}
      {showContactModal && contactListing && (
        <EmailContactModal
          apartment={contactListing}
          onClose={() => {
            setShowContactModal(false);
            setContactListing(null);
          }}
        />
      )}
    </div>
  );
};

export default TenantBrowsePage;