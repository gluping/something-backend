from fastapi import status, HTTPException,Depends, APIRouter, File, UploadFile
from sqlalchemy.orm import Session
import models, schemas, utils
from database import get_db
from typing import List
from oauth2 import get_current_user
import boto3
from botocore.exceptions import NoCredentialsError
from config import settings
import datetime





AWS_SERVER_PUBLIC_KEY = settings.AWS_SERVER_PUBLIC_KEY
AWS_SERVER_SECRET_KEY = settings.AWS_SERVER_SECRET_KEY

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.get("/{id}",response_model=schemas.UserOut)
def get_user(id : int,db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return user



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    
    hashed_password = utils.hash(user.password)
    user_dict = user.dict()
    user_dict.pop("confirm_password")  
    user_dict["password"] = hashed_password
    
    new_user = models.User(**user_dict)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user



request_time = datetime.datetime.utcnow()

@router.post("/profile", status_code=status.HTTP_201_CREATED, response_model=schemas.UserProfileOut)
def create_user_profile(username: str,  db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Check if username is provided
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is required")



   
    current_user.username = username
    

    
    db.commit()

    return current_user


@router.post("/profile_pic", status_code=status.HTTP_201_CREATED, response_model=schemas.UserProfileOut)
def create_user_profile_pic(profile_pic: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
            aws_secret_access_key=AWS_SERVER_SECRET_KEY,
            region_name='us-east-1'
        )
        s3.upload_fileobj(profile_pic.file, "travelactivity", profile_pic.filename)
        profile_pic_url = f"https://travelactivity.s3.amazonaws.com/{profile_pic.filename}"
    except NoCredentialsError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload profile picture to S3")

    
    current_user.profile_pic = profile_pic_url

    
    db.commit()

    return current_user