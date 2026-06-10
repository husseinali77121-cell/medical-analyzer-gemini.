import streamlit as st

st.set_page_config(page_title="...")

# إخفاء GitHub وعناصر Streamlit
st.markdown("""
    <style>
    .stActionButton {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header[data-testid="stHeader"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)
from google import genai
from PIL import Image

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MedInsight Analyzer",
    layout="wide"
)

# =========================================================
# SIMPLE LOGIN SYSTEM
# =========================================================
USERS = {
    "user1": "pass123",
    "user2": "med456",
    "user3": "lab789"
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.title("🔐 MedInsight Analyzer Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in USERS and USERS[username] == password:
            st.session_state.authenticated = True
            st.success("✅ Login successful")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

    st.stop()

# =========================================================
# HEADER
# =========================================================
st.title("🩺 MedInsight Analyzer")
st.caption("Advanced AI-Powered Laboratory Report Analysis & Quality Review")
st.caption("Developed by Dr/Hussein Ali")

# =========================================================
# API KEY
# =========================================================
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY not found in Streamlit Secrets")
    st.stop()

# =========================================================
# GEMINI CLIENT
# =========================================================
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Failed to initialize Gemini Client: {e}")
    st.stop()

# =========================================================
# FIXED MODEL
# =========================================================
MODEL_NAME = "gemini-2.5-flash"

# =========================================================
# SIDEBAR SETTINGS
# =========================================================
with st.sidebar:

    st.header("⚙️ Analysis Settings")

    detailed_mode = st.checkbox(
        "Enable Deep Clinical Interpretation",
        value=True
    )

    trend_analysis = st.checkbox(
        "Enable Previous Result Comparison",
        value=True
    )

    medication_correlation = st.checkbox(
        "Enable Medication Correlation",
        value=True
    )

    critical_alerts = st.checkbox(
        "Enable Critical Value Alerts",
        value=True
    )

    laboratory_quality_review = st.checkbox(
        "Enable Laboratory Quality Review",
        value=True
    )

# =========================================================
# OPTIONAL NOTES
# =========================================================
st.subheader("Additional Clinical Notes (Optional)")

extra_notes = st.text_area(
    "Add clinical information not clearly present in report images",
    placeholder=(
        "Examples:\n"
        "- Diabetes mellitus\n"
        "- Hypertension\n"
        "- Taking statins\n"
        "- Chronic kidney disease\n"
        "- Pregnancy\n"
        "- Chemotherapy\n"
        "- Dialysis\n"
        "- Smoker"
    ),
    height=180
)

# =========================================================
# AI QUESTION BOX
# =========================================================
st.subheader("AI Additional Instructions / سؤال إضافي للذكاء الاصطناعي")

user_question = st.text_area(
    "Ask AI to focus on specific medical or laboratory points",
    placeholder=(
        "Examples:\n"
        "- Comment on CBC\n"
        "- Evaluate peripheral smear\n"
        "- Assess severity\n"
        "- هل الحالة خطيرة؟\n"
        "- اعمل تعليق علي صورة الدم"
    ),
    height=140
)

# =========================================================
# FILE UPLOADER
# =========================================================
uploaded_files = st.file_uploader(
    "Upload laboratory report images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# =========================================================
# ANALYSIS BUTTON
# =========================================================
if st.button("🚀 Start Smart Medical Analysis"):

    if not uploaded_files:
        st.warning("Please upload at least one laboratory report image.")
        st.stop()

    try:

        with st.spinner("Analyzing laboratory reports with AI..."):

            # =========================================================
            # IMAGE PROCESSING
            # =========================================================
            images = []

            for file in uploaded_files:
                img = Image.open(file).convert("RGB")
                images.append(img)

            # =========================================================
            # DYNAMIC SETTINGS
            # =========================================================
            detailed_instruction = (
                "Provide deep clinical interpretation and advanced laboratory reasoning."
                if detailed_mode else
                "Provide concise interpretation."
            )

            trend_instruction = (
                "Carefully compare current and previous laboratory results."
                if trend_analysis else
                "Historical comparison is optional."
            )

            medication_instruction = (
                "Correlate laboratory abnormalities with medications and chronic diseases."
                if medication_correlation else
                "Medication correlation is optional."
            )

            critical_instruction = (
                "Clearly highlight critical or dangerous abnormalities."
                if critical_alerts else
                "Standard abnormality detection only."
            )

            quality_instruction = (
                """
Perform ADVANCED LABORATORY QUALITY REVIEW.

Carefully review the laboratory report for possible laboratory or reporting issues including:

- Typographical mistakes
- Incorrect medical terminology
- Missing reference ranges
- Missing interpretation
- Missing critical alerts
- Inconsistent units
- Possible analytical inconsistencies
- Contradictions between findings and interpretation
- Missing clinically important comments
- Reports requiring urgent physician attention
- Possible pre-analytical or post-analytical issues
- Incomplete reporting according to common laboratory guidelines
- Possible formatting or reporting weaknesses

If any issue is detected:
- Clearly explain the issue
- Suggest professional correction
- Mention why the issue may be clinically important

Generate a dedicated section titled:
# Laboratory Quality Review
"""
                if laboratory_quality_review else
                "Laboratory quality review is optional."
            )

            # =========================================================
            # MAIN MEDICAL PROMPT
            # =========================================================
            prompt = f"""
You are a world-class clinical pathologist and laboratory medicine consultant.

Analyze ALL uploaded laboratory report images with maximum medical accuracy.

GENERAL RULES:
- Use professional medical terminology.
- Be highly accurate and conservative.
- Never invent values not clearly visible in reports.
- Focus on clinical significance.
- Carefully evaluate both laboratory accuracy and reporting quality.

TASKS:

1. Extract:
- Patient name
- Age
- Gender
- Dates of tests
- Medical history
- Current medications
- Current laboratory results
- Previous laboratory results
- Reference ranges

2. Detect:
- High values
- Low values
- Critical abnormalities
- Dangerous trends
- Possible inconsistencies

3. Clinical Correlation:
- Correlate findings with diseases
- Correlate findings with medications
- Mention possible medication-induced abnormalities
- Mention clinically important interactions

4. Historical Comparison:
- Compare current vs previous results
- Detect improvement
- Detect deterioration
- Detect stability

5. Generate a PROFESSIONAL ENGLISH MEDICAL REPORT with sections:

# Patient Information
# Medical History
# Current Medications
# Current Laboratory Results
# Previous Laboratory Results
# Comparative Trend Analysis
# Abnormal Findings
# Clinical Interpretation
# Critical Alerts
# Recommendations

ADDITIONAL INSTRUCTIONS:
- {detailed_instruction}
- {trend_instruction}
- {medication_instruction}
- {critical_instruction}

QUALITY REVIEW:
{quality_instruction}

Additional user notes:
{extra_notes if extra_notes.strip() else "No additional notes provided."}

USER SPECIAL QUESTION / REQUEST:
{user_question if user_question.strip() else "No additional AI question provided."}
"""

            # =========================================================
            # GEMINI API REQUEST
            # =========================================================
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[prompt, *images],
                config={
                    "temperature": 0.2
                }
            )

            # =========================================================
            # DISPLAY OUTPUT
            # =========================================================
            st.success("✅ Analysis completed successfully")

            st.markdown("---")
            st.markdown("## 🧾 Smart Medical Report & Laboratory Quality Review")

            st.write(response.text)

            # =========================================================
            # DOWNLOAD REPORT
            # =========================================================
            st.download_button(
                label="📥 Download Report",
                data=response.text,
                file_name="medical_quality_report.txt",
                mime="text/plain"
            )

    except Exception as e:

        st.error(f"❌ Error during analysis: {e}")

        if "quota" in str(e).lower():
            st.warning(
                "Gemini API quota exceeded temporarily. "
                "Please try again later."
            )

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.info(
    "MedInsight Analyzer | AI-Powered Clinical Laboratory Analysis & "
    "Quality Review System | Developed by Dr/Hussein Ali"
)
