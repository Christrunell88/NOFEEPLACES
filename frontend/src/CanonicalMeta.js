import React from 'react';
import { Helmet } from 'react-helmet-async';

/**
 * Canonical URL and Meta Tags Component
 * Ensures all pages have proper canonical URLs
 */

export const CanonicalTag = ({ url }) => {
  const canonicalUrl = url || window.location.href.split('?')[0].split('#')[0];
  
  return (
    <Helmet>
      <link rel="canonical" href={canonicalUrl} />
    </Helmet>
  );
};

/**
 * Borough/City Page Meta Tags and Structured Data
 */
export const BoroughMetaTags = ({ borough, apartmentCount }) => {
  const boroughData = {
    'manhattan': {
      title: 'Manhattan No-Fee Apartments | Rent Without Broker Fees',
      description: `Find ${apartmentCount || '50+'} no-fee apartments in Manhattan, NYC. Zero broker fees on rentals across Upper West Side, Midtown, Financial District, and more. List, rent, and earn without commissions.`,
      neighborhoods: 'Upper West Side, Upper East Side, Midtown, Chelsea, Financial District, Hell\'s Kitchen, Tribeca, SoHo',
      image: 'https://images.pexels.com/photos/466685/pexels-photo-466685.jpeg?auto=compress&cs=tinysrgb&w=1200'
    },
    'brooklyn': {
      title: 'Brooklyn No-Fee Apartments | Rent Without Broker Fees',
      description: `Discover ${apartmentCount || '80+'} no-fee apartments in Brooklyn, NYC. Zero broker fees on rentals in Williamsburg, DUMBO, Park Slope, Greenpoint, and more. List, rent, and earn without commissions.`,
      neighborhoods: 'Williamsburg, DUMBO, Park Slope, Greenpoint, Bedford-Stuyvesant, Fort Greene, Crown Heights, Brooklyn Heights',
      image: 'https://images.pexels.com/photos/1547813/pexels-photo-1547813.jpeg?auto=compress&cs=tinysrgb&w=1200'
    },
    'queens': {
      title: 'Queens No-Fee Apartments | Rent Without Broker Fees',
      description: `Browse ${apartmentCount || '40+'} no-fee apartments in Queens, NYC. Zero broker fees on rentals in Long Island City, Astoria, Flushing, and more. List, rent, and earn without commissions.`,
      neighborhoods: 'Long Island City, Astoria, Flushing, Forest Hills, Jackson Heights, Sunnyside, Elmhurst, Rego Park',
      image: 'https://images.pexels.com/photos/2724749/pexels-photo-2724749.jpeg?auto=compress&cs=tinysrgb&w=1200'
    },
    'bronx': {
      title: 'Bronx No-Fee Apartments | Rent Without Broker Fees',
      description: `Find ${apartmentCount || '20+'} no-fee apartments in Bronx, NYC. Zero broker fees on affordable rentals across Riverdale, Fordham, and more. List, rent, and earn without commissions.`,
      neighborhoods: 'Riverdale, Fordham, Pelham Bay, Kingsbridge, Morris Park, Concourse, Grand Concourse',
      image: 'https://images.pexels.com/photos/1438832/pexels-photo-1438832.jpeg?auto=compress&cs=tinysrgb&w=1200'
    }
  };

  const data = boroughData[borough.toLowerCase()] || boroughData['manhattan'];
  const canonicalUrl = `https://nofeeplaces.com/${borough.toLowerCase()}`;

  // JSON-LD Structured Data for Borough Page
  const schema = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": data.title,
    "description": data.description,
    "url": canonicalUrl,
    "isPartOf": {
      "@type": "WebSite",
      "name": "NoFeePlaces",
      "url": "https://nofeeplaces.com"
    },
    "about": {
      "@type": "Place",
      "name": `${borough}, New York`,
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": borough === 'Manhattan' ? "40.7831" : borough === 'Brooklyn' ? "40.6782" : borough === 'Queens' ? "40.7282" : "40.8448",
        "longitude": borough === 'Manhattan' ? "-73.9712" : borough === 'Brooklyn' ? "-73.9442" : borough === 'Queens' ? "-73.7949" : "-73.8648"
      },
      "address": {
        "@type": "PostalAddress",
        "addressLocality": borough,
        "addressRegion": "NY",
        "addressCountry": "US"
      }
    },
    "breadcrumb": {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://nofeeplaces.com"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": borough,
          "item": canonicalUrl
        }
      ]
    }
  };

  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{data.title} | No Fee Places</title>
      <meta name="description" content={data.description} />
      
      {/* Canonical URL */}
      <link rel="canonical" href={canonicalUrl} />
      
      {/* OpenGraph / Facebook */}
      <meta property="og:type" content="website" />
      <meta property="og:url" content={canonicalUrl} />
      <meta property="og:title" content={data.title} />
      <meta property="og:description" content={data.description} />
      <meta property="og:image" content={data.image} />
      
      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:url" content={canonicalUrl} />
      <meta name="twitter:title" content={data.title} />
      <meta name="twitter:description" content={data.description} />
      <meta name="twitter:image" content={data.image} />
      
      {/* Additional SEO */}
      <meta name="geo.region" content="US-NY" />
      <meta name="geo.placename" content={`${borough}, New York`} />
      
      {/* JSON-LD Structured Data */}
      <script type="application/ld+json">
        {JSON.stringify(schema, null, 2)}
      </script>
    </Helmet>
  );
};

export default CanonicalTag;
