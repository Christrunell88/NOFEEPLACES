import React from 'react';
import ConversionOptimizedHero from './ConversionOptimizedHero';
import ConversionCTASection from './ConversionCTASection';
import { 
  ApartmentGrid,
  NewsletterPage,
  Footer,
  SEOAffordableSection 
} from './components';

const ConversionOptimizedHome = () => {
  return (
    <div className="min-h-screen">
      {/* Conversion-Optimized Hero with Clear Value Prop & Strong CTAs */}
      <ConversionOptimizedHero />
      
      {/* Conversion CTA Sections */}
      <ConversionCTASection />
      
      {/* SEO Content (kept for search rankings) */}
      <SEOAffordableSection />
      
      {/* Apartment Listings (social proof) */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Latest No-Fee Apartments
            </h2>
            <p className="text-xl text-gray-600">
              Fresh listings added daily • All verified • Zero broker fees
            </p>
          </div>
          <ApartmentGrid />
        </div>
      </div>
      
      {/* Newsletter (for lead generation) */}
      <div className="bg-white py-16">
        <NewsletterPage />
      </div>
      
      {/* Footer */}
      <Footer />
    </div>
  );
};

export default ConversionOptimizedHome;