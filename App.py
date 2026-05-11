import streamlit as st
import google.generativeai as genai
from PIL import Image

# إعدادات الصفحة (عرض واسع لتنظيم النوافذ)
st.set_page_config(page_title="نظام التحليل الطبي الشامل", layout="wide")

st.title("🩺 نظام التحليل الطبي الشامل (Gemini AI)")
st.write("يقوم النظام باستخراج بيانات المريض تلقائياً، قراءة نتائج التحاليل، وربطها بالتاريخ المرضي لتقديم تعليق طبي دقيق.")

# الشريط الجانبي لإعدادات الـ API
with st.sidebar:
    st.header("🔑 إعدادات النظام")
    api_key = st.text_input("أدخل Google API Key:", type="password")
    model_choice = st.selectbox("اختر النموذج:", ["gemini-1.5-pro", "gemini-1.5-flash"])
    st.caption("💡 نوصي باستخدام gemini-1.5-pro للحصول على أدق قراءة للخطوط اليدوية والتقارير المعقدة.")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_choice)

    # تقسيم الشاشة إلى عمودين (عمود للإدخال وعمود لمعاينة الصور)
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📥 إدخال بيانات وحالة المريض")
        
        # نافذة إدخال التاريخ المرضي اليدوي
        manual_history = st.text_area(
            "التاريخ المرضي والأدوية (إدخال يدوي):", 
            placeholder="مثال: يتلقى علاج للسكري (ميتفورمين) وضغط الدم، أو يعاني من ارتفاع الكوليسترول..."
        )

        # نافذة رفع الصور (تدعم الرفع المتعدد)
        uploaded_files = st.file_uploader(
            "ارفع صور التحاليل والتقارير الطبية (يمكنك تحديد أكثر من صورة معاً):", 
            type=['png', 'jpg', 'jpeg'], 
            accept_multiple_files=True
        )

    # معالجة الصور المرفوعة وعرضها في العمود الثاني
    images = []
    if uploaded_files:
        with col2:
            st.subheader("🖼️ الصور المرفوعة")
            for i, file in enumerate(uploaded_files):
                img = Image.open(file)
                images.append(img)
                # عرض معاينة للصور
                st.image(img, caption=f"صورة {i+1}", use_column_width=True)

    # زر تنفيذ التحليل
    st.divider()
    if st.button("🚀 بدء التحليل الطبي الشامل", use_container_width=True):
        if not images:
            st.warning("يرجى رفع صورة واحدة على الأقل لنتائج التحاليل.")
        else:
            with st.spinner("جاري قراءة الصور واستخراج البيانات وكتابة التقرير الطبي..."):
                # صياغة دقيقة للأمر الموجه للذكاء الاصطناعي لضمان هيكل التقرير
                prompt = f"""
                أنت خبير طبي ومحلل نتائج مختبرات محترف. يرجى تحليل الصور المرفقة بدقة شديدة واستخراج المطلوب وفقاً للهيكل التالي باللغة العربية:

                ## 1. البيانات الأساسية للمريض
                استخرج البيانات التالية من الصور المرفقة (إن وجدت):
                - **الاسم:**
                - **العمر:**
                - **الجنس:**

                ## 2. التاريخ المرضي
                - **المستخرج من الصور:** (ابحث عن أي تاريخ مرضي أو ملاحظات مكتوبة أسفل ورقة النتائج أو في التقرير).
                - **المدخل بواسطة الطبيب:** {manual_history if manual_history.strip() else 'لا يوجد إدخال إضافي'}

                ## 3. قراءة النتائج المخبرية
                - استعرض أهم النتائج المستخرجة.
                - ركز بشكل خاص على **القيم غير الطبيعية (Abnormal Values)** مع ذكر المعدل الطبيعي (Reference Range) المرفق بجانبها في الصورة.

                ## 4. التعليق الطبي والربط الإكلينيكي
                - قم بعمل ربط علمي بين النتائج المخبرية والتاريخ المرضي (مثل تأثير أدوية السكر أو الضغط أو الدهون على النتائج الحالية).
                - قدم تفسيراً إكلينيكياً متكاملاً للحالة بناءً على المعطيات.
                """

                try:
                    # إرسال النص مع قائمة الصور دفعة واحدة للنموذج
                    response = model.generate_content([prompt] + images)
                    
                    st.subheader("📋 التقرير الطبي المتكامل")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الاتصال بنموذج Gemini: {str(e)}")
else:
    st.info("👈 يرجى إدخال مفتاح API في الشريط الجانبي لتفعيل واجهة البرنامج.")
