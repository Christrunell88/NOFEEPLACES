import React from 'react';

const SEOAffordableSection = () => {
  return (
    <section className="bg-gradient-to-r from-teal-50 to-blue-50 py-16">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          {/* Main SEO Heading */}
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-6">
              Can't Find an Affordable Apartment in NYC?
            </h2>
            <p className="text-lg text-gray-600">
              Skip the broker fees. Find 240+ no-fee apartments starting at $1,900/month.
            </p>
          </div>

          {/* Minimal Problem & Solution */}
          <div className="bg-white rounded-xl p-6 shadow-lg mb-12">
            <div className="grid md:grid-cols-2 gap-8 text-center">
              <div>
                <div className="text-red-500 text-3xl mb-2">😤</div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">Broker fees cost $3,000-$8,000+</h3>
                <p className="text-gray-600">Most NYC rentals charge hefty broker fees</p>
              </div>
              <div>
                <div className="text-teal-500 text-3xl mb-2">✨</div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">We eliminate all broker fees</h3>
                <p className="text-gray-600">240+ verified no-fee apartments</p>
              </div>
            </div>
          </div>

          {/* Affordable Neighborhoods */}
          <div className="bg-white rounded-xl p-8 shadow-lg mb-12">
            <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">
              Affordable NYC Neighborhoods with No-Fee Apartments
            </h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl mb-2">🏙️</div>
                <h4 className="font-semibold text-gray-800 mb-2">Manhattan</h4>
                <p className="text-sm text-gray-600">Upper West Side, Hell's Kitchen, Financial District</p>
                <p className="text-teal-600 font-semibold">From $2,300/month</p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-2">🌉</div>
                <h4 className="font-semibold text-gray-800 mb-2">Brooklyn</h4>
                <p className="text-sm text-gray-600">Williamsburg, Bedford-Stuyvesant, Crown Heights</p>
                <p className="text-teal-600 font-semibold">From $1,900/month</p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-2">🏘️</div>
                <h4 className="font-semibold text-gray-800 mb-2">Queens</h4>
                <p className="text-sm text-gray-600">Long Island City, Astoria, Sunnyside</p>
                <p className="text-teal-600 font-semibold">From $2,100/month</p>
              </div>
            </div>
          </div>

          {/* SEO Content - Affordable Apartment Search Tips */}
          <div className="bg-white rounded-xl p-8 shadow-lg">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">
              Why NYC Apartment Hunting is So Expensive (And How to Fix It)
            </h3>
            <div className="prose prose-lg text-gray-600">
              <p className="mb-4">
                If you can't find an affordable apartment in NYC, it's not your fault. The traditional rental market is designed to extract maximum fees from renters through broker commissions, application fees, and inflated prices.
              </p>
              <p className="mb-4">
                <strong>The average NYC renter pays $4,500 in broker fees alone</strong> - money that could go toward your security deposit, furniture, or savings. NoFeePlaces.com eliminates these unnecessary costs by connecting renters directly with property owners who pay the fees themselves.
              </p>
              <p className="mb-4">
                Our platform features real, verified apartments in every NYC borough with transparent pricing and no hidden costs. Whether you're looking for a studio in Manhattan, a one-bedroom in Brooklyn, or a spacious two-bedroom in Queens, we help you find affordable options without the broker fee burden.
              </p>
            </div>
          </div>

          {/* CTA */}
          <div className="text-center mt-12">
            <button 
              onClick={() => window.scrollTo({ top: 1200, behavior: 'smooth' })}
              className="bg-teal-500 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-teal-600 transition-colors shadow-xl inline-flex items-center"
            >
              <span className="mr-2">🔍</span>
              Browse 240+ No-Fee Apartments Now
            </button>
            <p className="text-sm text-gray-500 mt-3">
              Save $3,000+ on your next NYC apartment rental
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SEOAffordableSection;