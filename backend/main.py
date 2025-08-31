# backend/main.py (HEALTH CHECK VERSION)

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import logging # --- NEW: Import the logging library ---

# --- Configure logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- PASTE YOUR LATEST NGROK URL FROM COLAB HERE ---
NGROK_URL = "https://<your-latest-ngrok-url>.ngrok-free.app"

class GenerationRequest(BaseModel):
    age: int
    view: str
    finding: list[str]
    severity: str
    num_images: int

app = FastAPI()

# =========================================================================
# === THE NEW HEALTH CHECK ENDPOINT ===
# =========================================================================
# This is a simple endpoint that will run on the main URL.
# If you can access this in your browser, it PROVES the app is running.
@app.get("/")
def read_root():
    logger.info("Health check endpoint was accessed successfully.")
    return {"status": "ok", "message": "SynthMed Backend is running successfully!"}
# =========================================================================

@app.post("/generate_dataset")
def post_generate(request: GenerationRequest):
    logger.info("Received request for /generate_dataset endpoint.")
    # Prompt Engineering
    findings_str = ", ".join(request.finding)
    prompt = (
        f"High-resolution monochrome chest X-ray, {request.view} view, "
        f"of a {request.age}-year-old patient. The image shows signs of "
        f"{request.severity.lower()} {findings_str}. "
        f"Medical imaging, photorealistic, 4k, detailed."
    )

    colab_payload = { "prompt": prompt, "num_images": request.num_images }

    logger.info(f"Sending request for {request.num_images} images to Colab worker at {NGROK_URL}")
    try:
        colab_response = requests.post(
            f"{NGROK_URL}/generate_dataset",
            json=colab_payload,
            headers={"Content-Type": "application/json"},
            timeout=150
        )
        colab_response.raise_for_status()

        logger.info("Received successful response from Colab. Forwarding to frontend.")
        return colab_response.json()

    except requests.exceptions.Timeout:
        logger.error("CRITICAL: The request to the Colab worker timed out.")
        return JSONResponse(status_code=504, content={"message": "The AI worker took too long to respond."})

    except requests.exceptions.RequestException as e:
        logger.error(f"CRITICAL: An error occurred while calling the Colab worker: {e}")
        return JSONResponse(status_code=500, content={"message": f"An error occurred with the AI worker: {e}"})