from fastapi import APIRouter

from api.routes import items, attributes, outfits

api_router = APIRouter()
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(attributes.router, prefix="/attributes", tags=["attributes"])
api_router.include_router(outfits.router, prefix="/outfits", tags=["outfits"])
