import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import requests  # url method
from io import BytesIO  # url method

# 1 url --> 1 CNN embedding

class CNN_EMBEDDING:
    def __init__(self, model_name='resnet50', weights='DEFAULT'):
        self.architecture = model_name
        self.weights = weights
        self.transform = self.assign_transform(weights)
        self.device = self.set_device()
        self.model = self.initiate_model()
        self.embed = self.assign_layer()
        print("CNN model initialized")

    def assign_transform(self, weights):
        return transforms.Compose([
            transforms.Resize(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def set_device(self):
        return 'cuda:0' if torch.cuda.is_available() else 'cpu'

    def initiate_model(self):
        model = getattr(models, self.architecture)(weights=self.weights)
        model.to(self.device)
        return model.eval()

    def assign_layer(self):
        return nn.Sequential(*list(self.model.children())[:-1])

    def embed_image(self, img_path):
        #img = Image.open(img_path).convert('RGB')  # path method
        #response = requests.get(img_path)  # url method
        #img = Image.open(BytesIO(response.content)).convert('RGB')  # url method

        # url method w/ header
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        response = requests.get(img_path, headers=headers)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch image from URL: {img_path}, status code: {response.status_code}")
        try:
            img = Image.open(BytesIO(response.content)).convert('RGB')
        except Exception as e:
            raise ValueError(f"Error opening image: {e}")
        
        img_trans = self.transform(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            embedding = self.embed(img_trans)
        return embedding.squeeze()
    
    def embed_images(self, upper_img_path, lower_img_path):
        upper_embedding = self.embed_image(upper_img_path)
        lower_embedding = self.embed_image(lower_img_path)
        combined_embedding = torch.cat((upper_embedding, lower_embedding), dim=0)
        
        return combined_embedding
