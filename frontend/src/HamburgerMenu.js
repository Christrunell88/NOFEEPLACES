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
                  <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}>Company</div>
                  
                  <Link
                    to="/about"
                    onClick={closeMenu}
                    className="block text-gray-800 hover:text-blue-600 hover:bg-blue-50 transition-all py-3 px-4 rounded-lg"
                    style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif', fontSize: '15px', fontWeight: '500', letterSpacing: '-0.01em' }}
                  >
                    About Us
                  </Link>
                  
                  <Link
                    to="/why-no-fee"
                    onClick={closeMenu}
                    className="block text-gray-800 hover:text-blue-600 hover:bg-blue-50 transition-all py-3 px-4 rounded-lg"
                    style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif', fontSize: '15px', fontWeight: '500', letterSpacing: '-0.01em' }}
                  >
                    Why No Fee?
                  </Link>
                  
                  <Link
                    to="/contact"
                    onClick={closeMenu}
                    className="block text-gray-800 hover:text-blue-600 hover:bg-blue-50 transition-all py-3 px-4 rounded-lg"
                    style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif', fontSize: '15px', fontWeight: '500', letterSpacing: '-0.01em' }}
                  >
                    Contact Us
                  </Link>
                  
                  <Link
                    to="/lets-talk"
                    onClick={closeMenu}
                    className="block text-gray-800 hover:text-blue-600 hover:bg-blue-50 transition-all py-3 px-4 rounded-lg"
                    style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif', fontSize: '15px', fontWeight: '500', letterSpacing: '-0.01em' }}
                  >
                    Let's Talk
                  </Link>
                </div>

                {/* Boroughs */}
              </div>

              {/* Right Side - Clean Menu */}
              <div className="w-40 bg-white border-l border-gray-200 flex flex-col">
                
                {/* Menu Items */}
                <div className="flex-1 p-6 space-y-4">
                  <Link
                    to="/tenant/list-apartment"
                    onClick={closeMenu}
                    className="block w-full text-center bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-serif text-base py-4 px-4 rounded-lg transition-all shadow-md hover:shadow-lg"
                  >
                    List Property
                  </Link>
                  
                  <Link
                    to="/admin"
                    onClick={closeMenu}
                    className="block w-full text-center bg-gray-800 hover:bg-gray-900 text-white font-serif text-base py-4 px-4 rounded-lg transition-all"
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