from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Product
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def save_parsed_products(
    db: AsyncSession, product_data: list[dict[str, Any]], category_id: int
) -> None:
    try:
        for item in product_data:
            asin = item.get("asin")
            if not asin:
                continue

            result = await db.execute(select(Product).where(Product.asin == asin))
            existing_product = result.scalars().first()

            if existing_product:
                logger.info(f"Updating data for ASIN: {asin}")
                for key, value in item.items():
                    setattr(existing_product, key, value)
                existing_product.category_id = category_id

            else:
                logger.info(f"✨ Creating new data for ASIN: {asin}")
                new_product = Product(**item, category_id=category_id)
                db.add(new_product)

        await db.commit()
        logger.info(f"Successfully processed {len(product_data)} products")

    except Exception as e:
        logger.error(f"Error in processing products in db: {e}")
        await db.rollback()
        raise
