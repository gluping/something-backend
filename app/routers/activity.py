from fastapi import status, File, UploadFile, HTTPException, Depends, APIRouter
from typing import List
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

def upload_images(images: List[UploadFile]):
    uploaded_urls = []

    for image in images:
        if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            raise HTTPException(status_code=400, detail="Unsupported image format")

        try:
            s3 = boto3.client('s3', aws_access_key_id=AWS_SERVER_PUBLIC_KEY, aws_secret_access_key=AWS_SERVER_SECRET_KEY, region_name='us-east-1')
            s3.upload_fileobj(image.file, "travelactivity", image.filename)
            image_url = f"https://travelactivity.s3.amazonaws.com/{image.filename}"
            uploaded_urls.append(image_url)
        except NoCredentialsError:
            raise HTTPException(status_code=500, detail="Failed to upload image to S3")

    return schemas.UploadResponse(url=uploaded_urls)



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Activity)
def create_activity(
    request_data: schemas.ActivityCreateWithImageURLAndTimeSlots,
    db: Session = Depends(get_db),
    current_provider: models.ActivityProvider = Depends(get_current_provider)
):
    image_url = request_data.image_url
    time_slots = request_data.time_slots

    
    activity_dict = request_data.dict(exclude={"image_url", "time_slots"})
    activity_dict["provider_id"] = current_provider.id
    activity_dict["image_url"] = image_url

    new_activity = models.Activity(**activity_dict)
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    
    for slot in time_slots:
        time_slot = models.TimeSlot(**slot.dict(), activity_id=new_activity.id)
        db.add(time_slot)

    db.commit()

    
    new_activity_with_slots = db.query(models.Activity).options(joinedload(models.Activity.time_slots)
    ).filter(models.Activity.id == new_activity.id).first()

    
    response_activity = schemas.Activity(
        id=new_activity_with_slots.id,
        name=new_activity_with_slots.name,
        description=new_activity_with_slots.description,
        location=new_activity_with_slots.location,
        price=new_activity_with_slots.price,
        image_url=new_activity_with_slots.image_url,
        provider_id=current_provider.id,
        likes=new_activity_with_slots.likes,
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



@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_provider: models.ActivityProvider = Depends(get_current_provider)
):
    
    activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.provider_id == current_provider.id
    ).first()

    db.query(models.TimeSlot).filter(models.TimeSlot.activity_id == activity_id).delete()

    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    
    db.delete(activity)
    db.commit()

    return {"message": "Activity deleted successfully"}



@router.put("/update_name_description/{activity_id}", status_code=status.HTTP_200_OK, response_model=schemas.Activity)
def update_name_description(
    activity_id: int,
    request_data: schemas.ActivityUpdateNameDescription,
    db: Session = Depends(get_db),
    current_provider: models.ActivityProvider = Depends(get_current_provider)
):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id, models.Activity.provider_id == current_provider.id).first()
    
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    activity.name = request_data.name
    activity.description = request_data.description
    
    db.commit()
    db.refresh(activity)
    
    return activity


@router.put("/update_location/{activity_id}", status_code=status.HTTP_200_OK, response_model=schemas.Activity)
def update_location(
    activity_id: int,
    request_data: schemas.ActivityUpdateLocation,
    db: Session = Depends(get_db),
    current_provider: models.ActivityProvider = Depends(get_current_provider)
):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id, models.Activity.provider_id == current_provider.id).first()
    
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    activity.location = request_data.location
    
    db.commit()
    db.refresh(activity)
    
    return activity


@router.put("/update_price/{activity_id}", status_code=status.HTTP_200_OK, response_model=schemas.Activity)
def update_price(
    activity_id: int,
    request_data: schemas.ActivityUpdatePrice,
    db: Session = Depends(get_db),
    current_provider: models.ActivityProvider = Depends(get_current_provider)
):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id, models.Activity.provider_id == current_provider.id).first()
    
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    activity.price = request_data.price
    
    db.commit()
    db.refresh(activity)
    
    return activity



@router.put("/update_image_url/{activity_id}", status_code=status.HTTP_200_OK, response_model=schemas.Activity)
def update_image_url(
    activity_id: int,
    request_data: schemas.ActivityUpdateImageURL,
    db: Session = Depends(get_db),
    current_provider: models.ActivityProvider = Depends(get_current_provider)
):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id, models.Activity.provider_id == current_provider.id).first()
    
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    activity.image_url = request_data.image_url
    
    db.commit()
    db.refresh(activity)
    
    return activity




@router.put("/update_time_slots/{activity_id}", status_code=status.HTTP_200_OK, response_model=schemas.Activity)
def update_time_slots(
    activity_id: int,
    request_data: List[schemas.TimeSlotUpdate],
    db: Session = Depends(get_db),
    current_provider: models.ActivityProvider = Depends(get_current_provider)
):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id, models.Activity.provider_id == current_provider.id).first()
    
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    # Deleting existing time slots
    db.query(models.TimeSlot).filter(models.TimeSlot.activity_id == activity_id).delete()
    
    # Adding new time slots
    for slot_data in request_data:
        time_slot = models.TimeSlot(**slot_data.dict(), activity_id=activity_id)
        db.add(time_slot)
    
    db.commit()
    
    updated_activity = db.query(models.Activity).options(joinedload(models.Activity.time_slots)).filter(models.Activity.id == activity_id).first()
    db.refresh(updated_activity)
    
    return updated_activity