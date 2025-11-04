import React, { useState } from 'react';
import { useAuth } from './auth';
import { GoogleLogin } from '@react-oauth/google';

const SocialAuthButtons = ({ onSuccess, onError, onClose }) => {
  const { loginWithGoogle, loading } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  // Google authentication callback handler
  const handleGoogleSuccess = async (credentialResponse) => {
    console.log('✅ Google Sign-In success, received credential');
    setIsLoading(true);
    try {
      // Send ID token to backend for verification
      const result = await loginWithGoogle(credentialResponse.credential);
      
      if (result.success) {
        console.log('✅ Backend authentication successful');
        onSuccess && onSuccess(result.user);
        onClose && onClose();
      } else {
        console.error('❌ Backend authentication failed:', result.error);
        onError && onError(result.error || 'Google Sign-In failed');
      }
    } catch (error) {
      console.error('❌ Authentication error:', error);
      onError && onError('Google Sign-In failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleError = () => {
    console.error('❌ Google Sign-In failed');
    onError && onError('Google Sign-In failed. Please try again.');
    setIsLoading(false);
  };

  const handleGoogleLogin = () => {
    // Trigger loading state when button is clicked
    setIsLoading(true);
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
        <div id="google-signin-button" className="w-full">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            useOneTap={false}
            theme="outline"
            size="large"
            text="continue_with"
            shape="rectangular"
            width="100%"
          />
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