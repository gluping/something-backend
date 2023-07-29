from sqlalchemy import Column, Integer, String, TIMESTAMP, text, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Association Table to link users and rooms in a many-to-many relationship
room_participants = Table(
    "room_participants",
    Base.metadata,
    Column("room_id", Integer, ForeignKey("rooms.id")),
    Column("user_id", Integer, ForeignKey("users.id"))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Establishing the many-to-many relationship with Room model
    joined_rooms = relationship("Room", secondary=room_participants, back_populates="participants")

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    current_participants = Column(Integer, default=0)  # New field to track current participants

    # Establishing the many-to-many relationship with User model
    participants = relationship("User", secondary=room_participants, back_populates="joined_rooms")
