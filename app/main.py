from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.db.session import engine, get_db
from app.db.base import Base

from app.api.routes_categories import router as categories_router
from app.api.routes_product import router as product_router
from app.utils.scheduler import sync_amazon_categories

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        scheduler.add_job(
        sync_amazon_categories, 
        CronTrigger(hour=3, minute=0), 
        id="sync_categories_daily",
        replace_existing=True
    )
        await conn.run_sync(Base.metadata.create_all)
        scheduler.start()
    yield

    scheduler.shutdown()


app = FastAPI(
    title="Amazon Best Sellers Parser API",
    description="API for parsing Amazon Best Sellers data and storing it in a database.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories_router)
app.include_router(product_router)
