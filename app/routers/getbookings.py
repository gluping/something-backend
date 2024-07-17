from fastapi import status, HTTPException,Depends, APIRouter
from sqlalchemy.orm import Session
import models, schemas, utils
from database import get_db
from typing import List
from oauth2 import get_current_user

router = APIRouter(
    prefix="/user",
    tags=['Booking']
)

@router.get("/booking", response_model=List[schemas.BookingOut])
def get_user_bookings(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    print(current_user.id)
    provider_bookings = db.query(models.Activity).join(models.Booking, models.Booking.activity_id==models.Activity.id)\
        .filter(models.Booking.user_id == current_user.id).all()
    booking_details = [
        schemas.BookingOutUser(
            booking_id=booking.id,
            activity_id=booking.activity_id,
            provider_id=booking.activity.provider_id,
            user_id=booking.user_id,
            activity_details=schemas.ActivityProviderOut(
                id=booking.activity.id,
                name=booking.activity.name,
                description=booking.activity.description,
                location=booking.activity.location,
                price=booking.activity.price,
                image_url=booking.activity.image_url,
                likes = booking.activity.likes,
                time_slots=[
                    {
                        "start_time": time_slot.start_time,
                        "end_time": time_slot.end_time,
                    
                    }
                    for time_slot in booking.activity.time_slots
                ]
            ),
            booking_date=booking.booking_date,
            is_completed=booking.is_completed
        )
        for booking in provider_bookings
    ]

    return booking_details