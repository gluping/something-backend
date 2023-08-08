from fastapi import status, HTTPException, Depends, APIRouter,WebSocket,WebSocketDisconnect
from sqlalchemy.orm import Session
import models, schemas, utils, database, oauth2
from database import get_db



router = APIRouter(
    prefix="/rooms",
    tags=['Rooms']
)

# Function to join a random room
def join_random_room(user: schemas.UserRoom, db: Session,current_user: models.User = Depends(oauth2.get_current_user)):
    rooms = db.query(models.Room).filter(models.Room.current_participants < 5).all()
    user_model = db.query(models.User).filter(models.User.email == user.email).first()
    
    if not rooms:
        # All rooms are full, create a new room
        new_room = models.Room(name="Random Room", description="Randomly created room", current_participants=1)
        db.add(new_room)
        db.commit()
        user_model.joined_rooms.append(new_room)
        # user_model.room_id = new_room.id
        db.commit()
        return new_room

    # Join an existing room with the fewest participants
    target_room = min(rooms, key=lambda r: r.current_participants)
    target_room.current_participants += 1
    user_model.joined_rooms.append(target_room)
    db.commit()
    return target_room

@router.post("/join_random_room/", response_model=schemas.UserRoomOut)
def join_random_room_endpoint(user: schemas.UserRoom, db: Session = Depends(get_db),current_user: models.User = Depends(oauth2.get_current_user)):
    return join_random_room(user, db)



@router.websocket("/join_random_room/{room_id}/")
async def chat_endpoint(
    websocket: WebSocket,
    room_id: int,
    current_user: models.User = Depends(oauth2.get_current_user),db:Session=Depends(get_db),
):
    # Ensure the user is authenticated
    if not current_user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Check if the user is part of the room
    user_in_room = db.query(models.Room).filter(
        models.Room.id == room_id,
        models.Room.participants.any(models.User.id == current_user.id)
    ).first()

    if not user_in_room:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Add the WebSocket to the room's chat group
    await websocket.accept()

    # Fetch and send previous messages in the room
    room = db.query(models.Room).get(room_id)
    if room.messages:
        for message in room.messages:
            await websocket.send_text(f"User {message.user.email}: {message.text}")

    # Continuously handle incoming messages from the WebSocket
    try:
        while True:
            data = await websocket.receive_text()
            # Save the received message to the database
            new_message = models.Message(text=data, user_id=current_user.id, room_id=room_id)
            db.add(new_message)
            db.commit()
            db.refresh(new_message)
            # Broadcast the message to all connected users in the room
            for participant in room.participants:
                for ws, user_id in utils.room_manager.active_rooms.get(room_id, []):
                    if participant.id == user_id:
                        await ws.send_text(f"User {current_user.email}: {data}")
                        break
    except WebSocketDisconnect:
        # If the WebSocket is disconnected, remove it from the chat group
        await utils.room_manager.disconnect(websocket, room_id, current_user.id)