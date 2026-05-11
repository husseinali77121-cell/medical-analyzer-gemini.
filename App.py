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

# ==========================================
# GEMINI CLIENT
# ==========================================
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Failed to initialize Gemini Client: {e}")
    st.stop()

# ==========================================
# MODEL SELECTION
# ==========================================
st.subheader("AI Model")

model_option = st.selectbox(
    "Select Gemini Model",
    [
        "gemini-2.5-flash",
        "gemini-2.5-pro"
    ]
)

# ==========================================
# OPTIONAL NOTES
# ==========================================
st.subheader("Additional Clinical Notes (Optional)")

extra_notes = st.text_area(
    "Add any clinical information not clearly present in the report images",
    placeholder=(
        "Examples:\n"
        "- Patient is diabetic\n"
        "- Hypertension\n"
        "- Taking statins\n"
        "- Chronic kidney disease\n"
        "- Pregnancy\n"
        "- Smoker\n"
        "- Chemotherapy"
    ),
    height=150
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
# ANALYSIS BUTTON
# ==========================================
if st.button("🚀 Start Smart Medical Analysis"):

    if not uploaded_files:
        st.warning("Please upload at least one laboratory image.")
        st.stop()

    try:

        with st.spinner("Analyzing laboratory reports with AI..."):

            # Convert uploaded files to images
            images = []

            for file in uploaded_files:
                img = Image.open(file).convert("RGB")
                images.append(img)

            # ==========================================
            # PROFESSIONAL MEDICAL PROMPT
            # ==========================================
            prompt = f"""
You are a highly experienced clinical pathologist and laboratory medicine consultant.

Your task is to carefully analyze ALL uploaded laboratory report images with maximum medical accuracy.

INSTRUCTIONS:

1. Extract accurately:
- Patient name
- Age
- Gender
- Medical history
- Current medications
- Current laboratory results
- Previous laboratory results (if present in report)
- Reference ranges
- Dates of tests

2. Compare:
- Current vs previous laboratory values
- Detect improvement, deterioration, or stability
- Mention clinically significant changes

3. Correlate findings with:
- Medical history
- Current medications
- Chronic diseases
- Possible drug effects on laboratory values

4. Detect:
- High values
- Low values
- Critical abnormalities
- Dangerous trends
- Possible laboratory inconsistencies

5. Generate a PROFESSIONAL ENGLISH MEDICAL REPORT with the following sections:

# Patient Information
# Medical History
# Current Medications
# Current Laboratory Results
# Previous Laboratory Results
# Comparative Analysis
# Abnormal Findings
# Clinical Interpretation
# Important Alerts
# Recommendations

6. Use professional medical terminology.

7. Be highly accurate and conservative.

8. Do NOT invent values not clearly visible in images.

9. If previous results are present at the bottom of the report,
compare them carefully with the current results.

10. Mention possible medication effects on abnormal values when relevant.

Additional clinical notes from user:
{extra_notes if extra_notes.strip() else "No additional notes provided."}
"""

            # ==========================================
            # GEMINI REQUEST
            # ==========================================
            response = client.models.generate_content(
                model=model_option,
                contents=[prompt, *images],
                config={
                    "temperature": 0.2
                }
            )

            # ==========================================
            # OUTPUT
            # ==========================================
            st.success("✅ Analysis completed successfully")

            st.markdown("## Smart Medical Report")

            st.write(response.text)

    except Exception as e:

        st.error(f"Error during analysis: {e}")

        if "quota" in str(e).lower():
            st.warning(
                "Gemini Pro quota may be exceeded or unavailable. "
                "Try using gemini-2.5-flash."
            )

# ==========================================
# FOOTER
# ==========================================
st.divider()

st.info("MedInsight Analyzer | Developed by Dr/Hussein Ali")
