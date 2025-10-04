from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import asyncio

# Load .env variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")


# Async test function
async def test_connection():
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client["PlanMySky"]  # replace with your database name
        collections = await db.list_collection_names()
        print("Connected to MongoDB! Collections:", collections)
    except Exception as e:
        print("Error connecting to MongoDB:", e)

# Run the async function
asyncio.run(test_connection())
