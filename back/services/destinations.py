from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from back.models import Destination

async def search_destinations( query: str):
    from back.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Destination).where(
                or_(
                    Destination.name.ilike(f"%{query}%"),
                    Destination.country.ilike(f"%{query}%"),
                    Destination.city.ilike(f"%{query}%"),
                )
            ).limit(20)
        )
        items = result.scalars().all()
        return [
            {
                "id": d.id,
                "name": d.name,
                "country": d.country,
                "city": d.city,
                "image_url": d.image_url,
                "avg_rating": d.avg_rating,
                "tags": d.tags,
            }
            for d in items
        ]
