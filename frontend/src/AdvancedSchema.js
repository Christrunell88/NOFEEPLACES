import React from 'react';
import { Helmet } from 'react-helmet-async';

// ApartmentComplex Schema for Individual Listings
export const ApartmentComplexSchema = ({ apartment }) => {
  const schema = {
    "@context": "https://schema.org",
    "@type": "ApartmentComplex",
    "name": apartment.title || `${apartment.bedrooms}BR Apartment in ${apartment.neighborhood}`,
    "description": apartment.description || `No-fee ${apartment.bedrooms} bedroom apartment in ${apartment.neighborhood}, ${apartment.borough}`,
    "address": {
      "@type": "PostalAddress",
      "streetAddress": apartment.address || apartment.location,
      "addressLocality": apartment.neighborhood,
      "addressRegion": "NY",
      "postalCode": apartment.zipcode || "",
      "addressCountry": "US"
    },
    "geo": apartment.latitude && apartment.longitude ? {
      "@type": "GeoCoordinates",
      "latitude": apartment.latitude,
      "longitude": apartment.longitude
    } : undefined,
    "numberOfBedrooms": apartment.bedrooms,
    "numberOfBathroomsTotal": apartment.bathrooms,
    "floorSize": apartment.square_feet ? {
      "@type": "QuantitativeValue",
      "value": apartment.square_feet,
      "unitCode": "FTK"
    } : undefined,
    "amenityFeature": apartment.amenities?.map(amenity => ({
      "@type": "LocationFeatureSpecification",
      "name": amenity,
      "value": true
    })),
    "photo": apartment.images?.map(img => img),
    "offers": {
      "@type": "Offer",
      "price": apartment.price,
      "priceCurrency": "USD",
      "availability": apartment.available ? "https://schema.org/InStock" : "https://schema.org/OutOfStock",
      "url": `https://nofeeplaces.com/apartment/${apartment.id}`,
      "priceSpecification": {
        "@type": "UnitPriceSpecification",
        "price": apartment.price,
        "priceCurrency": "USD",
        "unitText": "Monthly"
      }
    },
    "potentialAction": {
      "@type": "RentAction",
      "target": {
        "@type": "EntryPoint",
        "urlTemplate": `https://nofeeplaces.com/apartment/${apartment.id}`,
        "actionPlatform": [
          "http://schema.org/DesktopWebPlatform",
          "http://schema.org/MobileWebPlatform"
        ]
      }
    }
  };

  // Remove undefined values
  const cleanSchema = JSON.parse(JSON.stringify(schema));

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(cleanSchema)}
      </script>
    </Helmet>
  );
};

// LocalBusiness Schema for NoFeePlaces
export const LocalBusinessSchema = () => {
  const schema = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "@id": "https://nofeeplaces.com/#organization",
    "name": "NoFeePlaces",
    "alternateName": "No Fee Places NYC",
    "description": "Find verified no-fee apartments in NYC. Save thousands on broker fees with our curated listings across Manhattan, Brooklyn, Queens, and the Bronx.",
    "url": "https://nofeeplaces.com",
    "logo": "https://nofeeplaces.com/logo.png",
    "image": "https://nofeeplaces.com/og-image.png",
    "telephone": "+1-646-408-8048",
    "email": "hello@nofeeplaces.com",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "New York",
      "addressRegion": "NY",
      "addressCountry": "US"
    },
    "geo": {
      "@type": "GeoCoordinates",
      "latitude": 40.7128,
      "longitude": -74.0060
    },
    "areaServed": [
      {
        "@type": "City",
        "name": "New York",
        "sameAs": "https://en.wikipedia.org/wiki/New_York_City"
      },
      {
        "@type": "Neighborhood",
        "name": "Manhattan"
      },
      {
        "@type": "Neighborhood",
        "name": "Brooklyn"
      },
      {
        "@type": "Neighborhood",
        "name": "Queens"
      },
      {
        "@type": "Neighborhood",
        "name": "Bronx"
      }
    ],
    "priceRange": "$1000-$10000",
    "paymentAccepted": "Credit Card, Debit Card, Bank Transfer",
    "openingHours": "Mo-Su 00:00-23:59",
    "sameAs": [
      "https://www.facebook.com/nofeeplaces",
      "https://twitter.com/nofeeplaces",
      "https://www.instagram.com/nofeeplaces"
    ],
    "hasOfferCatalog": {
      "@type": "OfferCatalog",
      "name": "NYC No-Fee Apartments",
      "itemListElement": [
        {
          "@type": "Offer",
          "itemOffered": {
            "@type": "Service",
            "name": "No-Fee Apartment Listings"
          }
        },
        {
          "@type": "Offer",
          "itemOffered": {
            "@type": "Service",
            "name": "Apartment Search Assistance"
          }
        }
      ]
    }
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema)}
      </script>
    </Helmet>
  );
};

// BreadcrumbList Schema
export const BreadcrumbSchema = ({ items }) => {
  const schema = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": items.map((item, index) => ({
      "@type": "ListItem",
      "position": index + 1,
      "name": item.name,
      "item": item.url
    }))
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema)}
      </script>
    </Helmet>
  );
};

// FAQPage Schema
export const FAQSchema = ({ faqs }) => {
  const schema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqs.map(faq => ({
      "@type": "Question",
      "name": faq.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": faq.answer
      }
    }))
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema)}
      </script>
    </Helmet>
  );
};

// AggregateRating Schema
export const AggregateRatingSchema = ({ rating, reviewCount, itemName }) => {
  const schema = {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": itemName,
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": rating,
      "reviewCount": reviewCount,
      "bestRating": "5",
      "worstRating": "1"
    }
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema)}
      </script>
    </Helmet>
  );
};

// WebSite Schema with SearchAction
export const WebSiteSchema = () => {
  const schema = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "@id": "https://nofeeplaces.com/#website",
    "url": "https://nofeeplaces.com",
    "name": "NoFeePlaces",
    "description": "Find no-fee apartments in NYC. Save thousands on broker fees.",
    "potentialAction": {
      "@type": "SearchAction",
      "target": {
        "@type": "EntryPoint",
        "urlTemplate": "https://nofeeplaces.com/search?q={search_term_string}"
      },
      "query-input": "required name=search_term_string"
    }
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema)}
      </script>
    </Helmet>
  );
};

// ItemList Schema for Search Results
export const ItemListSchema = ({ apartments, listName = "NYC No-Fee Apartments" }) => {
  const schema = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": listName,
    "numberOfItems": apartments.length,
    "itemListElement": apartments.slice(0, 20).map((apartment, index) => ({
      "@type": "ListItem",
      "position": index + 1,
      "item": {
        "@type": "ApartmentComplex",
        "@id": `https://nofeeplaces.com/apartment/${apartment.id}`,
        "name": apartment.title || `${apartment.bedrooms}BR in ${apartment.neighborhood}`,
        "address": {
          "@type": "PostalAddress",
          "addressLocality": apartment.neighborhood,
          "addressRegion": "NY",
          "addressCountry": "US"
        },
        "offers": {
          "@type": "Offer",
          "price": apartment.price,
          "priceCurrency": "USD"
        }
      }
    }))
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema)}
      </script>
    </Helmet>
  );
};

// RealEstateAgent Schema
export const RealEstateAgentSchema = () => {
  const schema = {
    "@context": "https://schema.org",
    "@type": "RealEstateAgent",
    "name": "NoFeePlaces",
    "description": "NYC's premier no-fee apartment listing service. We help renters find verified no-fee apartments and save thousands on broker fees.",
    "url": "https://nofeeplaces.com",
    "logo": "https://nofeeplaces.com/logo.png",
    "email": "hello@nofeeplaces.com",
    "telephone": "+1-646-408-8048",
    "areaServed": {
      "@type": "City",
      "name": "New York City",
      "sameAs": "https://en.wikipedia.org/wiki/New_York_City"
    },
    "knowsAbout": [
      "No-Fee Apartments",
      "NYC Rental Market",
      "Apartment Hunting",
      "Broker Fee Savings"
    ],
    "memberOf": {
      "@type": "Organization",
      "name": "NYC Real Estate Community"
    }
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema)}
      </script>
    </Helmet>
  );
};

// Article Schema for Blog/Guide Pages
export const ArticleSchema = ({ title, description, author = "NoFeePlaces Team", datePublished, dateModified, image }) => {
  const schema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": title,
    "description": description,
    "image": image || "https://nofeeplaces.com/og-image.png",
    "author": {
      "@type": "Organization",
      "name": author,
      "url": "https://nofeeplaces.com"
    },
    "publisher": {
      "@type": "Organization",
      "name": "NoFeePlaces",
      "logo": {
        "@type": "ImageObject",
        "url": "https://nofeeplaces.com/logo.png"
      }
    },
    "datePublished": datePublished || new Date().toISOString(),
    "dateModified": dateModified || new Date().toISOString(),
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": "https://nofeeplaces.com/guide"
    }
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema)}
      </script>
    </Helmet>
  );
};

// VideoObject Schema (for future video content)
export const VideoSchema = ({ name, description, thumbnailUrl, uploadDate, duration, contentUrl }) => {
  const schema = {
    "@context": "https://schema.org",
    "@type": "VideoObject",
    "name": name,
    "description": description,
    "thumbnailUrl": thumbnailUrl,
    "uploadDate": uploadDate,
    "duration": duration,
    "contentUrl": contentUrl,
    "embedUrl": contentUrl,
    "publisher": {
      "@type": "Organization",
      "name": "NoFeePlaces",
      "logo": {
        "@type": "ImageObject",
        "url": "https://nofeeplaces.com/logo.png"
      }
    }
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema)}
      </script>
    </Helmet>
  );
};

export default {
  ApartmentComplexSchema,
  LocalBusinessSchema,
  BreadcrumbSchema,
  FAQSchema,
  AggregateRatingSchema,
  WebSiteSchema,
  ItemListSchema,
  RealEstateAgentSchema,
  ArticleSchema,
  VideoSchema
};
