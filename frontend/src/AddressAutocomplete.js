import React, { useEffect, useRef, useState } from 'react';

const AddressAutocomplete = ({ 
  value, 
  onChange, 
  onPlaceSelect = null,
  placeholder = "Enter your address",
  className = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent",
  required = false,
  name = "address"
}) => {
  const inputRef = useRef(null);
  const autocompleteRef = useRef(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // Check if Google Maps API is loaded
    const checkGoogleMaps = () => {
      if (window.google && window.google.maps && window.google.maps.places) {
        setIsLoaded(true);
        initializeAutocomplete();
      } else {
        // Try again in 100ms
        setTimeout(checkGoogleMaps, 100);
      }
    };

    checkGoogleMaps();

    return () => {
      if (autocompleteRef.current) {
        window.google?.maps?.event?.clearInstanceListeners(autocompleteRef.current);
      }
    };
  }, []);

  const initializeAutocomplete = () => {
    if (!inputRef.current || !window.google?.maps?.places) return;

    try {
      // Initialize Google Places Autocomplete
      autocompleteRef.current = new window.google.maps.places.Autocomplete(
        inputRef.current,
        {
          types: ['address'],
          componentRestrictions: { 
            country: 'us' // Restrict to US addresses
          },
          fields: [
            'address_components', 
            'formatted_address', 
            'geometry',
            'name',
            'place_id'
          ]
        }
      );

      // Add place changed listener
      autocompleteRef.current.addListener('place_changed', () => {
        const place = autocompleteRef.current.getPlace();
        
        if (!place || !place.formatted_address) {
          console.log('No valid place selected');
          return;
        }

        // Extract address components
        const addressComponents = place.address_components || [];
        let streetNumber = '';
        let streetName = '';
        let neighborhood = '';
        let borough = '';
        let city = '';
        let state = '';
        let zipCode = '';

        addressComponents.forEach(component => {
          const types = component.types;
          
          if (types.includes('street_number')) {
            streetNumber = component.long_name;
          } else if (types.includes('route')) {
            streetName = component.long_name;
          } else if (types.includes('neighborhood') || types.includes('sublocality_level_1')) {
            neighborhood = component.long_name;
          } else if (types.includes('sublocality') || types.includes('locality')) {
            city = component.long_name;
          } else if (types.includes('administrative_area_level_2')) {
            // For NYC, this often contains the borough
            const countyName = component.long_name;
            if (countyName.includes('New York')) borough = 'Manhattan';
            else if (countyName.includes('Kings')) borough = 'Brooklyn';
            else if (countyName.includes('Queens')) borough = 'Queens';
            else if (countyName.includes('Bronx')) borough = 'Bronx';
            else if (countyName.includes('Richmond')) borough = 'Staten Island';
          } else if (types.includes('administrative_area_level_1')) {
            state = component.short_name;
          } else if (types.includes('postal_code')) {
            zipCode = component.long_name;
          }
        });

        // Create structured address data
        const addressData = {
          formatted_address: place.formatted_address,
          street_address: `${streetNumber} ${streetName}`.trim(),
          neighborhood: neighborhood,
          borough: borough || city,
          city: city || 'New York',
          state: state || 'NY',
          zip_code: zipCode,
          latitude: place.geometry?.location?.lat(),
          longitude: place.geometry?.location?.lng(),
          place_id: place.place_id
        };

        // Update the input value
        const fullAddress = place.formatted_address;
        onChange({ target: { name, value: fullAddress } });

        // Call the place select callback if provided
        if (onPlaceSelect) {
          onPlaceSelect(addressData);
        }

        console.log('Address selected:', addressData);
      });

    } catch (error) {
      console.error('Error initializing address autocomplete:', error);
    }
  };

  const handleInputChange = (e) => {
    // Allow manual typing while autocomplete is loading
    onChange(e);
  };

  const handleKeyDown = (e) => {
    // Prevent form submission when selecting from autocomplete dropdown
    if (e.key === 'Enter' && autocompleteRef.current) {
      const predictions = document.querySelector('.pac-container');
      if (predictions && predictions.style.display !== 'none') {
        e.preventDefault();
      }
    }
  };

  return (
    <div className="relative">
      <input
        ref={inputRef}
        type="text"
        name={name}
        value={value}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        className={className}
        placeholder={isLoaded ? placeholder : "Loading address suggestions..."}
        required={required}
        autoComplete="address-line1"
      />
      
      {/* Loading indicator */}
      {!isLoaded && (
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
          <div className="animate-spin h-4 w-4 border-2 border-orange-500 border-t-transparent rounded-full"></div>
        </div>
      )}
      
      {/* Helper text */}
      <p className="mt-1 text-xs text-gray-500">
        {isLoaded 
          ? "Start typing your address for suggestions" 
          : "Loading Google Places..."
        }
      </p>
    </div>
  );
};

export default AddressAutocomplete;