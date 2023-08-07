from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

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

class UserRoom(BaseModel):
    email: EmailStr
 
class UserRoomOut(BaseModel):
    id : int
    name : str
    
    description : str
    class Config:
        orm_mode = True

# class UserInput(BaseModel):
#     weight: float
#     height: float
#     goal: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None