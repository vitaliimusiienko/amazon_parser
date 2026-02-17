from fastapi import APIRouter

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/")
async def get_categories():
    return {"message": "List of categories"}