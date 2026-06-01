from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from back.core.security import get_current_user_id
from back.core.redis import cache_get, cache_set
from back.schemas.schemas import FlightSearchRequest, HotelSearchRequest
from back.services.amadeus import search_flights, search_hotels
from back.services.weather import get_weather
from back.services.destinations import search_destinations

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/destinations")
async def destinations(query: str, user_id: Annotated[int, Depends(get_current_user_id)]):
    cache_key = f"destinations:{query}"
    cached_result = await cache_get(cache_key)
    if cached_result:
        return cached_result

    results = await search_destinations(query)
    if not results:
        raise HTTPException(status_code=404, detail="No destinations found")

    await cache_set(cache_key, results, expire=3600)  # Cache for 1 hour
    return results

@router.post("/flights")
async def flights(search_request: FlightSearchRequest, user_id: Annotated[int, Depends(get_current_user_id)]):
    cache_key = f"flights:{search_request.origin}:{search_request.destination}:{search_request.departure_date}"
    cached_result = await cache_get(cache_key)
    if cached_result:
        return cached_result

    results = await search_flights(search_request)
    if not results:
        raise HTTPException(status_code=404, detail="No flights found")

    await cache_set(cache_key, results, expire=3600)  # Cache for 1 hour
    return results

@router.post("/hotels")
async def hotels(search_request: HotelSearchRequest, user_id: Annotated[int, Depends(get_current_user_id)]):
    cache_key = f"hotels:{search_request.destination}:{search_request.check_in}:{search_request.check_out}"
    cached_result = await cache_get(cache_key)
    if cached_result:
        return cached_result

    results = await search_hotels(search_request)
    if not results:
        raise HTTPException(status_code=404, detail="No hotels found")

    await cache_set(cache_key, results, expire=3600)  # Cache for 1 hour
    return results

@router.get("/weather/{city}")
async def weather(city: str, user_id: Annotated[int, Depends(get_current_user_id)]):
    cache_key = f"weather:{city}"
    cached_result = await cache_get(cache_key)
    if cached_result:
        return cached_result

    results = await get_weather(city)
    if not results:
        raise HTTPException(status_code=404, detail="Weather data not found")

    await cache_set(cache_key, results, expire=3600)  # Cache for 1 hour
    return results
