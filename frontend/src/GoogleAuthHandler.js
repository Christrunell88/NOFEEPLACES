import { useEffect } from 'react';
import { useAuth } from './auth';
import axios from 'axios';

const GoogleAuthHandler = () => {
  const { setUser, setToken } = useAuth();

  useEffect(() => {
    const handleGoogleAuth = async () => {
      // Check if session_id exists in URL fragment
      const hash = window.location.hash;
      const params = new URLSearchParams(hash.substring(1));
      const sessionId = params.get('session_id');

      if (!sessionId) {
        return; // No session_id, nothing to do
      }

      try {
        console.log('[Google Auth] Processing session_id...');

        // Call Emergent's session-data endpoint
        const response = await axios.get(
          'https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data',
          {
            headers: {
              'X-Session-ID': sessionId
            }
          }
        );

        const { email, name, session_token } = response.data;

        console.log('[Google Auth] Session data received:', email);

        // Now send this session_token to our backend to create/login user
        const API_URL = process.env.REACT_APP_BACKEND_URL || '';
        const loginResponse = await axios.post(`${API_URL}/api/auth/google-emergent`, {
          email,
          name,
          session_token
        });

        const { access_token, user } = loginResponse.data;

        // Save token to localStorage
        localStorage.setItem('token', access_token);
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

        console.log('[Google Auth] User logged in successfully');

        // Clean URL fragment
        window.history.replaceState(null, '', window.location.pathname);

        // Reload page to update auth state
        window.location.reload();

      } catch (error) {
        console.error('[Google Auth] Error:', error);
        // Clean URL fragment even on error
        window.history.replaceState(null, '', window.location.pathname);
        alert('Google sign-in failed. Please try again.');
      }
    };

    handleGoogleAuth();
  }, []);

  return null; // This component doesn't render anything
};

export default GoogleAuthHandler;
