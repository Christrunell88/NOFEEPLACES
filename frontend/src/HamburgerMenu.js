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
              {/* Left Side - Navigation Links */}
              <div className="flex-1 p-6 space-y-6">
                <div className="space-y-4">
                  <Link
                    to="/about"
                    onClick={closeMenu}
                    className="block text-lg font-medium text-gray-800 hover:text-blue-600 transition-colors py-2 border-b border-gray-100"
                  >
                    About Us
                  </Link>
                  <Link
                    to="/why-no-fee"
                    onClick={closeMenu}
                    className="block text-lg font-medium text-gray-800 hover:text-blue-600 transition-colors py-2 border-b border-gray-100"
                  >
                    Why No Fee?
                  </Link>
                  <Link
                    to="/contact"
                    onClick={closeMenu}
                    className="block text-lg font-medium text-gray-800 hover:text-blue-600 transition-colors py-2 border-b border-gray-100"
                  >
                    Contact Us
                  </Link>
                  <Link
                    to="/lets-talk"
                    onClick={closeMenu}
                    className="block text-lg font-medium text-gray-800 hover:text-blue-600 transition-colors py-2 border-b border-gray-100"
                  >
                    Let's Talk
                  </Link>
                </div>

                {/* Existing Navigation Links */}
                <div className="pt-4 space-y-4 border-t border-gray-200">
                  <Link
                    to="/blog"
                    onClick={closeMenu}
                    className="block text-base text-gray-600 hover:text-blue-600 transition-colors py-1"
                  >
                    📖 Guides & Blog
                  </Link>
                  <Link
                    to="/tenant/list-apartment"
                    onClick={closeMenu}
                    className="block text-base text-gray-600 hover:text-blue-600 transition-colors py-1"
                  >
                    🏠 List Your Place
                  </Link>
                  <Link
                    to="/newsletter"
                    onClick={closeMenu}
                    className="block text-base text-gray-600 hover:text-blue-600 transition-colors py-1"
                  >
                    📧 Newsletter
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