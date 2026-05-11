import streamlit as st
from google import genai
from PIL import Image

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="MedInsight Analyzer",
    layout="wide"
)

# ==========================================
# HEADER
# ==========================================
st.title("🩺 MedInsight Analyzer")
st.caption("Developed by Dr/Hussein Ali")

# ==========================================
# API KEY
# ==========================================
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY not found in Streamlit Secrets")
    st.stop()

# Gemini Client
client = genai.Client(api_key=api_key)

# ==========================================
# OPTIONAL CLINICAL NOTES
# ==========================================
st.subheader("Additional Clinical Notes (Optional)")

extra_notes = st.text_area(
    "Add any extra information not present in the report images",
    placeholder="Example: patient is pregnant, taking statins, chemotherapy, dialysis, smoker, etc.",
    height=120
)

# ==========================================
# FILE UPLOADER
# ==========================================
uploaded_files = st.file_uploader(
    "Upload laboratory report images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# ==========================================
# ANALYSIS
# ==========================================
if st.button("🚀 Start Smart Analysis"):

    if not uploaded_files:
        st.warning("Please upload at least one image.")
        st.stop()

    try:

        with st.spinner("Analyzing medical reports..."):

            images = [
                Image.open(file).convert("RGB")
                for file in uploaded_files
            ]

            prompt = f"""
You are an expert laboratory medicine consultant.

Your tasks:

1. Extract:
- Patient name
- Age
- Gender
- Medical history
- Current medications
- Laboratory results
- Reference ranges

2. Detect:
- High values
- Low values
- Critical abnormalities

3. Correlate findings clinically.

4. Mention possible interactions between:
- diseases
- medications
- laboratory abnormalities

5. Generate a professional Arabic medical report with sections:

- بيانات المريض
- الأدوية الحالية
- التاريخ المرضي
- النتائج المستخرجة
- القيم غير الطبيعية
- التفسير الطبي
- التوصيات

6. Never invent values not visible in images.

Additional information from user:
{extra_notes if extra_notes.strip() else "No extra information provided."}
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, *images]
            )

            st.success("✅ Analysis completed successfully")

            st.markdown("## Smart Medical Report")
            st.write(response.text)

    except Exception as e:
        st.error(f"Error during analysis: {e}")

# ==========================================
# FOOTER
# ==========================================
st.info("Developed by Dr/Hussein Ali")
