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

          {/* Problem & Solution Grid */}
          <div className="grid md:grid-cols-2 gap-8 mb-12">
            {/* Problem Side */}
            <div className="bg-white rounded-xl p-8 shadow-lg">
              <div className="text-red-500 text-4xl mb-4">😤</div>
              <h3 className="text-2xl font-bold text-gray-800 mb-4">The NYC Apartment Problem</h3>
              <ul className="space-y-3 text-gray-600">
                <li className="flex items-start">
                  <span className="text-red-500 mr-2">•</span>
                  <span>Broker fees cost $3,000-$8,000+ per rental</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-500 mr-2">•</span>
                  <span>Limited affordable options in desirable neighborhoods</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-500 mr-2">•</span>
                  <span>Fake listings and bait-and-switch tactics</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-500 mr-2">•</span>
                  <span>Time-consuming apartment hunting process</span>
                </li>
              </ul>
            </div>

            {/* Solution Side */}
            <div className="bg-white rounded-xl p-8 shadow-lg">
              <div className="text-teal-500 text-4xl mb-4">✨</div>
              <h3 className="text-2xl font-bold text-gray-800 mb-4">The NoFeePlaces Solution</h3>
              <ul className="space-y-3 text-gray-600">
                <li className="flex items-start">
                  <span className="text-teal-500 mr-2">✓</span>
                  <span>240+ verified no-fee apartments across NYC</span>
                </li>
                <li className="flex items-start">
                  <span className="text-teal-500 mr-2">✓</span>
                  <span>Save $3,000-$8,000 on broker fees</span>
                </li>
                <li className="flex items-start">
                  <span className="text-teal-500 mr-2">✓</span>
                  <span>Direct contact with property owners</span>
                </li>
                <li className="flex items-start">
                  <span className="text-teal-500 mr-2">✓</span>
                  <span>AI-powered search and instant notifications</span>
                </li>
              </ul>
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