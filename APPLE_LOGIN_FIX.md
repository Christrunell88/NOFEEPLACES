# Apple Login Configuration Update

## Issue
Apple Sign-In is not working on the custom domain `nofeeplaces.com` due to domain change from the preview URL.

## Root Cause
The Apple OAuth redirect URI changed from:
- **Old**: `https://realty-login.preview.emergentagent.com/apple-callback.html`
- **New**: `https://nofeeplaces.com/apple-callback.html`

Apple Developer Console needs to be updated to recognize the new domain's callback URL.

## Solution Steps

### 1. Access Apple Developer Console
Visit: https://developer.apple.com/account

### 2. Navigate to Your App Configuration
Go to: **Certificates, Identifiers & Profiles** → **Identifiers** → Your App ID (`com.nofeeplaces.signin`)

### 3. Update Return URLs
Add or update the **Return URLs** section to include:
```
https://nofeeplaces.com/apple-callback.html
```

**Note:** You can keep the old preview URL if you want to maintain backward compatibility:
```
https://realty-login.preview.emergentagent.com/apple-callback.html
https://nofeeplaces.com/apple-callback.html
```

### 4. Save Changes
Click **Save** to apply the configuration changes.

### 5. Verify Configuration
After updating:
- Wait 5-10 minutes for Apple's changes to propagate
- Test Apple Sign-In on nofeeplaces.com
- Verify successful redirect and authentication

## Technical Details

**App Configuration:**
- Client ID: `com.nofeeplaces.signin`
- Team ID: `2H72887544`
- Key ID: `8R44R5BN6T`
- Callback file: `/app/frontend/public/apple-callback.html`

**Code Location:**
- Frontend implementation: `/app/frontend/src/SocialAuth.js` (line 18)
- Dynamic redirect URI: `${window.location.origin}/apple-callback.html`

## Testing After Update

Once the Apple Developer Console is updated, test:
1. Visit nofeeplaces.com
2. Click on any "Schedule Showing" button
3. Click "Sign In to Schedule" (for unauthenticated users)
4. Click "Continue with Apple"
5. Verify redirect to Apple authentication
6. Complete sign-in and verify return to the site

## Current Status
- ✅ Schedule Showing feature fully implemented
- ✅ Authentication gate working
- ✅ Google and Facebook Sign-In working
- ❌ Apple Sign-In blocked (needs Apple Developer Console update)
- ✅ Mobile responsive
- ✅ Backend API integration complete

---
**Last Updated:** January 2025
**Priority:** Medium (blocking Apple users from scheduling showings)
