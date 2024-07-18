import os
from typing import Union
from fastapi import APIRouter

from datetime import datetime
import requests
import pandas as pd
from dotenv import load_dotenv

router = APIRouter(prefix="/context", tags=["context"])

city_code = {
    "宜蘭縣": "01",
    "桃園市": "05",
    "臺北市": "61",
    "新北市": "69",
    "臺中市": "73",
    "臺南市": "77",
    "高雄市": "65",
    "新竹縣": "09",
    "苗栗縣": "13",
    "彰化縣": "17",
    "南投縣": "21",
    "雲林縣": "25",
    "嘉義縣": "29",
    "屏東縣": "33",
    "花蓮縣": "41",
    "臺東縣": "37",
    "澎湖縣": "45",
    "金門縣": "85",
    "連江縣": "81",
    "基隆市": "49",
    "新竹市": "53",
    "嘉義市": "57",
}


@router.get("/weather")
async def get_weather(city: str, place: str, current_Time: Union[str, None] = None):
    load_dotenv()
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-0" + city_code[city]

    if current_Time is None:
        current_Time = datetime.now()
    current_time_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    params = {
        "Authorization": os.getenv("WEATHER_API_KEY"),
        "elementName": ["PoP6h", "WeatherDescription", "CI", "T", "AT"],
        "locationName": [place],
        "timeFrom": current_time_str,
    }

    response = requests.get(url, params=params)
    data = pd.read_json(response.text)
    data = data.loc["locations", "records"][0]["location"]
    info_now = {}
    for element in data[0]["weatherElement"]:
        info_now[element["description"]] = element["time"][0]["elementValue"][0][
            "value"
        ]
    return info_now
