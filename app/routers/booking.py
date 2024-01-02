from fastapi import status, HTTPException,Depends, APIRouter
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import models, schemas, utils
from oauth2 import get_current_user
from database import get_db
from datetime import datetime, timedelta
from fastapi import Query
import razorpay
from config import settings


KEY_ID= settings.RAZORPAY_KEY_ID
KEY_SECRET= settings.RAZORPAY_KEY_SECRET
client = razorpay.Client(auth=(KEY_ID,KEY_SECRET))


router = APIRouter(
    prefix="/book",
    tags=['Booking']
)




@router.get("/available_time_slots/{activity_id}")
async def get_available_time_slots(
    activity_id: int,
    selected_date: str = Query(..., description="Selected date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    try:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get all time slots associated with the activity
    all_time_slots = db.query(models.TimeSlot).filter(models.TimeSlot.activity_id == activity_id).all()

    # Get booked time slots for the selected date
    booked_time_slots = (
        db.query(models.Booking.time_slot_id)
        .join(models.TimeSlot)
        .filter(models.TimeSlot.id.in_([slot.id for slot in all_time_slots]), models.Booking.activity_id == activity_id, models.Booking.created_at == selected_date)
        .all()
    )

    # Get available time slots for the selected date
    available_time_slots = [
    slot for slot in all_time_slots 
    if (
        slot.id not in [booked[0] for booked in booked_time_slots] and
        len(slot.bookings) < slot.max_capacity
    )
]


    return {"available_time_slots": available_time_slots}



@router.post("{activity_id}/{start_time}/{end_time}")
def book_activity(activity_id: int, start_time: str, end_time: str, db: Session = Depends(get_db),current_user: models.User= Depends(get_current_user)):
    activity = db.query(models.Activity).get(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
    end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")

    try:
        # Start a transaction
        with db.begin():
            # Check if the selected time slot is available
            time_slot = (
                db.query(models.TimeSlot)
                .filter_by(
                    activity_id=activity_id,
                    start_time=start_time,
                    end_time=end_time,
                    is_available=True
                )
                .with_for_update()
                .first()
            )

            if not time_slot:
                raise HTTPException(status_code=400, detail="Selected time slot not available")

            # Update the availability of the time slot
            time_slot.is_available = False

            # Create a booking record
            booking = models.Booking(activity_id=activity_id, start_time=start_time, end_time=end_time, user_id=current_user.id,payment_id=None)
            db.add(booking)
            db.flush()  # Flush to get the booking ID before creating the payment

            # Create a payment record
            razorpay_order = create_order(activity.price * 100, activity_id)
            payment = models.Payment(amount=activity.price, status="Pending", order_id=razorpay_order['id'], booking_id=booking.id)
            db.add(payment)
            
            db.add(payment)
            db.commit()
            return redirect_to_payment(razorpay_order['id'])

        # Return a success message
        

    except Exception as e:
        # Roll back the transaction in case of an error
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
def create_order(amount, activity_id):
    data = {
        "amount": amount,
        "currency": "INR",
        "receipt": f"order_receipt_{activity_id}",  # Use a unique identifier for each order
        "payment_capture": 1  # Auto-capture payment when the order is created
    }
    order = client.order.create(data=data)
    return order

def redirect_to_payment(order_id):
    payment_url = f"https://api.razorpay.com/v1/checkout/embedded/{order_id}"
    return RedirectResponse(payment_url)