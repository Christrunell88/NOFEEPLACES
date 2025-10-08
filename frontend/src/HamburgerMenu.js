import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './auth';

const HamburgerMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, user, logout } = useAuth();

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const closeMenu = () => {
    setIsOpen(false);
  };

  return (
    <div className="relative">
      {/* Professional Hamburger Button */}
      <button
        onClick={toggleMenu}
        className="flex flex-col justify-center items-center w-10 h-10 rounded-lg border border-gray-600 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-all duration-200 group bg-gray-800 hover:bg-gray-700"
        aria-label="Toggle navigation menu"
      >
        <div className={`w-5 h-0.5 bg-white transition-all duration-300 ${isOpen ? 'rotate-45 translate-y-1.5' : ''} group-hover:bg-blue-300`}></div>
        <div className={`w-5 h-0.5 bg-white transition-all duration-300 ${isOpen ? 'opacity-0' : 'my-1'} group-hover:bg-blue-300`}></div>
        <div className={`w-5 h-0.5 bg-white transition-all duration-300 ${isOpen ? '-rotate-45 -translate-y-1.5' : ''} group-hover:bg-blue-300`}></div>
      </button>

      {/* Menu Overlay */}
      {isOpen && (
        <>
          {/* Background Overlay */}
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={closeMenu}
          ></div>
          
          {/* Professional Menu Panel */}
          <div className="fixed top-0 right-0 w-96 h-screen bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out border-l border-gray-200">
            {/* Menu Header */}
            <div className="flex justify-between items-center p-6 bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                <div className="w-9 h-9 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center shadow-lg">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <div>
                  <div className="font-bold text-lg text-gray-900">
                    NoFee<span className="text-blue-600">Places</span>
                  </div>
                  <div className="text-xs text-gray-500 font-medium">Navigation Menu</div>
                </div>
              </div>
              <button
                onClick={closeMenu}
                className="w-9 h-9 flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-white rounded-xl transition-all shadow-sm border border-gray-200"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="flex h-full">
              {/* Left Side - Professional Navigation Links */}
              <div className="flex-1 p-6 space-y-6">
                <div className="space-y-1">
                  <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Company</div>
                  
                  <Link
                    to="/about"
                    onClick={closeMenu}
                    className="flex items-center space-x-3 text-gray-800 hover:text-blue-600 hover:bg-blue-50 transition-all py-3 px-3 rounded-lg group"
                  >
                    <div className="w-5 h-5 text-gray-500 group-hover:text-blue-600">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <span className="font-medium">About Us</span>
                  </Link>
                  
                  <Link
                    to="/why-no-fee"
                    onClick={closeMenu}
                    className="flex items-center space-x-3 text-gray-800 hover:text-blue-600 hover:bg-blue-50 transition-all py-3 px-3 rounded-lg group"
                  >
                    <div className="w-5 h-5 text-gray-500 group-hover:text-blue-600">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                      </svg>
                    </div>
                    <span className="font-medium">Why No Fee?</span>
                  </Link>
                  
                  <Link
                    to="/contact"
                    onClick={closeMenu}
                    className="flex items-center space-x-3 text-gray-800 hover:text-blue-600 hover:bg-blue-50 transition-all py-3 px-3 rounded-lg group"
                  >
                    <div className="w-5 h-5 text-gray-500 group-hover:text-blue-600">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <span className="font-medium">Contact Us</span>
                  </Link>
                  
                  <Link
                    to="/lets-talk"
                    onClick={closeMenu}
                    className="flex items-center space-x-3 text-gray-800 hover:text-blue-600 hover:bg-blue-50 transition-all py-3 px-3 rounded-lg group"
                  >
                    <div className="w-5 h-5 text-gray-500 group-hover:text-blue-600">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                    </div>
                    <span className="font-medium">Let's Talk</span>
                  </Link>
                </div>

                {/* Services Section */}
                <div className="pt-2 space-y-1">
                  <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Services</div>
                  
                  <Link
                    to="/blog"
                    onClick={closeMenu}
                    className="flex items-center space-x-3 text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all py-2.5 px-3 rounded-lg group"
                  >
                    <div className="w-4 h-4 text-gray-500 group-hover:text-blue-600">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                      </svg>
                    </div>
                    <span className="font-medium text-sm">Guides & Resources</span>
                  </Link>
                  
                  <Link
                    to="/tenant/list-apartment"
                    onClick={closeMenu}
                    className="flex items-center space-x-3 text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all py-2.5 px-3 rounded-lg group"
                  >
                    <div className="w-4 h-4 text-gray-500 group-hover:text-blue-600">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <span className="font-medium text-sm">List Your Property</span>
                  </Link>
                  
                  <Link
                    to="/newsletter"
                    onClick={closeMenu}
                    className="flex items-center space-x-3 text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all py-2.5 px-3 rounded-lg group"
                  >
                    <div className="w-4 h-4 text-gray-500 group-hover:text-blue-600">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM9 7h6m0 10v-3H9v3z M20.121 12.121A3 3 0 0 0 18 9h-1.172A3 3 0 0 0 13 7.172V6a3 3 0 1 0-6 0v1.172A3 3 0 0 0 3.172 9H2a3 3 0 0 0 2.121 3.121z" />
                      </svg>
                    </div>
                    <span className="font-medium text-sm">Market Updates</span>
                  </Link>
                </div>

                {/* User Links (if authenticated) */}
                {isAuthenticated && (
                  <div className="pt-4 space-y-4 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">Your Account</p>
                    <Link
                      to="/dashboard"
                      onClick={closeMenu}
                      className="block text-base text-gray-600 hover:text-blue-600 transition-colors py-1"
                    >
                      📊 Dashboard
                    </Link>
                    <Link
                      to="/favorites"
                      onClick={closeMenu}
                      className="block text-base text-gray-600 hover:text-blue-600 transition-colors py-1"
                    >
                      ❤️ Favorites
                    </Link>
                    <button
                      onClick={() => {
                        logout();
                        closeMenu();
                      }}
                      className="block w-full text-left text-base text-gray-600 hover:text-red-600 transition-colors py-1"
                    >
                      🚪 Sign Out
                    </button>
                  </div>
                )}
              </div>

              {/* Right Side - Admin Login */}
              <div className="w-32 bg-gray-50 p-6 border-l border-gray-200 flex flex-col justify-center items-center">
                <div className="text-center">
                  <div className="mb-4">
                    <div className="w-16 h-16 mx-auto bg-gradient-to-br from-blue-600 to-purple-700 rounded-full flex items-center justify-center mb-3">
                      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">Admin</h3>
                    <p className="text-xs text-gray-600 mb-4">Management Portal</p>
                  </div>
                  
                  <div className="space-y-3">
                    <Link
                      to="/analytics?admin=true"
                      onClick={closeMenu}
                      className="block w-full bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors"
                    >
                      Analytics
                    </Link>
                    <Link
                      to="/landlord/login"
                      onClick={closeMenu}
                      className="block w-full bg-gray-600 hover:bg-gray-700 text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors"
                    >
                      Landlord
                    </Link>
                    <button
                      onClick={() => {
                        // Could add admin login modal here
                        closeMenu();
                        alert('Admin login functionality - to be implemented');
                      }}
                      className="block w-full bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors"
                    >
                      Admin Login
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="absolute bottom-0 left-0 right-0 p-4 bg-gray-100 border-t border-gray-200">
              <div className="text-center text-xs text-gray-500">
                <p>© 2025 NoFeePlaces.com</p>
                <p className="mt-1">NYC's Premier No-Fee Apartment Platform</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default HamburgerMenu;