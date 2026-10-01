import streamlit as st
import google.generativeai as genai
from PIL import Image

import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- CONFIGURATION & TITLE ---
st.set_page_config(page_title="Allergy Chatbot", page_icon="🛡️", layout="centered")
st.title("🛡️ Allergy Safety Scanner Bot")

# --- STEP 1: LOAD PERMANENT SECRET KEY ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets!")

# Easy selection interface
selected_allergies = st.multiselect(
    "1. Select your allergies:",
    ["Peanuts", "Tree Nuts", "Dairy (Milk/Whey)", "Gluten/Wheat", "Eggs", "Soy", "Fish/Shellfish", "Sesame"]
)

# --- STEP 2: PHOTO UPLOADER ---
st.write("### 2. Take a Photo")
image_file = st.file_uploader("Upload or Take a Photo of the ingredients list", type=["jpg", "jpeg", "png"])

# --- STEP 3: THE HIGH-SPEED VISION LOGIC ---
if image_file is not None and len(selected_allergies) > 0:
    st.info("🔄 Processing image swiftly...")
    
    try:
        # Open the image file
        raw_img = Image.open(image_file)
        
        # 🏎️ SPEED TRICK 1: Aggressive compression for instant uploading
        # We shrink the image boundaries and lower the JPEG quality.
        # This reduces an 8MB iPhone photo down to a tiny 150KB while keeping text readable!
        raw_img.thumbnail((800, 800))
        buffer = io.BytesIO()
        raw_img.convert("RGB").save(buffer, format="JPEG", quality=60)
        optimized_img = Image.open(buffer)
        
        # Initialize the high-speed flash model
        model = genai.GenerativeModel('gemini-3.8-flash')
        
        # 🏎️ SPEED TRICK 2: Stream the answer line-by-line instead of waiting for the full block
        prompt = f"""
        You are an allergy safety bot. The user is allergic to: {', '.join(selected_allergies)}.
        Read this ingredient panel snapshot. 
        1. Explicitly output either '🟢 SAFE' or '🔴 DANGEROUS' in bold at the very top.
        2. List any warning ingredient triggers found in short bullet points.
        3. Print a quick transcription of the readable text.
        """
        
        st.write("### 📜 AI Safety Report:")
        
        # We use generate_content with stream=True so text chunks pop up instantly
        response_stream = model.generate_content([prompt, optimized_img], stream=True)
        
        # Streamlit reads the live incoming words automatically
        st.write_stream(response_stream)
        
    except Exception as e:
        st.error(f"Something went wrong: {e}")

elif image_file is not None and len(selected_allergies) == 0:
    st.warning("⚠️ Please select at least one allergy above before scanning.")
