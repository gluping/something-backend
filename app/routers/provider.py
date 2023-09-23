from fastapi import status, HTTPException,Depends, APIRouter
from sqlalchemy.orm import Session
import models, schemas, utils
from database import get_db


router = APIRouter(
    prefix="/providers",
    tags=['Activity Providers']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ProviderOut)
def register_provider(provider: schemas.ActivityProviderCreate, db: Session = Depends(get_db)):
    if provider.password != provider.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    
    hashed_password = utils.hash(provider.password)
    provider_dict = provider.dict()
    provider_dict.pop("confirm_password")
    provider_dict["password"] = hashed_password
    
    new_provider = models.ActivityProvider(**provider_dict)
    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)
    
    return new_provider