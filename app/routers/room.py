from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
import models, schemas, utils, database, oauth2
from database import get_db

router = APIRouter(
    prefix="/rooms",
    tags=['Rooms']
)

# Function to join a random room
def join_random_room(user: schemas.UserRoom, db: Session):
    rooms = db.query(models.Room).filter(models.Room.current_participants < 5).all()
    user_model = db.query(models.User).filter(models.User.email == user.email).first()
    
    if not rooms:
        # All rooms are full, create a new room
        new_room = models.Room(name="Random Room", description="Randomly created room", current_participants=1)
        db.add(new_room)
        db.commit()
        user_model.room_id = new_room.id
        db.commit()
        return new_room

    # Join an existing room with the fewest participants
    target_room = min(rooms, key=lambda r: r.current_participants)
    target_room.current_participants += 1
    user_model.room_id = target_room.id
    db.commit()
    return target_room

@router.post("/join_random_room/", response_model=schemas.UserRoomOut)
def join_random_room_endpoint(user: schemas.UserRoom, db: Session = Depends(get_db)):
    return join_random_room(user, db)
