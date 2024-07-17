from fastapi import FastAPI, status, HTTPException, Depends, APIRouter, Request
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from datetime import datetime
from fastapi import Query
from oauth2 import get_current_user
from config import settings
import razorpay

app = FastAPI()

router = APIRouter(
    prefix="/book",
    tags=['Booking']
)

KEY_ID = settings.RAZORPAY_KEY_ID
KEY_SECRET = settings.RAZORPAY_KEY_SECRET
WEBHOOK_SECRET = settings.RAZORPAY_WEBHOOK_SECRET
client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))


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

    all_time_slots = db.query(models.TimeSlot).filter(models.TimeSlot.activity_id == activity_id).all()

    booked_time_slots = (
        db.query(models.Booking.time_slot_id)
        .join(models.TimeSlot)
        .filter(models.TimeSlot.id.in_([slot.id for slot in all_time_slots]), models.Booking.activity_id == activity_id, models.Booking.created_at == selected_date)
        .all()
    )

    available_time_slots = [
        slot for slot in all_time_slots
        if (
            slot.id not in [booked[0] for booked in booked_time_slots] and
            len(slot.bookings) < slot.max_capacity
        )
    ]

    return {"available_time_slots": available_time_slots}


@router.post("/")
def book_activity(
    request_data: schemas.Booking,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    activity = db.query(models.Activity).get(request_data.activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    try:
        db.commit()
        with db.begin():
            booking = models.Booking(
                activity_id=request_data.activity_id,
                time_slot_id=request_data.slot_id,
                user_id=current_user.id,
                booking_date=request_data.booking_date,
                payment_id=None
            )
            db.add(booking)
            db.flush()

            razorpay_order = create_order(activity.price * 100, request_data.activity_id)
            print(razorpay_order)
            payment = models.Payment(amount=activity.price, status="Pending", order_id=razorpay_order['id'], booking_id=booking.id)
            db.add(payment)

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return razorpay_order['id']


@router.post("/create_order")
def create_order_endpoint(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(models.Activity).get(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    amount = activity.price * 100  # Assuming price is in INR and needs to be in paise
    order = create_order(amount, activity_id)

    return {"order_id": order['id']}


def create_order(amount, activity_id):
    data = {
        "amount": amount,
        "currency": "INR",
        "receipt": f"order_receipt_{activity_id}",
        "payment_capture": 1
    }
    order = client.order.create(data=data)
    return order


@router.post("/verify_payment")
async def verify_payment(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse JSON: {str(e)}")

    payment_id = body.get('payment_id')
    order_id = body.get('order_id')
    signature = body.get('signature')

    if not payment_id or not order_id or not signature:
        raise HTTPException(status_code=400, detail="Missing payment_id, order_id, or signature")

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Payment verification failed")

    payment = db.query(models.Payment).filter_by(order_id=order_id).first()
    if payment:
        payment.status = "Paid"
        db.commit()

    return {"status": "Payment verified and booking updated"}


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()  # Get raw body as bytes
    json_body = await request.json()  # Parse JSON body for event handling

    received_signature = request.headers.get('X-Razorpay-Signature')

    try:
        client.utility.verify_webhook_signature(
            body, received_signature, WEBHOOK_SECRET
        )
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Webhook signature verification failed")

    event = json_body['event']

    if event == "payment.captured":
        payment_id = json_body['payload']['payment']['entity']['id']
        order_id = json_body['payload']['payment']['entity']['order_id']

        payment = db.query(models.Payment).filter_by(order_id=order_id).first()
        if payment:
            payment.status = "Paid"
            db.commit()

    return {"status": "success"}


app.include_router(router)
