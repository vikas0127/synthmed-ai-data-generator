# backend/main.py 

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests


NGROK_URL = "https://22c98c8c232f.ngrok-free.app"

# Add num_images to the request model 
class GenerationRequest(BaseModel):
    age: int
    view: str
    finding: list[str]
    severity: str
    num_images: int # This will come from the Streamlit UI

app = FastAPI()

@app.post("/generate_dataset") # Renamed to match Colab
def post_generate(request: GenerationRequest):
    # 1. Prompt Engineering
    findings_str = ", ".join(request.finding)
    prompt = (
        f"High-resolution monochrome chest X-ray, {request.view} view, "
        f"of a {request.age}-year-old patient. The image shows signs of "
        f"{request.severity.lower()} {findings_str}. "
        f"Medical imaging, photorealistic, 4k, detailed."
    )

    # 2. Prepare payload for the remote worker
    colab_payload = {
        "prompt": prompt,
        "num_images": request.num_images
    }

    # 3. Call the Remote AI Worker
    print(f"Sending request for {request.num_images} images to Colab worker...")
    try:
        colab_response = requests.post(
            f"{NGROK_URL}/generate_dataset", # Using the new endpoint
            json=colab_payload,
            headers={"Content-Type": "application/json"}
        )
        colab_response.raise_for_status()

        # 4. Forward the response (which contains the zip file)
        print("Received zipped dataset from Colab. Forwarding to frontend.")
        return colab_response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error calling Colab worker: {e}")
        return JSONResponse(status_code=500, content={"message": "Failed to connect to the AI worker."})