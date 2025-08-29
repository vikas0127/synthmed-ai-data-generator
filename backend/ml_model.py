import torch
from diffusers import StableDiffusionPipeline
import os

# --- MOVED MODEL LOADING LOGIC ---
# We will now load the model inside the generation function to avoid
# loading it in the main process. We define a global variable to hold the model.
pipe = None
MODEL_ID = "runwayml/stable-diffusion-v1-5"

def generate_image(prompt: str) -> str:
    """
    Generates an image from a text prompt and saves it to a file.
    Loads the model if it hasn't been loaded yet.
    Returns the path to the saved image.
    """
    global pipe # ADDED: Use the global 'pipe' variable

    # --- ADDED: Lazy Loading ---
    # If the model pipeline is not loaded, load it
    if pipe is None:
        print("Model not loaded. Loading model...")
        DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {DEVICE}")

        # Set up the pipeline
        pipe = StableDiffusionPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
        )
        pipe = pipe.to(DEVICE)
        print("Model loaded successfully.")
    
    # It's good practice to use a generator for reproducibility
    # Note: On CPU, generation is very slow. Consider reducing steps for testing.
    num_steps = 20 if torch.cuda.is_available() else 10 # Fewer steps for CPU
    print(f"Generating image for prompt: '{prompt}' with {num_steps} steps...")

    generator = torch.Generator(device=pipe.device).manual_seed(42)

    # Generate the image
    image = pipe(
        prompt,
        num_inference_steps=num_steps,
        generator=generator
    ).images[0]

    # Save the image to a file. We'll use a simple name for now.
    # In a real app, you would generate a unique filename.
    output_path = "generated_image.png"
    # Ensure the path is relative to the project root
    # This helps Streamlit find it later
    if os.path.basename(os.getcwd()) == 'backend':
        output_path = f"../{output_path}"
        
    image.save(output_path)
    
    print(f"Image saved to {output_path}")
    # Return the simple filename, not the full path
    return os.path.basename(output_path)