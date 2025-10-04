#!/usr/bin/env python3
"""
Google Calendar Integration for PlanMySky
Handles OAuth 2.0 authentication and calendar event creation
"""

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import httpx

# Load environment variables
try:
    from dotenv import load_dotenv
    # Load from backend directory
    backend_dir = Path(__file__).parent.parent
    env_path = backend_dir / '.env'
    load_dotenv(env_path)
    print(f"Loading .env from: {env_path}")
except ImportError:
    print("python-dotenv not installed, using system environment variables")

router = APIRouter(prefix="/api/calendar", tags=["Google Calendar"])

# Google OAuth 2.0 Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/oauth/callback")

# Debug print
print(f"Google OAuth Config:")
print(f"  CLIENT_ID: {GOOGLE_CLIENT_ID[:20]}..." if GOOGLE_CLIENT_ID else "  CLIENT_ID: NOT SET")
print(f"  CLIENT_SECRET: {'SET' if GOOGLE_CLIENT_SECRET else 'NOT SET'}")
print(f"  REDIRECT_URI: {GOOGLE_REDIRECT_URI}")

# OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

# Scopes
CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar.events"

# Token storage (in production, use a proper database)
TOKEN_STORAGE_DIR = Path(__file__).parent.parent.parent / "data" / "tokens"
TOKEN_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


class CalendarEventRequest(BaseModel):
    """Request model for creating calendar event"""
    location_name: str
    location_coords: dict  # {lat, lng}
    date: str
    weather_data: dict  # Weather prediction data
    user_id: str  # Unique user identifier


def get_token_file(user_id: str) -> Path:
    """Get token file path for a user"""
    return TOKEN_STORAGE_DIR / f"user_{user_id}_tokens.json"


def save_tokens(user_id: str, tokens: dict):
    """Save OAuth tokens for a user"""
    token_file = get_token_file(user_id)
    with open(token_file, 'w') as f:
        json.dump({
            **tokens,
            'saved_at': datetime.now().isoformat()
        }, f, indent=2)
    print(f"✓ Saved tokens for user {user_id}")


def load_tokens(user_id: str) -> Optional[dict]:
    """Load OAuth tokens for a user"""
    token_file = get_token_file(user_id)
    if not token_file.exists():
        return None

    with open(token_file, 'r') as f:
        return json.load(f)


async def refresh_access_token(user_id: str) -> Optional[str]:
    """Refresh access token using refresh token"""
    tokens = load_tokens(user_id)
    if not tokens or 'refresh_token' not in tokens:
        return None

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'refresh_token': tokens['refresh_token'],
                'grant_type': 'refresh_token'
            }
        )

    if response.status_code == 200:
        new_tokens = response.json()
        # Keep the refresh token from original tokens
        new_tokens['refresh_token'] = tokens['refresh_token']
        save_tokens(user_id, new_tokens)
        return new_tokens['access_token']

    return None


@router.get("/auth/initiate")
async def initiate_oauth(user_id: str = Query(..., description="Unique user identifier")):
    """
    Initiate Google OAuth flow

    Redirects user to Google consent screen
    """
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
        )

    # Build OAuth URL
    auth_url = (
        f"{GOOGLE_AUTH_URL}?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope={CALENDAR_SCOPE}&"
        f"access_type=offline&"
        f"prompt=consent&"
        f"state={user_id}"  # Pass user_id as state
    )

    return {
        "auth_url": auth_url,
        "message": "Redirect user to this URL for authentication"
    }


@router.get("/auth/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code"),
    state: str = Query(..., description="User ID passed as state")
):
    """
    Handle OAuth callback from Google

    Exchange authorization code for tokens
    """
    user_id = state

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'code': code,
                'redirect_uri': GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange code for tokens: {response.text}"
        )

    tokens = response.json()
    save_tokens(user_id, tokens)

    # Return success response (will be handled by frontend callback page)
    return {
        "success": True,
        "message": "Authorization successful",
        "user_id": user_id
    }


@router.post("/create-event")
async def create_calendar_event(request: CalendarEventRequest):
    """
    Create a calendar event with weather prediction
    """
    user_id = request.user_id

    # Load tokens
    tokens = load_tokens(user_id)
    if not tokens:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated. Please authorize Google Calendar access first."
        )

    access_token = tokens.get('access_token')

    # Try to create event, refresh token if needed
    event_created = False
    for attempt in range(2):
        try:
            # Prepare event data
            event_data = create_event_data(request)

            # Create event via Google Calendar API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    GOOGLE_CALENDAR_API,
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    },
                    json=event_data,
                    timeout=10.0
                )

            if response.status_code == 200 or response.status_code == 201:
                event_created = True
                event_result = response.json()
                return {
                    "success": True,
                    "message": "Event created successfully",
                    "event_id": event_result.get('id'),
                    "event_link": event_result.get('htmlLink')
                }
            elif response.status_code == 401 and attempt == 0:
                # Token expired, try to refresh
                print("Access token expired, refreshing...")
                access_token = await refresh_access_token(user_id)
                if not access_token:
                    raise HTTPException(
                        status_code=401,
                        detail="Failed to refresh access token. Please re-authorize."
                    )
                continue
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to create event: {response.text}"
                )

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Request to Google Calendar API timed out"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating calendar event: {str(e)}"
            )

    if not event_created:
        raise HTTPException(
            status_code=500,
            detail="Failed to create calendar event after retries"
        )


def create_event_data(request: CalendarEventRequest) -> dict:
    """
    Create Google Calendar event data from weather prediction
    """
    weather = request.weather_data

    # Parse date
    try:
        event_date = datetime.fromisoformat(request.date.replace('Z', '+00:00'))
    except:
        event_date = datetime.strptime(request.date, '%Y-%m-%d')

    # Set event time (8 AM to 9 PM for all-day weather)
    start_time = event_date.replace(hour=8, minute=0, second=0)
    end_time = event_date.replace(hour=21, minute=0, second=0)

    # Build description
    description = build_event_description(weather, request.location_name)

    # Create event
    event = {
        "summary": f"Weather Prediction: {request.location_name}",
        "description": description,
        "location": f"{request.location_coords.get('lat')}, {request.location_coords.get('lng')}",
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "UTC"
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 60}
            ]
        }
    }

    return event


def build_event_description(weather: dict, location: str) -> str:
    """Build formatted event description from weather data"""

    description_parts = [
        f"Weather Prediction for {location}",
        "",
        "🌡️ Temperature:",
    ]

    # Temperature
    if 'temperature' in weather:
        temp = weather['temperature']
        if 'expected_range' in temp:
            description_parts.append(
                f"  Range: {temp['expected_range'].get('min')}°C - {temp['expected_range'].get('max')}°C"
            )
        if 'mean_avg_celsius' in temp:
            description_parts.append(f"  Average: {temp['mean_avg_celsius']}°C")

    # Rainfall
    if 'rainfall' in weather:
        rain = weather['rainfall']
        description_parts.append("")
        description_parts.append("☔ Rainfall:")
        if 'probability_percent' in rain:
            description_parts.append(f"  Probability: {rain['probability_percent']}%")
        if 'expected_amount_mm' in rain:
            description_parts.append(f"  Expected: {rain['expected_amount_mm']} mm")

    # Wind
    if 'wind' in weather:
        wind = weather['wind']
        description_parts.append("")
        description_parts.append("💨 Wind:")
        if 'mean_speed_ms' in wind:
            description_parts.append(f"  Speed: {wind['mean_speed_ms']} m/s")

    # Cloud Cover
    if 'cloud_cover' in weather:
        cloud = weather['cloud_cover']
        description_parts.append("")
        description_parts.append("☁️ Cloud Cover:")
        if 'mean_percent' in cloud:
            description_parts.append(f"  Coverage: {cloud['mean_percent']}%")

    # Weather Category
    if 'weather_category' in weather:
        description_parts.append("")
        description_parts.append(f"📊 Category: {weather['weather_category']}")

    # Confidence
    if 'category_confidence' in weather:
        confidence = weather['category_confidence'] * 100
        description_parts.append(f"🎯 Confidence: {confidence:.0f}%")

    description_parts.append("")
    description_parts.append("---")
    description_parts.append("Generated by PlanMySky - NASA Space Apps Challenge")

    return "\n".join(description_parts)


@router.get("/auth/status")
async def check_auth_status(user_id: str = Query(..., description="User ID")):
    """
    Check if user is authenticated with Google Calendar
    """
    tokens = load_tokens(user_id)

    if not tokens:
        return {
            "authenticated": False,
            "message": "User not authenticated"
        }

    return {
        "authenticated": True,
        "message": "User authenticated",
        "expires_at": tokens.get('expires_in')
    }


@router.get("/config/test")
async def test_config():
    """
    Test endpoint to verify OAuth configuration
    """
    return {
        "status": "ok",
        "config": {
            "client_id_set": bool(GOOGLE_CLIENT_ID),
            "client_id_prefix": GOOGLE_CLIENT_ID[:20] + "..." if GOOGLE_CLIENT_ID else "NOT SET",
            "client_secret_set": bool(GOOGLE_CLIENT_SECRET),
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "expected_redirect_format": "http://localhost:3000/oauth-callback.html"
        },
        "note": "Make sure redirect_uri matches expected_redirect_format and is added to Google Cloud Console"
    }


@router.delete("/auth/revoke")
async def revoke_auth(user_id: str = Query(..., description="User ID")):
    """
    Revoke Google Calendar access (delete stored tokens)
    """
    token_file = get_token_file(user_id)

    if token_file.exists():
        token_file.unlink()
        return {
            "success": True,
            "message": "Authorization revoked successfully"
        }

    return {
        "success": False,
        "message": "No authorization found for this user"
    }
