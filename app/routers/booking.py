# from fastapi import status, HTTPException,Depends, APIRouter
# from sqlalchemy.orm import Session
# import models, schemas, utils
# from database import get_db
# from datetime import datetime


# router = APIRouter(
#     prefix="/book",
#     tags=['Booking']
# )



# @router.get("/available-time-slots/{activity_id}")
# def get_available_time_slots(activity_id: int, db: Session = Depends(get_db)):
#     activity = db.query(models.Activity).filter(models.Activity.id == id).first()
    


#     if not activity:
#         raise HTTPException(status_code=404, detail="Activity not found")

#     # Get all time slots for the activity that are available
#     available_time_slots = (
#         db.query(models.TimeSlot)
#         .filter_by(activity_id=activity_id, is_available=True)
#         .all()
#     )

#     # Convert the time slots to a format that can be easily consumed by the frontend
#     time_slots = [
#         {
#             "start_time": slot.start_time.isoformat(),
#             "end_time": slot.end_time.isoformat(),
#         }
#         for slot in available_time_slots
#     ]

#     return {"available_time_slots": time_slots}



# @router.post("{activity_id}/{start_time}/{end_time}")
# def book_activity(activity_id: int, start_time: str, end_time: str, db: Session = Depends(get_db)):
#     activity = db.query(models.Activity).get(activity_id)
#     if not activity:
#         raise HTTPException(status_code=404, detail="Activity not found")

#     start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
#     end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")

#     try:
#         # Start a transaction
#         with db.begin():
#             # Check if the selected time slot is available
#             time_slot = (
#                 db.query(models.TimeSlot)
#                 .filter_by(
#                     activity_id=activity_id,
#                     start_time=start_time,
#                     end_time=end_time,
#                     is_available=True
#                 )
#                 .with_for_update()
#                 .first()
#             )

#             if not time_slot:
#                 raise HTTPException(status_code=400, detail="Selected time slot not available")

#             # Update the availability of the time slot
#             time_slot.is_available = False

#             # Create a booking record
#             booking = models.Booking(activity_id=activity_id, start_time=start_time, end_time=end_time, user_id=current_user.id)
#             db.add(booking)
#             db.flush()  # Flush to get the booking ID before creating the payment

#             # Create a payment record
#             payment = Payment(amount=activity.price, booking_id=booking.id)
#             db.add(payment)
#             db.commit()

#         # Return a success message
#         return {"message": "Activity booked successfully"}

#     except Exception as e:
#         # Roll back the transaction in case of an error
#         db.rollback()
#         raise HTTPException(status_code=500, detail="Internal Server Error")
