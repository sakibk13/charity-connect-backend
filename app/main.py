from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.storage import ensure_bucket_cors
from seed import seed_data


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    try:
        ensure_bucket_cors()
    except Exception as exc:
        print(f"Storage CORS info: {exc}")

    try:
        await seed_data()
    except Exception as exc:
        print(f"Automatic seed info: {exc}")
    yield


app = FastAPI(title="Charity Connect API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"],
    allow_origin_regex=r"https://.*\.vercel\.app|https://charity-connect-web\.vercel\.app|https?://(localhost|127\.0\.0\.1)(:[0-9]+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles

static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
elif os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

