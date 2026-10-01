import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. STABLE CONFIGURATION & TITLE ---
st.set_page_config(page_title="Instant Allergy Scanner", page_icon="🛡️", layout="centered")
st.title("🛡️ Instant Allergy Camera Scanner")

# --- 2. LOAD PERMANENT SECRET KEY ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets!")

# Easy selection interface for the user
selected_allergies = st.multiselect(
    "1. Select your allergies:",
    ["Peanuts", "Tree Nuts", "Dairy (Milk/Whey)", "Gluten/Wheat", "Eggs", "Soy", "Fish/Shellfish", "Sesame"]
)

# --- 3. THE CAMERA TRACK (iPhone Native Uploader) ---
st.write("### 2. Take a Photo")
# This button safely forces the native iPhone camera popup menu without loops
image_file = st.file_uploader(
    "Upload or Take a Photo of the ingredients list", 
    type=["jpg", "jpeg", "png"],
    key="stable_uploader"
)

# --- 4. THE PROTECTED GATEWAY BUTTON ---
st.write("### 3. Run Analysis")

# This boolean check ensures NOTHING runs in the background until the user taps the button
if st.button("🔍 Analyze Ingredients Safety Now", key="analysis_button"):
    if image_file is not None:
        if len(selected_allergies) > 0:
            st.info("🔄 Connecting securely to Gemini 3.8 Flash...")
            
            try:
                # Load the raw image file securely
                img = Image.open(image_file)
                
                # Compress the resolution to save data transit speeds
                img.thumbnail((1024, 1024))
                
                # Initialize the latest stable fast engine
                model = genai.GenerativeModel('gemini-3.8-flash')
                
                # Build tight safety instructions
                prompt = f"""
                You are a dedicated allergy safety bot. The user is strictly allergic to: {', '.join(selected_allergies)}.
                
                Meticulously analyze this provided photo of an ingredient panel text:
                1. Look for direct allergen matches and hidden derivatives.
                2. Output a prominent bold header: either '🟢 SAFE' or '🔴 DANGEROUS'.
                3. List out any warning items in brief bullet points if dangerous.
                4. Provide a transcription of the ingredients text you detected.
                """
                
                # Stream the output words line-by-line onto the user's screen
                response_stream = model.generate_content([prompt, img], stream=True)
                st.write_stream(response_stream)
                
            except Exception as e:
                st.error(f"Something went wrong during the analysis: {e}")
        else:
            st.warning("⚠️ Please select at least one allergy at the top before running.")
    else:
        st.warning("⚠️ Please snap or upload a photo of the ingredients list first.")
