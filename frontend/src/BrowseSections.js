import React from 'react';
import { ApartmentCard } from './components';

// Browse by Neighborhood Section
export const BrowseByNeighborhood = ({ neighborhoods, onNeighborhoodClick }) => {
  if (!neighborhoods || neighborhoods.length === 0) return null;

  return (
    <section className="bg-gradient-to-br from-gray-50 to-white py-16">
      <div className="container mx-auto px-4 md:px-6">
        <div className="text-center mb-10">
          <h2 className="text-3xl md:text-4xl font-semibold text-gray-900 mb-3">
            Browse by Neighborhood
          </h2>
          <p className="text-lg text-gray-600">
            Discover no-fee apartments in NYC's most popular neighborhoods
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 max-w-7xl mx-auto">
          {neighborhoods.map((neighborhood) => (
            <button
              key={neighborhood.name}
              onClick={() => onNeighborhoodClick(neighborhood.name)}
              className="group bg-white hover:bg-emerald-50 border border-gray-200 hover:border-emerald-500 rounded-lg p-4 transition-all duration-200 hover:shadow-md"
            >
              <div className="text-center">
                <h3 className="text-sm font-semibold text-gray-900 mb-1 truncate">
                  {neighborhood.name}
                </h3>
                <div className="text-2xl font-bold text-emerald-600">
                  {neighborhood.count}
                </div>
                <p className="text-xs text-gray-500">apartments</p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
};

// Borough Quick Links Section
export const BoroughQuickLinks = ({ boroughs, onBoroughClick }) => {
  if (!boroughs || boroughs.length === 0) return null;

  return (
    <div className="bg-white border-b border-gray-200 py-4">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex flex-wrap items-center justify-center gap-2">
          <span className="text-sm font-medium text-gray-700 mr-2">Browse by Borough:</span>
          {boroughs.map((borough, index) => (
            <React.Fragment key={borough.name}>
              <button
                onClick={() => onBoroughClick(borough.name)}
                className="text-sm font-medium text-emerald-600 hover:text-emerald-700 hover:underline transition-colors"
              >
                {borough.name} ({borough.count})
              </button>
              {index < boroughs.length - 1 && (
                <span className="text-gray-400">|</span>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};

// Recently Added Section
export const RecentlyAdded = ({ apartments, onApartmentClick }) => {
  if (!apartments || apartments.length === 0) return null;

  return (
    <section className="bg-white py-16 border-b border-gray-100">
      <div className="container mx-auto px-4 md:px-6">
        <div className="text-center mb-10">
          <div className="inline-block bg-emerald-100 text-emerald-700 text-xs font-semibold px-3 py-1 rounded-full mb-3">
            🆕 NEW LISTINGS
          </div>
          <h2 className="text-3xl md:text-4xl font-semibold text-gray-900 mb-3">
            Recently Added Apartments
          </h2>
          <p className="text-lg text-gray-600">
            Check out the latest no-fee apartments just added to our platform
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
          {apartments.slice(0, 8).map((apartment) => (
            <ApartmentCard
              key={apartment.id}
              apartment={apartment}
              onClick={() => onApartmentClick(apartment)}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

// Quick Filters Component
export const QuickFilters = ({ selectedAmenities, onToggleAmenity }) => {
  const commonAmenities = [
    { name: 'Pet Friendly', icon: '🐾' },
    { name: 'Doorman', icon: '🚪' },
    { name: 'Gym', icon: '💪' },
    { name: 'Laundry', icon: '👔' },
    { name: 'Elevator', icon: '🛗' }
  ];

  return (
    <div className="bg-white border-b border-gray-200 py-4">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-medium text-gray-700 mr-2">Quick Filters:</span>
          {commonAmenities.map((amenity) => (
            <button
              key={amenity.name}
              onClick={() => onToggleAmenity(amenity.name)}
              className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                selectedAmenities.includes(amenity.name)
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <span>{amenity.icon}</span>
              <span>{amenity.name}</span>
              {selectedAmenities.includes(amenity.name) && (
                <span className="ml-1">✓</span>
              )}
            </button>
          ))}
          {selectedAmenities.length > 0 && (
            <button
              onClick={() => selectedAmenities.forEach(a => onToggleAmenity(a))}
              className="text-sm text-gray-500 hover:text-gray-700 underline ml-2"
            >
              Clear all
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

// Enhanced Sort Options
export const SortOptions = ({ sortBy, sortOrder, onSortChange }) => {
  const sortOptions = [
    { value: 'price', label: 'Price' },
    { value: 'newest', label: 'Newest' },
    { value: 'bedrooms', label: 'Bedrooms' }
  ];

  return (
    <div className="flex items-center gap-3">
      <label className="text-sm font-medium text-gray-700">Sort by:</label>
      <div className="flex items-center gap-2">
        {sortOptions.map((option) => (
          <button
            key={option.value}
            onClick={() => onSortChange(option.value, option.value === 'newest' ? 'desc' : 'asc')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              sortBy === option.value
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {option.label}
            {sortBy === option.value && (
              <span className="ml-1">
                {sortOrder === 'asc' ? '↑' : '↓'}
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
};
