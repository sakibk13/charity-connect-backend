import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update

from app.core.config import settings
from app.models.campaign import Campaign
from app.models.event import Event
from app.models.blog_post import BlogPost
from app.models.hero_slide import HeroSlide
from app.models.gallery_photo import GalleryPhoto

async def fix_urls():
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    base_url = "http://localhost:9000/charity-connect"

    async with async_session() as db:
        print("Updating database image URLs to MinIO endpoints...")

        # Update Hero Slides
        res = await db.execute(select(HeroSlide))
        for slide in res.scalars().all():
            if slide.image_key and "http://localhost:8000" in slide.image_key:
                slide.image_key = slide.image_key.replace("http://localhost:8000", base_url)

        # Update Campaigns
        res = await db.execute(select(Campaign))
        for campaign in res.scalars().all():
            if campaign.image_key and "http://localhost:8000" in campaign.image_key:
                campaign.image_key = campaign.image_key.replace("http://localhost:8000", base_url)

        # Update Events
        res = await db.execute(select(Event))
        for event in res.scalars().all():
            if event.image_key and "http://localhost:8000" in event.image_key:
                event.image_key = event.image_key.replace("http://localhost:8000", event.image_key)
                event.image_key = event.image_key.replace("http://localhost:8000", base_url)

        # Update Blog Posts
        res = await db.execute(select(BlogPost))
        for post in res.scalars().all():
            if post.image_key and "http://localhost:8000" in post.image_key:
                post.image_key = post.image_key.replace("http://localhost:8000", base_url)

        # Update Gallery Photos
        res = await db.execute(select(GalleryPhoto))
        for photo in res.scalars().all():
            if photo.image_key and "http://localhost:8000" in photo.image_key:
                photo.image_key = photo.image_key.replace("http://localhost:8000", base_url)

        await db.commit()
        print("Database image URLs successfully updated!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_urls())
