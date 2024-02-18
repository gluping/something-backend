from typing import List
from fastapi import status, HTTPException,Depends, APIRouter
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from oauth2 import get_current_provider
import models, schemas, utils
from database import get_db


router = APIRouter(
    prefix="/providers",
    tags=['Activity Providers']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ProviderOut)
def register_provider(provider: schemas.ActivityProviderCreate, db: Session = Depends(get_db)):
    if provider.password != provider.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    
    hashed_password = utils.hash(provider.password)
    provider_dict = provider.dict()
    provider_dict.pop("confirm_password")
    provider_dict["password"] = hashed_password
    
    new_provider = models.ActivityProvider(**provider_dict)
    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)
    
    return new_provider


def activity_to_dict(activity):
    return {
        "id": activity.id,
        "name": activity.name,
        "duration": activity.location,
        "description": activity.description,
        "location": activity.location,
        "price": activity.price,
        "image_url": activity.image_url,
        "time_slots": [
            {
                "id": slot.id,  
                "is_available": slot.is_available,  
                "start_time": slot.start_time,
                "end_time": slot.end_time,
            }
            for slot in activity.time_slots
        ],
        "likes": activity.likes,
        
    }
@router.get("/{provider_id}/activities", response_model=schemas.ProviderWithActivitiesOut)
def get_provider_activities(provider_id: int, db: Session = Depends(get_db)):
    
    provider = (
        db.query(models.ActivityProvider)
        .options(joinedload(models.ActivityProvider.activities))
        .filter(models.ActivityProvider.id == provider_id)
        .first()
    )

    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")

    # Convert SQLAlchemy models to dictionaries
    activities_dict_list = [activity_to_dict(activity) for activity in provider.activities]

    # Use Pydantic model for the response
    response_model = schemas.ProviderWithActivitiesOut(
        id=provider.id,
        contact_email=provider.contact_email,
        created_at=provider.created_at,
        activities=activities_dict_list,
    )

    return response_model

@router.get("/bookings", response_model=List[schemas.BookingOut])
def get_provider_bookings(current_provider: models.ActivityProvider = Depends(get_current_provider), db: Session = Depends(get_db)):
    
    provider_bookings = db.query(models.Booking).join(models.Activity)\
        .filter(models.Activity.provider_id == current_provider.id)\
        .options(joinedload(models.Booking.activity)).all()

    
    booking_details = [
        schemas.BookingOut(
            id=booking.id,
            activity_id=booking.activity_id,
            user_email=booking.user_email,
            booking_time=booking.booking_time,
            activity_details=schemas.ActivityOut(
                id=booking.activity.id,
                name=booking.activity.name,
                description=booking.activity.description,
                location=booking.activity.location,
                price=booking.activity.price,
                image_url=booking.activity.image_url,
                time_slots=[],
            )
        )
        for booking in provider_bookings
    ]

    return booking_details


@router.post("/done/{booking_id}")

def activity_completed(booking_id:int,current_provider: models.ActivityProvider = Depends(get_current_provider),db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if booking.activity.provider_id != current_provider.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the provider of this activity")
    booking.is_completed = True
    return ("Succesfully marked the activity as completed")
    db.commit()
    db.refresh(booking)
    db