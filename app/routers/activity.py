from fastapi import status,File,Form, UploadFile, HTTPException,Depends, APIRouter
from sqlalchemy.orm import Session
import models, schemas, utils
from oauth2 import get_current_user
from database import get_db

router = APIRouter(
    prefix="/createactivity",
    tags=['Activity CREATE  ']
)

# @router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Activity)
# def create_activity(
#     activity: schemas.ActivityCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user),
#     image: UploadFile = File(...),
# ):
#     # Save the uploaded image to AWS S3 and get the image URL
#     image_url = utils.upload_image_to_s3(image, bucket_name='travelactivity')

#     if not image_url:
#         raise HTTPException(status_code=500, detail="Failed to upload image to S3")

#     # Create a new activity record in the database
#     activity_dict = activity.dict()
#     activity_dict["provider_id"] = current_user.id
#     activity_dict["image_url"] = image_url  

#     new_activity = models.Activity(**activity_dict)
#     db.add(new_activity)
#     db.commit()
#     db.refresh(new_activity)

#     return new_activity

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Activity)
def create_activity(
    data: schemas.ActivityCreateWithImage,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Extract data from data.activity for JSON fields
    name = data.activity.name
    description = data.activity.description
    location = data.activity.location
    price = data.activity.price

    # Access the uploaded image as data.image
    image = data.image

    # Save the uploaded image to AWS S3 and get the image URL
    image_url = utils.upload_image_to_s3(image, bucket_name='travelactivity')

    if not image_url:
        raise HTTPException(status_code=500, detail="Failed to upload image to S3")

    # Create a new activity record in the database
    activity_dict = {
        "name": name,
        "description": description,
        "location": location,
        "price": price,
        "image_url": image_url,
        "provider_id": current_user.id,
    }

    new_activity = models.Activity(**activity_dict)
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    return new_activity
