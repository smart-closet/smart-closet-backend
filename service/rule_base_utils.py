import csv
import json
import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
df2_api_key = os.getenv("DF2_API_KEY")


def load_subcategory_mapping():
    subcategory_mapping = {}
    with open("tools/subcategory.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            subcategory_mapping[row["value"]] = int(row["id"])
    return subcategory_mapping


def weather_rule_base(temperature, personal_temp=0):
    body_temp = int(temperature - personal_temp)

    candidate_subcategories = []
    final_recommend = {
        "body_temp": body_temp,
        "material": [],
        "subcategories": [],
        "outer_layer": [],
    }

    # 所有溫度皆適合的服飾 及和溫度無關的材質(花紋)
    all_temp_cloth = [
        "pants",
        "cotton-pants",
        "sweatpants",
        "long-skirt",
        "jeans",
        "jumpsuit",
        "overalls",
        "leggings",
        "sweatpants",
    ]
    
    # 不同等級的服裝種類
    subcategories = {
        1: [
            "tank-top",
            "dress",
            "skirt",
            "shorts",
            "t-shirt",
            "shirt",
            "polo-shirt",
            "tank-top",
            "suit-pants",
            "sheer",
            "yoga-pants",
            "short-sleeve button-up shirt",
            "short-sleeve flannel-shirt",
        ],
        2: [
            "dress",
            "skirt",
            "shorts",
            "t-shirt",
            "shirt",
            "polo-shirt",
            "knit-top",
            "suit-pants",
            "yoga-pants",
            "sheer",
            "short-sleeve button-up shirt",
            "short-sleeve flannel-shirt",
        ],
        3: ["dress", "pants", "shorts", "suit-pants", "yoga-pants", "overalls"],
        4: ["long-sleeve button-up shirt", "hoodie", "long-sleeve-shirt"],
        5: [
            "long-sleeve flannel-shirt",
            "long-sleeve button-up shirt",
            "hoodie",
            "turtleneck",
            "long-sleeve-shirt",
        ],
        6: [
            "sweater",
            "hoodie",
            "turtleneck",
            "college-sweatshirt",
            "long-sleeve-shirt",
        ],
        7: [
            "sweater",
            "hoodie",
            "turtleneck",
            "wool-pants",
            "windproof-pants",
            "college-sweatshirt",
            "long-sleeve-shirt",
        ],
        8: [
            "sweater",
            "hoodie",
            "turtleneck",
            "wool-pants",
            "windproof-pants",
            "college-sweatshirt",
        ],
    }
    
    # 不同等級的外套
    outer_layer = {
        0: ["vest", "cotton-vest"],
        1: ["sweater-vest", "jacket", "suit-jacket", "denim-jacket"],
        2: [
            "insulated-vest",
            "leather-jacket",
            "coat",
            "trench-coat",
            "cotton-coat",
            "padded-jacket",
            "down-jacket",
        ],
        3: ["padded-jacket", "down-jacket", "ski-jacket", "winter-sportswear"],
    }
    
    # 材質分為三種，透氣0，中性1，保暖2
    materials = {
        0: ["cotton", "linen", "linen-blend", "satin", "denim", "chiffon"],
        1: ["cotton", "knit", "nylon", "faux-suede", "chiffon"],
        2: ["velvet", "cotton", "woven", "crochet", "faux-fur", "faux-leather"],
    }

    # 如果是極端熱的情況 -> 材質選:透氣，服裝種類選:1度C
    if body_temp >= 27:
        candidate_subcategories += list(set(subcategories[1] + subcategories[2]))
        final_recommend["material"].extend(materials[0])
        final_recommend["subcategories"].extend(candidate_subcategories)
    
    # 如果是極端冷的情況 -> 材質選:保暖, 服裝種類選 7~8 度C, 建議洋蔥式穿搭
    elif body_temp <= 13:
        if body_temp <= 5:  # 霸王寒流級(建議洋蔥式穿搭)
            candidate_subcategories += list(set(subcategories[7] + subcategories[8]))
            final_recommend["outer_layer"].extend(outer_layer[3])
        else:  # 小冬天
            candidate_subcategories += list(set(subcategories[6] + subcategories[7]))
            final_recommend["outer_layer"].extend(outer_layer[2])

        final_recommend["material"].extend(materials[2])
        final_recommend["subcategories"].extend(candidate_subcategories)

    # 正常情況
    else:
        # 比較偏熱的情況下(22~26)，材質的選擇於0-2度C,間度1度C
        target = max(1, min(25 - body_temp, 5))
        if body_temp >= 26:
            final_recommend["material"].extend(materials[0])
            final_recommend["subcategories"].extend(subcategories[1])
            final_recommend["outer_layer"].extend([])
        elif body_temp >= 21:  # 類型適合[1,2,3]
            final_recommend["material"].extend(materials[0])
            final_recommend["subcategories"].extend(subcategories[target])
            final_recommend["outer_layer"].extend(outer_layer[0])
        elif body_temp >= 14:
            final_recommend["material"].extend(materials[2])  # 不確定要不要加0
            final_recommend["subcategories"].extend(subcategories[target])
            final_recommend["outer_layer"].extend(outer_layer[1])
        else:
            final_recommend["material"].extend(materials[2])  # 不確定要不要加
            final_recommend["subcategories"].extend(subcategories[8])
            final_recommend["outer_layer"].extend(outer_layer[2])
    
    final_recommend["subcategories"].extend(all_temp_cloth)
    
    return final_recommend


# 場合篩選
def occasion_filter(user_occasion):
    occasion_cloth_subcategory = {
        "Dating": [
            "long-skirt",
            "dress",
            "t-shirt",
            "sweater",
            "dress-shirt",
            "long-sleeve flannel-shirt",
            "long-sleeve button-up shirt",
            "short-sleeve button-up shirt",
            "short-sleeve flannel-shirt",
            "pants",
            "jeans",
            "cotton-pants",
            "shorts",
        ],
        "Daily_Work_and_Conference": [
            "dress-shirt",
            "jeans",
            "t-shirt",
            "sweater",
            "pants",
            "long-skirt",
            "cotton-pants",
            "shirt",
            "suit-jacket",
            "button-up-shirt",
            "long-sleeve button-up shirt",
        ],
        "Travel": ["t-shirt", "pants"],
        "Sports": ["t-shirt", "shorts", "yoga-pants", "sweatpants"],
        "Prom": ["skirt", "shirt", "sweater", "pants", "long-skirt"],
        "Shopping": ["pants", "t-shirt", "skirt", "cotton-pants", "shirt", "shorts"],
        "Party": [
            "dress",
            "long-skirt",
            "cotton-pants",
            "suit-jacket",
            "pants",
            "button-up-shirt",
            "dress-shirt",
        ],
        "School": [
            "pants",
            "jeans",
            "t-shirt",
            "hoodie",
            "sweater",
            "college-sweatshirt",
            "shorts",
            "shirt",
            "short-sleeve button-up shirt",
            "short-sleeve flannel shirt",
            "long-sleeve button-up shirt",
            "long-sleeve-shirt",
        ],
        "Wedding_Guest": [
            "dress",
            "dress-shirt",
            "long-sleeve button-up shirt",
            "short-sleeve button-up shirt",
            "cotton-pants",
            "skirt",
            "suit-jacket",
        ],
    }
    occasion_cloth_material = {
        "Dating": [
            "chiffon",
            "leather",
            "denim",
            "cotton",
            "faux-fur",
            "faux-leather",
            "faux-suede",
            "leather",
            "suede",
            "woven",
            "thermal",
            "velvet",
        ],
        "Daily_Work_and_Conference": ["denim", "cotton"],
        "Travel": ["chiffon", "cotton", "denim", "cotton-pants"],
        "Sports": ["cotton", "Nylon"],
        "Prom": ["leather", "chiffon", "cutton", "velvet"],
        "Shopping": [
            "leather",
            "denim",
            "cotton",
            "chiffon",
        ],
        "Party": ["chiffon", "crochet", "sheer", "velvet"],
        "School": ["leather", "cotton", "denim", "woven"],
        "Wedding_Guest": ["cotton", "leather", "chiffon"],
    }
    occasion_cloth_pattern = {
        "Dating": [
            "print",
            "pleated",
            "striped",
            "floral",
            "animal",
            "paisley-print",
            "abstract-print",
        ],
        "Daily_Work_and_Conference": [
            "striped",
            "print",
            "grid-print",
            "dotted",
            "colorblock",
        ],
        "Travel": ["print", "striped", "paisley-print", "camouflage", "colorblock"],
        "Sports": ["camouflage", "graphic", "tie-dye", "dotted", "abstract-print"],
        "Prom": ["print", "pleated", "floral", "glitter", "ornate-print", "baroque"],
        "Shopping": [
            "print",
            "striped",
            "floral",
            "graphic",
            "dotted",
            "paisley-print",
        ],
        "Party": ["pleated", "floral", "print", "glitter", "colorblock", "zebra-print"],
        "School": ["striped", "print", "grid-print", "abstract-print", "dotted"],
        "Wedding_Guest": [
            "floral",
            "paisley-print",
            "abstract-print",
            "ornate-print",
            "marble-print",
        ],
    }

    return {
        "occasion": user_occasion,
        "subcategories": occasion_cloth_subcategory[user_occasion],
        "material": occasion_cloth_material[user_occasion],
        "pattern": occasion_cloth_pattern[user_occasion],
    }


def rule_base_filter(temperature, consider_weather=True, user_occasion=None):
    indoor_activity = ["Conference", "Prom", "Party", "Wedding_Guest"]

    # 如果只考量天氣不考慮環境
    if consider_weather is True and user_occasion is None:
        candidate = weather_rule_base(temperature)

    # 只考量場合不考慮天氣 (不想考慮 or 室內)
    elif (consider_weather is False and user_occasion != "None") or (
        user_occasion in indoor_activity
    ):
        candidate = occasion_filter(user_occasion)

    # 考量天氣與場合
    else:
        candidate = weather_rule_base(temperature)
        occasion_info = occasion_filter(user_occasion)
        
        candidate["material"] = list(
            set(candidate["material"]) & set(occasion_info["material"])
        )
        candidate["subcategories"] = list(
            set(candidate["subcategories"]) & set(occasion_info["subcategories"])
        )

    return candidate


def scenario_filter(user_scenario):
    print("scenario_filter")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-1.5-flash-latest",
        generation_config={"response_mime_type": "application/json"},
    )

    # define prompt
    prompt = """Please consider the following scenario a user describe 
    and pick the cloths that satisfy the scenario, please only list the satisfy clothes, materials, patterns, mixed_categories without more description, 
    and output the answers as json format, where the keys are clothes, subcategories, patterns and the corresponding answer show place at the value :

    subcategories = [
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

    material = [
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



    """
    # user_scenario = '我今天要報告希望看起來正式又專業'
    response = model.generate_content(prompt + user_scenario)
    gemini_results_test = json.loads(
        response.text.replace("```json", "").replace("```", "")
    )
    print(gemini_results_test)
    return gemini_results_test
