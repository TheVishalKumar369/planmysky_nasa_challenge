from fastapi import APIRouter, HTTPException
from models import UserSignup, UserLogin
from auth_utils import hash_password, verify_password, create_token
from database import users_collection
from email_validator import validate_email, EmailNotValidError

auth_router = APIRouter()


@auth_router.post("/signup")
async def signup(user: UserSignup):
    """
    Register a new user and return an access token

    Validates the provided email and password, checks for existing users,
    and creates a new user account. Returns a JWT token upon successful registration.

    **Parameters:**
    - user: UserSignup object containing `email` and `password`

    **Returns:**
    - `token`: JWT token string for authentication
    - `message`: Confirmation message indicating successful signup

    **Raises:**
    - HTTPException 400 if the email is invalid
    - HTTPException 400 if the email is already registered

    **Example Request:**
    ```
    {
    "email": "user@example.com";
    password: "yourpassword"
    }
    ```
    """
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
    """
    Authenticate a user and return an access token

    Validates the provided email and password against the stored credentials.
    If authentication is successful, returns a JWT token to be used for authorized requests.

    **Parameters:**
    - user: UserLogin object containing `email` and `password`

    **Returns:**
    - `token`: JWT token string for authentication
    - `message`: Confirmation message indicating successful login

    **Raises:**
    - HTTPException 400 if email does not exist or password is incorrect

    **Example Request:**
    ```
    {
    "email": "user@example.com";
    password: "yourpassword"
    }
    ```
    """
    existing = await users_collection.find_one({"email": user.email})
    if not existing or not verify_password(user.password, existing["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_token({"email": user.email})
    return {"token": token, "message": "Login successful"}
