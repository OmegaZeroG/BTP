import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import os


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
model = torch.nn.Sequential(*list(model.children())[:-1])
model.to(device)
model.eval()


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def extract_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        embedding = model(image)

    return embedding.view(-1).cpu().numpy()



fingerprint_path = "fingerprint_dataset/dataset/FVC2002/DB1_B/104_1.tif"
iris_path = "iris_dataset/CASIA-Iris-Thousand/939/R/S5939R06.jpg"

fp_embedding = extract_embedding(fingerprint_path)
iris_embedding = extract_embedding(iris_path)

print("Fingerprint shape:", fp_embedding.shape)
print("Iris shape:", iris_embedding.shape)

combined = np.concatenate((fp_embedding, iris_embedding))
print("Combined template shape:", combined.shape)
