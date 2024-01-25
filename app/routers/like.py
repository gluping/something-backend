from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from oauth2 import get_current_user
from .listactivity import get_activities
from models import Activity, User, UserLikes
import schemas

from sqlalchemy.orm import joinedload


from database import get_db

router = APIRouter( prefix="/like",
    tags=['Like'])


@router.post("/like/{activity_id}")
def like_activity_endpoint(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    activity = db.query(Activity).filter(Activity.id == activity_id).first()


    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    like_activity(db, current_user.id, activity_id)
    return {"message": "Activity liked successfully"}

@router.get("/{user_id}/liked-activities", response_model=list[schemas.Activity])
def get_liked_activities(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Assuming you have a relationship named 'liked_activities' in the User model
    liked_activities = (
        db.query(Activity)
        .join(User.liked_activities)
        .filter(User.id == user_id)
        .options(joinedload(Activity.time_slots))  # Include time_slots in the query
        .all()
    )

    return liked_activities

def like_activity(db: Session, user_id: int, activity_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    activity = db.query(Activity).filter(Activity.id == activity_id).first()

    if user and activity:
        # Check if the user already liked the activity
        if db.query(UserLikes).filter(UserLikes.user_id == user_id, UserLikes.activity_id == activity_id).first():
            raise HTTPException(status_code=400, detail="User already liked this activity")

        # Add like relationship
        like_relationship = UserLikes(user_id=user_id, activity_id=activity_id)
        db.add(like_relationship)

        # Increment likes count
        activity.likes += 1

        db.commit()
        db.refresh(activity)

        return activity

    raise HTTPException(status_code=404, detail="User or activity not found")

def query_liked_activities_from_database(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    liked_activities = [like.activity for like in user.liked_activities]

    return liked_activities

