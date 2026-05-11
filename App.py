import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. إعدادات واجهة المستخدم
st.set_page_config(
    page_title="نظام معامل أورنج للتحليل الذكي",
    page_icon="🩺",
    layout="centered"
)

# تنسيق العنوان والشعار
st.markdown("""
    <div style="text-align: center;">
        <h1 style="color: #0047AB;">نظام التحليل الطبي الشامل (Gemini AI)</h1>
        <p style="font-size: 1.2em;">يقوم النظام باستخراج بيانات المريض تلقائياً، قراءة نتائج التحاليل، وربطها بالتاريخ المرضي لتقديم تعليق طبي دقيق.</p>
    </div>
""", unsafe_allow_html=True)

# 2. جلب مفتاح الـ API من Secrets
# تأكد من إضافة GEMINI_API_KEY في إعدادات Streamlit Cloud
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ عذراً: مفتاح API غير موجود. يرجى إضافته في إعدادات Secrets باسم GEMINI_API_KEY")
    st.stop()

# إعداد المكتبة
genai.configure(api_key=api_key)

# 3. اختيار الموديل (استخدام الاسم الكامل لتفادي خطأ 404)
try:
    # نستخدم gemini-1.5-flash لسرعته ودعمه الممتاز للصور
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
except Exception as e:
    st.error(f"خطأ في إعداد الموديل: {e}")
    st.stop()

# 4. واجهة رفع الملفات
st.sidebar.header("إعدادات التحليل")
patient_history = st.sidebar.text_area("التاريخ المرضي (اختياري):", placeholder="مثلاً: مريض سكري منذ 10 سنوات...")

uploaded_files = st.file_uploader(
    "قم برفع صور التحاليل أو التاريخ المرضي:", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True
)

# 5. زر بدء المعالجة
if st.button("🚀 بدء التحليل الطبي المتكامل"):
    if not uploaded_files:
        st.warning("⚠️ يرجى رفع صورة واحدة على الأقل للبدء.")
    else:
        with st.spinner("جاري قراءة الصور وتحليل البيانات الطبية..."):
            try:
                # تجهيز الصور للمعالجة
                image_parts = []
                for uploaded_file in uploaded_files:
                    bytes_data = uploaded_file.getvalue()
                    image_parts.append({
                        "mime_type": uploaded_file.type,
                        "data": bytes_data
                    })

                # البرومبت (الأوامر الموجهة للذكاء الاصطناعي)
                prompt_parts = [
                    "أنت طبيب مختبرات وخبير في تحليل النتائج الطبية. المطلوب منك:",
                    "1. استخراج بيانات المريض (الاسم، السن، الجنس) إن وجدت.",
                    "2. قراءة كل التحاليل الموجودة في الصور بدقة.",
                    "3. تحديد النتائج التي تقع خارج المعدل الطبيعي (High/Low) وتمييزها.",
                    "4. تقديم شرح طبي مبسط بالعربية للنتائج.",
                    f"5. ربط هذه النتائج بالتاريخ المرضي التالي: {patient_history if patient_history else 'لا يوجد تاريخ مرضي مقدم'}.",
                    "اجعل الإجابة منظمة في جداول أو نقاط واضحة.",
                ]

                # إرسال الطلب للموديل
                response = model.generate_content(prompt_parts + image_parts)
                
                # عرض النتائج
                st.success("✅ تم الانتهاء من التحليل")
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                if "404" in str(e):
                    st.error("خطأ 404: الموديل غير مدعوم في هذه النسخة. تأكد من تحديث ملف requirements.txt")
                else:
                    st.error(f"حدث خطأ فني: {e}")

st.markdown("---")
st.caption("تطوير د. حسين علي - معامل أورنج 2026")
