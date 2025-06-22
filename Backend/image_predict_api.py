import io
import base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import torch
import torch.nn.functional as F

from model_definition import DeepfakeDetectionModel, frequency_domain_conversion

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageRequest(BaseModel):
    image_base64: str

# Load model once
model = DeepfakeDetectionModel()
model.load_state_dict(torch.load("deepfake_detection_model.pth", map_location=torch.device("cpu")))
model.eval()

def preprocess_image(image):
    from torchvision.transforms import Compose, Resize, ToTensor
    transform = Compose([
        Resize((256, 256)),
        ToTensor()
    ])
    return transform(image).unsqueeze(0)

@app.post("/predict-image")
async def predict_image(req: ImageRequest):
    try:
        image_data = base64.b64decode(req.image_base64.split(',')[-1])
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        image_tensor = preprocess_image(image)
        frequency_features = frequency_domain_conversion(image_tensor)
        with torch.no_grad():
            prediction = model(image_tensor, frequency_features)
            probabilities = F.softmax(prediction, dim=1)
            confidence_real = probabilities[0, 0].item()
            confidence_fake = probabilities[0, 1].item()
        tag = "Real" if confidence_real >= confidence_fake else "Fake"
        return {"tag": tag, "confidence_real": confidence_real, "confidence_fake": confidence_fake}
    except Exception as e:
        return {"tag": "Unknown", "error": str(e)}
