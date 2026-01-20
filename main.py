import streamlit as st
import google.generativeai as genai
import time
import os
import warnings

# --- GÜVENLİK VE AYARLAR ---
warnings.filterwarnings("ignore")
st.set_page_config(page_title="PROJECT ZERO v2", page_icon="🧬", layout="centered")

# --- CSS TASARIM ---
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Montserrat:wght@300;400;600&display=swap');
        .stApp { background-color: #050505; background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.95)), url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop'); background-size: cover; background-attachment: fixed; }
        h1 { color: #FFD700 !important; font-family: 'Orbitron', sans-serif; text-align: center; letter-spacing: 2px; text-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
        .version-tag { text-align: center; color: #555; font-size: 0.8em; margin-top: -20px; font-family: 'Montserrat', sans-serif; }
        .welcome-text { text-align: center; color: #B0B0B0; font-family: 'Montserrat', sans-serif; font-size: 1em; margin-bottom: 30px; }
        .stTextInput > label, .stTextArea > label { color: #D4AF37 !important; font-family: 'Montserrat', sans-serif; font-weight: 600; }
        .stTextInput > div > div > input, .stTextArea > div > div > textarea { background-color: rgba(15, 15, 20, 0.95) !important; color: #ddd !important; border: 1px solid #333 !important; border-radius: 4px; }
        .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus { border-color: #FFD700 !important; box-shadow: none !important; }
        div.stButton > button { background: #1a1a1a; color: #FFD700; border: 1px solid #FFD700; padding: 15px 30px; font-size: 18px; border-radius: 4px; width: 100%; font-family: 'Orbitron', sans-serif; transition: all 0.3s ease; text-transform: uppercase; }
        div.stButton > button:hover { background: #FFD700; color: #000; box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
        .report-container { background-color: #080808; border-left: 5px solid #FFD700; padding: 40px; margin-top: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.9); font-family: 'Montserrat', sans-serif; }
        .report-header { color: #FFD700; font-family: 'Orbitron', sans-serif; font-size: 1.5em; border-bottom: 1px solid #333; padding-bottom: 15px; margin-bottom: 20px; }
        .report-content { color: #ccc; line-height: 1.7; font-size: 1em; white-space: pre-line; }
        .error-box { background-color: rgba(50, 0, 0, 0.9); border: 2px solid #ff0000; color: #ffcccc; padding: 20px; border-radius: 10px; text-align: center; font-family: 'Orbitron', sans-serif; margin-top: 20px; box-shadow: 0 0 20px rgba(255, 0, 0, 0.4); }
        #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# --- BAĞLANTI (GÜVENLİ YÖNTEM) ---
try:
    # Şifreyi güvenli kasadan (Secrets) çekiyoruz
    if "gemini_api_key" in st.secrets:
        api_key = st.secrets["gemini_api_key"]
        genai.configure(api_key=api_key)
    else:
        st.error("HATA: API Anahtarı bulunamadı! Lütfen Secrets ayarlarını kontrol edin.")
        st.stop()

    # Model Seçimi
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if available_models:
        model_name = next((m for m in available_models if "flash" in m), available_models[0])
        model = genai.GenerativeModel(model_name)
    else:
        st.error("Model Bulunamadı.")
        st.stop()
except Exception as e:
    # Hata durumunda kullanıcıya göster ama şifreyi gösterme
    st.error(f"Bağlantı Hatası: {e}")
    st.stop()

# --- ARAYÜZ ---
lang = st.sidebar.selectbox("Dil / Language", ["Türkçe", "English"])

if lang == "Türkçe":
    t = {
        "title": "PROJECT ZERO",
        "version": "Sistem Sürümü: v2.0 (Güvenli Mod)",
        "welcome": "Cevaplarınız bütünsel olarak analiz edilecek ve tek bir psikolojik dosya oluşturulacaktır.",
        "q1": "1. [MANTIK] Bir yarışta sonuncuyu geçerseniz sıralamanız ne olur?",
        "q2": "2. [DİKKAT] İstanbul'da 1 tane, İzmir'de 2 tane olan harf nedir?",
        "q3": "3. [ANALİTİK] 5 elmanız var, 3'ünü yediniz. Geriye ne kaldı?",
        "q4": "4. [SERİ] 3, 6, 12, 24... Seriyi devam ettiren sayı nedir?",
        "q5": "5. [SOYUT] 'İhanet' kavramını bir renkle tanımlasaydınız bu ne olurdu ve neden?",
        "q6": "6. [ETİK] Milyonlarca insanın hayatını kurtarmak için masum bir çocuğu feda eder miydiniz? Gerekçeniz nedir?",
        "q7": "7. [YARATICILIK] Zamanı durdurabilseydiniz, yapacağınız ilk şey ne olurdu? (Etik kaygısı olmadan)",
        "q8": "8. [SOSYAL] Bir liderde olması gereken en tehlikeli özellik nedir?",
        "q9": "9. [BİLİNÇALTI] Rüyalarınızda en sık karşılaştığınız duygu nedir?",
        "q10": "10. [EGO] Tarihte silmek istediğiniz tek bir olay ne olurdu?",
        "btn": "DOSYAYI OLUŞTUR",
        "wait": "Analiz yapılıyor... Lütfen bekleyiniz...",
        "prompt": """
        Sen FBI Profil Uzmanısın. Cevapları analiz et.
        PUANLAMA: Ortalama cevaplara 90-105, derin cevaplara 115+ ver. 120+ çok nadir olsun.
        RAPOR:
        1. **IQ:** [Aralık]
        2. **ARKETİP:** [Ünvan]
        3. **PSİKOLOJİK TANI:** [Paragraf]
        4. **KARAKTER EŞLEŞMESİ:** [Kişi ve Neden]
        5. **GÖLGE BENLİK:** [3 Madde]
        """
    }
else:
    t = {
        "title": "PROJECT ZERO",
        "version": "System Version: v2.0 (Secure Mode)",
        "welcome": "Your answers will be analyzed holistically to generate a single psychological dossier.",
        "q1": "1. [LOGIC] If you pass the last person in a race, what position are you in?",
        "q2": "2. [ATTENTION] What occurs once in a minute, twice in a moment, but never in a thousand years?",
        "q3": "3. [ANALYTIC] You have 5 apples, you ate 3. What do you have left?",
        "q4": "4. [SERIES] 3, 6, 12, 24... What represents the next step?",
        "q5": "5. [ABSTRACT] If 'Betrayal' were a color, what would it be and why?",
        "q6": "6. [ETHICS] Would you sacrifice an innocent child to save millions? What is your rationale?",
        "q7": "7. [CREATIVITY] If you could stop time, what is the first thing you would do? (Without ethical constraints)",
        "q8": "8. [SOCIAL] What is the most dangerous trait a leader can possess?",
        "q9": "9. [SUBCONSCIOUS] What is the recurring emotion in your dreams?",
        "q10": "10. [EGO] If you could erase one event from history, what would it be?",
        "btn": "GENERATE DOSSIER",
        "wait": "Synthesizing data... Constructing profile...",
        "prompt": """
        You are an FBI Profiler. Analyze answers holistically.
        SCORING: 90-105 for standard, 115+ for deep. 120+ rare.
        REPORT:
        1. **IQ:** [Range]
        2. **ARCHETYPE:** [Title]
        3. **DIAGNOSIS:** [Paragraph]
        4. **CHARACTER MATCH:** [Person & Why]
        5. **SHADOW SELF:** [3 Points]
        """
    }

st.markdown(f"<h1>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='version-tag'>{t['version']}</p>", unsafe_allow_html=True)
st.markdown(f"<p class='welcome-text'>{t['welcome']}</p>", unsafe_allow_html=True)

with st.form("main_form"):
    col1, col2 = st.columns(2)
    with col1:
        a1 = st.text_input(t['q1'])
        a2 = st.text_input(t['q2'])
        a3 = st.text_input(t['q3'])
        a4 = st.text_input(t['q4'])
        a5 = st.text_area(t['q5'])
    with col2:
        a6 = st.text_area(t['q6'])
        a7 = st.text_area(t['q7'])
        a8 = st.text_input(t['q8'])
        a9 = st.text_input(t['q9'])
        a10 = st.text_input(t['q10'])
    
    st.markdown("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        submitted = st.form_submit_button(t['btn'])

if submitted:
    if all([a1, a2, a3, a4, a5, a6, a7, a8, a9, a10]):
        with st.spinner(t['wait']):
            try:
                user_answers = f"1.{a1}\n2.{a2}\n3.{a3}\n4.{a4}\n5.{a5}\n6.{a6}\n7.{a7}\n8.{a8}\n9.{a9}\n10.{a10}"
                full_prompt = f"{t['prompt']}\n\nUSER ANSWERS:\n{user_answers}"
                response = model.generate_content(full_prompt)
                
                st.markdown(f"""
                <div class="report-container">
                    <div class="report-header">📂 GİZLİ ANALİZ DOSYASI</div>
                    <div class="report-content">{response.text}</div>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower():
                     st.markdown(f"""
                    <div class="error-box">
                        <h3>⚠️ KOTA DOLDU (YENİ KEY ÇALIŞMADI MI?)</h3>
                        <p>Sistem şu an hala dolu görünüyor.</p>
                        <p>Lütfen Secrets ayarlarını kontrol et.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Hata: {e}")
    else:
        st.warning("⚠️ Lütfen tüm alanları doldurunuz.")