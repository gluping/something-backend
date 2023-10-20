from fastapi import status,File,Form, UploadFile, HTTPException,Depends, APIRouter
from sqlalchemy.orm import Session
import models, schemas, utils
from oauth2 import get_current_user
from database import get_db
import boto3
from botocore.exceptions import NoCredentialsError
from config import  settings


AWS_SERVER_PUBLIC_KEY = settings.AWS_SERVER_PUBLIC_KEY
AWS_SERVER_SECRET_KEY = settings.AWS_SERVER_SECRET_KEY

router = APIRouter(
    prefix="/createactivity",
    tags=['Activity Create']
)



@router.post("/upload-file/", response_model=schemas.UploadResponse)
def upload_image(image: UploadFile):
    # Ensure that the uploaded file is an image (optional)
    if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
        raise HTTPException(status_code=400, detail="Unsupported image format")

    try:
        # s3 = boto3.client('s3') 
        s3 = boto3.client('s3', aws_access_key_id=AWS_SERVER_PUBLIC_KEY, aws_secret_access_key=AWS_SERVER_SECRET_KEY, region_name='us-east-1')
        s3.upload_fileobj(image.file, "travelactivity", image.filename)
        image_url = f"https://travelactivity.s3.amazonaws.com/{image.filename}"
        return schemas.UploadResponse(url=image_url)
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Failed to upload image to S3")

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Activity)

def create_activity(
    activity: schemas.ActivityCreate,
    image_url: str,
    db: Session = Depends(get_db),
    current_provider: models.User = Depends(get_current_user)
):

    # Create a new activity record in the database
    activity_dict = activity.dict()
    activity_dict["provider_id"] = current_provider.id
    activity_dict["image_url"] = image_url  

    new_activity = models.Activity(**activity_dict)
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    response_activity = schemas.Activity(
        **new_activity.__dict__
    )

    return response_activity




