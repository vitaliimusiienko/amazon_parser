from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

class ParseRequest(BaseModel):
    category_url: str

@router.get("/")
async def get_product(
    min_rating: float = Query(None, description="Minimum rating for filtering products"),
    max_price: float = Query(None, description="Maximum price for filtering products"),
    sort_by: str = Query(None, description="Field to sort by (e.g., 'price', 'rating')")
):
    return {
        "message": "This endpoint will return products based on the provided filters and sorting options.",
        "filters": {
            "min_rating": min_rating,
            "max_price": max_price
        },
        "sort_by": sort_by
    }

@router.post("/parse")
async def parse_category(request: ParseRequest):
    return {
        "message": "This endpoint will parse the category URL and return the products.",
        "category_url": request.category_url
    }