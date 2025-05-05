from fastapi import Header,status, HTTPException
from jose import JWTError, jwt
from typing import Optional
from config import SECRET_KEY, ALGORITHM
from database import users_collection
from model.auth import SignUpModel, SignInModel
from utils.auth import hash_password, verify_password, create_token
from utils.comman import custom_response
from pymongo.collection import ReturnDocument



async def signup_service(user: SignUpModel):
    if user.password != user.confirm_password:
        return custom_response(400, "Passwords do not match")

    if await users_collection.find_one({"email": user.email}):
        return custom_response(400,"User already exists")

    user_data = user.dict()
    user_data["password"] = hash_password(user.password)
    del user_data["confirm_password"]

    await users_collection.insert_one(user_data)
    return custom_response(201, "User created successfully")

async def signin_service(credentials: SignInModel):
    user = await users_collection.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        return custom_response(401, "Invalid credentials")

    token = create_token({"email": credentials.email})
    return custom_response(200, "Sign in successfully", {"token" : token})

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Authorization header"
        )

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload invalid"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token"
        )

    user = await users_collection.find_one({"email": email}, {"password": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user["_id"] = str(user["_id"])
    return user


async def update_user_profile(
    email: str, 
    update_fields: dict[str, str]
) -> dict:
    
    if not update_fields:
        raise custom_response(
            status.HTTP_400_BAD_REQUEST,
            "No fields provided for update"
        )

    # Perform the update operation
    updated_user = await users_collection.find_one_and_update(
        {"email": email},
        {"$set": update_fields},
        return_document=ReturnDocument.AFTER,
        projection={"password": 0}  # Exclude password from the response
    )

    if not updated_user:
        raise custom_response(
            status.HTTP_404_NOT_FOUND,
            "User not found"
        )

    updated_user["_id"] = str(updated_user["_id"])  # Convert _id to string for easier use
    return updated_user