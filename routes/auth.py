from fastapi import APIRouter, Depends
from model.auth import SignUpModel, SignInModel,UpdateProfileModel
from services.auth import get_current_user, signup_service, signin_service, update_user_profile

router = APIRouter(tags=["Auth"])

@router.post("/signup")
async def signup(user: SignUpModel):
    return await signup_service(user)

@router.post("/signin")
async def signin(credentials: SignInModel):
    return await signin_service(credentials)

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return current_user

@router.put("/profile")
async def update_profile(
    profile_data: UpdateProfileModel,
    current_user: dict = Depends(get_current_user)
):
    
    # Filter out None values from the profile data before passing it to the service
    update_fields = {k: v for k, v in profile_data.dict(exclude_unset=True).items() if v is not None}

    # Delegate the update logic to the service
    updated_user = await update_user_profile(current_user["email"], update_fields)

    return updated_user