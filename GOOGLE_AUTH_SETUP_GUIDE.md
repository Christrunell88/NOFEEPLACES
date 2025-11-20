# Google Sign-In Setup Guide

## Current State
- Email/Password authentication is fully functional
- Google Sign-In code has been removed temporarily
- SocialAuth.js backed up to SocialAuth.js.backup

## To Re-enable Google Sign-In

### 1. Google Cloud Console Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Enable Google+ API
4. Go to "Credentials"
5. Create OAuth 2.0 Client ID (Web application)
6. Add Authorized JavaScript origins:
   - `https://nofeeplaces.com`
   - `https://realty-login.preview.emergentagent.com` (for testing)
7. Add Authorized redirect URIs:
   - `https://nofeeplaces.com`
   - `https://realty-login.preview.emergentagent.com`
8. Save and copy the Client ID

### 2. Update Frontend Environment

Add to `/app/frontend/.env`:
```
REACT_APP_GOOGLE_CLIENT_ID=your_client_id_here
```

### 3. Restore Google Sign-In Code

1. Restore `SocialAuth.js`:
   ```bash
   mv /app/frontend/src/SocialAuth.js.backup /app/frontend/src/SocialAuth.js
   ```

2. Update `missing-components.js` to add Google option in AuthModal (keep email/password as primary)

3. Install required dependencies if needed:
   ```bash
   cd /app/frontend
   yarn add @react-oauth/google
   ```

4. Wrap App with GoogleOAuthProvider in `App.js`:
   ```javascript
   import { GoogleOAuthProvider } from '@react-oauth/google';
   
   // Wrap root component
   <GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}>
     <App />
   </GoogleOAuthProvider>
   ```

### 4. Backend Configuration

Backend already supports Google auth at `/api/auth/google` endpoint.
It accepts a `token` field with the Google token.

### 5. Test

1. Build frontend: `yarn build`
2. Restart frontend: `sudo supervisorctl restart frontend`
3. Test in incognito window

## Current Working Features

✅ Email/Password Sign Up
✅ Email/Password Sign In  
✅ Contact forms (authenticated users)
✅ Schedule showings (authenticated users)
✅ Listing teasing (encourages sign-up)
✅ 264 available apartments
✅ Borough filtering

## Backup Files

- `/app/frontend/src/SocialAuth.js.backup` - Original social auth component
- Can be restored when Google OAuth is configured
