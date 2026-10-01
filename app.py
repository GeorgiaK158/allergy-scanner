import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURATION & TITLE ---
st.set_page_config(page_title="Allergy Chatbot", page_icon="🛡️", layout="centered")
st.title("🛡️ Allergy Safety Scanner Bot")

# --- STEP 1: PASTE YOUR GOOGLE GEMINI KEY HERE ---
# Wrap your secret API key inside double quotation marks ""
# ERASE your old key string and replace it with this exact text:
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Configure the Gemini library
genai.configure(api_key=GEMINI_API_KEY)

# Easy selection interface for the user
selected_allergies = st.multiselect(
    "1. Select your allergies:",
    ["Peanuts", "Tree Nuts", "Dairy (Milk/Whey)", "Gluten/Wheat", "Eggs", "Soy", "Fish/Shellfish", "Sesame"]
)

# --- STEP 2: PHOTO UPLOADER (iPhone Compatible!) ---
st.write("### 2. Take a Photo")
image_file = st.file_uploader("Upload or Take a Photo of the ingredients list", type=["jpg", "jpeg", "png"])

# --- STEP 3: THE GEMINI AI VISION LOGIC ---
if image_file is not None and len(selected_allergies) > 0:
    st.info("🔄 Gemini is reading image and verifying safety status...")
    
    try:
        # Load the image using the Pillow library
        img = Image.open(image_file)

        # --- SPEED FIX: Resize massive smartphone photos ---
        # This keeps the text sharp but cuts the file size down by 90%!
        img.thumbnail((1024, 1024)) 
        
        # Initialize the free, fast vision model
        model = genai.GenerativeModel('gemini-3.8-flash')

        # Craft the strict safety instructions
        prompt = f"""
        You are a dedicated allergy safety assistant. The user is strictly allergic to: {', '.join(selected_allergies)}.
        
        Analyze the provided image of an ingredient list text:
        1. Transcribe the raw text of the ingredients found so the user can see what you read.
        2. Meticulously inspect every word for direct matches and hidden derivatives (e.g. whey/casein = dairy, lecithin = soy/egg, etc.).
        3. Output a prominent bold header: either '🟢 SAFE' or '🔴 DANGEROUS'.
        4. List out the warning items in brief bullet points if dangerous.
        """
        
        # Send the text prompt and image together to Gemini
        response = model.generate_content([prompt, img])
        
        # Display the result on the screen
        st.write("### 📜 AI Safety Report:")
        st.write(response.text)
        
    except Exception as e:
        st.error(f"Something went wrong: {e}")

elif image_file is not None and len(selected_allergies) == 0:
    st.warning("⚠️ Please select at least one allergy above before scanning.")
