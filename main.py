from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.main import api_router
from firebase_admin import credentials
import firebase_admin

# FastAPI app
app = FastAPI()

# Firebase storage
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'quiztory-f5e09.appspot.com'
})

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
