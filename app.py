import streamlit as st
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components

# --- CONFIGURATION & TITLE ---
st.set_page_config(page_title="Instant Allergy Scanner", page_icon="🛡️", layout="centered")
st.title("🛡️ Instant Allergy Camera Scanner")

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

# --- STEP 2: HIGH-SPEED CAMERA TEXT EXTRACTOR (Tesseract.js HTML Component) ---
st.write("### 2. Snap a Photo of the Ingredients")

# We embed a tiny custom HTML snippet that loads a fast, free scanner in the browser
tesseract_html = """
<script src="https://unpkg.com"></script>
<div style="font-family: sans-serif; display: flex; flex-direction: column; gap: 10px;">
    <input type="file" id="cam" accept="image/*" capture="environment" style="display: none;" onchange="processImage(this)">
    <button onclick="document.getElementById('cam').click()" style="padding: 12px; background: #FF4B4B; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%;">
        📷 Open Mobile Camera & Scan
    </button>
    <div id="status" style="font-size: 0.9rem; color: #555; margin-top: 5px;"></div>
</div>

<script>
function processImage(input) {
    if (!input.files || !input.files[0]) return;
    const file = input.files[0];
    const statusDiv = document.getElementById('status');
    statusDiv.innerText = "⏳ Extracting text directly on your phone...";
    
    // Tesseract reads the text out of the image pixels locally
    Tesseract.recognize(file, 'eng').then(({ data: { text } }) => {
        statusDiv.innerText = "✅ Text extracted successfully!";
        // Send the plain text out of HTML back up to Streamlit
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: text}, '*');
    }).catch(err => {
        statusDiv.innerText = "❌ Error reading image. Please try again.";
    });
}
</script>
"""

# Render the fast mobile camera component
extracted_text = components.html(tesseract_html, height=90)

# --- STEP 3: THE HIGH-SPEED TEXT AI LOGIC ---
# Once the phone extracts the text, the AI evaluates it in milliseconds
if extracted_text and len(selected_allergies) > 0:
    st.info("🔄 Verifying ingredients profile...")
    
    try:
        model = genai.GenerativeModel('gemini-3.8-flash')
        
        prompt = f"""
        You are a dedicated allergy safety bot. The user is strictly allergic to: {', '.join(selected_allergies)}.
        
        Meticulously analyze this extracted ingredient list text for direct matches and hidden derivatives:
        "{extracted_text}"
        
        Format your response exactly like this:
        **Verdict:** [🟢 SAFE or 🔴 DANGEROUS]
        **Triggers found:** [List any ingredients that match or are derivatives, or write 'None']
        **Text Detected:** [Briefly show what ingredients you evaluated]
        """
        
        response_stream = model.generate_content(prompt, stream=True)
        st.write_stream(response_stream)
        
    except Exception as e:
        st.error(f"Something went wrong: {e}")

elif extracted_text and len(selected_allergies) == 0:
    st.warning("⚠️ Please select at least one allergy above before scanning.")
