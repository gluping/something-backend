from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
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
        activity_details = {
            "id": activity.id,
            "provider_name": provider.business_name,
            "name": activity.name,
            "description": activity.description,
            "price": activity.price,
            "location": activity.location,
        }
        activity_list.append(activity_details)

    return activity_list