from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models, schemas, utils, database, oauth2




router = APIRouter(
    tags=['Auth']
)


@router.post("/login-provider", response_model=schemas.Token)
def login_provider(provider_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    provider = db.query(models.ActivityProvider).filter(models.ActivityProvider.contact_email == provider_credentials.username).first()

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(provider_credentials.password, provider.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    access_token = oauth2.create_access_token(data={"provider_id": provider.id})

    return {"access_token": access_token, "token_type": "bearer"}
