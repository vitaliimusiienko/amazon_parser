from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.product import Product
from app.schemas import ProductResponse

from app.services.amazon_parser import parse_category_full
from app.services.category_service import get_or_create_category
from app.services.product_service import save_parsed_products

router = APIRouter()


class ParseRequest(BaseModel):
    category_url: str


@router.get("/", response_model=ProductResponse)
async def get_products(
    min_rating: float = Query(None, description="Minimal price"),
    max_price: float = Query(None, description="Maximal price"),
    sort_by: str = Query(None, description="Sort by (price, rating, -rating)"),
    db: AsyncSession = Depends(get_db),
):

    query = select(Product)

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
    products = result.scalars().all()

    return products


@router.post("/parse")
async def parse_category(request: ParseRequest, db: AsyncSession = Depends(get_db)):
    try:
        products_data = await parse_category_full(request.category_url)

        if not products_data:
            raise HTTPException(status_code=404, detail="Parser not found products")

        category = await get_or_create_category(db, request.category_url)

        await save_parsed_products(db, products_data, category.id)

        return {
            "status": "success",
            "detail": f"Successfully parsed {len(products_data)} products",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
