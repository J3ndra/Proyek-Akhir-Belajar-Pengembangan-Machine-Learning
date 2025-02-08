from fastapi import FastAPI, File, UploadFile
import numpy as np
import requests
from PIL import Image
import io
import json

app = FastAPI()

TFSERVING_URL = "http://tensorflow_serving:8501/v1/models/animals_10_classification:predict"

labels = [
    "dog",
    "horse",
    "elephant",
    "butterfly",
    "chicken",
    "cat",
    "cow",
    "sheep",
    "spider",
    "squirrel",
]

def preprocess_image(image: UploadFile):
    img = Image.open(io.BytesIO(image.file.read()))
    img = img.resize((224, 224))
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)
    return img.tolist()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    img_data = preprocess_image(file)
    payload = {"instances": img_data}
    response = requests.post(TFSERVING_URL, json=payload)
    result = response.json()
    raw_predictions = result.get("predictions")[0]
    max_index = int(np.argmax(raw_predictions))

    predicted_label = labels[max_index] if max_index < len(labels) else "unknown"
    confidence = float(raw_predictions[max_index])
    
    return {"predict": predicted_label, "confidence": confidence}