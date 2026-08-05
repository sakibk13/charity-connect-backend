import asyncio
import os
import uuid
from datetime import date, datetime, timezone
import boto3
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.campaign import Campaign
from app.models.event import Event
from app.models.blog_post import BlogPost
from app.models.hero_slide import HeroSlide
from app.models.gallery_photo import GalleryPhoto
from app.models.zakat_setting import ZakatSetting


def upload_static_files_to_minio():
    """Upload all static files to MinIO bucket so image URLs serve properly."""
    print("Uploading static images to MinIO...")
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.storage_endpoint,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )

    static_dir = "/code/static" if os.path.exists("/code/static") else "static"
    if not os.path.exists(static_dir):
        print(f"Directory {static_dir} not found. Skipping static file upload.")
        return

    bucket = settings.r2_bucket_name
    for root, _, files in os.walk(static_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, os.path.dirname(static_dir)).replace("\\", "/")
            key = rel_path
            content_type = "image/jpeg" if file.endswith((".jpeg", ".jpg")) else "image/png"
            with open(file_path, "rb") as f:
                s3.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=f.read(),
                    ContentType=content_type,
                )
            print(f"Uploaded {key} to MinIO bucket {bucket}")


async def seed_data():
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        print("Seeding database...")

        # 1. Admin User
        admin_email = "admin@charityconnect.org"
        res = await db.execute(select(User).where(User.email == admin_email))
        admin = res.scalar_one_or_none()
        if not admin:
            admin = User(
                name="Admin User",
                email=admin_email,
                password_hash=hash_password("admin123"),
                role=UserRole.ADMIN,
                phone="+1234567890",
                location="Headquarters",
            )
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
            print(f"Created Admin User: {admin_email} (Password: admin123)")
        else:
            print(f"Admin User {admin_email} already exists.")

        base_url = settings.r2_public_base_url.rstrip("/")

        # 2. Hero Slides
        res = await db.execute(select(HeroSlide))
        slides = res.scalars().all()
        if not slides:
            hero_data = [
                {
                    "headline": "Empowering Communities, Changing Lives",
                    "badge_text": "Urgent Appeal",
                    "cta_label": "Donate Now",
                    "cta_href": "/campaigns",
                    "image_key": f"{base_url}/static/hero-slides/hero-image-1.jpeg",
                    "sort_order": 1,
                    "active": True,
                },
                {
                    "headline": "Emergency Flood Relief for Families in Need",
                    "badge_text": "Disaster Relief",
                    "cta_label": "Support Relief",
                    "cta_href": "/campaigns/flood-relief",
                    "image_key": f"{base_url}/static/hero-slides/hero-image-2.jpeg",
                    "sort_order": 2,
                    "active": True,
                },
                {
                    "headline": "Clean Water & Life-Saving Medical Care",
                    "badge_text": "Healthcare Initiative",
                    "cta_label": "Learn More",
                    "cta_href": "/campaigns/medicine-campaign",
                    "image_key": f"{base_url}/static/hero-slides/hero-image-3.jpeg",
                    "sort_order": 3,
                    "active": True,
                },
            ]
            for data in hero_data:
                db.add(HeroSlide(**data))
            await db.commit()
            print(f"Seeded {len(hero_data)} Hero Slides.")

        # 3. Campaigns
        res = await db.execute(select(Campaign))
        existing_campaigns = res.scalars().all()
        campaign_map = {}
        if not existing_campaigns:
            campaigns_data = [
                {
                    "title": "Emergency Flood Relief Campaign",
                    "slug": "flood-relief",
                    "description": "Providing emergency food packs, clean drinking water, temporary shelter, and medical supplies to families devastated by severe flooding.",
                    "category": "Emergency",
                    "goal": 50000.00,
                    "raised": 18500.00,
                    "image_key": f"{base_url}/static/campaigns/flood-relief.jpeg",
                    "active": True,
                },
                {
                    "title": "Life-Saving Medicine & Medical Supplies",
                    "slug": "medicine-campaign",
                    "description": "Delivering essential medicines, surgical equipment, and mobile health clinics to remote and underserved communities.",
                    "category": "Medical Aid",
                    "goal": 35000.00,
                    "raised": 12400.00,
                    "image_key": f"{base_url}/static/campaigns/medicine-campaign.jpeg",
                    "active": True,
                },
                {
                    "title": "Ramadan Food Packs & Iftar Distribution",
                    "slug": "ramadan-campaign",
                    "description": "Distributing nutritious monthly food packs to impoverished families, widows, and orphans throughout the holy month.",
                    "category": "Food Aid",
                    "goal": 25000.00,
                    "raised": 21000.00,
                    "image_key": f"{base_url}/static/campaigns/ramadan-campaign.jpeg",
                    "active": True,
                },
            ]
            for cdata in campaigns_data:
                c = Campaign(**cdata)
                db.add(c)
                await db.commit()
                await db.refresh(c)
                campaign_map[c.slug] = c
            print(f"Seeded {len(campaigns_data)} Campaigns.")

        # 4. Events
        res = await db.execute(select(Event))
        if not res.scalars().all():
            events_data = [
                {
                    "title": "Annual Charity Gala & Fundraising Dinner",
                    "slug": "annual-charity-gala",
                    "description": "Join us for an inspiring evening of stories, networking, and fundraising to support clean water and education initiatives worldwide.",
                    "date": date(2026, 9, 15),
                    "time": "6:00 PM - 9:30 PM",
                    "location": "Grand Ballroom, City Community Center",
                    "image_key": f"{base_url}/static/hero-slides/hero-image-1.jpeg",
                },
                {
                    "title": "Volunteer Fieldwork Orientation & Training",
                    "slug": "volunteer-orientation",
                    "description": "Comprehensive orientation session for new and returning volunteers preparing for upcoming community outreach programs.",
                    "date": date(2026, 9, 28),
                    "time": "10:00 AM - 1:00 PM",
                    "location": "Charity Connect HQ, Main Hall",
                    "image_key": f"{base_url}/static/hero-slides/hero-image-2.jpeg",
                },
            ]
            for edata in events_data:
                db.add(Event(**edata))
            await db.commit()
            print(f"Seeded {len(events_data)} Events.")

        # 5. Blog Posts
        res = await db.execute(select(BlogPost))
        if not res.scalars().all():
            flood_c = campaign_map.get("flood-relief")
            med_c = campaign_map.get("medicine-campaign")
            blog_data = [
                {
                    "title": "How Your Donations Transformed 500 Families' Lives This Season",
                    "slug": "how-your-donations-transformed-lives",
                    "summary": "A detailed report on our recent field operations and how donor generosity provided food, shelter, and medical support.",
                    "content": "Thanks to your generous contributions, Charity Connect successfully deployed emergency response teams across three affected regions. Over 500 families received emergency food packs and clean water filtration units.",
                    "category": "Impact Stories",
                    "author_id": admin.id,
                    "campaign_id": flood_c.id if flood_c else None,
                    "image_key": f"{base_url}/static/campaigns/flood-relief.jpeg",
                    "published": True,
                    "published_at": datetime.now(timezone.utc),
                },
                {
                    "title": "Bringing Clean Drinking Water to Remote Villages",
                    "slug": "bringing-clean-drinking-water",
                    "summary": "Highlighting the installation of deep-water wells and filtration systems for vulnerable rural communities.",
                    "content": "Access to clean water is a fundamental human right. Our engineers recently completed the installation of five new deep solar wells, serving over 2,000 residents daily.",
                    "category": "Water Aid",
                    "author_id": admin.id,
                    "campaign_id": med_c.id if med_c else None,
                    "image_key": f"{base_url}/static/campaigns/medicine-campaign.jpeg",
                    "published": True,
                    "published_at": datetime.now(timezone.utc),
                },
            ]
            for bdata in blog_data:
                db.add(BlogPost(**bdata))
            await db.commit()
            print(f"Seeded {len(blog_data)} Blog Posts.")

        # 6. Gallery Photos
        res = await db.execute(select(GalleryPhoto))
        if not res.scalars().all():
            categories = ["Water Aid", "Education", "Medical Aid", "Food Aid", "Housing", "Emergency"]
            gallery_data = []
            for i in range(1, 18):
                num_str = f"{i:02d}"
                cat = categories[(i - 1) % len(categories)]
                gallery_data.append(
                    {
                        "image_key": f"{base_url}/static/gallery/gallery-{num_str}.jpg",
                        "category": cat,
                        "alt_text": f"Community outreach photo {i} - {cat}",
                    }
                )
            for gdata in gallery_data:
                db.add(GalleryPhoto(**gdata))
            await db.commit()
            print(f"Seeded {len(gallery_data)} Gallery Photos.")

        # 7. Zakat Settings
        res = await db.execute(select(ZakatSetting))
        if not res.scalars().all():
            zakat = ZakatSetting(
                nisab_value=520.00,
                updated_by=admin.id,
            )
            db.add(zakat)
            await db.commit()
            print("Seeded Zakat Setting (Nisab: $520.00).")

        print("Database seeding completed successfully!")

    await engine.dispose()


if __name__ == "__main__":
    upload_static_files_to_minio()
    asyncio.run(seed_data())
