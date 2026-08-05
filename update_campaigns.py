import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete
from app.core.config import settings
from app.models.campaign import Campaign

async def update_db(db_url: str):
    try:
        engine = create_async_engine(db_url, echo=False)
        async with engine.begin() as conn:
            from app.db.base import Base
            await conn.run_sync(Base.metadata.create_all)

        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as db:
            await db.execute(delete(Campaign))
            await db.commit()

            campaigns_data = [
                {
                    "title": "Aqua Aid",
                    "slug": "aqua-aid",
                    "description": "Providing clean drinking water, deep tube wells, and solar filtration systems to remote communities in need.",
                    "category": "Water Aid",
                    "goal": 20000.00,
                    "raised": 14500.00,
                    "image_key": "/static/campaigns/aqua-aid.jpg",
                    "active": True,
                },
                {
                    "title": "Share Meals",
                    "slug": "share-meals",
                    "description": "Distributing hot nutritious meals and monthly food packs to hungry families, widows, and orphans.",
                    "category": "Food Aid",
                    "goal": 18000.00,
                    "raised": 13100.00,
                    "image_key": "/static/campaigns/share-meals.jpg",
                    "active": True,
                },
                {
                    "title": "Emergency Aid",
                    "slug": "emergency-aid",
                    "description": "Rapid disaster response providing immediate shelter, food packs, and emergency aid to flood & crisis victims.",
                    "category": "Emergency Relief",
                    "goal": 40000.00,
                    "raised": 27400.00,
                    "image_key": "/static/campaigns/emergency-aid.jpg",
                    "active": True,
                },
                {
                    "title": "Sustain Now",
                    "slug": "sustain-now",
                    "description": "Empowering families with sustainable income opportunities, livestock, and small business grants.",
                    "category": "Livelihood",
                    "goal": 25000.00,
                    "raised": 16800.00,
                    "image_key": "/static/campaigns/sustain-now.jpg",
                    "active": True,
                },
                {
                    "title": "Bright Futures",
                    "slug": "bright-futures",
                    "description": "Supporting underprivileged children with school supplies, scholarships, and safe learning environments.",
                    "category": "Education",
                    "goal": 15000.00,
                    "raised": 9200.00,
                    "image_key": "/static/campaigns/bright-futures.jpg",
                    "active": True,
                },
                {
                    "title": "Building Hope",
                    "slug": "building-hope",
                    "description": "Construct resilient, flood-resistant shelters and homes for climate-displaced families who lost everything to natural disasters.",
                    "category": "Housing",
                    "goal": 50000.00,
                    "raised": 32600.00,
                    "image_key": "/static/campaigns/building-hope.jpg",
                    "active": True,
                },
                {
                    "title": "Free Mobile Clinic",
                    "slug": "free-mobile-clinic",
                    "description": "Deploy fully-equipped mobile medical vans and doctors to deliver free diagnostic checkups, emergency care, and vital medicines in remote rural villages.",
                    "category": "Medical Aid",
                    "goal": 30000.00,
                    "raised": 14200.00,
                    "image_key": "/static/campaigns/free-mobile-clinic.jpg",
                    "active": True,
                },
            ]
            for cdata in campaigns_data:
                db.add(Campaign(**cdata))
            await db.commit()
            print(f"Successfully updated database {db_url}")
        await engine.dispose()
    except Exception as e:
        print(f"Error updating {db_url}: {e}")

async def main():
    urls = list(set([
        settings.database_url,
        settings.effective_database_url,
        "sqlite+aiosqlite:///./charity_connect.db",
    ]))
    for url in urls:
        if url:
            await update_db(url)

if __name__ == "__main__":
    asyncio.run(main())
