from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from back.core.database import get_db
from back.core.security import get_current_user_id, create_access_token, create_refresh_token, verify_password, hashed_password, decode_token
from back.models import User
from back.schemas import UserRegister, UserLogin, TokenResponse, RefreshRequest, UserOut, messageResponse

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post('/register', response_model=TokenResponse)
async def register(user: UserRegister, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')
    
    new_user = User(
        email=user.email,
        hashed_password=hashed_password(user.password),
        full_name=user.full_name
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = create_access_token(data={'sub': new_user.id})
    refresh_token = create_refresh_token(data={'sub': new_user.id})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post('/login', response_model=TokenResponse)
async def login(user: UserLogin, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if not existing_user or not verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Email not verified')
    
    access_token = create_access_token(data={'sub': existing_user.id})
    refresh_token = create_refresh_token(data={'sub': existing_user.id})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post('/refresh', response_model=TokenResponse)
async def refresh_token(request: RefreshRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        payload = decode_token(request.refresh_token)
        user_id: str = payload.get('sub')
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')

    result = await db.execute(select(User).where(User.id == user_id))
    existing_user = result.scalar_one_or_none()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    access_token = create_access_token(data={'sub': existing_user.id})
    refresh_token = create_refresh_token(data={'sub': existing_user.id})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get('/me', response_model=UserOut)
async def get_current_user(current_user_id: Annotated[str, Depends(get_current_user_id)], db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user

@router.delete('/delete', response_model=messageResponse)
async def delete_account(current_user_id: Annotated[str, Depends(get_current_user_id)], db  : Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    await db.delete(user)
    await db.commit()
    return messageResponse(message='Account deleted successfully')