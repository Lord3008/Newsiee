import streamlit as st
import torch
import torch.nn.functional as F
from torchvision.transforms import Compose, Resize, ToTensor
from PIL import Image

# Import your model and custom functions
from model_definition import DeepfakeDetectionModel, frequency_domain_conversion

# Load the model
@st.cache_resource
def load_model():
    model = DeepfakeDetectionModel()
    model.load_state_dict(torch.load("deepfake_detection_model.pth", map_location=torch.device("cpu")))
    model.eval()  # Set the model to evaluation mode
    return model

# Preprocessing function
def preprocess_image(image):
    transform = Compose([
        Resize((256, 256)),
        ToTensor()
    ])
    return transform(image).unsqueeze(0)  # Add batch dimension

# App UI
st.title("Deepfake Detection App")

st.write("Process how it works:")
st.image("C:\\Users\\DELL\\Pictures\\Screenshots\\Screenshot 2024-12-05 104840.png",caption="Novel DeepFake Architecture Built by Lord Sen. Published in 12th International Conference on Intelligent Systems and Embedded Design")
st.write("Upload an image, and the model will predict if it's **Real** or **Fake**.")
# File uploader
uploaded_file = st.file_uploader("Choose an image file...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Preprocess and predict
    model = load_model()
    image_tensor = preprocess_image(image)
    frequency_features = frequency_domain_conversion(image_tensor)
    
    with torch.no_grad():
        prediction = model(image_tensor, frequency_features)
        probabilities = F.softmax(prediction, dim=1)
        confidence_real = probabilities[0, 0].item()
        confidence_fake = probabilities[0, 1].item()

    # Display results
    st.write("### Prediction Results:")
    st.write(f"**Real** Confidence: {confidence_real * 100:.2f}%")
    st.write(f"**Fake** Confidence: {confidence_fake * 100:.2f}%")
