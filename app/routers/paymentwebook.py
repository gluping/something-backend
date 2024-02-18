from fastapi import status, HTTPException,Depends, APIRouter

from starlette.responses import RedirectResponse

from sqlalchemy.orm import Session
import models, schemas, utils
from database import get_db
from datetime import datetime, timedelta
from fastapi import Query
from oauth2 import get_current_user
from config import settings
import razorpay


router = APIRouter(
    prefix="/book",
    tags=['Booking']
)

@router.get("/payment/{activity_id}")
