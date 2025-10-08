import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './auth';

const ConversionOptimizedHero = () => {
  const { isAuthenticated } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  return (
    <div className="relative bg-gradient-to-br from-slate-900 via-gray-900 to-slate-800 min-h-screen flex items-center">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiMxZTI5M2IiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PHBhdGggZD0ibTM2IDM0djEwaDE0di0xMGgtMTR6bTAtMTR2MTBoMTR2LTEwaC0xNHoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-50"></div>
      
      <div className="relative max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          {/* Urgent Problem Statement */}
          <div className="inline-flex items-center bg-red-500/10 border border-red-400/20 text-red-300 px-6 py-3 rounded-full mb-8 text-sm font-semibold">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.864-.833-2.634 0L4.18 15.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            NYC BROKER FEES AVERAGE $3,000-$8,000 PER RENTAL
          </div>

          {/* Powerful Value Proposition Headline */}
          <h1 className="text-5xl md:text-7xl font-black text-white mb-6 leading-tight">
            <span className="block">Find NYC Apartments</span>
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400">
              With ZERO Fees
            </span>
          </h1>

          {/* Clear Benefit Subheading */}
          <p className="text-xl md:text-2xl text-gray-300 mb-4 max-w-4xl mx-auto font-medium leading-relaxed">
            Skip the $3,000+ broker fees. Access 400+ verified no-fee apartments directly from landlords.
          </p>

          {/* Social Proof */}
          <p className="text-emerald-400 text-lg font-semibold mb-12">
            ✓ Over $2M in broker fees saved by 1,000+ renters
          </p>

          {/* Primary Action CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
            {/* Primary CTA - Most Important Action */}
            <Link
              to="/"
              className="group relative overflow-hidden bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white px-12 py-5 rounded-2xl text-xl font-bold shadow-2xl hover:shadow-emerald-500/25 transition-all duration-300 transform hover:scale-105 border-2 border-emerald-400"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="relative flex items-center">
                <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                FIND NO-FEE APARTMENTS
              </div>
              <div className="text-sm opacity-90 mt-1">Browse 400+ verified listings</div>
            </Link>

            {/* Secondary CTA - Alternative Action */}
            {!isAuthenticated && (
              <button
                onClick={() => setShowAuthModal(true)}
                className="group bg-white/10 hover:bg-white/20 text-white border-2 border-white/30 hover:border-white/50 px-10 py-5 rounded-2xl text-lg font-semibold transition-all duration-300 backdrop-blur-sm"
              >
                <div className="flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  CREATE FREE ACCOUNT
                </div>
                <div className="text-sm opacity-80 mt-1">Save favorites & get alerts</div>
              </button>
            )}
          </div>

          {/* Value Proof Cards */}
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 text-center hover:bg-white/10 transition-colors">
              <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">$0 Broker Fees</h3>
              <p className="text-gray-400">Keep your money for move-in costs</p>
            </div>

            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 text-center hover:bg-white/10 transition-colors">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">400+ Verified Listings</h3>
              <p className="text-gray-400">All properties screened & authentic</p>
            </div>

            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 text-center hover:bg-white/10 transition-colors">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Instant Access</h3>
              <p className="text-gray-400">Contact landlords directly today</p>
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="mt-16 flex flex-col sm:flex-row items-center justify-center gap-8 text-gray-400">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
              </svg>
              <span className="font-semibold">Secure Platform</span>
            </div>
            <div className="flex items-center">
              <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
              </svg>
              <span className="font-semibold">NYC Licensed</span>
            </div>
            <div className="flex items-center">
              <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-semibold">1,000+ Happy Renters</span>
            </div>
          </div>
        </div>
      </div>

      {/* Auth Modal Trigger */}
      {showAuthModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Create Your Free Account</h3>
            <p className="text-gray-600 mb-6">Join thousands who've saved on broker fees</p>
            <button
              onClick={() => setShowAuthModal(false)}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-lg font-semibold"
            >
              Sign Up Now
            </button>
            <button
              onClick={() => setShowAuthModal(false)}
              className="w-full text-gray-500 mt-4"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConversionOptimizedHero;