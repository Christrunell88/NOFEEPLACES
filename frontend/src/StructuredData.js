import React from 'react';
import { Helmet } from 'react-helmet-async';

/**
 * JSON-LD Structured Data Component for Real Estate Listings
 * Implements schema.org RealEstateListing for rich search results
 */

export const RealEstateListingSchema = ({ apartment }) => {
  if (!apartment) return null;

  const {
    title,
    address,
    neighborhood,
    borough,
    price,
    bedrooms,
    bathrooms,
    sqft,
    description,
    images,
    building_name,
    amenities,
    available_date,
    contact_info
  } = apartment;

  // Get domain URL from environment variable
  const domainUrl = process.env.REACT_APP_DOMAIN_URL || 'https://nofeeplaces.com';

  // Create structured address
  const structuredAddress = {
    "@type": "PostalAddress",
    "streetAddress": address || `${neighborhood}, ${borough}`,
    "addressLocality": neighborhood || borough,
    "addressRegion": "NY",
    "addressCountry": "US",
    "postalCode": ""
  };

  // Create URL-friendly slug
  const slug = `${neighborhood}-${borough}-${bedrooms === 0 ? 'studio' : bedrooms + 'br'}`.toLowerCase().replace(/\s+/g, '-');
  const listingUrl = `${domainUrl}/listing/${slug}`;

  // Create JSON-LD schema
  const schema = {
    "@context": "https://schema.org",
    "@type": "RealEstateListing",
    "name": title || `${bedrooms === 0 ? 'Studio' : bedrooms + 'BR'} Apartment in ${neighborhood}, ${borough}`,
    "description": description || `Rent this ${bedrooms === 0 ? 'studio' : bedrooms + ' bedroom'} apartment in ${neighborhood}, ${borough} for $${price}/month with no broker fees.`,
    "url": listingUrl,
    "address": structuredAddress,
    "price": price,
    "priceCurrency": "USD",
    "priceSpecification": {
      "@type": "UnitPriceSpecification",
      "price": price,
      "priceCurrency": "USD",
      "unitText": "monthly"
    },
    "numberOfRooms": bedrooms === 0 ? 1 : bedrooms,
    "numberOfBedrooms": bedrooms,
    "numberOfBathroomsTotal": bathrooms,
    "floorSize": sqft ? {
      "@type": "QuantitativeValue",
      "value": sqft,
      "unitCode": "FTK"
    } : undefined,
    "image": images && images.length > 0 ? images : undefined,
    "amenityFeature": amenities && amenities.length > 0 ? amenities.slice(0, 10).map(amenity => ({
      "@type": "LocationFeatureSpecification",
      "name": amenity
    })) : undefined,
    "datePosted": new Date().toISOString().split('T')[0],
    "availableDate": available_date || "Immediately",
    "contactPoint": contact_info ? {
      "@type": "ContactPoint",
      "email": contact_info.email,
      "telephone": contact_info.phone,
      "contactType": "Rental Office"
    } : undefined,
    "landlord": {
      "@type": "Organization",
      "name": building_name || "NoFeePlaces",
      "url": "https://nofeeplaces.com"
    },
    "offers": {
      "@type": "Offer",
      "price": price,
      "priceCurrency": "USD",
      "availability": "https://schema.org/InStock",
      "validFrom": new Date().toISOString().split('T')[0],
      "seller": {
        "@type": "Organization",
        "name": "NoFeePlaces",
        "url": "https://nofeeplaces.com"
      }
    },
    "brand": {
      "@type": "Brand",
      "name": building_name || "NoFeePlaces"
    }
  };

  // Remove undefined fields
  Object.keys(schema).forEach(key => schema[key] === undefined && delete schema[key]);

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema, null, 2)}
      </script>
    </Helmet>
  );
};

export const ItemListSchema = ({ apartments, category }) => {
  if (!apartments || apartments.length === 0) return null;

  const categoryTitles = {
    'best-value': 'Best Value No-Fee Apartments NYC',
    'budget': 'Budget No-Fee Apartments NYC',
    'smart': 'Smart Value No-Fee Apartments NYC',
    'luxury': 'Luxury No-Fee Apartments NYC'
  };

  const schema = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": categoryTitles[category] || "No-Fee Apartments NYC",
    "description": `Browse ${apartments.length} no-fee apartments in NYC without broker fees`,
    "numberOfItems": apartments.length,
    "itemListElement": apartments.slice(0, 20).map((apt, index) => ({
      "@type": "ListItem",
      "position": index + 1,
      "item": {
        "@type": "RealEstateListing",
        "name": apt.title || `${apt.bedrooms === 0 ? 'Studio' : apt.bedrooms + 'BR'} in ${apt.neighborhood}`,
        "url": `https://nofeeplaces.com/listing/${apt.id}`,
        "address": {
          "@type": "PostalAddress",
          "streetAddress": apt.address,
          "addressLocality": apt.neighborhood,
          "addressRegion": "NY",
          "addressCountry": "US"
        },
        "price": apt.price,
        "priceCurrency": "USD"
      }
    }))
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema, null, 2)}
      </script>
    </Helmet>
  );
};

export const OrganizationSchema = () => {
  const schema = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "NoFeePlaces",
    "legalName": "NoFeePlaces LLC",
    "url": "https://nofeeplaces.com",
    "logo": "https://nofeeplaces.com/logo.png",
    "foundingDate": "2025",
    "description": "Find no-fee apartments in NYC. List, rent, and earn without brokers or commissions.",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "New York",
      "addressRegion": "NY",
      "addressCountry": "US"
    },
    "contactPoint": {
      "@type": "ContactPoint",
      "email": "placesfirm@gmail.com",
      "telephone": "+1-646-408-8048",
      "contactType": "Customer Service"
    },
    "sameAs": [
      "https://www.facebook.com/NoFeePlacesNYC",
      "https://twitter.com/NoFeePlacesNYC"
    ]
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema, null, 2)}
      </script>
    </Helmet>
  );
};

export default RealEstateListingSchema;
