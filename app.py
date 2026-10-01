import streamlit as st
from google import genai
from PIL import Image

# --- 1. SET UP THE SCREEN ---
st.set_page_config(page_title="Instant Allergy Scanner", page_icon="🛡️", layout="centered")
st.title("🛡️ Instant Allergy Camera Scanner")

# --- 2. LOAD YOUR SECRET PASSWORD SAFE ---
try:
    # This securely reads the key from your Streamlit Cloud vault
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
                # Load the raw picture using Python
                img = Image.open(image_file)
                img.thumbnail((1024, 1024)) # Shrink size for extreme speed
                
                # Configure the brand-new 2026 Google AI Client
                client = genai.Client(api_key=GEMINI_API_KEY)
                
                # Write strict instructions for the AI
                prompt = f"""
                You are a dedicated allergy safety assistant. The user is strictly allergic to: {', '.join(selected_allergies)}.
                
                Look closely at this image of an ingredient list panel:
                1. Meticulously check every word for direct matches or hidden derivatives (whey = dairy, lecithin = soy/egg, etc.).
                2. Output a prominent bold header: either '🟢 SAFE' or '🔴 DANGEROUS'.
                3. List out any warning items in brief bullet points if dangerous.
                """
                
                # Call the new modern Interactions API
                response = client.interactions.create(
                    model="gemini-3.8-flash",
                    input=[prompt, img]
                )
                
                # Display the beautiful text result on the phone, NOT code!
                st.write("### 📜 AI Safety Report:")
                st.write(response.output_text)
                
            except Exception as e:
                st.error(f"Something went wrong inside the server: {e}")
        else:
            st.warning("⚠️ Please select at least one allergy at the top before scanning.")
    else:
        st.warning("⚠️ Please snap or upload a photo of the ingredients list first.")
