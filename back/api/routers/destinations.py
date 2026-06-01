from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Annotated
from back.core.database import get_db
from back.models import Destination, Review,Wishlist
from back.schemas import ReviewCreate, ReviewOut, DestinationOut, MessageResponse

router = APIRouter(prefix="/destinations", tags=["destinations"])

@router.get("/", response_model=List[DestinationOut])
async def list_destinations(skip: int = 0, limit: int = 10, db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(Destination).offset(skip).limit(limit))
    destinations = result.scalars().all()
    return destinations

@router.get("/destination/{destination_id}", response_model=DestinationOut)
async def get_destination(destination_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Destination).where(Destination.id == destination_id))
    destination = result.scalar_one_or_none()
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    return destination

@router.post("/reviews", response_model=ReviewOut, status_code=201)
async def create_review(review: ReviewCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    review = Review(**review.dict())
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review

@router.get('/destinations/{destination_id}/reviews', response_model=List[ReviewOut])
async def get_reviews(destination_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Review).where(Review.destination_id == destination_id))
    reviews = result.scalars().all()
    return reviews

@router.post("/wishlist/{destination_id}", response_model=MessageResponse)
async def add_to_wishlist(destination_id: str, db: Annotated[AsyncSession,  Depends(get_db)]):
    wishlist_item = Wishlist(destination_id=destination_id)
    db.add(wishlist_item)
    await db.commit()
    return MessageResponse(message="Destination added to wishlist")

@router.delete("/wishlist/{destination_id}", response_model=MessageResponse)
async def remove_from_wishlist(destination_id: str, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Wishlist).where(Wishlist.destination_id == destination_id))
    wishlist_item = result.scalar_one_or_none()
    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Destination not found in wishlist")
    await db.delete(wishlist_item)
    await db.commit()
    return MessageResponse(message="Destination removed from wishlist")