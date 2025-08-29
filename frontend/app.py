# frontend/app.py (UPGRADED)

import streamlit as st
import requests
import base64

API_URL = "http://127.0.0.1:8000"

st.set_page_config(layout="wide")
st.title("🩺 SynthMed: AI-Powered Synthetic Dataset Generator")

st.sidebar.header("Dataset Parameters")
# Add a number input for dataset size
num_images = st.sidebar.number_input("Number of Images to Generate", min_value=1, max_value=100, value=5)

age = st.sidebar.slider("Patient Age", 20, 90, 65)
view = st.sidebar.selectbox("Image View", ["PA", "AP", "Lateral"])
findings = st.sidebar.multiselect(
    "Clinical Findings",
    ["Normal", "Pneumonia", "Cardiomegaly", "Lung Nodule"],
    default=["Pneumonia"]
)
severity = st.sidebar.select_slider(
    "Severity",
    options=["Mild", "Moderate", "Severe"],
    value="Severe"
)

if st.sidebar.button("Generate Dataset"):
    if not findings:
        st.error("Please select at least one clinical finding.")
    else:
        payload = {
            "num_images": num_images, # Add new parameter
            "age": age,
            "view": view,
            "finding": findings,
            "severity": severity
        }

        try:
            # Update spinner text
            spinner_text = f"Generating a dataset of {num_images} images... This may take a few minutes."
            with st.spinner(spinner_text):
                # Update endpoint URL
                response = requests.post(f"{API_URL}/generate_dataset", json=payload)
                response.raise_for_status()
                data = response.json()

                # Handle the zip file response 
                zip_file_base64 = data.get("zip_file_base64")

                if zip_file_base64:
                    # Decode the base64 string back into bytes
                    zip_data = base64.b64decode(zip_file_base64)
                    
                    st.success("Dataset generated successfully!")
                    
                    # Provide a download button for the zip file 
                    st.download_button(
                        label="⬇️ Download Dataset (.zip)",
                        data=zip_data,
                        file_name=f"synthmed_dataset_{num_images}_images.zip",
                        mime="application/zip"
                    )
                else:
                    st.error("Generation failed. The worker did not return a dataset.")

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to the backend API: {e}")