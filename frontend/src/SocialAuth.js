import React, { useState, useEffect } from 'react';
import { useAuth } from './auth';

const SocialAuthButtons = ({ onSuccess, onError, onClose }) => {
  const { loginWithGoogle, loading } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  // Google authentication handler with proper SDK
  const handleGoogleLogin = async () => {
    try {
      setIsLoading(true);
      
      // Check if Google SDK is loaded
      if (!window.google) {
        console.error('Google SDK not loaded');
        onError && onError('Google Sign-In not available. Please refresh the page.');
        return;
      }

      // Initialize Google Sign-In
      window.google.accounts.id.initialize({
        client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID,
        callback: handleGoogleCallback
      });

      // Prompt for sign-in
      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          // Fallback to one-tap if prompt fails
          window.google.accounts.id.renderButton(
            document.getElementById('google-signin-button'),
            { theme: 'outline', size: 'large' }
          );
        }
      });
    } catch (error) {
      console.error('Google Sign-In initialization error:', error);
      onError && onError('Failed to initialize Google Sign-In');
    } finally {
      setIsLoading(false);
    }
  };

  // Google callback handler
  const handleGoogleCallback = async (response) => {
    try {
      setIsLoading(true);
      const result = await loginWithGoogle(response.credential);
      
      if (result.success) {
        onSuccess && onSuccess(result.user);
        onClose && onClose();
      } else {
        onError && onError(result.error);
      }
    } catch (error) {
      console.error('Google authentication error:', error);
      onError && onError('Google Sign-In failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const isButtonDisabled = isLoading || loading;

  return (
    <div className="social-auth-container space-y-3">
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">
          Sign in to continue
        </h3>
        <p className="text-sm text-gray-600">
          Choose your preferred authentication method
        </p>
      </div>

      <div className="space-y-3">
        {/* Google Login Button */}
        <div id="google-signin-button">
          <button
            onClick={handleGoogleLogin}
            disabled={isButtonDisabled}
            className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
          <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          {isButtonDisabled ? 'Signing in...' : 'Continue with Google'}
        </button>
        </div>
      </div>

      <div className="mt-4 text-center text-xs text-gray-500">
        <p>
          By signing in, you agree to our{' '}
          <a href="/terms" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
            Terms of Service
          </a>{' '}
          and{' '}
          <a href="/privacy" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
            Privacy Policy
          </a>
        </p>
      </div>
    </div>
  );
};

export default SocialAuthButtons;