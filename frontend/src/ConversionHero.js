import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const ConversionHero = () => {
  const [showAuthModal, setShowAuthModal] = useState(false);

  return (
    <div className="relative bg-gradient-to-br from-slate-900 via-gray-900 to-slate-800 text-white py-20 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-black/20"></div>
      
      <div className="relative max-w-6xl mx-auto px-6 text-center">
        {/* Urgent Problem Statement */}
        <div className="inline-flex items-center bg-red-500/20 border border-red-400/30 text-red-300 px-6 py-3 rounded-full mb-8 text-sm font-semibold">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.864-.833-2.634 0L4.18 15.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          STOP PAYING $3,000+ BROKER FEES
        </div>

        {/* Clear Value Proposition Headline */}
        <h1 className="text-4xl md:text-6xl font-black mb-6 leading-tight">
          <span className="block text-white">Find NYC Apartments</span>
          <span className="block text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">
            With ZERO Fees
          </span>
        </h1>

        {/* Clear Benefits */}
        <p className="text-xl md:text-2xl text-gray-200 mb-4 max-w-4xl mx-auto leading-relaxed">
          Skip the broker fees. Access <strong className="text-emerald-400">400+ verified no-fee apartments</strong> directly from landlords.
        </p>

        {/* Social Proof */}
        <p className="text-emerald-400 text-lg font-semibold mb-12">
          ✓ $2M+ in broker fees saved • 1,000+ happy renters
        </p>

        {/* Strong Primary CTA */}
        <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
          <Link
            to="/"
            className="group bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white px-12 py-5 rounded-2xl text-xl font-bold shadow-2xl hover:shadow-emerald-500/25 transition-all duration-300 transform hover:scale-105 border-2 border-emerald-400"
          >
            <div className="flex items-center">
              <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              BROWSE NO-FEE APARTMENTS
            </div>
            <div className="text-sm opacity-90 mt-1">400+ listings • Zero broker fees</div>
          </Link>

          <button
            onClick={() => setShowAuthModal(true)}
            className="group bg-white/10 hover:bg-white/20 text-white border-2 border-white/30 hover:border-white/50 px-10 py-5 rounded-2xl text-lg font-semibold transition-all duration-300 backdrop-blur-sm"
          >
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              GET APARTMENT ALERTS
            </div>
            <div className="text-sm opacity-80 mt-1">Free account • Save favorites</div>
          </button>
        </div>

        {/* Value Proof */}
        <div className="mt-16 grid md:grid-cols-3 gap-8">
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">$0 Broker Fees</h3>
            <p className="text-gray-300">Keep $3,000-$6,000 in your pocket</p>
          </div>

          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">400+ Verified Listings</h3>
            <p className="text-gray-300">All properties screened & authentic</p>
          </div>

          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Direct Access</h3>
            <p className="text-gray-300">Contact landlords directly today</p>
          </div>
        </div>
      </div>

      {/* Simple Auth Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Get Apartment Alerts</h3>
            <p className="text-gray-600 mb-6">Be the first to know about new no-fee apartments in your area.</p>
            <button
              onClick={() => setShowAuthModal(false)}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-lg font-semibold mb-3"
            >
              Sign Up for Alerts
            </button>
            <button
              onClick={() => setShowAuthModal(false)}
              className="w-full text-gray-500 text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConversionHero;