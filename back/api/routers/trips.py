from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Annotated
from back.core.database import get_db
from back.core.security import get_current_user_id
from back.models import Trip, TripDay, Activity
from back.schemas.schemas import TripOut, TripCreate, TripUpdate, TripDayOut, TripDayCreate, ActivityCreate, ActivityOut, MessageResponse

router = APIRouter(prefix="/trips", tags=["trips"])

@router.get("/", response_model=List[TripOut])
async def get_trips(db: Annotated[AsyncSession, Depends(get_db)], user_id: Annotated[int, Depends(get_current_user_id)]):
    result = await db.execute(select(Trip).where(Trip.user_id == user_id))
    trips = result.scalars().all()
    return trips

@router.post("/", response_model=TripOut, status_code=status.HTTP_201_CREATED)
async def create_trip(trip: TripCreate, db: Annotated[AsyncSession, Depends(get_db)], user_id: Annotated[int, Depends(get_current_user_id)]):
    new_trip = Trip(**trip.model_dump(), user_id=user_id)
    db.add(new_trip)
    await db.commit()
    await db.refresh(new_trip)
    return new_trip

@router.get("/{trip_id}", response_model=TripOut)
async def get_trip(trip_id: str, db: Annotated[AsyncSession, Depends(get_db)], user_id: Annotated[str, Depends(get_current_user_id)]):
    result = await db.execute(select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip

@router.patch("/{trip_id}", response_model=TripOut)
async def update_trip(trip_id: str, trip_update: TripUpdate, db: Annotated[AsyncSession, Depends(get_db)], user_id: Annotated[int, Depends(get_current_user_id)]):
    result = await db.execute(select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    for key, value in trip_update.model_dump(exclude_unset=True).items():
        setattr(trip, key, value)
    
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    return trip

@router.delete("/{trip_id}", response_model=MessageResponse)
async def delete_trip(trip_id: str, db: Annotated[AsyncSession, Depends(get_db)], user_id: Annotated[int, Depends(get_current_user_id)]):
    result = await db.execute(select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    await db.delete(trip)
    await db.commit()
    return MessageResponse(message="Trip deleted successfully")


@router.post("/{trip_id}/days", response_model=TripDayOut, status_code=status.HTTP_201_CREATED)
async def create_trip_day(trip_id: str, day: TripDayCreate, db: Annotated[AsyncSession, Depends(get_db)], user_id: Annotated[int, Depends(get_current_user_id)]):
    result = await db.execute(select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    new_day = TripDay(**day.model_dump(), trip_id=trip_id)
    db.add(new_day)
    await db.commit()
    await db.refresh(new_day)
    return new_day

@router.delete("/{trip_id}/days/{day_id}", response_model=MessageResponse)
async def delete_trip_day(trip_id: str, day_id: str, db: Annotated[AsyncSession, Depends(get_db)], user_id: Annotated[int, Depends(get_current_user_id)]):
    result = await db.execute(select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    result = await db.execute(select(TripDay).where(TripDay.id == day_id, TripDay.trip_id == trip_id))
    day = result.scalar_one_or_none()
    if not day:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip day not found")
    
    await db.delete(day)
    await db.commit()
    return MessageResponse(message="Trip day deleted successfully")


@router.post("/{trip_id}/days/{day_id}/activities", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
async def create_activity(trip_id: str, day_id: str, activity: ActivityCreate, db: Annotated[AsyncSession, Depends(get_db)], user_id: Annotated[int, Depends(get_current_user_id)]):
    result = await db.execute(select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    result = await db.execute(select(TripDay).where(TripDay.id == day_id, TripDay.trip_id == trip_id))
    day = result.scalar_one_or_none()
    if not day:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip day not found")
    
    new_activity = Activity(**activity.model_dump(), day_id=day_id)
    db.add(new_activity)
    await db.commit()
    await db.refresh(new_activity)
    return new_activity

async def _get_trip_or_404(trip_id: str, user_id: int, db: AsyncSession) -> Trip:
    result = await db.execute(select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip
