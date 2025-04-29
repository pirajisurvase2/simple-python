from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class SignUpModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str
    confirm_password: str

class SignInModel(BaseModel):
    email: EmailStr
    password: str

class UpdateProfileModel(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
