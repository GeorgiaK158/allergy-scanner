import streamlit as st
from google import genai
from PIL import Image
import io
import base64

# --- 1. SET UP THE SCREEN ---
st.set_page_config(page_title="Instant Allergy Scanner", page_icon="🛡️", layout="centered")
st.title("🛡️ Instant Allergy Camera Scanner")

# --- 2. LOAD YOUR SECRET PASSWORD SAFE ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets!")

# Easy allergy choice checkboxes for the user
selected_allergies = st.multiselect(
    "1. Select your allergies:",
    ["Peanuts", "Tree Nuts", "Dairy (Milk/Whey)", "Gluten/Wheat", "Eggs", "Soy", "Fish/Shellfish", "Sesame"]
)

# --- 3. THE CAMERA SCANNER BUTTON ---
st.write("### 2. Take a Photo")
image_file = st.file_uploader(
    "Upload or Take a Photo of the ingredients list", 
    type=["jpg", "jpeg", "png"]
)

# --- 4. THE PROTECTED RUN BUTTON ---
st.write("### 3. Run Analysis")

if st.button("🔍 Analyze Ingredients Safety Now"):
    if image_file is not None:
        if len(selected_allergies) > 0:
            st.info("🔄 Connecting securely to Google AI servers...")
            
            try:
                # Open the image file securely
                img = Image.open(image_file)
                img.thumbnail((1024, 1024)) # Shrink resolution for extreme speed
                
                # 🏎️ SPEED & VALIDATION FIX: Convert image to a safe Base64 string
                img_byte_arr = io.BytesIO()
                img.convert("RGB").save(img_byte_arr, format='JPEG')
                image_bytes = img_byte_arr.getvalue()
                
                # Google's new 2026 system requires decoding bytes to a UTF-8 string
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                
                # Configure the Google AI Client
                client = genai.Client(api_key=GEMINI_API_KEY)
                
                # Write strict instructions for the AI
                prompt = f"""
                You are a dedicated allergy safety assistant. The user is strictly allergic to: {', '.join(selected_allergies)}.
                
                Look closely at this image of an ingredient list panel:
                1. Meticulously check every word for direct matches or hidden derivatives (whey = dairy, lecithin = soy/egg, etc.).
                2. Output a prominent bold header: either '🟢 SAFE' or '🔴 DANGEROUS'.
                3. List out any warning items in brief bullet points if dangerous.
                """
                
                # Call the modern Interactions API using Google's exact Base64 structure
                response = client.interactions.create(
                    model="gemini-3.8-flash",
                    input=[
                        {"type": "text", "text": prompt},
                        {"type": "image", "data": base64_image, "mime_type": "image/jpeg"}
                    ]
                )
                
                # Display the clean text report on your screen
                st.write("### 📜 AI Safety Report:")
                st.write(response.output_text)
                
            except Exception as e:
                st.error(f"Something went wrong inside the server: {e}")
        else:
            st.warning("⚠️ Please select at least one allergy at the top before scanning.")
    else:
        st.warning("⚠️ Please snap or upload a photo of the ingredients list first.")
