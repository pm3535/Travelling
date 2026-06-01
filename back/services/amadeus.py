import httpx
from back.core.config import settings
from back.schemas import FlightSearchRequest, HotelSearchRequest

AMADEUS_BASE = "https://test.api.amadeus.com/v1"

_token_cache: dict = {}

async def _get_token() -> str:
    import time
    if _token_cache.get("expires_at", 0)  > time.time():
       return _token_cache["token"]
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AMADEUS_BASE}/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": settings.AMADEUS_CLIENT_ID,
                "client_secret": settings.AMADEUS_CLIENT_SECRET,
            },
        )
        response.raise_for_status()
        data = response.json()
        _token_cache["token"] = data["access_token"]
        _token_cache["expires_at"] = time.time() + data["expires_in"] - 60  # Refresh 1 minute before expiry
        return _token_cache["token"]
    
    async def search_flights(request: FlightSearchRequest) -> dict:
        if not settings.AMADEUS_CLIENT_ID or not settings.AMADEUS_CLIENT_SECRET:
            raise ValueError("Amadeus API credentials are not set.")
        token = await _get_token()
        params={
                    "originLocationCode": request.origin,
                    "destinationLocationCode": request.destination,
                    "departureDate": request.departure_date,
                    "returnDate": request.return_date,
                    "adults": request.adults,
                    "children": request.children,
                    "infants": request.infants,
                    "travelClass": request.travel_class,
                },
        headers={"Authorization": f"Bearer {token}"},
            
        async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{AMADEUS_BASE}/shopping/flight-offers",
                    params={
                        "originLocationCode": request.origin,
                        "destinationLocationCode": request.destination,
                        "departureDate": request.departure_date,
                        "returnDate": request.return_date,
                        "adults": request.adults,
                        "children": request.children,
                        "infants": request.infants,
                        "travelClass": request.travel_class,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                response.raise_for_status()
                return response.json()
        
async def search_hotels(request: HotelSearchRequest) -> dict:
    if not settings.AMADEUS_CLIENT_ID or not settings.AMADEUS_CLIENT_SECRET:
        raise ValueError("Amadeus API credentials are not set.")
    token = await _get_token()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AMADEUS_BASE}/shopping/hotel-offers",
            params={
                "cityCode": request.city,
                "checkInDate": request.check_in,
                "checkOutDate": request.check_out,
                "adults": request.adults,
                "roomQuantity": request.rooms,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()
     
  


