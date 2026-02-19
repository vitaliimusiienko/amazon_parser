from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Category
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def get_or_create_category(db: AsyncSession, category_url: str) -> Category:
    try:
        result = await db.execute(select(Category).where(Category.url == category_url))
        category = result.scalars().first()

        if category:
            logger.info(f"Category found in db: {category_url}")
            return category

        logger.info(f"Creating new category: {category_url}")

        category_name = category_url.strip("/").split("/")[-1].replace("-", " ").title()
        new_category = Category(name=category_name, url=category_url)
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)

        return new_category

    except Exception as e:
        logger.error(f"Error in get/create category: {e}")
        await db.rollback()
        raise


async def get_all_categories(db: AsyncSession):
    result = await db.execute(select(Category))
    return result.scalars().all()
