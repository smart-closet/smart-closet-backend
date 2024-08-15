from fastapi import APIRouter

from api.routes import items, attributes

api_router = APIRouter()
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(attributes.router, prefix="/attributes", tags=["attributes"])
