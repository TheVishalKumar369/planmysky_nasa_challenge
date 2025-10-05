"""
Community Hub Routes - Community messaging and reactions
Allows users to post weather-related messages and react to them
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId
from database import db

community_router = APIRouter(prefix="/api/community", tags=["Community"])

# MongoDB collections
messages_collection = db["community_messages"]
reactions_collection = db["message_reactions"]


# ============================================================
# MODELS
# ============================================================

class MessageCreate(BaseModel):
    """Model for creating a new community message"""
    username: str = Field(..., min_length=1, max_length=50, description="Username of the poster")
    location: str = Field(..., min_length=1, max_length=100, description="Location of the user")
    text: str = Field(..., min_length=1, max_length=500, description="Message content")
    latitude: Optional[float] = Field(None, description="Latitude of user location")
    longitude: Optional[float] = Field(None, description="Longitude of user location")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "JohnDoe",
                "location": "Kathmandu, Nepal",
                "text": "Beautiful sunny day here! Perfect for outdoor activities.",
                "latitude": 27.7172,
                "longitude": 85.3240
            }
        }


class ReactionUpdate(BaseModel):
    """Model for updating reactions on a message"""
    message_id: str = Field(..., description="ID of the message to react to")
    reaction_type: str = Field(..., description="Type of reaction: like, sun, rain, wind")
    user_identifier: str = Field(..., description="Unique identifier for the user (username or session ID)")

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "507f1f77bcf86cd799439011",
                "reaction_type": "like",
                "user_identifier": "user123"
            }
        }


class MessageResponse(BaseModel):
    """Response model for a message"""
    id: str
    username: str
    location: str
    text: str
    timestamp: str
    latitude: Optional[float]
    longitude: Optional[float]
    reactions: Dict[str, int]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def serialize_message(message: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict"""
    message["id"] = str(message["_id"])
    del message["_id"]
    return message


async def get_message_reactions(message_id: str) -> Dict[str, int]:
    """Get aggregated reaction counts for a message"""
    reactions = {"like": 0, "sun": 0, "rain": 0, "wind": 0}

    cursor = reactions_collection.find({"message_id": message_id})
    async for reaction in cursor:
        reaction_type = reaction.get("reaction_type")
        if reaction_type in reactions:
            reactions[reaction_type] += 1

    return reactions


# ============================================================
# ENDPOINTS
# ============================================================

@community_router.get("/messages", response_model=List[MessageResponse])
async def get_messages(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of messages to return"),
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    location_filter: Optional[str] = Query(None, description="Filter by location")
):
    """
    Get community messages with pagination

    Returns a list of community messages sorted by most recent first.
    Optionally filter by location.

    **Parameters:**
    - **limit**: Maximum messages to return (default: 20, max: 100)
    - **skip**: Number of messages to skip for pagination (default: 0)
    - **location_filter**: Optional location filter

    **Example:**
    ```
    GET /api/community/messages?limit=10&skip=0
    GET /api/community/messages?location_filter=Kathmandu
    ```
    """
    try:
        # Build query
        query = {}
        if location_filter:
            query["location"] = {"$regex": location_filter, "$options": "i"}

        # Get messages with pagination
        cursor = messages_collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)

        messages = []
        async for message in cursor:
            # Get reactions for this message
            reactions = await get_message_reactions(str(message["_id"]))

            message_data = serialize_message(message)
            message_data["reactions"] = reactions
            messages.append(message_data)

        return messages

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching messages: {str(e)}")


@community_router.post("/messages", status_code=201)
async def create_message(message: MessageCreate):
    """
    Create a new community message

    Posts a new message to the community hub.

    **Request Body:**
    ```json
    {
      "username": "JohnDoe",
      "location": "Kathmandu, Nepal",
      "text": "Beautiful sunny day here!",
      "latitude": 27.7172,
      "longitude": 85.3240
    }
    ```

    **Returns:**
    - Message ID and creation timestamp
    """
    try:
        # Create message document
        message_doc = {
            "username": message.username,
            "location": message.location,
            "text": message.text,
            "latitude": message.latitude,
            "longitude": message.longitude,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Insert into database
        result = await messages_collection.insert_one(message_doc)

        return {
            "message": "Message posted successfully",
            "id": str(result.inserted_id),
            "timestamp": message_doc["timestamp"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating message: {str(e)}")


@community_router.post("/reactions")
async def update_reaction(reaction: ReactionUpdate):
    """
    Add or update a reaction to a message

    Users can react to messages with different emoji reactions.
    Each user can only have one reaction per message (updating replaces previous).

    **Valid reaction types:** like, sun, rain, wind

    **Request Body:**
    ```json
    {
      "message_id": "507f1f77bcf86cd799439011",
      "reaction_type": "like",
      "user_identifier": "user123"
    }
    ```
    """
    try:
        # Validate reaction type
        valid_reactions = ["like", "sun", "rain", "wind"]
        if reaction.reaction_type not in valid_reactions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid reaction type. Must be one of: {', '.join(valid_reactions)}"
            )

        # Validate message exists
        try:
            message_id_obj = ObjectId(reaction.message_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid message ID format")

        message = await messages_collection.find_one({"_id": message_id_obj})
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        # Check if user already reacted to this message
        existing_reaction = await reactions_collection.find_one({
            "message_id": reaction.message_id,
            "user_identifier": reaction.user_identifier
        })

        if existing_reaction:
            # Update existing reaction
            if existing_reaction["reaction_type"] == reaction.reaction_type:
                # Same reaction - remove it (toggle off)
                await reactions_collection.delete_one({"_id": existing_reaction["_id"]})
                return {"message": "Reaction removed", "action": "removed"}
            else:
                # Different reaction - update it
                await reactions_collection.update_one(
                    {"_id": existing_reaction["_id"]},
                    {"$set": {"reaction_type": reaction.reaction_type}}
                )
                return {"message": "Reaction updated", "action": "updated"}
        else:
            # Create new reaction
            reaction_doc = {
                "message_id": reaction.message_id,
                "user_identifier": reaction.user_identifier,
                "reaction_type": reaction.reaction_type,
                "timestamp": datetime.utcnow().isoformat()
            }

            await reactions_collection.insert_one(reaction_doc)
            return {"message": "Reaction added", "action": "added"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating reaction: {str(e)}")


@community_router.get("/messages/{message_id}")
async def get_message(message_id: str):
    """
    Get a specific message by ID

    **Parameters:**
    - **message_id**: MongoDB ObjectId of the message

    **Example:**
    ```
    GET /api/community/messages/507f1f77bcf86cd799439011
    ```
    """
    try:
        # Validate and convert message ID
        try:
            message_id_obj = ObjectId(message_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid message ID format")

        # Find message
        message = await messages_collection.find_one({"_id": message_id_obj})

        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        # Get reactions
        reactions = await get_message_reactions(message_id)

        message_data = serialize_message(message)
        message_data["reactions"] = reactions

        return message_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching message: {str(e)}")


@community_router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    user_identifier: str = Query(..., description="Username or session ID of the message creator")
):
    """
    Delete a message (only creator can delete)

    **Parameters:**
    - **message_id**: MongoDB ObjectId of the message
    - **user_identifier**: Username or session ID (must match creator)

    **Example:**
    ```
    DELETE /api/community/messages/507f1f77bcf86cd799439011?user_identifier=JohnDoe
    ```
    """
    try:
        # Validate and convert message ID
        try:
            message_id_obj = ObjectId(message_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid message ID format")

        # Find message
        message = await messages_collection.find_one({"_id": message_id_obj})

        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        # Verify ownership (basic check - in production use proper auth)
        if message.get("username") != user_identifier:
            raise HTTPException(status_code=403, detail="Only the message creator can delete it")

        # Delete message
        await messages_collection.delete_one({"_id": message_id_obj})

        # Delete associated reactions
        await reactions_collection.delete_many({"message_id": message_id})

        return {"message": "Message deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting message: {str(e)}")


@community_router.get("/stats")
async def get_community_stats():
    """
    Get overall community statistics

    Returns aggregated statistics about community activity.

    **Returns:**
    - Total messages count
    - Recent activity count (last 24 hours)
    - Top locations
    - Total reactions

    **Example:**
    ```
    GET /api/community/stats
    ```
    """
    try:
        # Total messages
        total_messages = await messages_collection.count_documents({})

        # Recent messages (last 24 hours)
        from datetime import timedelta
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
        recent_messages = await messages_collection.count_documents({
            "timestamp": {"$gte": yesterday}
        })

        # Top locations (aggregate)
        pipeline = [
            {"$group": {"_id": "$location", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_locations = []
        async for location in messages_collection.aggregate(pipeline):
            top_locations.append({
                "location": location["_id"],
                "count": location["count"]
            })

        # Total reactions
        total_reactions = await reactions_collection.count_documents({})

        return {
            "total_messages": total_messages,
            "recent_messages_24h": recent_messages,
            "top_locations": top_locations,
            "total_reactions": total_reactions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")
