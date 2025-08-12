import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Components } from './components';

const { 
  Header, 
  Hero, 
  SearchFilters, 
  ApartmentCard, 
  MapView, 
  Footer,
  LoadingSpinner 
} = Components;

// Mock apartment data for no-fee apartments in NYC
const mockApartments = [
  {
    id: 1,
    title: "Luxury 1BR in Financial District",
    address: "125 Greenwich St, New York, NY 10006",
    price: "$3,200",
    bedrooms: 1,
    bathrooms: 1,
    sqft: "650 sq ft",
    image: "https://images.unsplash.com/photo-1594295800284-990f74bb6928",
    neighborhood: "Financial District",
    amenities: ["Gym", "Doorman", "Rooftop", "Pet Friendly"],
    available: "Available Now",
    type: "No Fee"
  },
  {
    id: 2,
    title: "Modern 2BR in Midtown East",
    address: "300 E 55th St, New York, NY 10022",
    price: "$4,500",
    bedrooms: 2,
    bathrooms: 2,
    sqft: "900 sq ft",
    image: "https://images.pexels.com/photos/4090093/pexels-photo-4090093.jpeg",
    neighborhood: "Midtown East",
    amenities: ["Concierge", "Pool", "Laundry", "Parking"],
    available: "Dec 1st",
    type: "No Fee"
  },
  {
    id: 3,
    title: "Spacious Studio in Brooklyn Heights",
    address: "85 Livingston St, Brooklyn, NY 11201",
    price: "$2,800",
    bedrooms: 0,
    bathrooms: 1,
    sqft: "500 sq ft",
    image: "https://images.unsplash.com/photo-1568486776380-bf9c4e93347a",
    neighborhood: "Brooklyn Heights",
    amenities: ["Gym", "Garden", "Storage"],
    available: "Available Now",
    type: "No Fee"
  },
  {
    id: 4,
    title: "High-Rise 1BR in Long Island City",
    address: "42-12 28th St, Long Island City, NY 11101",
    price: "$2,900",
    bedrooms: 1,
    bathrooms: 1,
    sqft: "700 sq ft",
    image: "https://images.unsplash.com/photo-1551250930-ace1ad395cea",
    neighborhood: "Long Island City",
    amenities: ["River Views", "Gym", "Rooftop", "Concierge"],
    available: "Jan 15th",
    type: "No Fee"
  },
  {
    id: 5,
    title: "Luxury 2BR in Upper East Side",
    address: "200 E 89th St, New York, NY 10128",
    price: "$5,200",
    bedrooms: 2,
    bathrooms: 2,
    sqft: "1100 sq ft",
    image: "https://images.unsplash.com/photo-1553287222-da8a77d59c5c",
    neighborhood: "Upper East Side",
    amenities: ["Doorman", "Gym", "Laundry", "Storage"],
    available: "Available Now",
    type: "No Fee"
  },
  {
    id: 6,
    title: "Modern Studio in Chelsea",
    address: "150 W 26th St, New York, NY 10001",
    price: "$3,000",
    bedrooms: 0,
    bathrooms: 1,
    sqft: "450 sq ft",
    image: "https://images.unsplash.com/photo-1618861138969-0d7a9d315b1f",
    neighborhood: "Chelsea",
    amenities: ["Rooftop", "Gym", "Pet Friendly"],
    available: "Dec 15th",
    type: "No Fee"
  }
];

const Home = () => {
  const [apartments, setApartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchFilters, setSearchFilters] = useState({
    minPrice: '',
    maxPrice: '',
    bedrooms: '',
    neighborhood: '',
    searchTerm: ''
  });

  useEffect(() => {
    // Simulate API call with delay
    const timer = setTimeout(() => {
      setApartments(mockApartments);
      setLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  const filteredApartments = apartments.filter(apt => {
    const matchesSearchTerm = searchFilters.searchTerm === '' || 
      apt.title.toLowerCase().includes(searchFilters.searchTerm.toLowerCase()) ||
      apt.neighborhood.toLowerCase().includes(searchFilters.searchTerm.toLowerCase()) ||
      apt.address.toLowerCase().includes(searchFilters.searchTerm.toLowerCase());
    
    const matchesMinPrice = searchFilters.minPrice === '' || 
      parseInt(apt.price.replace(/[$,]/g, '')) >= parseInt(searchFilters.minPrice);
    
    const matchesMaxPrice = searchFilters.maxPrice === '' || 
      parseInt(apt.price.replace(/[$,]/g, '')) <= parseInt(searchFilters.maxPrice);
    
    const matchesBedrooms = searchFilters.bedrooms === '' || 
      apt.bedrooms.toString() === searchFilters.bedrooms;
    
    const matchesNeighborhood = searchFilters.neighborhood === '' || 
      apt.neighborhood === searchFilters.neighborhood;

    return matchesSearchTerm && matchesMinPrice && matchesMaxPrice && 
           matchesBedrooms && matchesNeighborhood;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <Hero />
      <SearchFilters 
        filters={searchFilters} 
        setFilters={setSearchFilters}
        apartments={apartments}
      />
      
      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            {filteredApartments.length} No Fee Apartments Available
          </h2>
          <div className="flex space-x-2">
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              List View
            </button>
            <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
              Map View
            </button>
          </div>
        </div>

        {loading ? (
          <LoadingSpinner />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredApartments.map(apartment => (
              <ApartmentCard key={apartment.id} apartment={apartment} />
            ))}
          </div>
        )}

        {!loading && filteredApartments.length === 0 && (
          <div className="text-center py-12">
            <div className="max-w-md mx-auto">
              <div className="w-16 h-16 mx-auto mb-4 bg-gray-200 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No apartments found</h3>
              <p className="text-gray-600 mb-4">Try adjusting your search filters to see more results.</p>
              <button 
                onClick={() => setSearchFilters({
                  minPrice: '',
                  maxPrice: '',
                  bedrooms: '',
                  neighborhood: '',
                  searchTerm: ''
                })}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;