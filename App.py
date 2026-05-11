import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. إعداد الصفحة
st.set_page_config(page_title="معامل أورنج - التحليل الذكي", layout="wide")

# 2. جلب المفتاح من Secrets (تأكد من كتابته GEMINI_API_KEY في الإعدادات)
api_key = st.secrets.get("GEMINI_API_KEY")

st.title("🩺 نظام التحليل الطبي (معامل أورنج)")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # استخدام موديل flash لأنه الأسرع والأكثر استقراراً للصور حالياً
        model = genai.GenerativeModel('gemini-1.5-flash')

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📤 رفع البيانات")
            manual_history = st.text_area("التاريخ المرضي (اختياري):")
            uploaded_files = st.file_uploader("ارفع صور التحاليل:", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

        with col2:
            if uploaded_files:
                images = [Image.open(f) for f in uploaded_files]
                for img in images:
                    st.image(img, use_column_width=True)

        if st.button("🚀 بدء التحليل المتكامل", use_container_width=True):
            if not uploaded_files:
                st.error("يرجى رفع الصور أولاً.")
            else:
                with st.spinner("جاري التحليل..."):
                    # تعليمات محددة للموديل
                    prompt = f"حلل الصور المرفقة لاستخراج اسم المريض وسنه ونتائج التحاليل المرتفعة. التاريخ المرضي المضاف: {manual_history}. الرد يكون بالعربية."
                    response = model.generate_content([prompt] + images)
                    st.success("✅ اكتمل التحليل")
                    st.markdown(response.text)

    except Exception as e:
        st.error(f"حدث خطأ تقني: {e}")
        st.info("تأكد من تحديث ملف requirements.txt وإعادة تشغيل التطبيق.")
else:
    st.warning("⚠️ يرجى ضبط GEMINI_API_KEY في إعدادات Secrets كما في الصورة التي التقطتها.")
