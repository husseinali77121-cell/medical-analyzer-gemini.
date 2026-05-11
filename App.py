import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="نظام التحليل الطبي الذكي",
    page_icon="🩺",
    layout="wide"
)

# 2. إدارة مفتاح الـ API
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    with st.sidebar:
        st.warning("⚠️ لم يتم العثور على مفتاح API في الإعدادات المخفية.")
        api_key = st.text_input("أدخل Google API Key يدوياً للبدء:", type="password")
        st.info("لجعل المفتاح يعمل تلقائياً، قم بإضافته في 'Secrets' بلوحة تحكم Streamlit.")

# 3. واجهة المستخدم الرئيسية
st.title("🩺 نظام التحليل الطبي الشامل (Gemini AI)")
st.markdown("""
هذا النظام مصمم لمساعدتك في قراءة وتحليل التقارير الطبية. 
* يقوم باستخراج **بيانات المريض** (الاسم، السن، الجنس).
* يحلل **نتائج المختبر** ويربطها بـ **التاريخ المرضي** المدخل.
""")

if api_key:
    try:
        # إعداد Gemini والبحث عن أفضل نموذج متاح
        genai.configure(api_key=api_key)

        @st.cache_resource
        def get_model():
            """يبحث عن أول نموذج متاح يدعم generateContent والصور."""
            models = genai.list_models()
            # ترتيب التفضيل: flash ثم pro ثم أي نموذج يدعم الرؤية
            preferred = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro-vision']
            for name in preferred:
                for m in models:
                    if name in m.name and 'generateContent' in m.supported_generation_methods:
                        return genai.GenerativeModel(m.name)
            # خيار احتياطي: أول نموذج يدعم generateContent والصور
            for m in models:
                if ('vision' in m.name.lower() or 'gemini' in m.name.lower()) and 'generateContent' in m.supported_generation_methods:
                    return genai.GenerativeModel(m.name)
            return None

        model = get_model()

        if model is None:
            st.error("❌ لا يوجد نموذج متاح يدعم تحليل الصور. تأكد من ترقية المكتبة `pip install --upgrade google-generativeai` وأن مفتاح API ساري.")
            st.stop()

        col1, col2 = st.columns([1.5, 1])

        with col1:
            st.subheader("📝 مدخلات الحالة")
            manual_history = st.text_area(
                "التاريخ المرضي الإضافي (مثلاً: يعاني من سكر النوع الثاني، ضغط مرتفع، أدوية حالية):",
                height=150,
                placeholder="اكتب هنا أي تفاصيل تود أن يأخذها الذكاء الاصطناعي في الاعتبار عند تحليل النتائج..."
            )
            uploaded_files = st.file_uploader(
                "ارفع صور النتائج والتقارير الطبية:",
                type=['png', 'jpg', 'jpeg'],
                accept_multiple_files=True
            )

        with col2:
            if uploaded_files:
                st.subheader("🖼️ معاينة الصور المرفوعة")
                images = []
                for i, file in enumerate(uploaded_files):
                    img = Image.open(file)
                    images.append(img)
                    st.image(img, caption=f"صورة {i+1}", use_column_width=True)
            else:
                st.info("يرجى رفع صور التحاليل لتظهر المعاينة هنا.")

        st.divider()
        if st.button("🚀 بدء التحليل الطبي المتكامل", use_container_width=True):
            if not uploaded_files:
                st.error("يرجى رفع صورة واحدة على الأقل للتحاليل.")
            else:
                with st.spinner("جاري قراءة البيانات وتحليلها بدقة..."):
                    prompt = f"""
                    أنت خبير في التحاليل الطبية والتشخيص الإكلينيكي. 
                    بناءً على الصور المرفقة، قم باستخراج وتحليل البيانات التالية باللغة العربية بأسلوب مهني ومنظم:

                    1. **بيانات المريض:** (الاسم، السن، الجنس) من ترويسة التقارير.
                    2. **التاريخ المرضي:** - لخص التاريخ المرضي المكتوب في أسفل الصور (إن وجد).
                       - ادمجه مع التاريخ المرضي المكتوب يدوياً هنا: [{manual_history}].
                    3. **تحليل النتائج المخبرية:**
                       - استخرج النتائج الرئيسية.
                       - حدد بوضوح أي نتائج "خارج المعدل الطبيعي" (High/Low) مع ذكر المرجعية.
                    4. **التعليق الطبي الشامل:**
                       - اربط بين التاريخ المرضي (مثل أدوية السكر أو الضغط) وبين النتائج الحالية.
                       - قدم رؤية إكلينيكية حول استقرار الحالة أو حاجتها لمراجعة الطبيب.

                    يرجى كتابة التقرير بشكل منظم باستخدام العناوين والجداول إذا لزم الأمر.
                    """
                    
                    response = model.generate_content([prompt] + images)
                    
                    st.success("✅ تم الانتهاء من التحليل")
                    st.markdown("---")
                    st.markdown(response.text)

    except Exception as e:
        st.error(f"حدث خطأ في النظام: {e}")
        st.info("تأكد من صحة مفتاح API ومن جودة اتصال الإنترنت. قد تحتاج لترقية المكتبة عبر `pip install --upgrade google-generativeai`.")
else:
    st.info("👈 يرجى إعداد مفتاح الـ API من الشريط الجانبي أو من إعدادات Secrets للبدء.")
