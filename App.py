import streamlit as st
import google.generativeai as genai
from PIL import Image

# إعدادات الصفحة
st.set_page_config(page_title="نظام التحليل الطبي - معامل أورنج", page_icon="🩺", layout="wide")

# جلب المفتاح التلقائي من Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

st.title("🩺 نظام التحليل الطبي (Gemini AI) الشامل")
st.write("خاص بمعامل أورنج - 6 أكتوبر / الشيخ زايد")

if api_key:
    try:
        # إعداد المكتبة
        genai.configure(api_key=api_key)
        
        # اختيار الموديل المستقر
        model = genai.GenerativeModel('gemini-1.5-flash')

        col1, col2 = st.columns([1.5, 1])

        with col1:
            st.subheader("📝 مدخلات الحالة")
            manual_history = st.text_area(
                "التاريخ المرضي الإضافي (سكر، ضغط، دهون، أدوية):", 
                placeholder="اكتب أي ملاحظات تود دمجها في التقرير..."
            )
            uploaded_files = st.file_uploader(
                "ارفع صور التحاليل (يمكن رفع أكثر من صورة):", 
                type=['png', 'jpg', 'jpeg'], 
                accept_multiple_files=True
            )

        with col2:
            if uploaded_files:
                st.subheader("🖼️ الصور المرفوعة")
                images = []
                for i, file in enumerate(uploaded_files):
                    img = Image.open(file)
                    images.append(img)
                    st.image(img, caption=f"صورة {i+1}", use_column_width=True)

        if st.button("🚀 بدء التحليل الطبي المتكامل", use_container_width=True):
            if not uploaded_files:
                st.error("يرجى رفع صور التحاليل أولاً.")
            else:
                with st.spinner("جاري استخراج البيانات وتحليل الحالة..."):
                    # تعليمات دقيقة لاستخراج الاسم والسن والتعليق
                    prompt = f"""
                    أنت خبير مختبرات طبية محترف. حلل الصور المرفقة واستخرج الآتي باللغة العربية:
                    1. بيانات المريض: (الاسم، السن، الجنس) من ترويسة النتائج.
                    2. التاريخ المرضي: ادمج الملاحظات المكتوبة أسفل الصور مع هذا التاريخ: {manual_history}
                    3. النتائج: وضح القيم غير الطبيعية (High/Low) فقط.
                    4. التعليق الطبي: قدم رؤية إكلينيكية تربط الحالة بالتاريخ المرضي.
                    """
                    
                    response = model.generate_content([prompt] + images)
                    st.success("✅ تم التحليل بنجاح")
                    st.markdown("---")
                    st.markdown(response.text)

    except Exception as e:
        st.error(f"حدث خطأ في النظام: {e}")
else:
    st.info("👈 يرجى التأكد من إضافة GEMINI_API_KEY في إعدادات Secrets.")
