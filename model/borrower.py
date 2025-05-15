from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class BorrowerModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    dob: str
    address: str
    country: str
    state: str
    pincode: str
    phone: str
    city : str

class FilterBorrowerModel(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
