# Google Calendar Integration Setup Guide

This guide will help you set up Google Calendar integration for PlanMySky.

## Prerequisites

- Google Account
- Access to [Google Cloud Console](https://console.cloud.google.com/)

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `PlanMySky` (or your preferred name)
4. Click "Create"

## Step 2: Enable Google Calendar API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Select "External" user type (or "Internal" if using Google Workspace)
3. Click "Create"

### Fill in the required information:

- **App name**: PlanMySky
- **User support email**: Your email
- **Developer contact email**: Your email
- Click "Save and Continue"

### Scopes (Step 2):

1. Click "Add or Remove Scopes"
2. Filter/search for: `https://www.googleapis.com/auth/calendar.events`
3. Select it and click "Update"
4. Click "Save and Continue"

### Test users (Step 3):

1. Add your Google account email as a test user
2. Click "Save and Continue"

## Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Application type: **Web application**
4. Name: `PlanMySky Web Client`

### Authorized JavaScript origins:

```
http://localhost:3000
```

(Add production domain when deployed)

### Authorized redirect URIs:

```
http://localhost:3000/oauth/callback
```

(Add production callback URL when deployed)

5. Click "Create"
6. **Important**: Copy the Client ID and Client Secret

## Step 5: Configure Backend Environment Variables

1. Navigate to `backend/` directory
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` file and add your credentials:
   ```env
   GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   GOOGLE_REDIRECT_URI=http://localhost:3000/oauth/callback
   ```

4. **IMPORTANT**: Never commit `.env` file to version control!

## Step 6: Install Required Python Packages

```bash
cd backend
pip install httpx python-dotenv
```

## Step 7: Test the Integration

1. Start the backend server:
   ```bash
   cd backend/api
   python weather_api.py
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm start
   ```

3. Open http://localhost:3000
4. Click on a location on the map
5. In the Weather Prediction tab, click "Add to Google Calendar"
6. Authorize the app when prompted
7. Check your Google Calendar for the new event!

## Security Best Practices

### Development

- Keep `.env` file in `.gitignore`
- Never share your Client Secret
- Only add trusted email addresses as test users

### Production

1. **Update redirect URIs** in Google Cloud Console:
   - Add: `https://yourdomain.com/oauth/callback`
   - Remove or keep localhost for local testing

2. **Environment Variables**:
   ```env
   GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_production_secret
   GOOGLE_REDIRECT_URI=https://yourdomain.com/oauth/callback
   ```

3. **Publish OAuth Consent Screen**:
   - Go to OAuth consent screen
   - Click "Publish App"
   - This removes the test user limitation

4. **Secure Token Storage**:
   - Current implementation uses file storage
   - For production, use encrypted database (PostgreSQL, MongoDB)
   - Consider using services like AWS Secrets Manager or Google Secret Manager

## API Endpoints

### Check Auth Status
```http
GET /api/calendar/auth/status?user_id={user_id}
```

### Initiate OAuth Flow
```http
GET /api/calendar/auth/initiate?user_id={user_id}
```

### OAuth Callback (handled automatically)
```http
GET /api/calendar/auth/callback?code={code}&state={user_id}
```

### Create Calendar Event
```http
POST /api/calendar/create-event
Content-Type: application/json

{
  "user_id": "user_123",
  "location_name": "Kathmandu, Nepal",
  "location_coords": {"lat": 27.7172, "lng": 85.3240},
  "date": "2024-07-15",
  "weather_data": { ... }
}
```

### Revoke Access
```http
DELETE /api/calendar/auth/revoke?user_id={user_id}
```

## Token Storage

Tokens are stored in `data/tokens/user_{user_id}_tokens.json`:

```json
{
  "access_token": "ya29.a0...",
  "refresh_token": "1//0g...",
  "expires_in": 3599,
  "scope": "https://www.googleapis.com/auth/calendar.events",
  "token_type": "Bearer",
  "saved_at": "2024-10-04T12:00:00"
}
```

**Important**: Add `data/tokens/` to `.gitignore`!

## Troubleshooting

### "Redirect URI mismatch" error
- Check that the redirect URI in your code matches exactly what's in Google Cloud Console
- Include the protocol (http:// or https://)
- No trailing slashes

### "Access blocked: This app's request is invalid"
- Make sure you've added your email as a test user
- Check that Calendar API is enabled
- Verify OAuth consent screen is configured

### "Invalid grant" error when refreshing token
- Refresh token may have expired (they can expire if unused for 6 months)
- User revoked access
- Re-authorize the app

### Calendar event not appearing
- Check the backend logs for errors
- Verify the date format is correct (ISO 8601)
- Check that the user's timezone is set correctly

## Need Help?

- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [PlanMySky GitHub Issues](https://github.com/TheVishalkumar369/PlanMySky/issues)
