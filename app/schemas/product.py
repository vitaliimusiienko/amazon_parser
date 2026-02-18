from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProductBase(BaseModel):
    asin: str
    title: str
    rank: int
    price: Optional[float] = None
    list_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    is_prime: Optional[bool] = None
    best_seller_rank: Optional[int] = None
    bullet_points: Optional[str] = None
    main_image_url: Optional[str] = None


class ProductCreate(ProductBase):
    category_id: int


class ProductResponse(ProductBase):
    id: int
    category_id: int

    model_config = ConfigDict(from_attributes=True)
