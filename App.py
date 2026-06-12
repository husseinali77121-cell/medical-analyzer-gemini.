import streamlit as st
import hashlib
import json
import datetime
import os
from pathlib import Path

# =========================================================
# PAGE CONFIG — يجب أن تكون أول أمر في الكود
# =========================================================
st.set_page_config(
    page_title="MedInsight Analyzer",
    page_icon="🩺",
    layout="wide"
)

# =========================================================
# إخفاء عناصر Streamlit الافتراضية
# =========================================================
st.markdown("""
    <style>
    .stActionButton {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header[data-testid="stHeader"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# =========================================================
# IMPORTS
# =========================================================
from google import genai
from PIL import Image

# =========================================================
# CONSTANTS
# =========================================================
TRIAL_DAYS = 15
TRIAL_ANALYSES_LIMIT = 20   # عدد التحليلات المسموح بها في الفترة التجريبية

# =========================================================
# DATABASE FILE PATH (يُخزَّن في st.secrets أو ملف JSON)
# =========================================================
DB_FILE = "users_db.json"

# =========================================================
# HELPER: تحميل / حفظ قاعدة البيانات
# =========================================================
def load_db() -> dict:
    """تحميل قاعدة بيانات المستخدمين من ملف JSON."""
    if "users_db" not in st.session_state:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                st.session_state["users_db"] = json.load(f)
        else:
            st.session_state["users_db"] = {}
    return st.session_state["users_db"]


def save_db(db: dict):
    """حفظ قاعدة بيانات المستخدمين إلى ملف JSON."""
    st.session_state["users_db"] = db
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


# =========================================================
# HELPER: تشفير كلمة المرور
# =========================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# =========================================================
# HELPER: حالة الاشتراك
# =========================================================
def get_subscription_status(user_data: dict) -> dict:
    """
    يرجع dict يحتوي على:
        status : "trial" | "active" | "expired" | "trial_exceeded"
        days_left : int (للتجريب)
        analyses_left : int (للتجريب)
        message : str وصف بشري
    """
    today = datetime.date.today()
    reg_date = datetime.date.fromisoformat(user_data["registered_date"])
    trial_end = reg_date + datetime.timedelta(days=TRIAL_DAYS)
    analyses_used = user_data.get("analyses_used", 0)
    subscription = user_data.get("subscription", "none")  # "none" | "active"
    sub_end_str = user_data.get("subscription_end", None)

    # ── مشترك بفاتورة ──────────────────────────────────
    if subscription == "active" and sub_end_str:
        sub_end = datetime.date.fromisoformat(sub_end_str)
        if today <= sub_end:
            return {
                "status": "active",
                "days_left": (sub_end - today).days,
                "analyses_left": None,
                "message": f"✅ اشتراك فعّال حتى {sub_end.strftime('%d/%m/%Y')} ({(sub_end - today).days} يوم متبقي)"
            }
        else:
            return {
                "status": "expired",
                "days_left": 0,
                "analyses_left": 0,
                "message": "❌ انتهت صلاحية اشتراكك. يرجى التجديد للاستمرار."
            }

    # ── فترة تجريبية ────────────────────────────────────
    days_left = (trial_end - today).days
    analyses_left = max(0, TRIAL_ANALYSES_LIMIT - analyses_used)

    if today > trial_end:
        return {
            "status": "expired",
            "days_left": 0,
            "analyses_left": 0,
            "message": "❌ انتهت فترة التجربة المجانية (15 يوم). يرجى الاشتراك للاستمرار."
        }

    if analyses_left <= 0:
        return {
            "status": "trial_exceeded",
            "days_left": days_left,
            "analyses_left": 0,
            "message": f"⚠️ استنفذت {TRIAL_ANALYSES_LIMIT} تحليلات في الفترة التجريبية. اشترك للمتابعة."
        }

    return {
        "status": "trial",
        "days_left": days_left,
        "analyses_left": analyses_left,
        "message": f"🔬 فترة تجريبية: {days_left} يوم و {analyses_left} تحليل متبقي"
    }


# =========================================================
# HELPER: هل يُسمح بالتحليل؟
# =========================================================
def can_analyze(user_data: dict) -> bool:
    status = get_subscription_status(user_data)["status"]
    return status in ("trial", "active")


# =========================================================
# SESSION STATE INIT
# =========================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"   # "login" | "register"


# =========================================================
# ═══════════════════  AUTH SCREENS  ═════════════════════
# =========================================================
if not st.session_state.authenticated:

    # ── شعار / عنوان ──────────────────────────────────
    st.markdown("""
        <div style="text-align:center; padding: 2rem 0 1rem 0;">
            <h1 style="font-size:2.8rem;">🩺 MedInsight Analyzer</h1>
            <p style="color:#666; font-size:1.05rem;">
                AI-Powered Clinical Laboratory Analysis & Quality Review
            </p>
        </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.6, 1])

    with col_c:

        # ── التبديل بين تسجيل الدخول والتسجيل ──
        tab_login, tab_register = st.tabs(["🔑 تسجيل الدخول", "📝 حساب جديد (تجريبي مجاني)"])

        # ──────────────────────────────────────
        # تاب: تسجيل الدخول
        # ──────────────────────────────────────
        with tab_login:
            st.markdown("#### الدخول إلى حسابك")

            email_in = st.text_input("البريد الإلكتروني", key="login_email",
                                     placeholder="example@email.com")
            pass_in  = st.text_input("كلمة المرور", type="password", key="login_pass")

            if st.button("🔓 دخول", use_container_width=True, key="btn_login"):
                db = load_db()
                email_key = email_in.strip().lower()

                if email_key in db:
                    stored = db[email_key]
                    if stored["password"] == hash_password(pass_in):
                        st.session_state.authenticated = True
                        st.session_state.current_user  = email_key
                        st.success("✅ تم تسجيل الدخول بنجاح")
                        st.rerun()
                    else:
                        st.error("❌ كلمة المرور غير صحيحة")
                else:
                    st.error("❌ البريد الإلكتروني غير مسجّل")

        # ──────────────────────────────────────
        # تاب: التسجيل (حساب جديد تجريبي)
        # ──────────────────────────────────────
        with tab_register:
            st.markdown("#### إنشاء حساب تجريبي مجاني")
            st.info(
                f"🎁 **{TRIAL_DAYS} يوم مجاناً** — حتى {TRIAL_ANALYSES_LIMIT} تحليلاً "
                "دون أي بيانات بنكية."
            )

            new_name  = st.text_input("الاسم الكامل", key="reg_name",
                                      placeholder="د. محمد أحمد")
            new_email = st.text_input("البريد الإلكتروني", key="reg_email",
                                      placeholder="example@email.com")
            new_pass  = st.text_input("كلمة المرور (8 أحرف على الأقل)",
                                      type="password", key="reg_pass")
            new_pass2 = st.text_input("تأكيد كلمة المرور",
                                      type="password", key="reg_pass2")

            if st.button("🚀 إنشاء الحساب والبدء مجاناً",
                         use_container_width=True, key="btn_register"):
                db = load_db()
                email_key = new_email.strip().lower()

                # Validations
                if not new_name.strip():
                    st.error("❌ يرجى إدخال الاسم")
                elif "@" not in email_key or "." not in email_key:
                    st.error("❌ بريد إلكتروني غير صالح")
                elif len(new_pass) < 8:
                    st.error("❌ كلمة المرور يجب أن تكون 8 أحرف على الأقل")
                elif new_pass != new_pass2:
                    st.error("❌ كلمتا المرور غير متطابقتين")
                elif email_key in db:
                    st.warning("⚠️ هذا البريد مسجّل مسبقاً. يرجى تسجيل الدخول.")
                else:
                    db[email_key] = {
                        "name": new_name.strip(),
                        "email": email_key,
                        "password": hash_password(new_pass),
                        "registered_date": datetime.date.today().isoformat(),
                        "analyses_used": 0,
                        "subscription": "none",
                        "subscription_end": None
                    }
                    save_db(db)
                    st.success(
                        f"✅ تم إنشاء حسابك! تمتع بـ {TRIAL_DAYS} يوماً مجاناً."
                    )
                    st.balloons()

        # ── معلومات الاشتراك ──────────────────────────
        st.markdown("---")
        st.markdown("""
            <div style="text-align:center; font-size:0.85rem; color:#888;">
                للاشتراك المدفوع أو الدعم الفني تواصل مع:<br>
                <strong>Dr/Hussein Ali — Orange Lab</strong>
            </div>
        """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# ═══════════  AUTHENTICATED — MAIN APP  ═════════════════
# =========================================================

db          = load_db()
email_key   = st.session_state.current_user
user_data   = db.get(email_key, {})
sub_status  = get_subscription_status(user_data)
user_name   = user_data.get("name", email_key)

# ──────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────
col_title, col_user = st.columns([4, 1])

with col_title:
    st.title("🩺 MedInsight Analyzer")
    st.caption("Advanced AI-Powered Laboratory Report Analysis & Quality Review")
    st.caption("Developed by Dr/Hussein Ali")

with col_user:
    st.markdown(f"**👤 {user_name}**")
    st.markdown(f"<small>{email_key}</small>", unsafe_allow_html=True)
    if st.button("🚪 تسجيل الخروج", key="logout_btn"):
        st.session_state.authenticated = False
        st.session_state.current_user  = None
        st.rerun()

# ──────────────────────────────────────────────────────
# شريط حالة الاشتراك
# ──────────────────────────────────────────────────────
status_code = sub_status["status"]

if status_code == "active":
    st.success(sub_status["message"])

elif status_code == "trial":
    st.info(sub_status["message"])

elif status_code in ("expired", "trial_exceeded"):
    st.error(sub_status["message"])

    st.markdown("""
    ---
    ### 💳 الاشتراك في MedInsight Analyzer

    للحصول على وصول غير محدود يرجى التواصل مع:

    | طريقة | التفاصيل |
    |---|---|
    | 📱 WhatsApp | `+20XXXXXXXXXX` |
    | 📧 Email | `hussein@orangelab.com` |
    | 🌐 الموقع | `orangelab.streamlit.app` |

    **بعد السداد سيتم تفعيل حسابك خلال ساعة.**
    """)

    # أزرار الاشتراك
    col_a, col_b = st.columns(2)
    with col_a:
        st.link_button("💬 تواصل عبر WhatsApp",
                       "https://wa.me/20XXXXXXXXXX?text=أريد الاشتراك في MedInsight",
                       use_container_width=True)
    with col_b:
        st.link_button("📧 تواصل عبر Email",
                       "mailto:hussein@orangelab.com?subject=MedInsight Subscription",
                       use_container_width=True)

    st.stop()

# ──────────────────────────────────────────────────────
# API KEY
# ──────────────────────────────────────────────────────
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY not found in Streamlit Secrets")
    st.stop()

# ──────────────────────────────────────────────────────
# GEMINI CLIENT
# ──────────────────────────────────────────────────────
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Failed to initialize Gemini Client: {e}")
    st.stop()

MODEL_NAME = "gemini-2.5-flash"

# ──────────────────────────────────────────────────────
# SIDEBAR SETTINGS
# ──────────────────────────────────────────────────────
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

    st.markdown("---")

    # ── إدارة الحساب في السايدبار ──────────────────
    st.header("👤 حسابي")
    st.markdown(f"**الاسم:** {user_name}")
    st.markdown(f"**البريد:** {email_key}")

    reg_date = user_data.get("registered_date", "—")
    analyses_used = user_data.get("analyses_used", 0)
    st.markdown(f"**تاريخ التسجيل:** {reg_date}")
    st.markdown(f"**التحليلات المُجراة:** {analyses_used}")

    if status_code == "trial":
        st.progress(
            analyses_used / TRIAL_ANALYSES_LIMIT,
            text=f"{analyses_used}/{TRIAL_ANALYSES_LIMIT} تحليل"
        )

    st.markdown("---")

    # ── تفعيل اشتراك (للأدمن فقط — عبر مفتاح سري) ──
    with st.expander("🔑 تفعيل كود اشتراك"):
        activation_code = st.text_input("أدخل كود التفعيل", type="password",
                                        key="activation_code_input")
        activation_months = st.number_input("مدة الاشتراك (أشهر)", min_value=1,
                                            max_value=12, value=3, key="act_months")

        if st.button("✅ تفعيل الاشتراك", key="btn_activate"):
            # الأكواد المتاحة — يُفضَّل تخزينها في st.secrets
            valid_codes = st.secrets.get("ACTIVATION_CODES", {})

            if activation_code in valid_codes or activation_code == st.secrets.get("MASTER_CODE", "__none__"):
                new_end = (
                    datetime.date.today()
                    + datetime.timedelta(days=30 * activation_months)
                ).isoformat()
                db[email_key]["subscription"] = "active"
                db[email_key]["subscription_end"] = new_end
                save_db(db)
                st.success(
                    f"✅ تم تفعيل اشتراكك حتى {new_end}!"
                )
                st.rerun()
            else:
                st.error("❌ كود التفعيل غير صحيح")


# ──────────────────────────────────────────────────────
# OPTIONAL NOTES
# ──────────────────────────────────────────────────────
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

# ──────────────────────────────────────────────────────
# AI QUESTION BOX
# ──────────────────────────────────────────────────────
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

# ──────────────────────────────────────────────────────
# FILE UPLOADER
# ──────────────────────────────────────────────────────
uploaded_files = st.file_uploader(
    "Upload laboratory report images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# ──────────────────────────────────────────────────────
# ANALYSIS BUTTON
# ──────────────────────────────────────────────────────
analyses_left_display = (
    f" ({sub_status['analyses_left']} تحليل متبق)"
    if status_code == "trial" else ""
)

if st.button(f"🚀 Start Smart Medical Analysis{analyses_left_display}"):

    if not uploaded_files:
        st.warning("Please upload at least one laboratory report image.")
        st.stop()

    # ── التحقق من الصلاحية مرة أخرى لحظة الضغط ──
    db        = load_db()
    user_data = db[email_key]
    if not can_analyze(user_data):
        st.error("❌ لا يمكنك إجراء تحليلات. يرجى الاشتراك أو تجديد اشتراكك.")
        st.stop()

    try:
        with st.spinner("Analyzing laboratory reports with AI..."):

            # ── معالجة الصور ──────────────────────────
            images = []
            for file in uploaded_files:
                img = Image.open(file).convert("RGB")
                images.append(img)

            # ── تعليمات ديناميكية ─────────────────────
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

            # ── البرومبت الرئيسي ──────────────────────
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

            # ── Gemini API Request ─────────────────────
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[prompt, *images],
                config={"temperature": 0.2}
            )

            # ── تحديث عداد التحليلات ─────────────────
            db = load_db()
            db[email_key]["analyses_used"] = db[email_key].get("analyses_used", 0) + 1
            save_db(db)

        # ── عرض النتيجة ──────────────────────────────
        st.success("✅ Analysis completed successfully")
        st.markdown("---")
        st.markdown("## 🧾 Smart Medical Report & Laboratory Quality Review")
        st.write(response.text)

        # ── تحميل التقرير ────────────────────────────
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

# ──────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────
st.markdown("---")
st.info(
    "MedInsight Analyzer | AI-Powered Clinical Laboratory Analysis & "
    "Quality Review System | Developed by Dr/Hussein Ali"
)
