import streamlit as st
import google.generativeai as genai
from PIL import Image

# إعدادات الصفحة
st.set_page_config(page_title="Medical Image Analyzer", layout="centered")

# العنوان والوصف
st.title("🩺 محلل البيانات الطبية الذكي")
st.write("قم برفع صور التاريخ المرضي ونتائج التحاليل للحصول على قراءة تحليلية.")

# إدخال الـ API Key في الشريط الجانبي
with st.sidebar:
    st.header("الإعدادات")
    api_key = st.text_input("Google API Key:", type="password")
    model_choice = st.selectbox("اختر النموذج:", ["gemini-1.5-flash", "gemini-1.5-pro"])
    st.info("موديل Flash سريع جداً، بينما Pro أفضل في التحليل العميق.")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_choice)

    # خانة رفع الملفات
    uploaded_files = st.file_uploader("ارفع صور (JPG, PNG)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

    if uploaded_files:
        images = []
        for uploaded_file in uploaded_files:
            img = Image.open(uploaded_file)
            images.append(img)
        
        # عرض مصغرات للصور المرفوعة
        st.image(images, width=150, caption=[f"صورة {i+1}" for i in range(len(images))])

        # منطقة الأوامر (Prompt)
        prompt_text = st.text_area("التعليمات:", 
                                  value="اقرأ البيانات الموجودة في هذه الصور (سواء كانت بخط اليد أو مطبوعة). لخص التاريخ المرضي ونتائج التحاليل، ونبهني لأي قيم خارج المعدل الطبيعي.")

        if st.button("بدء التحليل"):
            with st.spinner("جاري معالجة الصور والتحليل..."):
                try:
                    # إرسال الصور مع النص
                    response = model.generate_content([prompt_text] + images)
                    
                    st.divider()
                    st.subheader("📝 نتائج التحليل:")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
else:
    st.warning("يرجى إدخال مفتاح API في الشريط الجانبي لتفعيل البرنامج.")
