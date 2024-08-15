from fastapi import FastAPI
from api.main import api_router

# FastAPI app
app = FastAPI()
app.include_router(api_router)