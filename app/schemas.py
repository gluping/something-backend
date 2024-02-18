from pydantic import BaseModel, EmailStr
from datetime import datetime,time as Time, date
from typing import Dict, Optional, Union

from fastapi import UploadFile
from fastapi import Form, File
from typing import List

class UserCreate(BaseModel):
    email: EmailStr
    password : str
    confirm_password: str
    

class UserOut(BaseModel):
    id : int
    email : EmailStr
    created_at : datetime
    class Config:
        from_attributes = True

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
        from_attributes = True

class ActivityBase(BaseModel):
    name: str
    description: str
    location: str
    price: float

class ActivityCreateWithImageURL(ActivityBase):
    image_url: List[str]

class ActivityCreate(ActivityBase):
    pass

class UploadResponse(BaseModel):
    url: List[str]

class TimeSlot(BaseModel):
    id: int
    start_time: Time
    end_time: Time
    is_available: bool
    max_capacity:int

class TimeSlotProvider(BaseModel):
    start_time: Time
    end_time: Time
    
class Activity(BaseModel):
    id: int
    provider_id: int
    name: str
    description: str
    location: str
    price: float
    image_url: str
    time_slots: List[TimeSlot]
    likes: int

class ActivityProviderOut(BaseModel):
    id: int
    name: str
    description: str
    location: str
    price: float
    image_url: str
    time_slots: List[TimeSlotProvider]
    likes: int 

class TimeSlotBase(BaseModel):
    start_time: Time
    end_time: Time
    max_capacity: int

class Booking(BaseModel):
    activity_id: int
    slot_id: int
    booking_date: date

class ActivityCreateWithImageURLAndTimeSlots(ActivityCreateWithImageURL):
    time_slots: List[TimeSlotBase]


    

    # Add more fields as needed

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int
class ProviderWithActivitiesOut(ProviderOut):
    activities: List[Activity]

class BookingOut(BaseModel):
    booking_id: int
    activity_id: int
    user_email: EmailStr
    booking_date: datetime
    activity_details: ActivityProviderOut
    is_completed: bool
class ActivityResponse(BaseModel):
    id: int
    provider_name: str
    name: str
    description: str
    price: float
    location: str
    image: str
    time_slots: List[Dict[str, Union[int, str, bool]]]