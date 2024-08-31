from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.main import api_router


import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# FastAPI app
app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
