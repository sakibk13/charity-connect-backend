import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete
from app.core.config import settings
from app.models.campaign import Campaign

async def update_campaigns():
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    base_url = settings.r2_public_base_url.rstrip("/")

    async with async_session() as db:
        await db.execute(delete(Campaign))
        await db.commit()

        campaigns_data = [
            {
                "title": "Iftar for Little Hearts",
                "slug": "iftar-for-little-hearts",
                "description": "Provide nutritious Iftar meals and joy to vulnerable orphaned and underprivileged children throughout the holy month of Ramadan.",
                "category": "Food Aid",
                "goal": 15000.00,
                "raised": 9800.00,
                "image_key": f"{base_url}/static/campaigns/iftar-for-little-hearts.jpg",
                "active": True,
            },
            {
                "title": "Ramadan Food Pack for Families in Need",
                "slug": "ramadan-food-pack",
                "description": "Supply essential month-long food rations including rice, lentils, oil, and dates for impoverished families during Ramadan.",
                "category": "Food Aid",
                "goal": 25000.00,
                "raised": 18400.00,
                "image_key": f"{base_url}/static/campaigns/ramadan-food-pack.jpg",
                "active": True,
            },
            {
                "title": "Free Mobile Clinic",
                "slug": "free-mobile-clinic",
                "description": "Deploy fully-equipped mobile medical vans and doctors to deliver free diagnostic checkups, emergency care, and vital medicines in remote rural villages.",
                "category": "Medical Aid",
                "goal": 30000.00,
                "raised": 14200.00,
                "image_key": f"{base_url}/static/campaigns/free-mobile-clinic.jpg",
                "active": True,
            },
            {
                "title": "Building Hope",
                "slug": "building-hope",
                "description": "Construct resilient, flood-resistant shelters and homes for climate-displaced families who lost everything to natural disasters.",
                "category": "Housing",
                "goal": 50000.00,
                "raised": 32600.00,
                "image_key": f"{base_url}/static/campaigns/building-hope.jpg",
                "active": True,
            },
            {
                "title": "Food Relief",
                "slug": "food-relief",
                "description": "Immediate emergency food packet distribution to communities experiencing acute food shortages, natural disasters, and extreme hardship.",
                "category": "Emergency Aid",
                "goal": 20000.00,
                "raised": 16500.00,
                "image_key": f"{base_url}/static/campaigns/food-relief.jpg",
                "active": True,
            },
            {
                "title": "Hope and Hygiene",
                "slug": "hope-and-hygiene",
                "description": "Distribute essential hygiene kits, clean water purification tools, and sanitary supplies to protect vulnerable women and children.",
                "category": "Health & Hygiene",
                "goal": 12000.00,
                "raised": 7900.00,
                "image_key": f"{base_url}/static/campaigns/hope-and-hygiene.jpg",
                "active": True,
            },
        ]
        for cdata in campaigns_data:
            db.add(Campaign(**cdata))
        await db.commit()
        print("Updated 6 Featured Appeals in Database successfully!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(update_campaigns())
