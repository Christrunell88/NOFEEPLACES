# NoFeePlaces.com - Admin System Guide

## 🔐 Admin Access

**Login URL:** https://rentauth-test.preview.emergentagent.com/admin

**Admin Credentials:**
- Email: `placesfirm@gmail.com`
- Password: `Checkers080/?`

⚠️ **Security Note:** Your credentials are securely stored in the backend `.env` file and are NOT visible in the frontend code. All admin activities are logged.

---

## 📊 Dashboard Overview

After logging in, you'll see the main admin dashboard with 5 tabs:

### 1. Overview Tab (Default)

Displays key metrics at a glance:

- **Total Apartments**: Current count of all apartment listings
- **Available Apartments**: Number of apartments currently available
- **Registered Users**: Total users who signed up
- **Total Visitors**: Website visitor count
- **Feedback Submissions**: User feedback count
- **Newsletter Subscribers**: Email list size
- **Average Price**: Average apartment rental price with min/max range

**Recent Activity:**
- Last 5 registered users
- Last 5 feedback submissions

---

### 2. Apartments Tab

**Manage all apartment listings:**

**View:**
- Title, Location (neighborhood + borough)
- Price, Bedrooms, Availability status
- Partial apartment ID

**Actions:**
- **View**: Opens apartment detail page in new tab
- **Delete**: Removes apartment from database (requires confirmation)
- **Refresh**: Reload apartment list with latest data

**Current Status:** 10 apartments listed (all available)

---

### 3. Users Tab

**View all registered users:**

**Information Displayed:**
- Email address
- Full name
- Authentication provider (Google, Manual, etc.)
- Join date
- Account status (Active/Inactive)

**Current Status:** 13 registered users

---

### 4. Feedback Tab

**Review user feedback submissions:**

**Information Displayed:**
- Feedback type (bug, feature, improvement, compliment)
- Priority level (high, medium, low)
- Title and description
- User email
- Page/URL where feedback was submitted
- Timestamp

**Current Status:** 41 feedback submissions

---

### 5. Newsletter Tab

**Manage newsletter subscribers:**

**Information Displayed:**
- Email address
- Subscriber name
- Source (where they subscribed from)
- Subscription date
- Status (Active/Unsubscribed)

**Current Status:** 18 newsletter subscribers

---

## 🔧 Admin Features

### Authentication
- Secure JWT-based authentication
- 24-hour token expiration
- Automatic logout on token expiry
- All API calls protected with admin token

### Dashboard Controls
- **View Site**: Quick link to main website
- **Logout**: Clear admin session and return to login
- **Refresh Buttons**: Update data in each tab independently

### Data Management
- View full apartment details
- Delete apartments (with confirmation)
- View user registration history
- Access all feedback for review
- Export-ready newsletter subscriber list

---

## 📱 How to Use

### Logging In
1. Go to `/admin` URL
2. Enter your email: `placesfirm@gmail.com`
3. Enter your password: `Checkers080/?`
4. Click "Login to Admin Panel"
5. You'll be redirected to the dashboard

### Managing Apartments
1. Click "Apartments" tab
2. View full list of all apartments
3. Click "View" to see apartment on main site
4. Click "Delete" to remove an apartment (asks for confirmation)
5. Use "Refresh" to reload the latest data

### Checking Users
1. Click "Users" tab
2. See all registered users with their details
3. Track join dates and authentication providers

### Reviewing Feedback
1. Click "Feedback" tab
2. Review all user submissions
3. Filter by type (bug, feature, improvement)
4. Track priority levels

### Managing Newsletter
1. Click "Newsletter" tab
2. View all email subscribers
3. Check subscription dates and status
4. Export list for email campaigns

---

## 🔒 Security Features

- ✅ Credentials stored in backend .env (not in code)
- ✅ JWT token authentication for all API calls
- ✅ Admin-only protected routes
- ✅ 24-hour session timeout
- ✅ All activities logged in backend
- ✅ Automatic logout on unauthorized access

---

## 🛠️ Technical Details

**Backend Endpoints:**
- `POST /api/admin/login` - Admin authentication
- `GET /api/admin/apartments` - List all apartments
- `PUT /api/admin/apartments/{id}` - Update apartment
- `DELETE /api/admin/apartments/{id}` - Delete apartment
- `GET /api/admin/users` - List all users
- `GET /api/admin/analytics` - Dashboard statistics
- `GET /api/admin/feedback` - List feedback
- `GET /api/admin/newsletter` - List subscribers

**Frontend Components:**
- `/admin` - AdminLogin component
- `/admin/dashboard` - AdminDashboard component

**Authentication Flow:**
1. User submits credentials to `/api/admin/login`
2. Backend verifies against .env variables
3. JWT token generated and returned
4. Token stored in localStorage
5. All subsequent requests include token in Authorization header
6. Backend validates token on each admin API call

---

## 📝 Current Stats (as of implementation)

- **Total Apartments:** 10
- **Registered Users:** 13
- **Feedback Submissions:** 41
- **Newsletter Subscribers:** 18
- **Average Rental Price:** $4,413.80
- **Price Range:** $2,500 - $8,995

---

## 💡 Tips

1. **Regular Monitoring**: Check the Overview tab daily for quick insights
2. **User Growth**: Track new user registrations in the Users tab
3. **Feedback Priority**: Focus on "high priority" and "bug" type feedback first
4. **Data Export**: You can view and copy data from any tab for external analysis
5. **Apartment Management**: Use the View button to see how apartments appear to users

---

## 🆘 Troubleshooting

**If you get logged out:**
- Your session expired (24 hours)
- Simply log in again with the same credentials

**If you see "Invalid token" error:**
- Token has expired
- Click Logout and log in again

**If data isn't loading:**
- Click the Refresh button in the specific tab
- Check your internet connection
- Try logging out and back in

---

## 📞 Admin Support

This admin panel was custom-built for NoFeePlaces.com by Emergent AI.

For technical issues or feature requests related to the admin panel, please document them in the feedback system or contact your development team.

---

**Last Updated:** October 13, 2025
**Version:** 1.0
**Platform:** NoFeePlaces.com Admin Dashboard
