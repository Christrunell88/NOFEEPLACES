import React from 'react';
import { Helmet } from 'react-helmet-async';

// Default SEO values
const DEFAULT_SEO = {
  siteName: 'NoFeePlaces',
  siteUrl: 'https://nofeeplaces.com',
  defaultTitle: 'NYC No-Fee Apartments | Save Thousands on Broker Fees | NoFeePlaces',
  defaultDescription: 'Find verified no-fee apartments in NYC. Browse 1000+ listings in Manhattan, Brooklyn, Queens & the Bronx. No broker fees, no hidden costs. Start your search today!',
  defaultImage: 'https://nofeeplaces.com/og-image.png',
  twitterHandle: '@nofeeplaces'
};

// Homepage SEO
export const HomePageSEO = () => (
  <Helmet>
    <title>{DEFAULT_SEO.defaultTitle}</title>
    <meta name="description" content={DEFAULT_SEO.defaultDescription} />
    <meta name="keywords" content="no fee apartments NYC, no broker fee apartments, NYC apartments, Manhattan apartments, Brooklyn apartments, Queens apartments, Bronx apartments, NYC rentals, apartment search NYC" />
    
    {/* Open Graph */}
    <meta property="og:type" content="website" />
    <meta property="og:url" content={DEFAULT_SEO.siteUrl} />
    <meta property="og:title" content={DEFAULT_SEO.defaultTitle} />
    <meta property="og:description" content={DEFAULT_SEO.defaultDescription} />
    <meta property="og:image" content={DEFAULT_SEO.defaultImage} />
    <meta property="og:site_name" content={DEFAULT_SEO.siteName} />
    
    {/* Twitter Card */}
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:site" content={DEFAULT_SEO.twitterHandle} />
    <meta name="twitter:title" content={DEFAULT_SEO.defaultTitle} />
    <meta name="twitter:description" content={DEFAULT_SEO.defaultDescription} />
    <meta name="twitter:image" content={DEFAULT_SEO.defaultImage} />
    
    {/* Canonical */}
    <link rel="canonical" href={DEFAULT_SEO.siteUrl} />
  </Helmet>
);

// Individual Apartment Listing SEO
export const ApartmentListingSEO = ({ apartment }) => {
  const bedroomText = apartment.bedrooms === 0 ? 'Studio' : `${apartment.bedrooms}BR`;
  const bathroomText = apartment.bathrooms ? `${apartment.bathrooms}BA` : '';
  const title = `${bedroomText} ${bathroomText} in ${apartment.neighborhood} - $${apartment.price?.toLocaleString()}/mo | No Fee | NoFeePlaces`;
  const description = apartment.description 
    ? apartment.description.substring(0, 155) + '...'
    : `No-fee ${bedroomText} apartment in ${apartment.neighborhood}, ${apartment.borough}. $${apartment.price?.toLocaleString()}/mo. ${apartment.amenities?.slice(0, 3).join(', ')}. Schedule a showing today!`;
  const url = `${DEFAULT_SEO.siteUrl}/apartment/${apartment.id}`;
  const image = apartment.images?.[0] || DEFAULT_SEO.defaultImage;

  return (
    <Helmet>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={`${apartment.neighborhood} apartments, ${apartment.borough} ${bedroomText}, no fee ${apartment.neighborhood}, ${apartment.price} apartments NYC, ${apartment.neighborhood} rentals`} />
      
      {/* Open Graph */}
      <meta property="og:type" content="product" />
      <meta property="og:url" content={url} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={image} />
      <meta property="og:site_name" content={DEFAULT_SEO.siteName} />
      <meta property="product:price:amount" content={apartment.price} />
      <meta property="product:price:currency" content="USD" />
      
      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={image} />
      
      {/* Canonical */}
      <link rel="canonical" href={url} />
    </Helmet>
  );
};

// Search Results Page SEO
export const SearchPageSEO = ({ filters }) => {
  const borough = filters?.borough || '';
  const bedrooms = filters?.bedrooms || '';
  const maxPrice = filters?.max_price || '';
  
  let title = 'Search No-Fee Apartments in NYC | NoFeePlaces';
  let description = 'Browse our curated collection of no-fee apartments across NYC. Filter by location, price, bedrooms, and amenities to find your perfect home.';
  
  if (borough) {
    title = `No-Fee Apartments in ${borough} | NYC Rentals | NoFeePlaces`;
    description = `Find verified no-fee apartments in ${borough}, NYC. Browse available ${bedrooms ? bedrooms + 'BR ' : ''}units ${maxPrice ? `under $${maxPrice?.toLocaleString()}/mo` : ''}. No broker fees.`;
  }

  return (
    <Helmet>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={`${borough} apartments, no fee ${borough}, ${bedrooms}BR ${borough}, NYC apartment search, ${borough} rentals`} />
      
      {/* Open Graph */}
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={`${DEFAULT_SEO.siteUrl}/search`} />
      <meta property="og:image" content={DEFAULT_SEO.defaultImage} />
      
      {/* Twitter Card */}
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={DEFAULT_SEO.defaultImage} />
      
      {/* Canonical */}
      <link rel="canonical" href={`${DEFAULT_SEO.siteUrl}/search`} />
    </Helmet>
  );
};

// Borough Page SEO
export const BoroughPageSEO = ({ borough }) => {
  const title = `No-Fee Apartments in ${borough} | NYC Rentals | NoFeePlaces`;
  const description = `Discover no-fee apartments in ${borough}, NYC. Browse verified listings with no broker fees. Studios, 1BR, 2BR, 3BR+ available. Find your next home in ${borough} today!`;
  const url = `${DEFAULT_SEO.siteUrl}/borough/${borough.toLowerCase()}`;

  return (
    <Helmet>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={`${borough} apartments no fee, ${borough} rentals, ${borough} no broker fee, apartments in ${borough}, ${borough} NYC, ${borough} housing`} />
      
      {/* Open Graph */}
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={url} />
      <meta property="og:image" content={DEFAULT_SEO.defaultImage} />
      
      {/* Twitter Card */}
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      
      {/* Canonical */}
      <link rel="canonical" href={url} />
    </Helmet>
  );
};

// Neighborhood Page SEO
export const NeighborhoodPageSEO = ({ neighborhood, borough }) => {
  const title = `${neighborhood} No-Fee Apartments | ${borough} | NoFeePlaces`;
  const description = `Find no-fee apartments in ${neighborhood}, ${borough}. Browse verified listings with no broker fees. Studios, 1BR, 2BR, 3BR units available in ${neighborhood}. Schedule showings online!`;
  const url = `${DEFAULT_SEO.siteUrl}/neighborhood/${neighborhood.toLowerCase().replace(/\s+/g, '-')}`;

  return (
    <Helmet>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={`${neighborhood} apartments, ${neighborhood} no fee, ${neighborhood} ${borough}, ${neighborhood} rentals, apartments in ${neighborhood}`} />
      
      {/* Open Graph */}
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={url} />
      
      {/* Twitter Card */}
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      
      {/* Canonical */}
      <link rel="canonical" href={url} />
    </Helmet>
  );
};

// Dashboard Page SEO
export const DashboardSEO = () => (
  <Helmet>
    <title>My Dashboard | NoFeePlaces</title>
    <meta name="description" content="Manage your saved apartments, searches, and scheduled showings. Track your NYC apartment search progress." />
    <meta name="robots" content="noindex, nofollow" />
    <link rel="canonical" href={`${DEFAULT_SEO.siteUrl}/dashboard`} />
  </Helmet>
);

// Favorites Page SEO
export const FavoritesSEO = () => (
  <Helmet>
    <title>My Favorite Apartments | NoFeePlaces</title>
    <meta name="description" content="View all your saved no-fee apartments in NYC. Keep track of your favorite listings and schedule showings." />
    <meta name="robots" content="noindex, nofollow" />
    <link rel="canonical" href={`${DEFAULT_SEO.siteUrl}/favorites`} />
  </Helmet>
);

// Saved Searches Page SEO
export const SavedSearchesSEO = () => (
  <Helmet>
    <title>My Saved Searches | NoFeePlaces</title>
    <meta name="description" content="Access your saved apartment searches. Get email alerts when new no-fee apartments match your criteria." />
    <meta name="robots" content="noindex, nofollow" />
    <link rel="canonical" href={`${DEFAULT_SEO.siteUrl}/saved-searches`} />
  </Helmet>
);

// Rent Calculator SEO
export const RentCalculatorSEO = () => (
  <Helmet>
    <title>NYC Rent Calculator - How Much Rent Can I Afford? | NoFeePlaces</title>
    <meta name="description" content="Calculate how much rent you can afford in NYC based on your income. Free rent affordability calculator using the 30% rule. Find apartments within your budget." />
    <meta name="keywords" content="rent calculator NYC, rent affordability calculator, how much rent can I afford, NYC rent budget, 30% rent rule, apartment budget calculator" />
    
    {/* Open Graph */}
    <meta property="og:title" content="NYC Rent Calculator - Calculate Your Rent Budget" />
    <meta property="og:description" content="Free NYC rent calculator. Find out how much rent you can afford based on your income using the 30% rule." />
    <meta property="og:url" content={`${DEFAULT_SEO.siteUrl}/rent-calculator`} />
    
    {/* Canonical */}
    <link rel="canonical" href={`${DEFAULT_SEO.siteUrl}/rent-calculator`} />
  </Helmet>
);

// Savings Calculator SEO
export const SavingsCalculatorSEO = () => (
  <Helmet>
    <title>No-Fee Apartment Savings Calculator | Calculate Broker Fee Savings | NoFeePlaces</title>
    <meta name="description" content="Calculate how much you save with no-fee apartments vs. broker fee apartments in NYC. See your total savings instantly. Average broker fee is 15% of annual rent!" />
    <meta name="keywords" content="broker fee savings calculator, NYC broker fee calculator, no fee apartment savings, NYC rental savings, broker fee comparison" />
    
    {/* Open Graph */}
    <meta property="og:title" content="Calculate Your No-Fee Apartment Savings" />
    <meta property="og:description" content="See how much you save by choosing a no-fee apartment. Calculate your broker fee savings instantly." />
    <meta property="og:url" content={`${DEFAULT_SEO.siteUrl}/savings-calculator`} />
    
    {/* Canonical */}
    <link rel="canonical" href={`${DEFAULT_SEO.siteUrl}/savings-calculator`} />
  </Helmet>
);

// Cost of Living Calculator SEO
export const CostOfLivingCalculatorSEO = () => (
  <Helmet>
    <title>NYC Cost of Living Calculator | Living Expenses Calculator | NoFeePlaces</title>
    <meta name="description" content="Calculate your total cost of living in NYC. Estimate rent, utilities, transportation, food, and other expenses. Plan your NYC budget accurately." />
    <meta name="keywords" content="NYC cost of living calculator, NYC living expenses, NYC budget calculator, cost to live in NYC, NYC expenses calculator" />
    
    {/* Open Graph */}
    <meta property="og:title" content="NYC Cost of Living Calculator" />
    <meta property="og:description" content="Calculate your total cost of living in NYC. Get accurate estimates for all living expenses." />
    <meta property="og:url" content={`${DEFAULT_SEO.siteUrl}/cost-of-living-calculator`} />
    
    {/* Canonical */}
    <link rel="canonical" href={`${DEFAULT_SEO.siteUrl}/cost-of-living-calculator`} />
  </Helmet>
);

// FAQ Page SEO
export const FAQSEO = () => (
  <Helmet>
    <title>Frequently Asked Questions | No-Fee Apartments NYC | NoFeePlaces</title>
    <meta name="description" content="Get answers to common questions about no-fee apartments in NYC. Learn about broker fees, apartment hunting tips, and how NoFeePlaces works." />
    <meta name="keywords" content="no fee apartments FAQ, NYC apartment questions, broker fee questions, renting in NYC, apartment hunting NYC" />
    
    {/* Open Graph */}
    <meta property="og:title" content="FAQ - No-Fee Apartments NYC" />
    <meta property="og:description" content="Common questions about finding no-fee apartments in NYC answered." />
    <meta property="og:url" content={`${DEFAULT_SEO.siteUrl}/faq`} />
    
    {/* Canonical */}
    <link rel="canonical" href={`${DEFAULT_SEO.siteUrl}/faq`} />
  </Helmet>
);

// Guide Page SEO
export const GuideSEO = () => (
  <Helmet>
    <title>Complete Guide to No-Fee Apartments in NYC | NoFeePlaces</title>
    <meta name="description" content="Ultimate guide to finding no-fee apartments in NYC. Learn about broker fees, tenant rights, apartment hunting strategies, and how to save thousands on your next rental." />
    <meta name="keywords" content="NYC apartment guide, no fee apartment guide, NYC renting guide, how to find no fee apartments, NYC tenant rights, apartment hunting NYC" />
    
    {/* Open Graph */}
    <meta property="og:title" content="Complete Guide to No-Fee Apartments in NYC" />
    <meta property="og:description" content="Learn everything about finding and renting no-fee apartments in NYC. Save thousands on broker fees." />
    <meta property="og:url" content={`${DEFAULT_SEO.siteUrl}/guide`} />
    
    {/* Canonical */}
    <link rel="canonical" href={`${DEFAULT_SEO.siteUrl}/guide`} />
  </Helmet>
);

export default {
  HomePageSEO,
  ApartmentListingSEO,
  SearchPageSEO,
  BoroughPageSEO,
  NeighborhoodPageSEO,
  DashboardSEO,
  FavoritesSEO,
  SavedSearchesSEO,
  RentCalculatorSEO,
  SavingsCalculatorSEO,
  CostOfLivingCalculatorSEO,
  FAQSEO,
  GuideSEO
};
