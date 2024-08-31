import torch
from torchvision import transforms
from torch.autograd import Variable
from PIL import Image
# Define the model

#MODEL_PATH = "analysis/lib/df1.pkl"
#CLASSES_PATH = "analysis/lib/attribute-classes.txt"
##
MODEL_PATH = r"model_zoo/feature_classification/df1.pkl"
CLASSES_PATH = r"model_zoo/feature_classification/attribute-classes.txt"

class DeepFashion1Model:
    def __init__(self):
        self.model = None
        self.labels = []
        self.load(MODEL_PATH, CLASSES_PATH)

    def load(self, model_path, labels_path, eval_mode=False):
        self.model = torch.load(model_path)
        self.model.eval()  
        self.labels = open(labels_path, "r").read().splitlines()

        if eval_mode:
            print(self.model)

    def infer(self, img, threshold=0.1):
        device = torch.device("cpu")
        # img = Image.open(image_path).convert("RGB")

        test_transforms = transforms.Compose(
            [
                transforms.Resize(224),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]
        )

        image_tensor = test_transforms(img).float()
        image_tensor = image_tensor.unsqueeze_(0)  
        inp = Variable(image_tensor).to(device)

        with torch.no_grad():
            output = self.model(inp)

      

        probabilities = torch.sigmoid(output).cpu().numpy()[0]

        predictions = (probabilities >= threshold).astype(int)



        predicted_attributes = [
            self.labels[i] for i in range(len(predictions)) if predictions[i] == 1
        ]
        return predicted_attributes




#test_code
#df1_model = DeepFashion1Model()
#img = Image.open(r"C:\Users\chen\zara.png").convert("RGB")
#df1_tags = df1_model.infer(img, 0.13)
#print(df1_tags) 