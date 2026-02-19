from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import Product, Category
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class ProductService:
    @staticmethod
    async def get_filtered_products(
        db: AsyncSession,
        category_url: str | None = None,
        min_rating: float | None = None,
        max_price: float | None = None,
        sort_by: str | None = None
    ) -> Sequence[Product]:
        query = select(Product)

        if category_url:
            query = query.join(Category).where(Category.url == category_url)

        if min_rating is not None:
            query = query.where(Product.rating >= min_rating)

        if max_price is not None:
            query = query.where(Product.price <= max_price)

        if sort_by == "price":
            query = query.order_by(Product.price.asc())
        elif sort_by == "-price":
            query = query.order_by(Product.price.desc())
        elif sort_by == "rating":
            query = query.order_by(Product.rating.desc())

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def check_products_exist(db: AsyncSession, category_id: int) -> bool:
        query = select(func.count(Product.id)).where(Product.category_id == category_id)
        result = await db.execute(query)
        count = result.scalar() or 0
        return count > 0

    @classmethod
    async def save_parsed_products(
        cls, db: AsyncSession, product_data: list[dict[str, Any]], category_id: int
    ) -> int:
        try:
            processed_count = 0
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
                
                processed_count += 1

            await db.commit()
            logger.info(f"Successfully processed {processed_count} products")
            return processed_count

        except Exception as e:
            logger.error(f"Error in processing products in db: {e}")
            await db.rollback()
            raise