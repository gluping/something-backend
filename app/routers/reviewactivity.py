from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from oauth2 import get_current_user
from .listactivity import get_activities
from models import Activity, User, UserLikes
import schemas, models

from sqlalchemy.orm import joinedload


from database import get_db

router = APIRouter( prefix="/review",
    tags=['Like'])


@router.post("/{booking_id}", response_model=schemas.ReviewOut)
def submit_review(booking_id: int, review: schemas.ReviewCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if the booking exists and belongs to the current user
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id, models.Booking.user_id == current_user.id, models.Booking.is_completed == True).first()

    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    # Check if a review has already been submitted for this booking
    existing_review = db.query(models.Review).filter(models.Review.booking_id == booking_id).first()
    if existing_review:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Review already submitted for this booking")

    # Create the review
    new_review = models.Review(**review.dict(), user_id=current_user.id, booking_id=booking_id)
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review