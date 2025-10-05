# Community Hub Implementation

## Overview
The Weather Connect tab has been transformed into a real community hub where users can post weather-related messages and react to posts from other community members. All data is stored in MongoDB.

## Features Implemented

### 1. **Backend API** (`backend/api/community_routes.py`)
- **GET /api/community/messages** - Get community messages with pagination
  - Supports limit, skip, and location filtering
  - Returns messages with reaction counts

- **POST /api/community/messages** - Create a new message
  - Accepts username, location, text, latitude, longitude
  - Stores in MongoDB `community_messages` collection

- **POST /api/community/reactions** - Add/update/remove reactions
  - Reaction types: like (👍), sun (☀️), rain (🌧), wind (💨)
  - Each user can only have one reaction per message
  - Toggle on/off by clicking same reaction again

- **GET /api/community/stats** - Get community statistics
  - Total messages count
  - Recent messages (last 24 hours)
  - Top locations by message count
  - Total reactions count

- **DELETE /api/community/messages/{message_id}** - Delete a message
  - Only creator can delete their own posts

### 2. **Frontend Components**

#### **MiniPosts Component** (`frontend/src/components/MiniPosts.jsx`)
- Displays community messages in chronological order
- **New Post Form** - Create new messages with:
  - Username (saved to localStorage for convenience)
  - Location
  - Message text (max 500 characters)

- **Real-time Reactions** - Click emoji buttons to react
  - Reactions update immediately in database
  - Visual feedback with reaction counts

- **Delete Posts** - Users can delete their own posts
  - Shows delete button only for posts you created

- **Smart Timestamps** - Shows relative time (e.g., "2h ago", "Just now")

- **View More/Less** - Pagination to show 3 posts at a time

#### **LocalTrends Component** (`frontend/src/components/LocalTrends.jsx`)
- **Real-time Statistics Dashboard**:
  - Total messages
  - Messages in last 24 hours
  - Total reactions
  - Active locations count

- **Top Locations Chart** - Interactive pie chart showing message distribution by location

- **Location Breakdown** - List of locations with message counts

- **Auto-refresh** - Stats update every 30 seconds

### 3. **API Service** (`frontend/src/services/communityApi.js`)
Centralized API client for all community endpoints:
- `getMessages(limit, skip, locationFilter)`
- `createMessage(messageData)`
- `updateReaction(messageId, reactionType, userIdentifier)`
- `getMessage(messageId)`
- `deleteMessage(messageId, userIdentifier)`
- `getCommunityStats()`

## Database Schema

### MongoDB Collections

#### **community_messages**
```javascript
{
  _id: ObjectId,
  username: String,
  location: String,
  text: String,
  latitude: Float (optional),
  longitude: Float (optional),
  timestamp: ISODate
}
```

#### **message_reactions**
```javascript
{
  _id: ObjectId,
  message_id: String,
  user_identifier: String,
  reaction_type: String, // "like", "sun", "rain", "wind"
  timestamp: ISODate
}
```

## User Experience

### Posting Messages
1. Click "+ New Post" button
2. Enter username and location (auto-filled from localStorage if previously used)
3. Type your weather experience
4. Click "Post Message"
5. Message appears immediately in the feed

### Reacting to Messages
1. Click any emoji reaction button on a message
2. Reaction count updates immediately
3. Click same emoji again to remove your reaction
4. Each user can only have one reaction per message

### Viewing Community Activity
1. Navigate to "Weather Connect" tab
2. Scroll through community messages
3. View real-time stats in the bottom section
4. See top active locations in pie chart

## Testing Results

✅ **Backend API Tests:**
- Message creation: SUCCESS
- Message retrieval: SUCCESS
- Reaction addition: SUCCESS
- Reaction counting: SUCCESS
- Community stats: SUCCESS

✅ **Sample Test Data:**
- Created test message from "TestUser" in "Kathmandu, Nepal"
- Added sun reaction (☀️)
- Stats showing: 1 message, 1 reaction, 1 location

## Environment Setup

### Backend Requirements
- MongoDB connection configured in `.env`
- `MONGO_URI` environment variable set
- Motor (async MongoDB driver) installed

### Frontend Configuration
- `VITE_API_URL` should point to backend (default: http://localhost:8000)
- No authentication required (uses localStorage for user tracking)

## Future Enhancements
- Image uploads for weather photos
- Location-based filtering
- Trending topics/hashtags
- Real-time WebSocket updates
- User profiles and avatars
- Moderation tools
- Weather alert notifications

## How to Use

1. **Start Backend:**
   ```bash
   cd backend/api
   python weather_api.py
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access Community Hub:**
   - Open PlanMySky application
   - Click on "Weather Connect" tab
   - Start posting and reacting!

## API Documentation
Full API documentation available at: http://localhost:8000/docs
