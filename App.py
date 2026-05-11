import streamlit as st
import google.generativeai as genai
from PIL import Image

# إعداد الصفحة
st.set_page_config(page_title="معامل أورنج - التحليل الذكي", layout="wide")

# جلب المفتاح
api_key = st.secrets.get("GEMINI_API_KEY")

st.title("🩺 نظام التحليل الطبي (معامل أورنج)")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # كود ذكي لاختيار الموديل المتاح
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # تجربة وهمية للتأكد من الموديل
            model.get_model() 
        except:
            model = genai.GenerativeModel('gemini-pro-vision') # كود احتياطي

        col1, col2 = st.columns([1.5, 1])

        with col1:
            st.subheader("📝 بيانات المريض والحالة")
            manual_history = st.text_area("التاريخ المرضي (اختياري):", placeholder="مثلاً: مريض ضغط، سكر...")
            uploaded_files = st.file_uploader("ارفع صور التحاليل:", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

        with col2:
            if uploaded_files:
                images = [Image.open(f) for f in uploaded_files]
                for i, img in enumerate(images):
                    st.image(img, caption=f"صورة {i+1}", use_column_width=True)

        if st.button("🚀 بدء التحليل الطبي واستخراج البيانات", use_container_width=True):
            if not uploaded_files:
                st.error("يرجى رفع الصور أولاً.")
            else:
                with st.spinner("جاري القراءة والتحليل..."):
                    prompt = f"""
                    أنت طبيب مختبرات خبير. من الصور المرفقة:
                    1. استخرج: (الاسم، السن، الجنس).
                    2. اقرأ التاريخ المرضي أسفل الورقة وادمجه مع: {manual_history}
                    3. لخص النتائج المرتفعة والمنخفضة.
                    4. اكتب تعليقاً طبياً مهنياً.
                    اجعل الرد منظماً جداً وباللغة العربية.
                    """
                    response = model.generate_content([prompt] + images)
                    st.success("✅ اكتمل التحليل")
                    st.markdown(response.text)

    except Exception as e:
        st.error(f"حدث خطأ: {e}")
        st.info("نصيحة: تأكد من تحديث ملف requirements.txt كما ذكرت لك.")
else:
    st.warning("⚠️ يرجى إضافة GEMINI_API_KEY في إعدادات Secrets.")
