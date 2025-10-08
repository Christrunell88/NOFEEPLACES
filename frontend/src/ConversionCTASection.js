import React from 'react';
import { Link } from 'react-router-dom';

const ConversionCTASection = () => {
  return (
    <>
      {/* Urgent Action Section */}
      <div className="bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 py-20">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <h2 className="text-4xl md:text-5xl font-black text-white mb-6">
            Stop Paying Broker Fees Today
          </h2>
          <p className="text-xl text-emerald-100 mb-8 max-w-3xl mx-auto">
            Why waste $3,000-$8,000 on broker fees when you can rent directly? 
            <strong className="text-white"> Start browsing 400+ no-fee apartments right now.</strong>
          </p>
          
          {/* Dual CTAs */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
            <Link
              to="/"
              className="group bg-white hover:bg-gray-50 text-emerald-700 px-10 py-5 rounded-2xl text-xl font-bold shadow-2xl transition-all duration-300 transform hover:scale-105 border-2 border-white"
            >
              <div className="flex items-center">
                <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                BROWSE APARTMENTS NOW
              </div>
              <div className="text-sm opacity-80">400+ no-fee listings available</div>
            </Link>

            <Link
              to="/tenant/list-apartment"
              className="group bg-emerald-800 hover:bg-emerald-900 text-white border-2 border-emerald-300 hover:border-emerald-200 px-10 py-5 rounded-2xl text-xl font-bold transition-all duration-300"
            >
              <div className="flex items-center">
                <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                LIST YOUR APARTMENT
              </div>
              <div className="text-sm opacity-90">For landlords - Post for FREE</div>
            </Link>
          </div>

          {/* Urgency Indicator */}
          <div className="mt-8 inline-flex items-center bg-red-500/20 border border-red-300 text-white px-6 py-3 rounded-full text-sm font-semibold">
            <svg className="w-4 h-4 mr-2 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" />
            </svg>
            47 new no-fee apartments added this week
          </div>
        </div>
      </div>

      {/* Social Proof & Conversion Section */}
      <div className="bg-white py-20">
        <div className="max-w-6xl mx-auto px-6">
          {/* Social Proof Header */}
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Join 1,000+ New Yorkers Who Ditched Broker Fees
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Real people, real savings, real apartments
            </p>
            
            {/* Savings Counter */}
            <div className="inline-flex items-center bg-emerald-50 border-2 border-emerald-200 px-8 py-4 rounded-2xl">
              <div className="text-center">
                <div className="text-3xl font-black text-emerald-700">$2,047,395</div>
                <div className="text-sm font-semibold text-emerald-600">Total Broker Fees Saved</div>
              </div>
            </div>
          </div>

          {/* Benefit Comparison */}
          <div className="grid md:grid-cols-2 gap-8 mb-16">
            {/* Traditional Way (Bad) */}
            <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-8">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-red-800 mb-2">Traditional Rental</h3>
                <div className="text-red-600 font-semibold">What you used to pay</div>
              </div>
              
              <div className="space-y-4 text-red-700">
                <div className="flex justify-between items-center py-2 border-b border-red-200">
                  <span>Monthly Rent</span>
                  <span className="font-semibold">$3,000</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-red-200">
                  <span>Security Deposit</span>
                  <span className="font-semibold">$3,000</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-red-200">
                  <span className="text-red-800 font-bold">Broker Fee (15%)</span>
                  <span className="font-bold text-red-800">$5,400</span>
                </div>
                <div className="flex justify-between items-center py-3 bg-red-100 rounded-lg px-4">
                  <span className="font-bold text-lg">Total Move-in Cost</span>
                  <span className="font-bold text-xl text-red-800">$11,400</span>
                </div>
              </div>
            </div>

            {/* NoFee Way (Good) */}
            <div className="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-8">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-emerald-800 mb-2">NoFee Places</h3>
                <div className="text-emerald-600 font-semibold">What you pay now</div>
              </div>
              
              <div className="space-y-4 text-emerald-700">
                <div className="flex justify-between items-center py-2 border-b border-emerald-200">
                  <span>Monthly Rent</span>
                  <span className="font-semibold">$3,000</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-emerald-200">
                  <span>Security Deposit</span>
                  <span className="font-semibold">$3,000</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-emerald-200">
                  <span className="text-emerald-800 font-bold">Broker Fee</span>
                  <span className="font-bold text-emerald-800">$0</span>
                </div>
                <div className="flex justify-between items-center py-3 bg-emerald-100 rounded-lg px-4">
                  <span className="font-bold text-lg">Total Move-in Cost</span>
                  <span className="font-bold text-xl text-emerald-800">$6,000</span>
                </div>
              </div>
              
              {/* Savings Highlight */}
              <div className="mt-6 bg-emerald-600 text-white p-4 rounded-xl text-center">
                <div className="text-2xl font-bold">YOU SAVE $5,400!</div>
                <div className="text-emerald-100 text-sm">Use it for furniture, moving, or save it!</div>
              </div>
            </div>
          </div>

          {/* Final Conversion CTA */}
          <div className="text-center bg-gradient-to-r from-gray-900 to-black rounded-3xl p-12">
            <h3 className="text-3xl md:text-4xl font-black text-white mb-4">
              Ready to Save Thousands?
            </h3>
            <p className="text-xl text-gray-300 mb-8">
              Don't let brokers take your money. Start apartment hunting the smart way.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                to="/"
                className="group bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white px-12 py-6 rounded-2xl text-xl font-bold shadow-2xl transition-all duration-300 transform hover:scale-105"
              >
                <div className="flex items-center">
                  <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  START BROWSING APARTMENTS
                </div>
                <div className="text-sm opacity-90 mt-1">Free • No broker fees • Instant access</div>
              </Link>
            </div>

            {/* Trust Elements */}
            <div className="mt-8 flex flex-wrap justify-center items-center gap-6 text-gray-400 text-sm">
              <div className="flex items-center">
                <svg className="w-4 h-4 text-green-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
                </svg>
                No hidden fees
              </div>
              <div className="flex items-center">
                <svg className="w-4 h-4 text-green-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
                </svg>
                Verified listings
              </div>
              <div className="flex items-center">
                <svg className="w-4 h-4 text-green-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
                </svg>
                Direct landlord contact
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ConversionCTASection;