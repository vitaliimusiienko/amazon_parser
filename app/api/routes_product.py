from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import ProductResponse

from app.services.amazon_parser import parse_category_full
from app.services.category_service import get_or_create_category
from app.services.product_service import ProductService

router = APIRouter()


class ParseRequest(BaseModel):
    category_url: str


@router.get("/", response_model=list[ProductResponse])
async def get_products(
    category_url: str = Query(None, description="Filter by category URL"),
    min_rating: float = Query(None, description="Minimal rating"),
    max_price: float = Query(None, description="Maximal price"),
    sort_by: str = Query(None, description="Sort by (price, rating, -rating)"),
    db: AsyncSession = Depends(get_db),
):
    products = await ProductService.get_filtered_products(db, category_url, min_rating, max_price, sort_by)
    return products


@router.post("/parse")
async def parse_category(request: ParseRequest, db: AsyncSession = Depends(get_db)):
    category = await get_or_create_category(db, request.category_url)

    if await ProductService.check_products_exist(db, category.id):
        return {
            "status": "success",
            "detail": "Data already exists in database. Skipping Playwright.",
            "cached": True
        }

    products_data = await parse_category_full(request.category_url)
    
    if not products_data:
        raise HTTPException(status_code=404, detail="Amazon returned no products")

    await ProductService.save_parsed_products(db, products_data, category.id)

    return {
        "status": "success",
        "detail": f"Successfully parsed {len(products_data)} products",
        "cached": False
    }
