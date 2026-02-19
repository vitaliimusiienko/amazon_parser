from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.category_service import get_all_categories
from app.schemas.category import CategoryResponse
from app.utils.scheduler import sync_amazon_categories

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    categories = await get_all_categories(db)
    return categories

@router.post("/api/admin/force-sync-categories")
async def force_sync_categories(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_amazon_categories)
    return {"message": "Syncing category"}
