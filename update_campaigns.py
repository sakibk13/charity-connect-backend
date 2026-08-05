import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete
from app.core.config import settings
from app.models.campaign import Campaign

async def update_campaigns():
    engine = create_async_engine(settings.effective_database_url, echo=False)
    async with engine.begin() as conn:
        from app.db.base import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    base_url = settings.r2_public_base_url.rstrip("/")
    if "localhost" in base_url or not base_url:
        base_url = ""

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
                "image_key": f"{base_url}/static/campaigns/aqua-aid.jpg",
                "active": True,
            },
            {
                "title": "Sustain Now",
                "slug": "sustain-now",
                "description": "Empowering families with sustainable income opportunities, livestock, and small business grants.",
                "category": "Livelihood",
                "goal": 25000.00,
                "raised": 16800.00,
                "image_key": f"{base_url}/static/campaigns/sustain-now.jpg",
                "active": True,
            },
            {
                "title": "Bright Futures",
                "slug": "bright-futures",
                "description": "Supporting underprivileged children with school supplies, scholarships, and safe learning environments.",
                "category": "Education",
                "goal": 15000.00,
                "raised": 9200.00,
                "image_key": f"{base_url}/static/campaigns/bright-futures.jpg",
                "active": True,
            },
            {
                "title": "Medi Help",
                "slug": "medi-help",
                "description": "Delivering free medical checkups, essential medicines, and emergency healthcare support to rural communities.",
                "category": "Medical Aid",
                "goal": 30000.00,
                "raised": 18600.00,
                "image_key": f"{base_url}/static/campaigns/medi-help.jpg",
                "active": True,
            },
            {
                "title": "Emergency Aid",
                "slug": "emergency-aid",
                "description": "Rapid disaster response providing immediate shelter, food packs, and emergency aid to flood & crisis victims.",
                "category": "Emergency Relief",
                "goal": 40000.00,
                "raised": 27400.00,
                "image_key": f"{base_url}/static/campaigns/emergency-aid.jpg",
                "active": True,
            },
            {
                "title": "Share Meals",
                "slug": "share-meals",
                "description": "Distributing hot meals and monthly dry ration packs to hungry families, widows, and orphans.",
                "category": "Food Aid",
                "goal": 18000.00,
                "raised": 13100.00,
                "image_key": f"{base_url}/static/campaigns/share-meals.jpg",
                "active": True,
            },
        ]
        for cdata in campaigns_data:
            db.add(Campaign(**cdata))
        await db.commit()
        print("Successfully updated Featured Appeals to the 6 new causes!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(update_campaigns())
