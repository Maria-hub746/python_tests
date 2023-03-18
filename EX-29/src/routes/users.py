import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, status, Depends, File, UploadFile, HTTPException, BackgroundTasks, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from src.schemas import UserDB, ResetPassword, RequestEmail, UserResponse
from src.services.auth import auth_service
from src.conf.config import settings
from src.database.db import get_db
from src.database.models import User
import src.repository.auth as repository_auth

router = APIRouter(prefix='/users', tags=["users"])
security = HTTPBearer()


@router.get('/me/', response_model=UserDB, description='No more than 10 requests per minute',
            status_code=status.HTTP_200_OK)
            # dependencies=[Depends(RateLimiter(times=10, seconds=60))], status_code=status.HTTP_200_OK)
async def get_user_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_user_me function returns the current user.
    :param current_user: User: Get the current user
    :return: The current user
    """
    return current_user


@router.patch('/avatar', response_model=UserDB, description='No more than 5 requests per minute',
              dependencies=[Depends(RateLimiter(times=5, seconds=60))], status_code=status.HTTP_200_OK)
async def update_avatar(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):
    """
    The update_avatar function is used to update the avatar of a user.
    It takes in an UploadFile object, which contains the file that will be uploaded to Cloudinary.
    The current_user and db objects are also passed into this function, as they are required for updating
    the avatar URL in the database.
    :param file: UploadFile: Receive the file sent by the user
    :param current_user: User: Get the current user object from the database
    :param db: Session: Get the database session
    :return: The updated user object
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    cloudinary.uploader.upload(file.file, public_id=f'PythonContactsApp/{current_user.username}',
                               overwrite=True)
    avatar_url = cloudinary.CloudinaryImage(f'PythonContactsApp/{current_user.username}') \
        .build_url(width=250, height=250, crop='fill')
    user = await repository_auth.update_avatar(current_user.email, avatar_url, db)
    return user