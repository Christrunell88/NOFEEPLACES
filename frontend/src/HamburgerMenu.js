import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './auth';
import { isAdminAuthenticated } from './AdminAuth';
import { WordMark } from './WordMark';

const HamburgerMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, user, logout } = useAuth();

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const closeMenu = () => {
    setIsOpen(false);
  };

  const handleLoginClick = () => {
    closeMenu();
    // Dispatch event to open auth modal in App.js
    window.dispatchEvent(new CustomEvent('openAuthModal'));
  };

  const handleLogout = () => {
    logout();
    closeMenu();
  };

  return (
    <div className="relative">
      {/* Professional Hamburger Button */}
      <button
        onClick={toggleMenu}
        className="flex flex-col justify-center items-center w-10 h-10 rounded-lg border border-gray-600 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-all duration-200 group bg-gray-800 hover:bg-gray-700"
        aria-label={isOpen ? "Close navigation menu" : "Open navigation menu"}
        aria-expanded={isOpen}
        aria-haspopup="true"
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
            role="presentation"
            aria-hidden="true"
          ></div>
          
          {/* Professional Menu Panel */}
          <nav 
            className="fixed top-0 right-0 w-96 h-screen bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out border-l border-gray-200"
            role="navigation"
            aria-label="Main navigation menu"
          >
            {/* Menu Header */}
            <div className="flex justify-between items-center p-6 bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
              <WordMark 
                size="small" 
                theme="light" 
                tagline="NAVIGATION MENU"
                linkTo="/"
                hover={false}
              />
              <button
                onClick={closeMenu}
                className="w-9 h-9 flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-white rounded-xl transition-all shadow-sm border border-gray-200"
                aria-label="Close navigation menu"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="flex h-full">
              {/* Left Side - Professional Navigation Links */}
              <div className="flex-1 p-6 space-y-6">
                {/* User Authentication Section - TOP PLACEMENT */}
                {!isAuthenticated && (
                  <div className="mb-6 pb-6 border-b border-gray-200">
                    <button
                      onClick={handleLoginClick}
                      className="w-full bg-gray-900 hover:bg-gray-800 text-white py-3 px-4 rounded-lg transition-colors font-medium text-sm"
                      aria-label="Sign in to your account"
                    >
                      Sign In / Sign Up
                    </button>
                    <p className="text-xs text-gray-500 text-center mt-2">
                      Google • Facebook • Apple
                    </p>
                  </div>
                )}

                {/* Authenticated User Profile - TOP PLACEMENT */}
                {isAuthenticated && (
                  <div className="mb-6 pb-6 border-b border-gray-200">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-10 h-10 bg-gray-900 text-white rounded-full flex items-center justify-center font-semibold">
                        {user?.name ? user.name.charAt(0).toUpperCase() : user?.email?.charAt(0).toUpperCase() || 'U'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900 truncate text-sm">
                          {user?.name || user?.email?.split('@')[0]}
                        </div>
                        <div className="text-xs text-gray-500 truncate">
                          {user?.email}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 py-2 px-4 rounded-lg transition-colors font-medium text-sm"
                    >
                      Sign Out
                    </button>
                  </div>
                )}

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

                {/* Boroughs */}
              </div>

              {/* Right Side - Professional Admin Panel */}
              <div className="w-36 bg-gradient-to-b from-slate-50 to-slate-100 border-l border-gray-200 flex flex-col">
                {/* Admin Header */}
                
                {/* Services & Admin Actions */}
                <div className="flex-1 p-4 space-y-3">
                  {/* Services moved to right */}
                  <Link
                    to="/blog"
                    onClick={closeMenu}
                    className="flex items-center justify-center w-full bg-white hover:bg-blue-50 text-slate-700 hover:text-blue-700 text-xs font-semibold py-3 px-3 rounded-lg transition-all border border-slate-200 hover:border-blue-300 shadow-sm group"
                  >
                    <svg className="w-4 h-4 mr-2 group-hover:text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    Guides
                  </Link>
                  
                  <Link
                    to="/tenant/list-apartment"
                    onClick={closeMenu}
                    className="flex items-center justify-center w-full bg-white hover:bg-emerald-50 text-slate-700 hover:text-emerald-700 text-xs font-semibold py-3 px-3 rounded-lg transition-all border border-slate-200 hover:border-emerald-300 shadow-sm group"
                  >
                    <svg className="w-4 h-4 mr-2 group-hover:text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    List Property
                  </Link>
                  
                  <Link
                    to="/newsletter"
                    onClick={closeMenu}
                    className="flex items-center justify-center w-full bg-white hover:bg-purple-50 text-slate-700 hover:text-purple-700 text-xs font-semibold py-3 px-3 rounded-lg transition-all border border-slate-200 hover:border-purple-300 shadow-sm group"
                  >
                    <svg className="w-4 h-4 mr-2 group-hover:text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM9 7h6m0 10v-3H9v3z M20.121 12.121A3 3 0 0 0 18 9h-1.172A3 3 0 0 0 13 7.172V6a3 3 0 1 0-6 0v1.172A3 3 0 0 0 3.172 9H2a3 3 0 0 0 2.121 3.121z" />
                    </svg>
                    Newsletter
                  </Link>
                  
                  {/* Admin - Simplified */}
                  <Link
                    to="/admin"
                    onClick={closeMenu}
                    className="flex items-center justify-center w-full bg-white hover:bg-gray-50 text-gray-700 hover:text-gray-900 text-xs font-medium py-3 px-3 rounded-lg transition-all border border-gray-200 hover:border-gray-300"
                  >
                    Admin
                  </Link>
                </div>
              </div>
            </div>

            {/* Professional Footer */}
            <div className="absolute bottom-0 left-0 right-32 bg-gradient-to-r from-gray-100 to-gray-200 border-t border-gray-300 p-4">
              <div className="text-center">
                <div className="text-xs font-semibold text-gray-700 mb-1">© 2025 NoFeePlaces.com</div>
                <div className="text-xs text-gray-500 font-medium">Professional Real Estate Platform</div>
                <div className="mt-2 flex justify-center items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                  <span className="text-xs text-gray-600">Trusted & Verified</span>
                </div>
              </div>
            </div>
          </nav>
        </>
      )}
    </div>
  );
};

export default HamburgerMenu;