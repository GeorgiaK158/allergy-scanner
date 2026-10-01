import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION & TITLE ---
st.set_page_config(page_title="Instant Allergy Checker", page_icon="🛡️", layout="centered")
st.title("🛡️ Instant Allergy Text Checker")
st.write("Type or paste ingredients to check safety profiles instantly.")

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

# --- STEP 2: INSTANT TEXT INPUT ---
st.write("### 2. Enter Ingredients")
user_text = st.text_area(
    "Paste the ingredient text list here:", 
    placeholder="Example: Enriched flour, sugar, whey protein, soy lecithin, natural flavors..."
)

# --- STEP 3: HIGH-SPEED TEXT PROCESSING LOGIC ---
if st.button("Verify Ingredients Now") and len(selected_allergies) > 0 and user_text.strip() != "":
    st.info("🔄 Checking profile...")
    
    try:
        # Initialize the flash text model
        model = genai.GenerativeModel('gemini-3.8-flash')
        
        prompt = f"""
        You are a dedicated allergy safety bot. The user is strictly allergic to: {', '.join(selected_allergies)}.
        
        Meticulously analyze this ingredient list text for direct matches and hidden chemical derivatives:
        "{user_text}"
        
        Format your response exactly like this:
        **Verdict:** [🟢 SAFE or 🔴 DANGEROUS]
        **Triggers found:** [List any ingredients that match or are derivatives, or write 'None']
        **Explanation:** [A short one-sentence explanation of why it is safe or dangerous]
        """
        
        # Stream the pure text answer line-by-line
        response_stream = model.generate_content(prompt, stream=True)
        st.write_stream(response_stream)
        
    except Exception as e:
        st.error(f"Something went wrong: {e}")

elif len(selected_allergies) == 0 and user_text.strip() != "":
    st.warning("⚠️ Please select at least one allergy above before checking.")

