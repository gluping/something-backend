from fastapi import status, File, UploadFile, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session,joinedload
import models, schemas, utils
from oauth2 import get_current_provider
from database import get_db
import boto3
from botocore.exceptions import NoCredentialsError
from config import settings


AWS_SERVER_PUBLIC_KEY = settings.AWS_SERVER_PUBLIC_KEY
AWS_SERVER_SECRET_KEY = settings.AWS_SERVER_SECRET_KEY

router = APIRouter(
    prefix="/createactivity",
    tags=['Activity Create']
)

@router.post("/upload-file/", response_model=schemas.UploadResponse)
def upload_image(image: UploadFile):
    if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
        raise HTTPException(status_code=400, detail="Unsupported image format")

    try:
        s3 = boto3.client('s3', aws_access_key_id=AWS_SERVER_PUBLIC_KEY, aws_secret_access_key=AWS_SERVER_SECRET_KEY, region_name='us-east-1')
        s3.upload_fileobj(image.file, "travelactivity", image.filename)
        image_url = f"https://travelactivity.s3.amazonaws.com/{image.filename}"
        return schemas.UploadResponse(url=image_url)
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Failed to upload image to S3")

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Activity)
def create_activity(
    request_data: schemas.ActivityCreateWithImageURLAndTimeSlots,  # Modify the schema to include time_slots
    db: Session = Depends(get_db),
    current_provider: models.ActivityProvider = Depends(get_current_provider)
):
    
    image_url = request_data.image_url
    time_slots = request_data.time_slots

    # Create a new activity record in the database
    activity_dict = request_data.dict(exclude={"image_url", "time_slots"})  # Exclude image_url and time_slots from activity fields
    activity_dict["provider_id"] = current_provider.id
    activity_dict["image_url"] = image_url  

    new_activity = models.Activity(**activity_dict)
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    # Add time slots to the database
    for slot in time_slots:
        time_slot = models.TimeSlot(**slot.dict(),
        activity_id=new_activity.id)
        db.add(time_slot)

    db.commit()

    # Fetch the time slots from the database
    new_activity_with_slots = db.query(models.Activity).options(joinedload(models.Activity.time_slots)
    ).filter(models.Activity.id == new_activity.id).first()

    # Map the SQLAlchemy model to Pydantic model
    response_activity = schemas.Activity(
        id=new_activity_with_slots.id,
        name=new_activity_with_slots.name,
        description=new_activity_with_slots.description,
        location=new_activity_with_slots.location,
        price=new_activity_with_slots.price,
        image_url=new_activity_with_slots.image_url,
        time_slots=[
            schemas.TimeSlot(
                id=slot.id,
                start_time=slot.start_time,
                end_time=slot.end_time,
                is_available=slot.is_available,
                max_capacity=slot.max_capacity
            )
            for slot in new_activity_with_slots.time_slots
        ],
    )

    return response_activity


