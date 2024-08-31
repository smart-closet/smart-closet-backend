import torch
from torchvision import transforms
from torch.autograd import Variable
import csv
import time
#from lib.df1 import DeepFashion1Model
from PIL import Image
import os
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time


import speech_recognition
import tempfile
from gtts import gTTS
from pygame import mixer





#獲取天氣資訊

def getWeatherData(city, place, current_Time=None):


    district = {
        '宜蘭縣': '01', '桃園市': '05', '臺北市': '61', '新北市': '69', '臺中市': '73', '臺南市': '77',
        '高雄市': '65', '新竹縣': '09', '苗栗縣': '13', '彰化縣': '17', '南投縣': '21', '雲林縣': '25',
        '嘉義縣': '29', '屏東縣': '33', '花蓮縣': '41', '臺東縣': '37', '澎湖縣': '45', '金門縣': '85',
        '連江縣': '81', '基隆市': '49', '新竹市': '53', '嘉義市': '57'
    }
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-0" + district[city]

    # 資料是每3個小時更新一次，如果沒輸入時間就 default 是現在時間，取離現在時間最近的前一筆資料
    if current_Time is None:
        current_Time = datetime.now()
    current_time_str = current_Time.strftime('%Y-%m-%dT%H:%M:%S')

    params = {
        "Authorization": "CWA-7EBCB64E-EA36-4A13-9D77-82DC3F7E877C",
        "elementName": ['PoP6h', 'WeatherDescription', 'CI', 'T', 'AT'],
        "locationName": [place],
        "timeFrom": current_time_str
    }

    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # 若請求失敗會引發 HTTPError
            data = pd.read_json(response.text)
            data = data.loc['locations', 'records'][0]['location']
            info_now = {}
            for element in data[0]['weatherElement']:
                info_now[element['description']] = element['time'][0]['elementValue'][0]['value']
            return info_now
        except requests.exceptions.RequestException as e:
            print(f"網路異常，請耐心等待")
            retries += 1
            time.sleep(2)  # 等待2秒後重試
        except (KeyError, IndexError) as e:
            print(f"Parsing failed: {e}. Retrying ({retries + 1}/{max_retries})...")
            retries += 1
            time.sleep(2)  # 等待2秒後重試

    print("Failed to retrieve data after multiple retries.")
    return None




# 天氣篩選

def split_clothing_dict(data):
    # Initialize list of dictionaries to hold the split data
    split_data = []
    
    # Loop over the indices to create separate dictionaries
    for i in range(0,len(data['body_tempture'])):
        # Create a new dictionary for each temperature
        temp_dict = {
            'body_tempture': data['body_tempture'][i],
            'material': data['material'][i],
            'subcategories': data['subcategories'][i],
            'outer_layer': data['outer_layer'][i],
        }
        split_data.append(temp_dict)
    
    return split_data



def weather_rule_Base(input_data, personal_temp=0):
    
    body_temp = int(input_data['體感溫度']) - personal_temp
    
    candidate_attribute=[]
    candidate_cloth_type=[]
    Final_recommend={'body_tempture':[],'material':[],'subcategories':[],'outer_layer':[],'Note':[]}

    
    
    #所有溫度皆適合的服飾 及和溫度無關的材質(花紋)
    All_temp_cloth =['pants','cotton-pants','sweatpants','long-skirt','jeans','jumpsuit','overalls','leggings','sweatpants']
    All_temp_attr = []
    Clothe_type={1:['tank-top','dress','skirt','shorts','t-shirt','shirt','polo-shirt','tank-top','suit-pants','sheer','yoga-pants','short-sleeve button-up shirt','short-sleeve flannel shirt'],
                 2:['dress','skirt','shorts','t-shirt','shirt','polo-shirt','knit-top','suit-pants','yoga-pants','sheer','short-sleeve button-up shirt'
'short-sleeve flannel shirt'],
                 3:['dress','pants','shorts','suit-pants','yoga-pants','overalls'],
                 4:['long-sleeve button-up shirt','hoodie','long-sleeve-shirt'],
                 5:['long-sleeve flannel-shirt','long-sleeve button-up shirt','hoodie','turtleneck','long-sleeve-shirt'],
                 6:['sweater','hoodie','turtleneck','college-sweatshirt','long-sleeve-shirt'],
                 7:['sweater','hoodie','turtleneck','wool-pants','windproof-pants','college-sweatshirt','long-sleeve-shirt'],
                 8:['sweater','hoodie','turtleneck','wool-pants','windproof-pants','college-sweatshirt']}
    #不同等級的外套
    Outer_layer={0:['vest','cotton-vest'],1:['sweater-vest','jacket','suit-jacket','denim-jacket'],2:['insulated-vest','leather-jacket','coat','trench-coat','cotton-coat','padded-jacket','down-jacket'],3:['padded-jacket','down-jacket','ski-jacket','winter-sportswear']}
    #材質分為三種，透氣0，中性1，保暖2
    Fabric_type={0:['cotton','linen','linen-blend','satin','denim','chiffon'],1:['cotton','knit','nylon','faux-suede','chiffon'],2:['velvet','cotton','woven','crochet','faux-fur','faux-leather']}
    
    #如果是極端熱的情況 -> 材質選:透氣，服裝種類選:1度C
    if (body_temp >= 27):
        candidate_cloth_type += list(set(Clothe_type[1] + Clothe_type[2]))
        Final_recommend['body_tempture'].append(body_temp)
        Final_recommend['material'].extend(Fabric_type[0])
        Final_recommend['subcategories'].extend(candidate_cloth_type)
    #如果是極端冷的情況 -> 材質選:保暖, 服裝種類選 7~8 度C, 建議洋蔥式穿搭                             
    elif (body_temp <= 13):

        if (body_temp <= 5): #霸王寒流級(建議洋蔥式穿搭)
            candidate_cloth_type += list(set(Clothe_type[7]+Clothe_type[8]))
            Final_recommend['outer_layer'].extend(Outer_layer[3])
            Final_recommend['Note'].append( 'thermal-underwear')
        else: #小冬天
            candidate_cloth_type += list(set(Clothe_type[6]+Clothe_type[7]))
            Final_recommend['outer_layer'].extend(Outer_layer[2])
        
        Final_recommend['body_tempture'].append(body_temp)
        Final_recommend['material'].extend(Fabric_type[2])
        Final_recommend['subcategories'].extend(candidate_cloth_type)

    #正常情況
    else:
        # 比較偏熱的情況下(22~26)，材質的選擇於0-2度C,間度1度C
        temp_rang = [body_temp + 2, body_temp, body_temp - 2]
        for temp in temp_rang:
            Final_recommend['body_tempture'].append(temp)
            target = max(1, min(25 - temp, 5))
            if (temp >= 26):
                Final_recommend['material'].append(Fabric_type[0])
                Final_recommend['subcategories'].append(Clothe_type[1])
                Final_recommend['outer_layer'].append([])
            elif (temp >= 21):#類型適合[1,2,3]
                Final_recommend['material'].append(Fabric_type[0])
                Final_recommend['subcategories'].append(Clothe_type[target])
                Final_recommend['outer_layer'].append(Outer_layer[0])
            elif (temp >= 14):
                Final_recommend['material'].append(Fabric_type[2]) #不確定要不要加0
                Final_recommend['subcategories'].append(Clothe_type[target])
                Final_recommend['outer_layer'].append(Outer_layer[1])
            else:
                Final_recommend['material'].append(Fabric_type[2]) #不確定要不要加
                Final_recommend['subcategories'].append(Clothe_type[8])
                Final_recommend['outer_layer'].append(Outer_layer[2])
                
    
 
    if (len(Final_recommend['body_tempture'])>=2): 
        #print("ok")
        for i in Final_recommend['subcategories']:
            i.extend(All_temp_cloth)
        Final_recommend=split_clothing_dict(Final_recommend)
    else:   
        Final_recommend['subcategories'].extend(All_temp_cloth)
        Final_recommend=[Final_recommend]                    
    return Final_recommend

#場合篩選

def occation_filter(user_occation):
    data={'occation':[],'pattern':[],'material':[],'subcategories':[],'戶外與否':[]}
    occation_cloth_type = {
        'Dating': [
            'long-skirt', 'dress', 't-shirt', 'sweater', 
            'dress-shirt', 'long-sleeve flannel-shirt', 
            'long-sleeve button-up shirt', 'short-sleeve button-up shirt', 
            'short-sleeve flannel shirt', 'pants', 'jeans', 'cotton-pants','shorts'
        ],
        'Daily_Work_and_Conference': [
            'dress-shirt', 'jeans', 't-shirt', 'sweater', 
            'pants', 'long-skirt', 'cotton-pants', 'shirt', 
            'suit-jacket', 'button-up-shirt', 'long-sleeve button-up shirt'
        ],
        'Travel': ['t-shirt', 'pants'],
        'Sports': ['t-shirt', 'shorts', 'yoga-pants', 'sweatpants'],
        'Prom': [
            'skirt', 'shirt', 'sweater', 'pants', 'long-skirt'
        ],
        'Shopping': ['pants', 't-shirt', 'skirt', 'cotton-pants', 'shirt', 'shorts'],
        'Party': [
            'dress', 'long-skirt', 'cotton-pants', 'suit-jacket', 
            'pants', 'button-up-shirt', 'dress-shirt'
        ],
        'School': [
            'pants', 'jeans', 't-shirt', 'hoodie', 'sweater', 'college-sweatshirt','shorts','shirt','short-sleeve button-up shirt','short-sleeve flannel shirt','long-sleeve button-up shirt','long-sleeve-shirt'
        ],
        'Wedding_Guest': [
            'dress', 'dress-shirt', 'long-sleeve button-up shirt', 
            'short-sleeve button-up shirt', 'cotton-pants'
        ]
    }
    occation_cloth_textrue = {'Dating':['chiffon', 'leather', 'denim', 'cotton', 'faux-fur', 'faux-leather', 'faux-suede', 'leather', 'suede', 'woven', 'thermal', 'velvet'],
                  'Daily_Work_and_Conference':['denim','cotton'],
                  'Travel':['chiffon','cotton','denim','cotton-pants'],
                  'Sports':['cotton','Nylon'],
                  'Prom':['leather','chiffon','cutton','velvet'],
                  'Shopping':['leather','denim','cotton','chiffon',],
                  'Party':['chiffon','crochet','sheer','velvet'],
                  'School':['leather','cotton','denim', 'woven'],
                  'Wedding_Guest':['cotton','leather','chiffon']}
    occation_cloth_Fabric = {
                  'Dating': ['print', 'pleated', 'striped', 'floral', 'animal', 'paisley-print', 'abstract-print'],
                  'Daily_Work_and_Conference': ['striped', 'print', 'grid-print', 'dotted', 'colorblock'],
                  'Travel': ['print', 'striped', 'paisley-print', 'camouflage', 'colorblock'],
                  'Sports': ['camouflage', 'graphic', 'tie-dye', 'dotted', 'abstract-print'],
                  'Prom': ['print', 'pleated', 'floral', 'glitter', 'ornate-print', 'baroque'],
                  'Shopping': ['print', 'striped', 'floral', 'graphic', 'dotted', 'paisley-print'],
                  'Party': ['pleated', 'floral', 'print', 'glitter', 'colorblock', 'zebra-print'],
                  'School': ['striped', 'print', 'grid-print', 'abstract-print', 'dotted'],
                  'Wedding_Guest': ['floral', 'paisley-print', 'abstract-print', 'ornate-print', 'marble-print']}

    
    Indoor_activity = ['Conference','Porm','Party','Wedding_Guest']
    Outdoor= False
    
    if (user_occation not in Indoor_activity):
        Outdoor = True
    data['occation'] = user_occation
    data['pattern'] = occation_cloth_Fabric[user_occation]
    data['subcategories'] = occation_cloth_type[user_occation]
    data['material'] = occation_cloth_textrue[user_occation]
    data['戶外與否'] = Outdoor
    
    return data


def rule_base_filter(city,place,consider_weather=True, user_occation=None,personal_temp=0):

    #如果只考量天氣不考慮環境
    if (consider_weather == True and user_occation==None):
        weather_info = getWeatherData(city, place)
        candidate = weather_rule_Base(weather_info)
    #只考量場合不考慮天氣 (不想考慮 or 室內)
    elif (consider_weather == False and user_occation!='None') or ( occation_filter(user_occation)['戶外與否']==False):
        candidate = occation_filter(user_occation)
    #考量天氣與場合
    else:
        weather_info = getWeatherData(city, place)
        candidate = weather_rule_Base(weather_info)
        #測試用
        #candidate = weather_rule_Base(inputdata)
        #print(candidate)
        occation_info = occation_filter(user_occation)
        #print(occation_info)
        for i in range(0,len(candidate)):

            item = candidate[i]["material"]
            candidate[i]["material"] = list(set(item) & set(occation_info["material"]))
            #item = candidate["種類"][i]
            item = candidate[i]["subcategories"]
            candidate[i]["subcategories"] = list(set(item) & set(occation_info["subcategories"]))
   
            #candidate["種類"][i] =  item

    return candidate


### 情境




def scenario_filter(user_scenario):
    # Set up Gemini API
    load_dotenv()
    #這裡改
    
    genai.configure(api_key='AIzaSyB2UIdAswA9HLc6jM9sFmh-6KrSoaSO2F8')
    #genai.configure(api_key=os.getenv(GEMINI_API_KEY))
    model = genai.GenerativeModel("gemini-1.5-flash-latest")


    genai.configure(api_key='AIzaSyB2UIdAswA9HLc6jM9sFmh-6KrSoaSO2F8')
    #genai.configure(api_key=os.getenv(GEMINI_API_KEY))
    model = genai.GenerativeModel("gemini-1.5-flash-latest")

    # define prompt
    prompt = """Please consider the following scenario a user describe 
    and pick the cloths that satisfy the scenario, please only list the satisfy clothes, materials, patterns, mixed_categories without more describtion, 
    and output the answers as jyson fromat, where the keys are clothes, materials, patterns and the corresponding answer show place at the value :

    clothing_items = [
        "t-shirt", "shirt", "dress-shirt", "button-up-shirt", "flannel-shirt", "sweater", 
        "hoodie", "jacket", "coat", "trench-coat", "suit-jacket", "denim-jacket", 
        "leather-jacket", "polo-shirt", "knit-top", "vest", "sweater-vest", "tank-top", 
        "turtleneck", "dress", "skirt", "long-skirt", "pants", "jeans", "shorts", 
        "suit-pants", "yoga-pants", "sweatpants", "overalls", "jumpsuit", "pajamas", 
        "bathrobe", "cotton-pants", "wool-pants", "leggings", "windproof-pants", 
        "cotton-vest", "down-jacket", "ski-jacket", "cotton-coat", "thermal-underwear", 
        "padded-jacket", "winter-sportswear", "insulated-vest", "thick-jeans", 
        "college-sweatshirt"
    ]

    materials = [
        'cotton', 'denim', 'chiffon', 'faux-fur', 'faux-leather',
        'faux-suede', 'leather', 'linen', 'linen-blend', 'mesh',
        'metallic', 'neoprene', 'nylon', 'organza', 'sateen',
        'satin', 'suede', 'velvet', 'woven', 'thermal', 'crochet']
    patterns = [
        'abstract-print', 'animal', 'baroque', 'bird-print',
        'botanical-print', 'camouflage', 'colorblock', 'dotted',
        'floral', 'glitter', 'graphic', 'grid-print', 'leaf-print',
        'leopard-print', 'marble-print', 'medallion-print',
        'mixed-print', 'multi-stripe', 'ombre', 'ornate-print',
        'paisley-print', 'palm-print', 'pattern', 'pleated',
        'print', 'striped', 'tie-dye', 'zigzag']
    mixed_categories = [
        'boho', 'cargo', 'chic', 'cozy',
        'cute', 'elegant', 'everyday', 'fancy', 'retro',
        'safari', 'sporty', 'sweet', 'utility']



    The given user sencario are:
    """
    #user_scenario = '我今天要報告希望看起來正式又專業'
    response = model.generate_content(prompt + user_scenario)
    gemini_results_test = json.loads(response.text.replace("```json","").replace("```",""))
    return [gemini_results_test]

