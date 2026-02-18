from typing import TYPE_CHECKING
from sqlalchemy import String, Float, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import Optional

if TYPE_CHECKING:
    from .category import Category

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    asin: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    list_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    discount_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reviews_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_prime: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    best_sellers_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bullet_points: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    main_image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=False)
    category: Mapped["Category"] = relationship(back_populates="products")