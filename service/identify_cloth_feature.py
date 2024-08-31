# -*- coding: utf-8 -*-

import csv
import time
import sys
import os

##test
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
#from lib.df1 import DeepFashion1Model

from model_zoo.feature_classification.inference import DeepFashion1Model


from PIL import Image
import os
import google.generativeai as genai
from dotenv import load_dotenv



df1_model = DeepFashion1Model()

# Set up Gemini API
load_dotenv()


genai.configure(api_key='AIzaSyB2UIdAswA9HLc6jM9sFmh-6KrSoaSO2F8')
#genai.configure(api_key=os.getenv(GEMINI_API_KEY))
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# define prompt
prompt = """Please examine the following images and identify the types of clothing they contain. For each image, only list the types from the following list, output them in order, separated by commas:

t-shirt
shirt
long-sleeve-shirt
dress-shirt
long-sleeve flannel-shirt
long-sleeve button-up shirt
short-sleeve button-up shirt
short-sleeve flannel shirt
sweater
hoodie
jacket
coat
trench-coat
suit-jacket
denim-jacket
leather-jacket
polo-shirt
knit-top
vest
sweater-vest
tank-top
turtleneck
dress
skirt
long-skirt
pants
jeans
shorts
suit-pants
yoga-pants
sweatpants
overalls
jumpsuit
cotton-pants
wool-pants
leggings
windproof-pants
cotton-vest
down-jacket
ski-jacket
cotton-coat
thermal-underwear
padded-jacket
winter-sportswear
insulated-vest
thick-jeans
college-sweatshirt

Format example: 
Image 1: t-shirt, jeans, hoodie
Image 2: sweater, pants, jacket


Please start identifying and listing the types of clothing in each image:
"""



def identify_cloth_feature(img_path):
    
    
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

    
    images=[]
    img = Image.open(img_path).convert("RGB")
    images.append(img)
    cloth_info={'material':[],'pattern':[],'sytle':[],'subcategories':[]}
    
    try:
        gemini_results=[]
        response1 = model.generate_content([prompt] + images)
        response2 = model.generate_content([prompt] + images)
        gemini_results_test1 = response1.text.strip().split('\n')
        #gemini_results_test2 = response2.text.strip().split('\n')
        gemini_results_test1[0] = gemini_results_test1[0].split(': ')[1]
        #gemini_results_test2[0] = gemini_results_test2[0].split(': ')[1]
        #gemini_results = list(set(gemini_results_test1) and set(gemini_results_test2))
        gemini_results = gemini_results_test1
        #
        #print(gemini_results_test1[0])
        #print(gemini_results_test2[0])
        #print(gemini_results)
        df1_tags = df1_model.infer(img, 0.13)
        df1_tags = [item.lower() for item in df1_tags]
        for tag in df1_tags:
            if tag in materials:
                cloth_info["material"].append(tag)
            elif tag in patterns:
                cloth_info["pattern"].append(tag)
            elif tag in mixed_categories:
                cloth_info["syle"].append(tag)
        cloth_info["subcategories"] = gemini_results
    except Exception as e:
        print(f"Error: {str(e)}")
    
    return cloth_info


#print(identify_cloth_feature(r"C:\Users\chen\zara.png"))