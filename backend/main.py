# backend/main.py (FINAL, BULLETPROOF VERSION)

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests

# --- PASTE YOUR LATEST NGROK URL FROM COLAB HERE ---
NGROK_URL = "https://4c8d9e2433ea.ngrok-free.app"

class GenerationRequest(BaseModel):
    age: int
    view: str
    finding: list[str]
    severity: str
    num_images: int

app = FastAPI()

# --- NEW: ADD A ROOT ENDPOINT FOR HEALTH CHECKS ---
# This proves to us and to Render that the app is alive.
@app.get("/")
def read_root():
    return {"status": "ok", "message": "SynthMed Backend is running!"}

@app.post("/generate_dataset")
def post_generate(request: GenerationRequest):
    # 1. Prompt Engineering (no changes here)
    findings_str = ", ".join(request.finding)
    prompt = (
        f"High-resolution monochrome chest X-ray, {request.view} view, "
        f"of a {request.age}-year-old patient. The image shows signs of "
        f"{request.severity.lower()} {findings_str}. "
        f"Medical imaging, photorealistic, 4k, detailed."
    )

    colab_payload = {
        "prompt": prompt,
        "num_images": request.num_images
    }

    # --- THIS ENTIRE BLOCK IS UPGRADED FOR ROBUSTNESS ---
    print("Sending request to Colab worker...")
    try:
        # NEW: Add a timeout to the request. We will wait 150 seconds for Colab to respond.
        # This is longer than Render's gateway timeout, but good practice.
        colab_response = requests.post(
            f"{NGROK_URL}/generate_dataset",
            json=colab_payload,
            headers={"Content-Type": "application/json"},
            timeout=150  # Timeout in seconds
        )
        
        # NEW: Check for non-200 status codes from Colab
        # This will catch 404s, 500s, etc., from the Colab worker itself.
        colab_response.raise_for_status()

        print("Received successful response from Colab. Forwarding to frontend.")
        return colab_response.json()

    # NEW: Catch the specific exceptions for better logging
    except requests.exceptions.Timeout:
        # This error is critical. It will now be clearly printed in your Render logs.
        print("ERROR: The request to the Colab worker timed out.")
        return JSONResponse(status_code=504, content={"message": "The AI worker took too long to respond."})

    except requests.exceptions.RequestException as e:
        # This will catch any other network error, like ConnectionError or a 404,
        # and print the EXACT error message to your logs.
        print(f"ERROR: An error occurred while calling the Colab worker: {e}")
        return JSONResponse(status_code=500, content={"message": f"An error occurred with the AI worker: {e}"})