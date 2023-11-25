from sqlalchemy import Column, Integer, String,Float, TIMESTAMP, text, Table, ForeignKey,DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

  
class ActivityProvider(Base):
    __tablename__ = "activity_providers"
    id = Column(Integer, primary_key=True, nullable=False)
    business_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    activities = relationship("Activity", back_populates="provider")

class Activity(Base):
    __tablename__="activities"  # Corrected table name
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    location = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    image_url = Column(String)  # Store the URL of the uploaded image

    provider_id = Column(Integer, ForeignKey("activity_providers.id"), nullable=False)
    provider = relationship("ActivityProvider", back_populates="activities")

    # time_slots = relationship("TimeSlot", back_populates="activities")


# class TimeSlot(Base):
#     __tablename__ = "time_slots"
#     id = Column(Integer, primary_key=True, nullable=False)
#     start_time = Column(DateTime, nullable=False)
#     end_time = Column(DateTime, nullable=False)
#     activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)  # Corrected foreign key
#     is_available = Column(Boolean, nullable=False, default=True)

# class Payment(Base):
#     __tablename__ = "payments"
#     id = Column(Integer, primary_key=True, nullable=False)
#     amount = Column(Float, nullable=False)
#     status = Column(String, nullable=False, default="Pending")
#     booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
#     booking = relationship("Booking", back_populates="payment")


# class Booking(Base):
#     __tablename__ = "bookings"
#     id = Column(Integer, primary_key=True, nullable=False)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
#     time_slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=False)
#     payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

#     user = relationship("User", back_populates="bookings")
#     activity = relationship("Activity", back_populates="bookings")
#     time_slot = relationship("TimeSlot", back_populates="bookings")
#     payment = relationship("Payment", back_populates="booking")

    # You can add more columns based on your booking requirements
