
from email.mime import text
from turtle import title
import uuid
from datetime import datetime, timezone
from sqlalchemy import DATETIME, Integer, String,Boolean, Float, Text, DateTime, ForeignKey, Enum as SAEnum, JSON, true
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from back.core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

def new_uuid():
    return str(uuid.uuid4())

class PlanTier(str, enum.Enum):
    free = 'free'
    pro = 'pro'
    team = 'team'

class TripStatus(str, enum.Enum):
    draft = 'draft'
    planned = 'planned'
    active = 'active'
    completed = 'completed'

class BookingStatus(str, enum.Enum):
    pending = 'pending'
    confirmed = 'confirmed'
    cancelled = 'cancelled'

class User(Base):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    avatar_url : Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verifed : Mapped[bool] = mapped_column(Boolean, default= True)
    plan: Mapped[PlanTier] = mapped_column(SAEnum(PlanTier), default=PlanTier.free)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at :Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    trips: Mapped[list['Trip']] = relationship('Trip', back_populates='owner', cascade='all, delete-orphan')
    reviews: Mapped[list['Review']] = relationship('Review', back_populates='author')
    wishlists: Mapped[list['Wishlists']] = relationship('Wishlist', back_populates='user')


    class Destination(Base):
        __tablename__ = 'destinations'

        id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
        name : Mapped[str] = mapped_column(String(255), nullable= False, index=True)
        country: Mapped[str] = mapped_column(String(100), nullable=False)
        city: Mapped[str | None] = mapped_column(String(100))
        description: Mapped[str | None] = mapped_column(Text)
        latitude: Mapped[float | None] = mapped_column(Float)
        langitude:  Mapped[float | None] = mapped_column(Float)
        image_url: Mapped[str | None] = mapped_column(String(500))
        tags: Mapped[list] = mapped_column(JSON, default=list)
        avg_rating: Mapped[float] = mapped_column(Float, default=0)
        review_count: Mapped[int] =mapped_column(Integer, default=0) 
        create_at: Mapped[datetime] = mapped_column(DATETIME(timezone=True), default=utcnow)

        reviews: Mapped[list["Review"]] = relationship("Review", back_populates="destination")
        wishlists: Mapped[list["Wishlist"]] = relationship("Wishlist", back_populates="destination")

    class Trip(Base):
        __tablename__ = 'tables'

        id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
        owner_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False, index=True)
        title: Mapped[str] = mapped_column(String(255), nullable=False)
        description: Mapped[str | None] = mapped_column(text)
        destination_id: Mapped[str | None] = mapped_column(String, ForeignKey("destinations.id"))
        start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
        end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
        budget: Mapped[float | None] = mapped_column(Float)
        status: Mapped[TripStatus]= mapped_column(SAEnum(TripStatus), default=TripStatus.draft)
        is_public: Mapped[bool] = mapped_column(Boolean, default=False)
        cover_image_url: Mapped[str | None] = mapped_column(String(500))
        created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
        updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

        owner: Mapped["User"] = relationship("User", back_populates="trips")
        days: Mapped[list["TripDay"]] = relationship("TripDay", back_populates="trip", cascade="all, delete-orphan", order_by="TripDay.day_number")

    class TripDay(Base):
        __tablename__ = 'trip_days'

        id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
        trip_id: Mapped[str] = mapped_column(String, ForeignKey("trips.id"), nullable=False, index=True)
        day_number: Mapped[int] = mapped_column(Integer, nullable=False)
        date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
        notes: Mapped[str | None] = mapped_column(Text)

        trip: Mapped["Trip"] = relationship("Trip", back_populates="days")
        activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="day", cascade="all, delete-orphan", order_by="Activity.order")

    class Activity(Base):
        __tablename__ = 'activities'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    day_id: Mapped[str] = mapped_column(String, ForeignKey("trip_days.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(255))
    start_time: Mapped[str | None] = mapped_column(String(10))
    end_time: Mapped[str | None] = mapped_column(String(10))
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    order: Mapped[int] = mapped_column(Integer, default=0)
    extra: Mapped[dict] = mapped_column(JSON, default=dict)
 
    day: Mapped["TripDay"] = relationship("TripDay", back_populates="activities")

class Review(Base):
    __tablename__ = "reviews"
 
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    author_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    destination_id: Mapped[str] = mapped_column(String, ForeignKey("destinations.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    body: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
 
    author: Mapped["User"] = relationship("User", back_populates="reviews")
    destination: Mapped["Destination"] = relationship("Destination", back_populates="reviews")

class Wishlist(Base):
    __tablename__ = "wishlists"
 
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    destination_id: Mapped[str] = mapped_column(String, ForeignKey("destinations.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
 
    user: Mapped["User"] = relationship("User", back_populates="wishlists")
    destination: Mapped["Destination"] = relationship("Destination", back_populates="wishlists")

class PriceAlert(Base):
    __tablename__ = "price_alerts"
 
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    origin: Mapped[str] = mapped_column(String(10))
    destination: Mapped[str] = mapped_column(String(10))
    target_price: Mapped[float] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_checked: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
 
 
 

        