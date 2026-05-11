import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# إعدادات الصفحة
st.set_page_config(page_title="نظام معامل أورنج الذكي", layout="wide")

# عرض الشعار والاسم
st.title("🩺 محلل البيانات الطبية الذكي - معامل أورنج")

# جلب المفتاح من Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    # إعداد المكتبة
    genai.configure(api_key=api_key)
    
    # استخدام الموديل Flash لأنه الأسرع والأكثر استقراراً للصور
    # جربنا هنا كتابة الاسم بطريقة تضمن التعرف عليه في كل الإصدارات
    model = genai.GenerativeModel('gemini-1.5-flash')

    # واجهة رفع الملفات
    uploaded_files = st.file_uploader("ارفع صور التحاليل (JPG/PNG):", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    
    if st.button("🚀 بدء التحليل المتكامل"):
        if uploaded_files:
            with st.spinner("جاري قراءة الصور وتحليل البيانات..."):
                try:
                    images = []
                    for f in uploaded_files:
                        img = Image.open(f)
                        images.append(img)
                    
                    # البرومبت الطبي
                    prompt = "أنت طبيب مختبرات محترف. قم باستخراج كافة النتائج الطبية من الصور المرفقة، حدد القيم المرتفعة أو المنخفضة، وقدم ملخصاً باللغة العربية."
                    
                    # إرسال الصور للموديل
                    response = model.generate_content([prompt] + images)
                    
                    st.success("✅ اكتمل التحليل")
                    st.markdown("### النتائج المستخلصة:")
                    st.write(response.text)
                    
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}")
        else:
            st.warning("يرجى رفع ملفات أولاً.")
else:
    st.error("❌ مفتاح API غير موجود. تأكد من إضافته في Streamlit Cloud Secrets باسم GEMINI_API_KEY")

st.info("تطوير د. حسين علي - 2026")
