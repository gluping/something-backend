from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import ActivityResponse
from database import get_db
from models import Activity


router = APIRouter(
    prefix="/listactivity",
    tags=['Activity List']
)

@router.get("/activities/")
def get_activities(db: Session = Depends(get_db)):
    activities = db.query(Activity).all()
    activity_list = []

    for activity in activities:
        provider = activity.provider
        time_slots = [
            {
                "id": slot.id,
                "start_time": slot.start_time,
                "end_time": slot.end_time,
                "is_available": slot.is_available,
            }
            for slot in activity.time_slots
        ]
        activity_details = {
            "id": activity.id,
            "provider_name": provider.business_name,
            "name": activity.name,
            "description": activity.description,
            "price": activity.price,
            "location": activity.location,
            "image":activity.image_url,
            "time_slots": time_slots,
        }
        activity_list.append(activity_details)

    return activity_list