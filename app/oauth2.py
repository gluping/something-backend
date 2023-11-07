from jose import JWTError, jwt
from datetime import datetime, timedelta
import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from config import  settings
from typing import Union
# from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict, token_type: str):
    to_encode = data.copy() 

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": token_type})  # Include the 'type' field

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        provider_id = str(payload.get("provider_id"))  # Ensure provider_id is handled as a string
        token_type = payload.get("type")

        if token_type not in ["user", "provider"]:
            raise credentials_exception  # Invalid token type

        if token_type == "user":
            if user_id is None:
                raise credentials_exception
            token_data = schemas.TokenData(id=user_id, type="user")
        elif token_type == "provider":
            if provider_id is None:
                raise credentials_exception
            token_data = schemas.TokenData(id=provider_id, type="provider")
    except JWTError:
        raise credentials_exception

    return token_data




# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
#     credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                           detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

#     token = verify_access_token(token, credentials_exception)

#     user = db.query(models.User).filter(models.User.id == token.id).first()

#     return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token_data = verify_access_token(token, credentials_exception)

    # Check if the token data indicates a user or provider (you should have a role or type field in the token payload).
    user = None

    if token_data.type == "user":
        user = db.query(models.User).filter(models.User.id == token_data.id).first()
    elif token_data.type == "provider":
        user = db.query(models.ActivityProvider).filter(models.ActivityProvider.id == token_data.id).first()

    return user

    