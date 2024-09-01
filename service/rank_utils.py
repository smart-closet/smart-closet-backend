# functions.py

import torch
import torch.nn as nn
import requests
import base64
import time
from transformers import BertTokenizer, BertModel

def generate_description(top_cloth_url, bottom_cloth_url, api_key):
    response_top = requests.get(top_cloth_url)
    response_top.raise_for_status()
    image_base64_string_2 = base64.b64encode(response_top.content).decode('utf-8')

    response_bottom = requests.get(bottom_cloth_url)
    response_bottom.raise_for_status()
    image_base64_string_3 = base64.b64encode(response_bottom.content).decode('utf-8')
    
    url = f'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}'
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": "Based on the two pictures of clothing, describe the appearance, material and texture of the clothing respectively, and treat the two clothing as a set of outfits. Do you think this outfit belongs to European and American style, Korean style or Japanese style?"},
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_base64_string_2}},
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_base64_string_3}}
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # 確保 HTTP 請求成功
    description = response.json()['candidates'][0]['content']['parts'][0]['text'].replace('\n', '')
    return description

def generate_description_with_retry(top_cloth_url, bottom_cloth_url, api_key):
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            return generate_description(top_cloth_url, bottom_cloth_url, api_key)
        except requests.RequestException as e:
            if 'RESOURCE_EXHAUSTED' in str(e):
                print(f"Resource exhausted: {e}")
                time.sleep(60)
            else:
                print(f"Error: {e}. Retrying... ({retry_count + 1}/{max_retries})")
                retry_count += 1
                time.sleep(5)
    raise Exception(f"Failed to generate description after {max_retries} retries.")

def generate_bert_embeddings(descriptions):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    embeddings = []

    for description in descriptions:
        inputs = tokenizer(description, return_tensors='pt').to(device)
        outputs = model(**inputs)
        cls_embedding = outputs.last_hidden_state[0, 0, :].detach().cpu().numpy()
        embeddings.append(cls_embedding)

    return embeddings

class myMLP(nn.Module):
        def __init__(self, input_dim, num_classes):
            super(myMLP, self).__init__()
            self.mlp = nn.Sequential(
                nn.Linear(input_dim, 256),
                nn.BatchNorm1d(256),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(256, 256),
                nn.BatchNorm1d(256),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(256, num_classes)
            )

        def forward(self, x):
            return self.mlp(x)

def evaluate_model(model_path, embeddings):
    torch.serialization.add_safe_globals([myMLP])
    model = torch.load(model_path, map_location=torch.device('cpu'))
    model.eval()
    scores = []

    for embedding in embeddings:
        embedding_tensor = torch.tensor(embedding).unsqueeze(0).float()
        with torch.no_grad():
            score = model(embedding_tensor).item()
        scores.append(score)

    return scores
