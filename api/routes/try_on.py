from typing import List
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
import os
from service.virtual_try_on_utils import send_request, construct_data

router = APIRouter()

load_dotenv()
api_key = os.getenv("VIRTUAL_TRY_ON_API_KEY")
api_url = "https://api.segmind.com/v1/idm-vton"


@router.post("/")
async def process_images(request: List[str]):
    for url in request:
        print("received url: ", url, "\n")
    try:
        if len(request) == 2:
            data = construct_data(request[0], request[1], "dresses")
            result = await send_request(data, api_url, api_key)
            return {"result": result}
        elif len(request) == 3:
            data = construct_data(request[0], request[1], mode="upper_body")
            first_result = await send_request(data, api_url, api_key)
            second_data = construct_data(first_result, request[2], mode="lower_body")
            final_result = await send_request(second_data, api_url, api_key)
            return {"result": final_result}
        else:
            raise HTTPException(status_code=400, detail="Invalid number of images.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
