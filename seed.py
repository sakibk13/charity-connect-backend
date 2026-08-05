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
    engine = create_async_engine(settings.effective_database_url, echo=False)
    async with engine.begin() as conn:
        from app.db.base import Base
        await conn.run_sync(Base.metadata.create_all)

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
        if "localhost" in base_url or not base_url:
            base_url = ""

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

        # Commented out legacy campaigns as requested:
        # {
        #     "title": "Emergency Flood Relief Campaign",
        #     "slug": "flood-relief", ...
        # },
        # {
        #     "title": "Life-Saving Medicine & Medical Supplies",
        #     "slug": "medicine-campaign", ...
        # },
        # {
        #     "title": "Ramadan Food Packs & Iftar Distribution",
        #     "slug": "ramadan-campaign", ...
        # }

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
                "title": "Share Meals",
                "slug": "share-meals",
                "description": "Distributing hot nutritious meals and monthly food packs to hungry families, widows, and orphans.",
                "category": "Food Aid",
                "goal": 18000.00,
                "raised": 13100.00,
                "image_key": f"{base_url}/static/campaigns/share-meals.jpg",
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
        ]

        existing_slugs = {c.slug for c in existing_campaigns}
        for cdata in campaigns_data:
            if cdata["slug"] not in existing_slugs:
                c = Campaign(**cdata)
                db.add(c)
                await db.commit()
                await db.refresh(c)
                campaign_map[c.slug] = c
            else:
                c_obj = next(c for c in existing_campaigns if c.slug == cdata["slug"])
                campaign_map[c_obj.slug] = c_obj
        print(f"Seeded/Updated {len(campaigns_data)} Featured Appeals.")

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
        existing_gallery = res.scalars().all()
        categories = ["Water Aid", "Education", "Medical Aid", "Food Aid", "Housing", "Emergency"]

        gallery_dir = "/code/static/gallery" if os.path.exists("/code/static/gallery") else "static/gallery"
        image_files = []
        if os.path.exists(gallery_dir):
            image_files = sorted(
                [f for f in os.listdir(gallery_dir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
            )

        existing_keys = {g.image_key for g in existing_gallery}
        new_photos_count = 0

        for idx, filename in enumerate(image_files):
            img_key = f"{base_url}/static/gallery/{filename}"
            if img_key not in existing_keys:
                cat = categories[idx % len(categories)]
                db.add(
                    GalleryPhoto(
                        image_key=img_key,
                        category=cat,
                        alt_text=f"Community outreach photo - {cat}",
                    )
                )
                new_photos_count += 1

        if new_photos_count > 0:
            await db.commit()
            print(f"Seeded {new_photos_count} new Gallery Photos (Total in folder: {len(image_files)}).")
        else:
            print(f"Gallery photos up to date (Total in folder: {len(image_files)}).")

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
