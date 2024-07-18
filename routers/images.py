from fastapi import APIRouter, UploadFile, File
from utils.df1 import DeepFashion1Model
from PIL import Image


router = APIRouter(prefix="/images", tags=["images"])


@router.post("/attributes/")
async def get_image_attribute(file: UploadFile = File(...)):
    df1_model = DeepFashion1Model()
    img = Image.open(file.file).convert("RGB")

    return df1_model.infer(img, 0.13)
