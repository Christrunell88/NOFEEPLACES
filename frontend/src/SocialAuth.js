import React, { useState, useEffect } from 'react';
import FacebookLogin from '@greatsumini/react-facebook-login';
import { useAuth } from './auth';

const SocialAuthButtons = ({ onSuccess, onError, onClose }) => {
  const { loginWithFacebook, loginWithApple, loginWithGoogle, loading } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [appleLoaded, setAppleLoaded] = useState(false);

  // Load Apple SDK
  useEffect(() => {
    const loadAppleSDK = () => {
      if (window.AppleID) {
        setAppleLoaded(true);
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://appleid.cdn-apple.com/appleauth/static/jsapi/appleid/1/en_US/appleid.auth.js';
      script.async = true;
      script.onload = () => {
        if (window.AppleID) {
          window.AppleID.auth.init({
            clientId: process.env.REACT_APP_APPLE_CLIENT_ID || 'com.nofeeplaces.signin',
            scope: 'name email',
            redirectURI: `${window.location.origin}/apple-callback.html`,
            state: 'apple-auth-state',
            usePopup: true
          });
          setAppleLoaded(true);
        }
      };
      script.onerror = () => {
        console.error('Failed to load Apple SDK');
        setAppleLoaded(false);
      };
      document.body.appendChild(script);
    };

    loadAppleSDK();
  }, []);

  // Facebook authentication handler
  const handleFacebookSuccess = async (response) => {
    setIsLoading(true);
    try {
      const result = await loginWithFacebook(response.accessToken, response.userID);
      
      if (result.success) {
        onSuccess && onSuccess(result.user);
        onClose && onClose();
      } else {
        onError && onError(result.error);
      }
    } catch (error) {
      onError && onError('Facebook login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFacebookError = (error) => {
    console.error('Facebook login error:', error);
    onError && onError('Facebook login failed. Please try again.');
  };

  // Apple authentication handler
  const handleAppleSignIn = async () => {
    if (!appleLoaded || !window.AppleID) {
      onError && onError('Apple authentication service is not available');
      return;
    }

    setIsLoading(true);
    try {
      const response = await window.AppleID.auth.signIn();
      
      const result = await loginWithApple(
        response.authorization.code,
        response.authorization.id_token,
        response.user
      );
      
      if (result.success) {
        onSuccess && onSuccess(result.user);
        onClose && onClose();
      } else {
        onError && onError(result.error);
      }
    } catch (error) {
      console.error('Apple Sign-In error:', error);
      
      // Handle user cancellation
      if (error.error === 'popup_closed_by_user') {
        return; // Don't show error for user cancellation
      }
      
      onError && onError('Apple Sign-In failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Google authentication handler (existing implementation)
  const handleGoogleLogin = () => {
    // Redirect to existing Google OAuth
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/api/auth/google/login`;
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

        {/* Facebook Login Button */}
        <FacebookLogin
          appId={process.env.REACT_APP_FACEBOOK_APP_ID}
          onSuccess={handleFacebookSuccess}
          onFail={handleFacebookError}
          fields="name,email,picture"
          scope="public_profile,email"
          render={({ onClick }) => (
            <button
              onClick={onClick}
              disabled={isButtonDisabled}
              className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24" fill="currentColor">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
              {isButtonDisabled ? 'Signing in...' : 'Continue with Facebook'}
            </button>
          )}
        />

        {/* Apple Sign-In Button */}
        <button
          onClick={handleAppleSignIn}
          disabled={isButtonDisabled || !appleLoaded}
          className="w-full flex items-center justify-center px-4 py-3 bg-black text-white rounded-lg hover:bg-gray-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09z" />
            <path d="M15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.56-1.701" />
          </svg>
          {isButtonDisabled ? 'Signing in...' : !appleLoaded ? 'Loading Apple...' : 'Continue with Apple'}
        </button>
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