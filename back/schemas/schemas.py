from tarfile import tar_filter

from pydantic import BaseModel, Field, EmailStr,ConfigDict
from typing import Optional,List,Any
from datetime import datetime
from back.models import PlanTier, TripStatus


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    plan_tier: PlanTier
    created_at: datetime
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    preferences: Optional[dict] = None

class DestinationOut(BaseModel):
    id: str
    name: str
    country: str
    city: Optional[str]
    description: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    image_url: Optional[str]
    tags: List[Any]
    avg_rating: float
    review_count: int

    model_config = ConfigDict(from_attributes=True)

class ActivityCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    cost: float = 0.0
    order: int = 0

class ActivityOut(ActivityCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    day_id: str

class TripDayCreate(BaseModel):
    day_number: int
    date: Optional[datetime] = None
    notes: Optional[str] = None
    activities: List[ActivityCreate] = []

class TripDayOut(BaseModel):
    id: str
    day_number: int
    date: Optional[datetime] = None
    notes: Optional[str] = None
    activities: List[ActivityOut] = []

    model_config = ConfigDict(from_attributes=True)

class TripCreate(BaseModel):
    title: str
    description: Optional[str] = None
    destination_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    is_public: bool = False


class TripUpdate(TripCreate):
   title: Optional[str] = None
   description: Optional[str] = None
   start_date: Optional[datetime] = None
   end_date: Optional[datetime] = None
   budget: Optional[float] = None
   is_public: Optional[bool] = None
   status: Optional[TripStatus] = None

class TripOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    destination_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    is_public: bool = False
    status: TripStatus
    cover_image_url: Optional[str] = None
    days: List[TripDayOut] = []

    model_config = ConfigDict(from_attributes=True)

class ReviewCreate(BaseModel):
    destination_id: str
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None

class ReviewOut(BaseModel):
    id: str
    user_id: str
    destination_id: str
    rating: int
    title: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FlightSearchRequest(BaseModel):
    origin: str = Field(description='IATA code of the departure airport')
    destination: str = Field(description='IATA code of the arrival airport')
    departure_date: datetime = Field(description='Date of departure in YYYY-MM-DD format')
    return_date: Optional[datetime] = None
    adults:int = 1


class HotelSearchRequest(BaseModel):
    city_code: str
    check_in: datetime
    check_out: datetime
    adults: int = 1

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    trip_id: Optional[str] = None

class PriceAlertCreate(BaseModel):
   origin: str
   destination: str
   target_price: float

class PriceAlertOut(PriceAlertCreate):
    id: str
    origin: str
    destination: str
    created_at: datetime
    target_price: float
    is_active: bool
    created_at: datetime


    model_config = ConfigDict(from_attributes=True)
  

class MessageResponse(BaseModel):
    message: str

class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[Any]
  
  