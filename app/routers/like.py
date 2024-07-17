from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from oauth2 import get_current_user
from models import Activity, User, UserLikes
import schemas
from database import get_db

router = APIRouter(
    prefix="/like",
    tags=['Like']
)

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

@router.get("/liked-activities", response_model=list[schemas.Activity])
def get_liked_activities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    liked_activities = (
        db.query(Activity)
        .join(UserLikes)
        .filter(UserLikes.user_id == current_user.id)
        .options(joinedload(Activity.time_slots)) 
        .all()
    )

    return liked_activities

def like_activity(db: Session, user_id: int, activity_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    activity = db.query(Activity).filter(Activity.id == activity_id).first()

    if user and activity:
        if db.query(UserLikes).filter(UserLikes.user_id == user_id, UserLikes.activity_id == activity_id).first():
            raise HTTPException(status_code=400, detail="User already liked this activity")

        like_relationship = UserLikes(user_id=user_id, activity_id=activity_id)
        db.add(like_relationship)

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

@router.delete("/like/{activity_id}")
def unlike_activity_endpoint(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_like = db.query(UserLikes).filter(
        UserLikes.user_id == current_user.id,
        UserLikes.activity_id == activity_id
    ).first()

    if not user_like:
        raise HTTPException(status_code=404, detail="Like not found")

    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

   
    db.delete(user_like)
    
    
    activity.likes -= 1

    db.commit()
    db.refresh(activity)

    return {"message": "Activity unliked successfully"}
