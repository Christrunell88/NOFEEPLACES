import React from 'react';
import { Helmet } from 'react-helmet-async';

/**
 * SEO Meta Tags Component for Dynamic Pages
 * Handles title, description, and OpenGraph tags for individual listings
 */

export const ListingMetaTags = ({ apartment }) => {
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
    images,
    building_name
  } = apartment;

  // Format bedroom type
  const bedroomType = bedrooms === 0 ? 'Studio' : `${bedrooms}BR`;
  const bathroomText = bathrooms ? `${bathrooms}BA` : '';
  
  // Create dynamic title
  const pageTitle = `${bedroomType} ${bathroomText} in ${neighborhood}, ${borough} - $${price.toLocaleString()}/mo | No Fee Places`;
  
  // Create dynamic description
  const sqftText = sqft ? `${sqft} sqft ` : '';
  const pageDescription = `Rent this ${bedroomType} ${bathroomText} apartment in ${neighborhood}, ${borough} for $${price.toLocaleString()}/month with no broker fees. ${sqftText}${address}. List, rent, and earn without commissions.`;
  
  // Get first image or default
  const imageUrl = (images && images.length > 0) 
    ? images[0] 
    : 'https://images.pexels.com/photos/28426361/pexels-photo-28426361.jpeg?auto=compress&cs=tinysrgb&w=1200&h=630';
  
  // Create URL-friendly slug
  const slug = `${neighborhood}-${borough}-${bedroomType}`.toLowerCase().replace(/\s+/g, '-');
  const pageUrl = `https://nofeeplaces.com/listing/${slug}`;

  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{pageTitle}</title>
      <meta name="description" content={pageDescription} />
      
      {/* OpenGraph / Facebook */}
      <meta property="og:type" content="article" />
      <meta property="og:url" content={pageUrl} />
      <meta property="og:title" content={pageTitle} />
      <meta property="og:description" content={pageDescription} />
      <meta property="og:image" content={imageUrl} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:image:alt" content={`${bedroomType} apartment in ${neighborhood}, ${borough}`} />
      <meta property="og:site_name" content="NoFeePlaces.com" />
      
      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:url" content={pageUrl} />
      <meta name="twitter:title" content={pageTitle} />
      <meta name="twitter:description" content={pageDescription} />
      <meta name="twitter:image" content={imageUrl} />
      
      {/* Additional Meta */}
      <link rel="canonical" href={pageUrl} />
    </Helmet>
  );
};

export const CategoryMetaTags = ({ category, apartmentCount, avgPrice }) => {
  const categoryConfig = {
    'best-value': {
      title: 'Best Value No-Fee Apartments NYC | Top 20% Deals',
      description: `Find the top ${apartmentCount} best value apartments in NYC with luxury amenities at great prices. No broker fees, verified listings.`
    },
    'budget': {
      title: 'Budget No-Fee Apartments NYC | Under $4,500/mo',
      description: `Browse ${apartmentCount} affordable NYC apartments under $4,500/month with zero broker fees. Manhattan, Brooklyn & Queens.`
    },
    'smart': {
      title: 'Smart Value No-Fee Apartments NYC | $4,500-$6,500/mo',
      description: `Discover ${apartmentCount} smart-priced NYC apartments $4,500-$6,500/month. No broker fees, best value for professionals.`
    },
    'luxury': {
      title: 'Luxury No-Fee Apartments NYC | Sky\'s the Limit',
      description: `Explore ${apartmentCount} premium luxury NYC apartments over $6,500/month. No broker fees on high-end rentals.`
    }
  };

  const config = categoryConfig[category] || categoryConfig['budget'];
  const avgPriceText = avgPrice ? ` Average: $${Math.round(avgPrice).toLocaleString()}/mo.` : '';
  const canonicalUrl = `https://nofeeplaces.com/apartments/${category}`;

  return (
    <Helmet>
      <title>{config.title} | No Fee Places</title>
      <meta name="description" content={config.description + avgPriceText} />
      
      <meta property="og:title" content={config.title} />
      <meta property="og:description" content={config.description} />
      <meta property="og:url" content={canonicalUrl} />
      
      <meta name="twitter:title" content={config.title} />
      <meta name="twitter:description" content={config.description} />
      
      <link rel="canonical" href={canonicalUrl} />
    </Helmet>
  );
};

export const HomeMetaTags = () => (
  <Helmet>
    <title>No Fee Places | Rent Apartments Without Broker Fees</title>
    <meta name="description" content="Find no-fee apartments in NYC. List, rent, and earn without brokers or commissions. 250+ verified rentals across Manhattan, Brooklyn & Queens." />
    <link rel="canonical" href="https://nofeeplaces.com/" />
  </Helmet>
);

export default ListingMetaTags;
