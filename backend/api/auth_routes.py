from fastapi import APIRouter, HTTPException
from models import UserSignup, UserLogin
from auth_utils import hash_password, verify_password, create_token
from database import users_collection
from email_validator import validate_email, EmailNotValidError

auth_router = APIRouter()


@auth_router.post("/signup")
async def signup(user: UserSignup):
    # Validate email
    try:
        valid = validate_email(user.email)
        email = valid.email
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email address")

    # Check if already exists
    existing = await users_collection.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and insert
    hashed_pw = hash_password(user.password)
    new_user = {"email": email, "password_hash": hashed_pw}
    await users_collection.insert_one(new_user)

    # Generate JWT
    token = create_token({"email": email})
    return {"token": token, "message": "Signup successful"}


@auth_router.post("/login")
async def login(user: UserLogin):
    existing = await users_collection.find_one({"email": user.email})
    if not existing or not verify_password(user.password, existing["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_token({"email": user.email})
    return {"token": token, "message": "Login successful"}
