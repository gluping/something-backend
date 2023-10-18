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
    return activities

