from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from fastapi import UploadFile
from fastapi import Form, File

class UserCreate(BaseModel):
    email: EmailStr
    password : str
    confirm_password: str
    

class UserOut(BaseModel):
    id : int
    email : EmailStr
    created_at : datetime
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email : EmailStr
    password : str

class ActivityProviderCreate(BaseModel):
    business_name: str
    contact_email: EmailStr
    password: str
    confirm_password: str

class ProviderOut(BaseModel):
    id : int
    contact_email : EmailStr
    created_at : datetime
    class Config:
        orm_mode = True

class ActivityBase(BaseModel):
    name: str
    description: str
    location: str
    price: float

class ActivityCreateWithImageURL(ActivityBase):
    image_url: str

class ActivityCreate(ActivityBase):
    pass

class UploadResponse(BaseModel):
    url: str

class Activity(BaseModel):
    id: int
    name: str
    description: str
    location: str
    price: float
    image_url: str
    

    # Add more fields as needed

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
    type: str

