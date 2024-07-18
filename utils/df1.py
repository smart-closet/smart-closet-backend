import torch
from torchvision import transforms
from torch.autograd import Variable

# Define the model
MODEL_PATH = "utils/df1.pkl"
CLASSES_PATH = "utils/attribute-classes.txt"

class DeepFashion1Model:
    def __init__(self):
        self.model = None
        self.labels = []
        self.load(MODEL_PATH, CLASSES_PATH)

    def load(self, model_path, labels_path, eval_mode=False):
        self.model = torch.load(model_path)
        self.model.eval()  # 設置模型為推理模式
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
        image_tensor = image_tensor.unsqueeze_(0)  # 增加 batch 維度
        inp = Variable(image_tensor).to(device)

        with torch.no_grad():
            output = self.model(inp)

        # 打印輸出以進行檢查
        # print("Raw model output:", output)

        probabilities = torch.sigmoid(output).cpu().numpy()[0]

        # 打印概率以進行檢查
        # print("Probabilities:", probabilities)

        predictions = (probabilities >= threshold).astype(int)

        # 打印二值化結果以進行檢查
        # print("Binary predictions:", predictions)

        predicted_attributes = [
            self.labels[i] for i in range(len(predictions)) if predictions[i] == 1
        ]
        return predicted_attributes