import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import json
import time

# ==========================================
# 1. AYARLAR VE GÜVENLİK
# ==========================================
st.set_page_config(
    page_title="PROJECT ZERO",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. GLOBAL CSS - Mobil App için Tam Optimizasyon
# ==========================================
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#0b0e19">

<style>
    /* ============================================
       STREAMLIT BRANDING TAMAMEN KALDIR
    ============================================ */
    
    /* Header, Footer, Menu - HEPSİNİ GİZLE */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .styles_viewerBadge__1yB5_ {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    /* Streamlit logosu ve tüm branding */
    .streamlit-footer {display: none !important;}
    .css-1rs6os {display: none !important;}
    .css-17eq0hr {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}
    
    /* Sidebar tamamen gizle */
    section[data-testid="stSidebar"] {display: none !important;}
    .stApp > header {display: none !important;}
    
    /* ============================================
       MOBİL OPTİMİZASYON
    ============================================ */
    
    /* Full screen app deneyimi */
    html, body, [data-testid="stAppViewContainer"], .main {
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
    }
    
    .stApp {
        background-color: #0b0e19 !important;
        max-width: 100% !important;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    
    /* Mobil viewport ayarları */
    @viewport {
        width: device-width;
        zoom: 1.0;
    }
    
    /* Touch-friendly butonlar */
    .stButton > button {
        background: linear-gradient(135deg, #0a3f4d 0%, #063640 100%) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        color: white !important;
        font-family: 'Epilogue', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.15em !important;
        padding: 1.2rem 2rem !important; /* Daha büyük touch area */
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        min-height: 48px !important; /* Touch standartları */
        font-size: 14px !important;
    }
    
    .stButton > button:active {
        transform: scale(0.98) !important;
        background: linear-gradient(135deg, #0d5a6e 0%, #0a4a58 100%) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0d5a6e 0%, #0a4a58 100%) !important;
        border-color: rgba(0, 229, 255, 0.6) !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.3) !important;
    }
    
    /* Radio butonları - mobil dostu */
    .stRadio > div {
        background: #1B222D !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    .stRadio label {
        color: #e2e8f0 !important;
        font-family: 'Manrope', sans-serif !important;
        min-height: 44px !important; /* Touch-friendly */
        display: flex !important;
        align-items: center !important;
        padding: 8px !important;
    }
    
    /* Text input - mobil klavye uyumlu */
    .stTextInput input, .stTextArea textarea {
        background: #0E111A !important;
        border: none !important;
        border-bottom: 2px solid #374151 !important;
        color: #e2e8f0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        border-radius: 0 !important;
        font-size: 16px !important; /* iOS zoom önleme */
        padding: 12px 8px !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-bottom-color: #00E5FF !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Markdown text renkleri */
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #e2e8f0 !important;
    }
    
    /* Expander (Admin panel için) */
    .streamlit-expanderHeader {
        background: #1B222D !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 14px !important;
    }
    
    /* ============================================
       MOBİL RESPONSIVE AYARLAR
    ============================================ */
    
    @media only screen and (max-width: 768px) {
        /* Mobilde daha küçük margin */
        .block-container {
            padding: 0 !important;
        }
        
        /* Mobil font boyutları */
        .stButton > button {
            font-size: 13px !important;
            padding: 1rem 1.5rem !important;
        }
        
        /* Mobilde components daha küçük */
        .streamlit-expanderHeader {
            font-size: 12px !important;
        }
    }
    
    /* Çok küçük ekranlar */
    @media only screen and (max-width: 480px) {
        .stButton > button {
            font-size: 12px !important;
            padding: 0.9rem 1.2rem !important;
            letter-spacing: 0.1em !important;
        }
    }
    
    /* iOS Safari safe area */
    @supports (padding: max(0px)) {
        .block-container {
            padding-left: max(0px, env(safe-area-inset-left)) !important;
            padding-right: max(0px, env(safe-area-inset-right)) !important;
            padding-bottom: max(0px, env(safe-area-inset-bottom)) !important;
        }
    }
    
    /* Disable text selection on mobile */
    * {
        -webkit-tap-highlight-color: rgba(0, 229, 255, 0.2);
        -webkit-touch-callout: none;
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
    }
</style>

<link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@300;400;500;600;700;900&family=Manrope:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
""", unsafe_allow_html=True)

# ==========================================
# 3. SESSION STATE
# ==========================================
if 'page' not in st.session_state: st.session_state['page'] = 'landing'
if 'language' not in st.session_state: st.session_state['language'] = 'TR'
if 'user_data' not in st.session_state: st.session_state['user_data'] = {}
if 'analysis_result' not in st.session_state: st.session_state['analysis_result'] = None
# Maliyet takip sistemi
if 'api_costs' not in st.session_state: st.session_state['api_costs'] = {
    'total_input_tokens': 0,
    'total_output_tokens': 0,
    'total_cost_usd': 0.0,
    'total_analyses': 0,
    'last_analysis_cost': None
}

# ==========================================
# 4. İÇERİK VERİTABANI
# ==========================================
CONTENT = {
    "TR": {
        "LANDING": {"STATUS": "Sistem Hazır", "TITLE": "Zihninin derinliklerine dal", "BTN": "SİSTEME GİRİŞ"},
        "QUIZ": {"HEADER": "Değerlendirme Protokolü", "SEC": "PSİKOLOJİK ANALİZ", "TITLE": "DERİN DEĞERLENDİRME", "SUB": "// GİZLİ: SEVİYE 5 ERİŞİM", "BTN_NEXT": "ANALİZİ BAŞLAT"},
        "PAYWALL": {"ALERT": "Güvenlik Uyarısı", "TITLE": "DOSYA ŞİFRELENDİ", "DESC": "Gelişmiş veriler yüksek güvenlik yetkisi gerektirir.", "BTN_AD": "ŞİFRE ÇÖZ"},
        "RESULT": {"TITLE": "GİZLİ DOSYA", "MATCH": "EŞLEŞME", "IQ_LBL": "IQ SKORU", "LOGIC": "MANTIK", "RISK": "RİSK SEVİYESİ", "WARN": "GÖLGE BENLİK TESPİT EDİLDİ", "BTN_PURGE": "VERİLERİ SİL"},
        "QUESTIONS": [
            {"id": "s1", "section": "BÖLÜM 1: STRATEJİK KARAR", "text": "1. [LİDERLİK] Yönettiğin şirket batıyor. Kendi itibarını mı kurtarırsın yoksa sadık ekibini mi?", "opts": ["Kendi itibarımı kurtaracak ama çalışanları suçlayacak bir strateji izlerim", "Sorumluluğu üstlenir, itibar kaybetsem de ekibi koruyup yeniden başlamayı denerim"]},
            {"id": "s2", "text": "2. [STRATEJİ] Rakibin toplantıda büyük bir hata yapıyor. Tepkin ne olur?", "opts": ["Toplantıda hatasını düzeltip zekamı kanıtlarım", "Hata yapmasına izin veririm, proje başarısız olunca kurtarıcı olarak devreye girerim", "Toplantıdan sonra gizlice uyarır ve bana borçlanmasını sağlarım"]},
            {"id": "s3", "text": "3. [ANALİTİK] Nilüfer yaprağı her gün 2 kat büyüyor. Göl 48 günde doluyorsa, yarısı kaçıncı günde dolar?", "opts": ["24", "47", "12", "46"]},
            {"id": "s4", "text": "4. [ADALET] Yozlaşmış bir kurumun sisteminde açık buldun. Ne yaparsın?", "opts": ["Parayı kendime alırım", "Parayı hayır kurumlarına dağıtırım", "Açığı bildirip ödül/statü isterim", "Hiçbir şey yapmam"]},
            {"id": "q1", "section": "BÖLÜM 2: BİLİŞSEL TEMELLER", "text": "5. [MANTIK] Bir yarışta ikinciyi geçerseniz sıralamanız ne olur?", "type": "text"},
            {"id": "q2", "text": "6. [DİKKAT] İstanbul'da 1 tane, İzmir'de 2 tane olan harf nedir?", "type": "text"},
            {"id": "q3", "text": "7. [ANALİTİK] 5 elmanız var, 1 tanesi yere düştü 3'ünü yediniz. Geriye kaç elmanız kaldı?", "type": "text"},
            {"id": "q4", "text": "8. [SERİ] 3, 8, 18, 38... Seriyi devam ettiren sayı nedir?", "type": "text"},
            {"id": "q5", "text": "9. [ÖZ-FARKINDALIK] Kendi zekanızı nasıl tanımlarsınız?", "type": "textarea"},
            {"id": "q6", "text": "10. [BAŞARI] En gurur duyduğunuz başarınız nedir?", "type": "textarea"},
            {"id": "q7", "text": "11. [STRES] Stresle başa çıkma yöntemleriniz nelerdir?", "type": "textarea"},
            {"id": "q8", "text": "12. [SOSYAL] Bir liderde olması gereken en tehlikeli özellik nedir?", "type": "textarea"},
            {"id": "q9", "text": "13. [BİLİNÇALTI] Rüyalarınızda en sık karşılaştığınız duygu nedir?", "type": "text"},
            {"id": "q10", "text": "14. [EGO] Tarihten bir olayı silmek isteseydiniz o tek bir olay ne olurdu?", "type": "textarea"},
            {"id": "q11", "section": "BÖLÜM 3: DAVRANIŞSAL DERİNLİK", "text": "15. [SOYUT] 'İhanet' kavramını bir renkle tanımlasaydınız bu ne olurdu ve neden?", "type": "textarea"},
            {"id": "q12", "text": "16. [ETİK] Milyonlarca insanın hayatını kurtarmak için masum bir çocuğu feda eder miydiniz? Neden?", "type": "textarea"},
            {"id": "q13", "text": "17. [İKTİDAR] Üstün zekayı insanları yönetmek için mi yoksa onlara hizmet etmek için mi kullanırdın?", "type": "textarea"},
            {"id": "q14", "text": "18. [GERÇEKÇİLİK] Zekanın tek başına başarıyı garantilemediği durumlara örnek verebilir misiniz?", "type": "textarea"},
            {"id": "q15", "text": "19. [YARATICILIK] Zamanı durdurabilseniz ilk yapacağınız şey ne olurdu?", "type": "textarea"},
            {"id": "q16", "text": "20. [ETKİ] Hayatınızda en çok etkilendiğiniz kitap veya film nedir?", "type": "textarea"},
            {"id": "q17", "text": "21. [ANLAM] Boş vakitlerinizi nasıl değerlendirirsiniz?", "type": "textarea"},
            {"id": "q18", "text": "22. [GÜNLÜK YAŞAM] Günde kaç saat uyursunuz?", "type": "text"},
            {"id": "q19", "text": "23. [GÜNLÜK YAŞAM] Gece kaçta yatarsınız?", "type": "text"},
            {"id": "q20", "text": "24. [BENZETME] Kendinizi bir hayvana benzetseniz hangi hayvan olurdu ve neden?", "type": "textarea"}
        ]
    },
    "EN": {
        "LANDING": {"STATUS": "System Ready", "TITLE": "Dive into the depths of your mind", "BTN": "ENTER SYSTEM"},
        "QUIZ": {"HEADER": "Assessment Protocol", "SEC": "PSYCHOLOGICAL ANALYSIS", "TITLE": "DEEP EVALUATION", "SUB": "// CLASSIFIED: LEVEL 5 EYES ONLY", "BTN_NEXT": "INITIATE ANALYSIS"},
        "PAYWALL": {"ALERT": "Security Alert", "TITLE": "FILE ENCRYPTED", "DESC": "Advanced data requires higher security clearance.", "BTN_AD": "DECRYPT"},
        "RESULT": {"TITLE": "CONFIDENTIAL FILE", "MATCH": "MATCH", "IQ_LBL": "IQ SCORE", "LOGIC": "LOGIC", "RISK": "RISK LEVEL", "WARN": "SHADOW SELF DETECTED", "BTN_PURGE": "PURGE DATA"},
        "QUESTIONS": [
            {"id": "s1", "section": "SECTION 1: STRATEGIC DECISION", "text": "1. [LEADERSHIP] Your company is failing. Do you save your reputation or your loyal team?", "opts": ["I follow a strategy to save my reputation but blame employees", "I take responsibility, protect the team even if I lose reputation"]},
            {"id": "s2", "text": "2. [STRATEGY] Your rival makes a big mistake in a meeting. Your reaction?", "opts": ["Correct their mistake in the meeting to prove my intelligence", "Let them fail, then step in as the savior when the project fails", "Warn them privately afterwards, making them owe me"]},
            {"id": "s3", "text": "3. [ANALYTIC] Lily pad doubles daily. Lake fills in 48 days. When is it half full?", "opts": ["24", "47", "12", "46"]},
            {"id": "s4", "text": "4. [JUSTICE] You found a vulnerability in a corrupt institution. What do you do?", "opts": ["Take the money for myself", "Distribute to charities", "Report and ask for reward/status", "Do nothing"]},
            {"id": "q1", "section": "SECTION 2: COGNITIVE FOUNDATIONS", "text": "5. [LOGIC] If you pass the person in 2nd place, what is your position?", "type": "text"},
            {"id": "q2", "text": "6. [ATTENTION] Which letter appears once in 'MISSISSIPPI' but three times in 'MASSACHUSETTS'?", "type": "text"},
            {"id": "q3", "text": "7. [ANALYTIC] You have 5 apples, 1 falls, you eat 3. How many remain?", "type": "text"},
            {"id": "q4", "text": "8. [SERIES] 3, 8, 18, 38... What is the next number?", "type": "text"},
            {"id": "q5", "text": "9. [SELF-AWARENESS] How would you describe your own intelligence?", "type": "textarea"},
            {"id": "q6", "text": "10. [ACHIEVEMENT] What is your proudest accomplishment?", "type": "textarea"},
            {"id": "q7", "text": "11. [STRESS] What are your methods for coping with stress?", "type": "textarea"},
            {"id": "q8", "text": "12. [SOCIAL] What is the most dangerous trait a leader should have?", "type": "textarea"},
            {"id": "q9", "text": "13. [SUBCONSCIOUS] What emotion do you most frequently encounter in your dreams?", "type": "text"},
            {"id": "q10", "text": "14. [EGO] If you could erase one event from history, what would it be?", "type": "textarea"},
            {"id": "q11", "section": "SECTION 3: BEHAVIORAL DEPTH", "text": "15. [ABSTRACT] If you defined 'Betrayal' with a color, what would it be and why?", "type": "textarea"},
            {"id": "q12", "text": "16. [ETHICS] Would you sacrifice an innocent child to save millions? Why?", "type": "textarea"},
            {"id": "q13", "text": "17. [POWER] Would you use superior intelligence to govern people or serve them?", "type": "textarea"},
            {"id": "q14", "text": "18. [REALISM] Can you give examples where intelligence alone doesn't guarantee success?", "type": "textarea"},
            {"id": "q15", "text": "19. [CREATIVITY] If you could stop time, what would be the first thing you'd do?", "type": "textarea"},
            {"id": "q16", "text": "20. [INFLUENCE] What book or movie has influenced you the most?", "type": "textarea"},
            {"id": "q17", "text": "21. [MEANING] How do you spend your free time?", "type": "textarea"},
            {"id": "q18", "text": "22. [DAILY LIFE] How many hours do you sleep per day?", "type": "text"},
            {"id": "q19", "text": "23. [DAILY LIFE] What time do you go to bed?", "type": "text"},
            {"id": "q20", "text": "24. [COMPARISON] If you were to compare yourself to an animal, which would it be and why?", "type": "textarea"}
        ]
    }
}

# ==========================================
# 5. SAYFA FONKSİYONLARI
# ==========================================

def show_landing():
    """Giriş ekranı - Geliştirilmiş tasarım"""
    lang = st.session_state['language']
    t = CONTENT[lang]['LANDING']
    
    landing_html = f'''
    <link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@400;500;700;900&family=Manrope:wght@400;500;700&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet"/>
    
    <style>
        @keyframes breath {{
            0%, 100% {{ opacity: 0.4; transform: scale(0.95); }}
            50% {{ opacity: 0.8; transform: scale(1.05); }}
        }}
        .animate-breath {{ animation: breath 4s ease-in-out infinite; }}
        .scanlines {{
            background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.2));
            background-size: 100% 4px;
            pointer-events: none;
        }}
        .material-symbols-outlined {{
            font-family: 'Material Symbols Outlined';
            font-weight: normal;
            font-style: normal;
            font-size: 24px;
            line-height: 1;
            letter-spacing: normal;
            text-transform: none;
            display: inline-block;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
            -webkit-font-feature-settings: 'liga';
            font-feature-settings: 'liga';
            -webkit-font-smoothing: antialiased;
        }}
    </style>
    
    <div style="position: relative; display: flex; flex-direction: column; min-height: 100vh; width: 100%; margin: 0; background: #0b0e19; overflow: hidden;">
        
        <!-- Grid Background -->
        <div style="position: absolute; inset: 0; opacity: 0.03; pointer-events: none; background-image: linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px); background-size: 40px 40px;"></div>
        
        <!-- Vignette -->
        <div style="position: absolute; inset: 0; background: radial-gradient(ellipse at center, transparent 0%, rgba(0,0,0,0.7) 100%); pointer-events: none; z-index: 0;"></div>
        
        <!-- Scanlines -->
        <div class="scanlines" style="position: absolute; inset: 0; opacity: 0.1; z-index: 10;"></div>
        
        <!-- Top Status Bar -->
        <div style="position: relative; z-index: 20; display: flex; justify-content: space-between; align-items: center; padding: 20px 24px 8px; font-size: 12px; color: #64748b; font-family: 'Epilogue', sans-serif; letter-spacing: 0.2em; text-transform: uppercase; opacity: 0.6;">
            <span>{t['STATUS']}</span>
            <span>V 2.0.4</span>
        </div>
        
        <!-- Main Content -->
        <div style="position: relative; z-index: 20; flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; padding: 0 24px;">
            
            <!-- Brain Icon with Glow -->
            <div style="position: relative; margin-bottom: 48px;">
                <!-- Outer Glow -->
                <div class="animate-breath" style="position: absolute; inset: -20px; background: #00E5FF; border-radius: 50%; filter: blur(80px); opacity: 0.25;"></div>
                
                <!-- Icon Container -->
                <div style="position: relative; display: flex; align-items: center; justify-content: center; width: 140px; height: 140px; border-radius: 20px; background: rgba(17, 30, 33, 0.5); border: 1px solid rgba(255,255,255,0.08); backdrop-filter: blur(8px); box-shadow: 0 0 30px rgba(0, 229, 255, 0.2); transition: transform 0.7s ease-out;">
                    <span class="material-symbols-outlined" style="font-size: 72px; color: #00E5FF; filter: drop-shadow(0 0 12px rgba(0,229,255,0.6));">psychology</span>
                    <!-- Keyhole overlay -->
                    <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;">
                        <span class="material-symbols-outlined" style="font-size: 28px; color: #0b0e19; margin-top: 36px; margin-left: 4px;">key_vertical</span>
                    </div>
                </div>
                
                <!-- Decorative Lines -->
                <div style="position: absolute; right: -60px; top: 50%; width: 48px; height: 1px; background: linear-gradient(to right, rgba(0, 229, 255, 0.5), transparent);"></div>
                <div style="position: absolute; left: -60px; top: 50%; width: 48px; height: 1px; background: linear-gradient(to left, rgba(0, 229, 255, 0.5), transparent);"></div>
            </div>
            
            <!-- Title Section -->
            <div style="text-align: center; margin-bottom: 48px;">
                <h1 style="color: white; font-family: 'Epilogue', sans-serif; font-weight: 900; font-size: 48px; letter-spacing: 0.25em; line-height: 1.2; margin: 0; text-shadow: 0 4px 8px rgba(0,0,0,0.5);">
                    PROJECT<br/><span style="color: rgba(0, 229, 255, 0.95);">ZERO</span>
                </h1>
                <div style="display: flex; align-items: center; justify-content: center; gap: 12px; margin-top: 20px;">
                    <div style="height: 1px; width: 32px; background: #334155;"></div>
                    <p style="color: #94a3b8; font-size: 15px; margin: 0; letter-spacing: 0.08em;">{t['TITLE']}</p>
                    <div style="height: 1px; width: 32px; background: #334155;"></div>
                </div>
            </div>
        </div>
        
        <!-- Bottom Gradient Line -->
        <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 2px; background: linear-gradient(to right, transparent, #0a3f4d, transparent); opacity: 0.5;"></div>
    </div>
    '''
    
    components.html(landing_html, height=750, scrolling=False)
    
    # Native Streamlit butonları
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(f"🔐 {t['BTN']}", use_container_width=True, type="primary"):
            st.session_state['page'] = 'quiz'
            st.rerun()
        
        # Dil seçimi
        lang_col1, lang_col2 = st.columns(2)
        with lang_col1:
            if st.button("🇹🇷 TR", use_container_width=True):
                st.session_state['language'] = 'TR'
                st.rerun()
        with lang_col2:
            if st.button("🇬🇧 EN", use_container_width=True):
                st.session_state['language'] = 'EN'
                st.rerun()


def show_quiz():
    """Quiz ekranı - Birebir HTML şablonu"""
    t = CONTENT[st.session_state['language']]['QUIZ']
    questions = CONTENT[st.session_state['language']]['QUESTIONS']
    total_q = len(questions)
    
    # Tailwind + Custom CSS'li header + stilleri enjekte et
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@400;500;600;700&family=Manrope:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <style>
        .material-symbols-outlined {
            font-family: 'Material Symbols Outlined';
            font-weight: normal;
            font-style: normal;
            font-size: 24px;
            line-height: 1;
            letter-spacing: normal;
            text-transform: none;
            display: inline-block;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
            -webkit-font-feature-settings: 'liga';
            font-feature-settings: 'liga';
        }
        .sr-only-input {
            position: absolute;
            opacity: 0;
            cursor: pointer;
            height: 0;
            width: 0;
        }
        @keyframes ping-anim {
            75%, 100% { transform: scale(2); opacity: 0; }
        }
        .animate-ping-custom {
            animation: ping-anim 1s cubic-bezier(0, 0, 0.2, 1) infinite;
        }
        
        /* Styled Radio Buttons */
        div[data-testid="stRadio"] > div {
            background: transparent !important;
            gap: 8px !important;
        }
        div[data-testid="stRadio"] > div > label {
            background: #0d1117 !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 4px !important;
            padding: 12px 16px !important;
            margin: 0 !important;
            transition: all 0.3s !important;
            cursor: pointer !important;
        }
        div[data-testid="stRadio"] > div > label:hover {
            border-color: rgba(0, 229, 255, 0.4) !important;
            background: rgba(0, 229, 255, 0.05) !important;
        }
        div[data-testid="stRadio"] > div > label[data-checked="true"] {
            border-color: #00E5FF !important;
            background: rgba(0, 229, 255, 0.1) !important;
            box-shadow: 0 0 10px rgba(0, 229, 255, 0.3) !important;
        }
        div[data-testid="stRadio"] label p {
            color: #9ca3af !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 13px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }
        div[data-testid="stRadio"] label:hover p {
            color: white !important;
        }
        
        /* Custom Input Styles */
        .stTextInput input, .stTextArea textarea {
            background: rgba(13, 17, 23, 0.8) !important;
            border: none !important;
            color: #00E5FF !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 14px !important;
            padding: 16px !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            box-shadow: none !important;
            outline: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Sticky Header (components.html ile)
    header_html = f'''
    <div style="background: rgba(11, 14, 25, 0.95); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(255,255,255,0.05); position: sticky; top: 0; z-index: 50;">
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 16px;">
            <div style="color: #9ca3af; font-size: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 50%; border: 1px solid transparent; transition: all 0.2s;">
                <span class="material-symbols-outlined" style="font-size: 20px;">arrow_back</span>
            </div>
            <h1 style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; letter-spacing: 0.2em; color: rgba(0, 229, 255, 0.7); text-transform: uppercase; margin: 0;">Protocol: Active</h1>
            <div style="display: flex; align-items: center; gap: 6px; padding: 4px 8px; border-radius: 4px; background: rgba(0, 229, 255, 0.1); border: 1px solid rgba(0, 229, 255, 0.2);">
                <span style="position: relative; display: flex; height: 8px; width: 8px;">
                    <span class="animate-ping-custom" style="position: absolute; display: inline-flex; height: 100%; width: 100%; border-radius: 50%; background: #00E5FF; opacity: 0.75;"></span>
                    <span style="position: relative; display: inline-flex; border-radius: 50%; height: 8px; width: 8px; background: #00E5FF;"></span>
                </span>
                <span style="font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 11px; color: #00E5FF;">35%</span>
            </div>
        </div>
        <div style="height: 2px; width: 100%; background: #1B222D; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; height: 100%; background: #00E5FF; box-shadow: 0 0 10px #00E5FF; width: 35%; transition: all 1s ease-out;"></div>
        </div>
    </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)
    
    # Geri butonu (native Streamlit)
    if st.button("← Geri", key="back_btn"):
        st.session_state['page'] = 'landing'
        st.rerun()
    
    # Quiz form - collect answers
    user_answers = {}
    question_num = 0
    
    for q in questions:
        question_num += 1
        
        # Section headers
        if 'section' in q:
            section_parts = q['section'].split(':')
            section_num = section_parts[0].strip() if len(section_parts) > 1 else 'Section'
            section_name = section_parts[1].strip() if len(section_parts) > 1 else q['section']
            
            section_html = f'''
            <div style="margin: 40px 0 24px 0; position: relative;">
                <div style="position: absolute; left: -8px; top: 0; bottom: 0; width: 3px; background: linear-gradient(180deg, transparent, #00E5FF, transparent); opacity: 0.5;"></div>
                <div style="padding-left: 16px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        <span style="font-size: 10px; font-family: 'JetBrains Mono', monospace; color: rgba(0, 229, 255, 0.6); letter-spacing: 0.2em; text-transform: uppercase; border: 1px solid rgba(0, 229, 255, 0.3); padding: 2px 4px; border-radius: 2px;">Confidential</span>
                        <span style="height: 1px; width: 32px; background: rgba(0, 229, 255, 0.2);"></span>
                    </div>
                    <h2 style="font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; letter-spacing: 0.2em; color: #00E5FF; text-transform: uppercase; margin: 0 0 4px 0;">{section_num}</h2>
                    <h3 style="font-family: 'Epilogue', sans-serif; font-size: 20px; font-weight: 700; color: white; text-transform: uppercase; letter-spacing: 0.05em; margin: 0;">{section_name}</h3>
                </div>
            </div>
            '''
            st.markdown(section_html, unsafe_allow_html=True)
        
        # Parse question text
        q_text = q['text']
        clean_text = q_text.split(']')[-1].strip() if ']' in q_text else q_text
        q_id_display = f"Q-{question_num:03d}"
        
        if 'opts' in q:
            # Terminal Card header + question
            card_header_html = f'''
            <div style="background: #161b22; border: 1px solid rgba(255,255,255,0.05); border-radius: 6px; overflow: hidden; margin: 20px 0 0 0;">
                <div style="background: rgba(0,0,0,0.4); border-bottom: 1px solid rgba(255,255,255,0.05); padding: 8px 16px; display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #6b7280; text-transform: uppercase;">Input_Stream: {q_id_display}</span>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 6px; height: 6px; border-radius: 50%; background: #00E5FF; box-shadow: 0 0 6px #00E5FF;"></div>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 9px; color: rgba(0, 229, 255, 0.6); letter-spacing: 0.1em;">ACTIVE</span>
                    </div>
                </div>
                <div style="padding: 24px;">
                    <p style="font-family: 'JetBrains Mono', monospace; font-weight: 500; font-size: 14px; color: rgba(0, 229, 255, 0.9); margin: 0 0 20px 0; line-height: 1.6;">
                        <span style="color: #00E5FF; margin-right: 8px;">&gt;</span>{clean_text}
                    </p>
                </div>
            </div>
            '''
            st.markdown(card_header_html, unsafe_allow_html=True)
            
            # Native Streamlit radio with CSS styling
            user_answers[q['id']] = st.radio(
                label=q['text'],
                options=q['opts'],
                key=q['id'],
                label_visibility="collapsed"
            )
            
        elif q.get('type') in ['text', 'textarea']:
            # Text input with corner brackets
            is_textarea = q.get('type') == 'textarea'
            
            bracket_html = f'''
            <div style="margin: 24px 0;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding: 0 4px;">
                    <label style="font-family: 'Epilogue', sans-serif; font-weight: 700; font-size: 14px; color: white; letter-spacing: 0.03em;">
                        <span style="color: #00E5FF; margin-right: 8px;">&gt;</span>{clean_text}
                    </label>
                    <span style="font-size: 10px; font-family: 'JetBrains Mono', monospace; color: #6b7280; text-transform: uppercase;">Max Char: 500</span>
                </div>
                <div style="position: relative;">
                    <div style="position: absolute; top: -4px; left: -4px; width: 16px; height: 16px; border-top: 2px solid #4b5563; border-left: 2px solid #4b5563;"></div>
                    <div style="position: absolute; top: -4px; right: -4px; width: 16px; height: 16px; border-top: 2px solid #4b5563; border-right: 2px solid #4b5563;"></div>
                    <div style="position: absolute; bottom: -4px; left: -4px; width: 16px; height: 16px; border-bottom: 2px solid #4b5563; border-left: 2px solid #4b5563;"></div>
                    <div style="position: absolute; bottom: -4px; right: -4px; width: 16px; height: 16px; border-bottom: 2px solid #4b5563; border-right: 2px solid #4b5563;"></div>
                    <div style="background: rgba(13, 17, 23, 0.8); backdrop-filter: blur(4px); padding: 4px;">
            '''
            st.markdown(bracket_html, unsafe_allow_html=True)
            
            if is_textarea:
                user_answers[q['id']] = st.text_area("", key=q['id'], label_visibility="collapsed", height=128, placeholder="INITIATING INPUT STREAM...")
            else:
                user_answers[q['id']] = st.text_input("", key=q['id'], label_visibility="collapsed", placeholder="INITIATING INPUT STREAM...")
            
            bracket_close_html = f'''
                    </div>
                    <div style="position: absolute; bottom: 8px; right: 16px; display: flex; align-items: center; gap: 8px; pointer-events: none;">
                        <div style="height: 6px; width: 6px; background: rgba(0, 229, 255, 0.5); border-radius: 50%;"></div>
                        <span style="font-size: 10px; font-family: 'JetBrains Mono', monospace; color: rgba(0, 229, 255, 0.5);">AWAITING_DATA</span>
                    </div>
                </div>
            </div>
            '''
            st.markdown(bracket_close_html, unsafe_allow_html=True)
    
    # Fixed Bottom Submit Bar
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("İptal Et", key="terminate_btn"):
            st.session_state['page'] = 'landing'
            st.rerun()
    with col2:
        if st.button("🔏 MÜHÜRLE VE GÖNDER", use_container_width=True, type="primary"):
            st.session_state['user_data'] = user_answers
            st.session_state['page'] = 'paywall'
            st.rerun()


def show_paywall():
    """Paywall ekranı"""
    t = CONTENT[st.session_state['language']]['PAYWALL']
    
    paywall_html = f"""
    <div style="background: #0b0e19; min-height: 80vh; display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: 'Manrope', sans-serif; padding: 40px 20px;">
        <!-- Lock icon -->
        <div style="position: relative; margin-bottom: 32px;">
            <div style="position: absolute; inset: -30px; background: #ef4444; border-radius: 50%; filter: blur(40px); opacity: 0.2;"></div>
            <span class="material-symbols-outlined" style="font-size: 80px; color: #ef4444; filter: drop-shadow(0 0 15px rgba(239, 68, 68, 0.4)); font-variation-settings: 'FILL' 1;">lock</span>
        </div>
        
        <!-- Alert badge -->
        <div style="display: flex; align-items: center; gap: 8px; padding: 6px 16px; border-radius: 20px; background: rgba(127, 29, 29, 0.2); border: 1px solid rgba(239, 68, 68, 0.2); margin-bottom: 24px;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: #ef4444; animation: pulse 2s infinite;"></span>
            <span style="color: #f87171; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;">{t['ALERT']}</span>
        </div>
        
        <!-- Title -->
        <h1 style="color: white; font-family: 'Epilogue', sans-serif; font-size: 32px; letter-spacing: 0.2em; text-transform: uppercase; margin: 0 0 16px 0; text-align: center;">{t['TITLE']}</h1>
        <p style="color: #9ca3af; font-size: 14px; text-align: center; max-width: 280px;">{t['DESC']}</p>
        
        <style>
            @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
        </style>
    </div>
    """
    
    components.html(paywall_html, height=500, scrolling=False)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(f"🔓 {t['BTN_AD']}", use_container_width=True, type="primary"):
            st.session_state['page'] = 'result'
            st.rerun()
        
        if st.button("← Geri", use_container_width=True):
            st.session_state['page'] = 'quiz'
            st.rerun()


# Gemini 2.5 Flash Fiyatlandırması (Ocak 2026)
GEMINI_PRICING = {
    'input_per_million': 0.15,   # $0.15 per 1M input tokens
    'output_per_million': 0.60,  # $0.60 per 1M output tokens
}
USD_TO_TRY = 35.0  # Yaklaşık döviz kuru

def calculate_api_cost(input_tokens, output_tokens):
    """API maliyetini hesapla"""
    input_cost = (input_tokens / 1_000_000) * GEMINI_PRICING['input_per_million']
    output_cost = (output_tokens / 1_000_000) * GEMINI_PRICING['output_per_million']
    total_usd = input_cost + output_cost
    total_try = total_usd * USD_TO_TRY
    return {
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'input_cost_usd': input_cost,
        'output_cost_usd': output_cost,
        'total_usd': total_usd,
        'total_try': total_try
    }

def run_fbi_analysis(user_data, lang):
    """AI analiz motoru - FBI Davranış Bilimcisi (Maliyet Takipli)"""
    prompt = f"""
    Sen, FBI Davranış Analizi Birimi'nde görevli üst düzey bir profil uzmanı ve davranış bilimcisisin.
    20 yıllık tecrübenle binlerce suçlu ve lider profilini analiz ettin.
    
    Görevin: Aşağıdaki kullanıcı verilerini derinlemesine analiz ederek kapsamlı bir psikolojik profil oluşturmak.
    
    DİL: {lang}. (Tüm yanıtları bu dilde ver).

    ÇIKTI FORMATI (Sadece JSON, tüm alanları eksiksiz doldur):
    {{
        "iq": "Sayı (95-145 arası)",
        "archetype": "İngilizce kod adı (örn: The Architect, The Shadow Walker, The Void Strategist, The Silent Predator, The Chaos Theorist)",
        "logic_score": 0-100 arası sayı,
        "empathy_score": 0-100 arası sayı,
        "risk_level": "LOW / MEDIUM / HIGH",
        "neuroticism": "Low / Medium / High",
        "stability": "Low / Medium / High",
        "pattern": "Stable / Normal / Erratic / Volatile",
        
        "character_match": "Kullanıcının psikolojik profiliyle eşleşen ünlü bir kurgusal karakter, tarihi figür veya komutan. Örnek: Hannibal Lecter, Sherlock Holmes, Sun Tzu, Machiavelli, Walter White, Loki, Light Yagami, Erwin Smith, Thomas Shelby, Tyrion Lannister, Napoleon Bonaparte, Julius Caesar, Joker, V (V for Vendetta), Professor (Money Heist)",
        
        "character_match_reason": "Bu karakterle neden eşleştiğinin 2-3 cümlelik açıklaması. Ortak özellikleri, düşünce yapısını ve davranış kalıplarını belirt.",
        
        "detailed_analysis": "5-6 cümlelik kapsamlı psikolojik analiz. Kullanıcının stratejik düşünce yapısını, karar alma mekanizmalarını, duygusal kalıplarını, liderlik potansiyelini, zayıf noktalarını ve benzersiz yeteneklerini detaylı açıkla. Profesyonel ve etkileyici bir dille yaz.",
        
        "shadow_trait": "Bastırılmış karanlık yön ve stres altındaki tehlikeli eğilimlerin detaylı açıklaması (3-4 cümle). Bu kişinin çöküş senaryosu ne olabilir? Hangi tetikleyiciler onu dengesizleştirebilir?"
    }}
    
    ÖNEMLİ: Analiz çok detaylı ve etkileyici olmalı. Kullanıcı kendini özel hissetmeli.
    
    VERİLER: {user_data}
    """
    
    try:
        if "gemini_api_key" in st.secrets:
            genai.configure(api_key=st.secrets["gemini_api_key"])
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            # Token kullanımını al
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            
            # Maliyeti hesapla
            cost_info = calculate_api_cost(input_tokens, output_tokens)
            
            # Session state'i güncelle
            st.session_state['api_costs']['total_input_tokens'] += input_tokens
            st.session_state['api_costs']['total_output_tokens'] += output_tokens
            st.session_state['api_costs']['total_cost_usd'] += cost_info['total_usd']
            st.session_state['api_costs']['total_analyses'] += 1
            st.session_state['api_costs']['last_analysis_cost'] = cost_info
            
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_json)
            result['_cost_info'] = cost_info  # Maliyet bilgisini sonuca ekle
            return result
        else:
            # Demo mod - tahmini token değerleri
            demo_cost = calculate_api_cost(2000, 500)
            st.session_state['api_costs']['total_input_tokens'] += 2000
            st.session_state['api_costs']['total_output_tokens'] += 500
            st.session_state['api_costs']['total_cost_usd'] += demo_cost['total_usd']
            st.session_state['api_costs']['total_analyses'] += 1
            st.session_state['api_costs']['last_analysis_cost'] = demo_cost
            
            time.sleep(2)
            result = {
                "iq": "128", 
                "archetype": "The Silent Architect", 
                "logic_score": 94, 
                "empathy_score": 38,
                "risk_level": "HIGH", 
                "neuroticism": "High",
                "stability": "Low",
                "pattern": "Erratic",
                "character_match": "Professor (Money Heist)",
                "character_match_reason": "Tıpkı Profesör gibi, olağanüstü planlama yetenekleri ve detaylara takıntılı bir yaklaşım sergiliyor. Her hamleyi önceden hesaplayan, duygularını mantığın gerisinde tutan bir stratejist.",
                "detailed_analysis": "Özne, olağanüstü analitik beceriler ve stratejik planlama kapasitesi sergiliyor. Karar alma süreçlerinde duygusal faktörleri minimize ederek salt mantık odaklı bir yaklaşım benimsiyor. Sosyal dinamikleri bir satranç tahtası gibi analiz etme eğiliminde ve birkaç hamle ilerisini görebilme yeteneğine sahip. Liderlik potansiyeli yüksek ancak empati eksikliği takım dinamiklerinde sorunlara yol açabilir. En büyük gücü aynı zamanda en büyük zayıflığı: aşırı kontrol ihtiyacı.",
                "shadow_trait": "Kontrol kaybı senaryolarında şiddetli anksiyete ve panik tepkileri gözlemlenebilir. Stres altında manipülatif davranışlara başvurma eğilimi yüksek. Başarısızlık durumunda kendini ve çevresini yıkıcı şekilde suçlama potansiyeli mevcut. Tetikleyiciler: beklenmedik değişkenler, sadakatsizlik algısı ve planların bozulması.",
                "_cost_info": demo_cost
            }
            return result
    except Exception as e:
        return {"iq": "100", "archetype": "ERROR", "logic_score": 50, "empathy_score": 50, "risk_level": "MEDIUM", "detailed_analysis": f"Hata: {str(e)}", "shadow_trait": "Bilinmiyor.", "character_match": "Unknown", "character_match_reason": "Analiz tamamlanamadı.", "_cost_info": None}


def show_result():
    """Sonuç ekranı - Detaylı FBI Raporu"""
    t = CONTENT[st.session_state['language']]['RESULT']
    
    # Analiz yap
    if st.session_state['analysis_result'] is None:
        with st.spinner("🧠 NÖRAL DESENLER ÇÖZÜMLENİYOR..."):
            st.session_state['analysis_result'] = run_fbi_analysis(st.session_state['user_data'], st.session_state['language'])
    
    res = st.session_state['analysis_result']
    
    # Değerleri al
    iq = res.get('iq', '100')
    archetype = res.get('archetype', 'THE UNKNOWN')
    detailed_analysis = res.get('detailed_analysis', res.get('analysis', 'Analiz işleniyor...'))
    logic_score = res.get('logic_score', 50)
    empathy_score = res.get('empathy_score', 50)
    risk_level = res.get('risk_level', 'MEDIUM')
    shadow_trait = res.get('shadow_trait', 'Bilinmiyor')
    neuroticism = res.get('neuroticism', 'Medium')
    stability = res.get('stability', 'Medium')
    pattern = res.get('pattern', 'Normal')
    character_match = res.get('character_match', 'Unknown')
    character_match_reason = res.get('character_match_reason', '')
    
    # IQ için SVG offset hesapla
    try:
        iq_val = int(iq)
        normalized = min(max((iq_val - 70) / 80 * 100, 0), 100)
        iq_offset = 251.2 - (251.2 * normalized / 100)
    except:
        iq_offset = 125
    
    # Risk level renk ve Türkçe çevirisi
    risk_color = "#ef4444" if risk_level == "HIGH" else ("#f59e0b" if risk_level == "MEDIUM" else "#22c55e")
    risk_level_tr = "YÜKSEK" if risk_level == "HIGH" else ("ORTA" if risk_level == "MEDIUM" else "DÜŞÜK")
    
    result_html = f'''
    <style>
        @keyframes scanline {{ 0% {{ transform: translateY(-100%); }} 100% {{ transform: translateY(100%); }} }}
        .scan-overlay {{ background: linear-gradient(to bottom, transparent 50%, rgba(0, 229, 255, 0.02) 51%, transparent 51%); background-size: 100% 4px; animation: scanline 10s linear infinite; }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
        .animate-pulse {{ animation: pulse 2s infinite; }}
    </style>
    
    <div style="background: #111e21; min-height: 100vh; font-family: 'Epilogue', sans-serif; color: white; padding-bottom: 20px;">
        <div style="position: fixed; inset: 0; pointer-events: none; z-index: 0; opacity: 0.2;" class="scan-overlay"></div>
        
        <header style="position: sticky; top: 0; z-index: 50; background: rgba(17, 30, 33, 0.95); backdrop-filter: blur(8px); border-bottom: 1px solid #3d4d52;">
            <div style="display: flex; align-items: center; padding: 16px; justify-content: space-between; max-width: 500px; margin: 0 auto;">
                <span class="material-symbols-outlined" style="color: rgba(255,255,255,0.7);">lock_open</span>
                <div style="text-align: center;">
                    <h2 style="color: white; font-size: 10px; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.2em; opacity: 0.7; margin: 0;">PROJECT ZERO</h2>
                    <h1 style="color: white; font-size: 14px; font-weight: 700; margin: 4px 0 0 0;">DOSYA #8392-A</h1>
                </div>
                <span class="material-symbols-outlined" style="color: rgba(255,255,255,0.7);">share</span>
            </div>
        </header>
        
        <main style="max-width: 500px; margin: 0 auto; padding: 0 16px; position: relative; z-index: 10;">
            <!-- Confidential Stamp -->
            <div style="padding: 32px 0 24px; display: flex; justify-content: center;">
                <div style="border: 4px solid rgba(239, 68, 68, 0.8); padding: 8px; transform: rotate(-6deg); border-radius: 4px; opacity: 0.9;">
                    <h2 style="color: #ef4444; font-size: 28px; font-weight: 900; letter-spacing: 0.2em; text-transform: uppercase; text-align: center; border: 2px solid rgba(239, 68, 68, 0.8); padding: 4px 16px; margin: 0;">GİZLİ</h2>
                </div>
            </div>
            
            <div style="display: flex; flex-direction: column; gap: 16px;">
                <!-- Archetype Card -->
                <div style="background: #1c2426; border: 1px solid #3d4d52; border-radius: 12px; overflow: hidden; box-shadow: 0 0 15px rgba(0,0,0,0.3);">
                    <div style="height: 180px; background: linear-gradient(135deg, #0a3f4d 0%, #063640 100%); position: relative; display: flex; align-items: flex-end; padding: 16px;">
                        <div style="position: absolute; inset: 0; background: linear-gradient(to top, #1c2426, rgba(28, 36, 38, 0.5), transparent);"></div>
                        <div style="position: relative; z-index: 10;">
                            <span style="background: rgba(10, 63, 77, 0.9); color: #00E5FF; font-size: 10px; font-family: 'JetBrains Mono', monospace; font-weight: 700; padding: 4px 8px; border-radius: 4px; border: 1px solid rgba(0, 229, 255, 0.3); display: inline-block; margin-bottom: 8px;">MATCH 98.2%</span>
                            <h3 style="color: white; font-size: 24px; font-weight: 700; margin: 0; letter-spacing: -0.02em;">{archetype}</h3>
                        </div>
                    </div>
                    <div style="padding: 16px;">
                        <div style="display: flex; align-items: flex-start; gap: 12px;">
                            <span class="material-symbols-outlined" style="color: #9eb2b7; font-size: 20px; margin-top: 2px;">psychology</span>
                            <p style="color: #9eb2b7; font-size: 13px; font-family: 'JetBrains Mono', monospace; line-height: 1.7; margin: 0;">{detailed_analysis}</p>
                        </div>
                        <div style="height: 1px; background: rgba(61, 77, 82, 0.5); margin: 16px 0;"></div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 10px; color: #9eb2b7; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; letter-spacing: 0.1em;">NADİRLİK</span>
                            <div style="display: flex; gap: 4px;">
                                <div style="width: 32px; height: 4px; background: #00E5FF; border-radius: 2px;"></div>
                                <div style="width: 32px; height: 4px; background: #00E5FF; border-radius: 2px;"></div>
                                <div style="width: 32px; height: 4px; background: #00E5FF; border-radius: 2px;"></div>
                                <div style="width: 8px; height: 4px; background: #3d4d52; border-radius: 2px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Character Match Card -->
                <div style="background: linear-gradient(135deg, #2d2215 0%, #1c2426 100%); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; padding: 16px; position: relative; overflow: hidden;">
                    <div style="position: absolute; right: -20px; top: -20px; width: 100px; height: 100px; background: rgba(245, 158, 11, 0.08); border-radius: 50%; filter: blur(30px);"></div>
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <span class="material-symbols-outlined" style="color: #f59e0b; font-size: 24px;">theater_comedy</span>
                        <div>
                            <span style="font-size: 10px; color: #9eb2b7; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; letter-spacing: 0.1em;">KARAKTER EŞLEŞMESİ</span>
                            <h3 style="color: #f59e0b; font-size: 18px; font-weight: 700; margin: 4px 0 0 0; letter-spacing: 0.02em;">{character_match}</h3>
                        </div>
                    </div>
                    <p style="color: #9eb2b7; font-size: 12px; font-family: 'JetBrains Mono', monospace; line-height: 1.6; margin: 0; padding-left: 36px;">
                        <span style="color: #f59e0b;">&gt;&gt;</span> {character_match_reason}
                    </p>
                </div>
                
                <!-- IQ & Metrics Grid -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                    <!-- IQ Gauge -->
                    <div style="background: #1c2426; border: 1px solid #3d4d52; border-radius: 12px; padding: 16px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative;">
                        <div style="position: absolute; top: 12px; left: 12px; display: flex; align-items: center; gap: 4px;">
                            <span style="width: 6px; height: 6px; border-radius: 50%; background: #00E5FF;" class="animate-pulse"></span>
                            <span style="font-size: 10px; color: #00E5FF; font-family: 'JetBrains Mono', monospace; text-transform: uppercase;">CANLI</span>
                        </div>
                        <div style="width: 110px; height: 110px; position: relative; margin-top: 8px;">
                            <svg style="width: 100%; height: 100%; transform: rotate(-90deg);" viewBox="0 0 100 100">
                                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#111617" stroke-width="8"></circle>
                                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#0a3f4d" stroke-width="8" stroke-dasharray="251.2" stroke-dashoffset="40" stroke-linecap="round"></circle>
                                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#00E5FF" stroke-width="8" stroke-dasharray="251.2" stroke-dashoffset="{iq_offset}" stroke-linecap="round" style="opacity: 0.8;"></circle>
                            </svg>
                            <div style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                                <span style="font-size: 28px; font-weight: 700; color: white; letter-spacing: -0.05em;">{iq}</span>
                                <span style="font-size: 9px; color: #9eb2b7; font-family: 'JetBrains Mono', monospace; text-transform: uppercase;">IQ SKORU</span>
                            </div>
                        </div>
                        <p style="font-size: 11px; color: #9eb2b7; font-family: 'JetBrains Mono', monospace; margin-top: 8px;">Üstün Zeka</p>
                    </div>
                    
                    <!-- Metrics -->
                    <div style="display: flex; flex-direction: column; gap: 12px;">
                        <div style="flex: 1; background: #1c2426; border: 1px solid #3d4d52; border-radius: 12px; padding: 12px; display: flex; flex-direction: column; justify-content: center;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                <span style="font-size: 10px; color: #9eb2b7; font-family: 'JetBrains Mono', monospace; text-transform: uppercase;">MANTIK</span>
                                <span style="font-size: 12px; color: white; font-weight: 700; font-family: 'JetBrains Mono', monospace;">{logic_score}%</span>
                            </div>
                            <div style="width: 100%; height: 6px; background: #111617; border-radius: 3px; overflow: hidden;">
                                <div style="height: 100%; width: {logic_score}%; background: #0a3f4d; border-radius: 3px;"></div>
                            </div>
                        </div>
                        <div style="flex: 1; background: #1c2426; border: 1px solid #3d4d52; border-radius: 12px; padding: 12px; display: flex; flex-direction: column; justify-content: center;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                <span style="font-size: 10px; color: #9eb2b7; font-family: 'JetBrains Mono', monospace; text-transform: uppercase;">EMPATİ</span>
                                <span style="font-size: 12px; color: white; font-weight: 700; font-family: 'JetBrains Mono', monospace;">{empathy_score}%</span>
                            </div>
                            <div style="width: 100%; height: 6px; background: #111617; border-radius: 3px; overflow: hidden;">
                                <div style="height: 100%; width: {empathy_score}%; background: #9eb2b7; border-radius: 3px;"></div>
                            </div>
                        </div>
                        <div style="flex: 1; background: #1c2426; border: 1px solid #3d4d52; border-radius: 12px; padding: 12px; display: flex; align-items: center; justify-content: space-between; position: relative; overflow: hidden;">
                            <div style="position: absolute; right: 0; top: 0; bottom: 0; width: 4px; background: {risk_color};"></div>
                            <span style="font-size: 10px; color: #9eb2b7; font-family: 'JetBrains Mono', monospace; text-transform: uppercase;">RİSK SEVİYESİ</span>
                            <span style="font-size: 13px; color: {risk_color}; font-weight: 700; font-family: 'JetBrains Mono', monospace; text-transform: uppercase;">{risk_level_tr}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Shadow Self Warning -->
                <div style="background: linear-gradient(135deg, #1c2426 0%, #0f0a0a 100%); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 16px; position: relative; overflow: hidden;">
                    <div style="position: absolute; right: -40px; top: -40px; width: 120px; height: 120px; background: rgba(239, 68, 68, 0.05); border-radius: 50%; filter: blur(40px);"></div>
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <span class="material-symbols-outlined" style="color: #ef4444;" class="animate-pulse">warning</span>
                        <h3 style="color: white; font-weight: 700; letter-spacing: 0.02em; text-transform: uppercase; margin: 0; font-size: 14px;">GÖLGE KİŞİLİK TESPİT EDİLDİ</h3>
                    </div>
                    <p style="color: #9eb2b7; font-size: 13px; font-family: 'JetBrains Mono', monospace; line-height: 1.6; margin: 0 0 16px 0;">
                        <span style="color: #ef4444;">&gt;&gt; UYARI:</span> {shadow_trait}
                    </p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px;">
                        <div style="background: rgba(0,0,0,0.4); padding: 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); text-align: center;">
                            <span style="display: block; font-size: 9px; color: #9eb2b7; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; margin-bottom: 4px;">NEVROTİZM</span>
                            <span style="display: block; color: white; font-weight: 700; font-size: 13px;">{neuroticism}</span>
                        </div>
                        <div style="background: rgba(0,0,0,0.4); padding: 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); text-align: center;">
                            <span style="display: block; font-size: 9px; color: #9eb2b7; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; margin-bottom: 4px;">STABİLİTE</span>
                            <span style="display: block; color: white; font-weight: 700; font-size: 13px;">{stability}</span>
                        </div>
                        <div style="background: rgba(0,0,0,0.4); padding: 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); text-align: center;">
                            <span style="display: block; font-size: 9px; color: #9eb2b7; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; margin-bottom: 4px;">DESEN</span>
                            <span style="display: block; color: #00E5FF; font-weight: 700; font-size: 13px;">{pattern}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Volatility Graph -->
                <div style="background: #1c2426; border: 1px solid #3d4d52; border-radius: 12px; padding: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <h3 style="color: white; font-size: 14px; font-weight: 500; margin: 0;">Psikolojik Değişkenlik</h3>
                        <span style="background: #111617; color: #9eb2b7; font-size: 10px; font-family: 'JetBrains Mono', monospace; padding: 4px 8px; border-radius: 4px; border: 1px solid #3d4d52;">SON 24 SAAT</span>
                    </div>
                    <div style="height: 100px; width: 100%;">
                        <svg style="width: 100%; height: 100%; overflow: visible;" viewBox="0 0 300 100" preserveAspectRatio="none">
                            <defs>
                                <linearGradient id="grid-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                    <stop offset="0%" style="stop-color:#0a3f4d;stop-opacity:0.2"></stop>
                                    <stop offset="100%" style="stop-color:#0a3f4d;stop-opacity:0"></stop>
                                </linearGradient>
                            </defs>
                            <line x1="0" y1="25" x2="300" y2="25" stroke="#3d4d52" stroke-width="0.5" stroke-dasharray="4 4" opacity="0.5"></line>
                            <line x1="0" y1="50" x2="300" y2="50" stroke="#3d4d52" stroke-width="0.5" stroke-dasharray="4 4" opacity="0.5"></line>
                            <line x1="0" y1="75" x2="300" y2="75" stroke="#3d4d52" stroke-width="0.5" stroke-dasharray="4 4" opacity="0.5"></line>
                            <path d="M0 80 C 40 80, 50 30, 80 40 C 110 50, 130 90, 160 60 C 190 30, 210 20, 240 40 C 270 60, 280 50, 300 30" fill="url(#grid-gradient)" stroke="#0a3f4d" stroke-width="2"></path>
                            <circle cx="300" cy="30" r="4" fill="#00E5FF" class="animate-pulse"></circle>
                        </svg>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 8px; font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #9eb2b7;">
                        <span>00:00</span>
                        <span>12:00</span>
                        <span>NOW</span>
                    </div>
                </div>
                
                <!-- Footer Meta -->
                <div style="text-align: center; padding: 16px 0; opacity: 0.5;">
                    <p style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #9eb2b7; letter-spacing: 0.2em; margin: 0;">SYSTEM ACCESS LEVEL: 5 // ENCRYPTION ACTIVE</p>
                </div>
            </div>
        </main>
    </div>
    '''
    
    components.html(result_html, height=1300, scrolling=True)
    
    # Maliyet Bilgisi Paneli (Sadece Admin için)
    cost_info = res.get('_cost_info')
    costs = st.session_state['api_costs']
    
    # Admin modu kontrolü - secrets dosyasında admin_mode: true olmalı
    is_admin = st.secrets.get("admin_mode", False) if hasattr(st, 'secrets') and st.secrets else False
    
    if is_admin:
        with st.expander("📊 API Maliyet Raporu (Admin)", expanded=False):
            st.markdown("""
            <style>
                .cost-card {
                    background: linear-gradient(135deg, #1a2332 0%, #0d1117 100%);
                    border: 1px solid rgba(0, 229, 255, 0.2);
                    border-radius: 12px;
                    padding: 16px;
                    margin: 8px 0;
                }
                .cost-title {
                    color: #00E5FF;
                    font-size: 12px;
                    font-family: 'JetBrains Mono', monospace;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    margin-bottom: 8px;
                }
                .cost-value {
                    color: white;
                    font-size: 24px;
                    font-weight: 700;
                }
                .cost-sub {
                    color: #9ca3af;
                    font-size: 11px;
                    font-family: 'JetBrains Mono', monospace;
                }
            </style>
            """, unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if cost_info:
                    st.markdown(f"""
                    <div class="cost-card">
                        <div class="cost-title">📍 Bu Analiz</div>
                        <div class="cost-value">${cost_info['total_usd']:.6f}</div>
                        <div class="cost-sub">≈ ₺{cost_info['total_try']:.4f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="cost-card">
                        <div class="cost-title">📥 Input Tokens</div>
                        <div class="cost-value">{cost_info['input_tokens']:,}</div>
                        <div class="cost-sub">${cost_info['input_cost_usd']:.6f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="cost-card">
                        <div class="cost-title">📍 Bu Analiz</div>
                        <div class="cost-value">N/A</div>
                        <div class="cost-sub">Token bilgisi alınamadı</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col_b:
                st.markdown(f"""
                <div class="cost-card">
                    <div class="cost-title">📊 Toplam Harcama</div>
                    <div class="cost-value">${costs['total_cost_usd']:.6f}</div>
                    <div class="cost-sub">≈ ₺{costs['total_cost_usd'] * USD_TO_TRY:.4f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if cost_info:
                    st.markdown(f"""
                    <div class="cost-card">
                        <div class="cost-title">📤 Output Tokens</div>
                        <div class="cost-value">{cost_info['output_tokens']:,}</div>
                        <div class="cost-sub">${cost_info['output_cost_usd']:.6f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Özet İstatistikler
            st.markdown("---")
            st.markdown(f"""
            | Metrik | Değer |
            |--------|-------|
            | **Toplam Analiz Sayısı** | {costs['total_analyses']} |
            | **Toplam Input Token** | {costs['total_input_tokens']:,} |
            | **Toplam Output Token** | {costs['total_output_tokens']:,} |
            | **Ortalama Analiz Maliyeti** | ${(costs['total_cost_usd'] / max(costs['total_analyses'], 1)):.6f} |
            """)
            
            # Maliyet Projeksiyonu
            avg_cost = costs['total_cost_usd'] / max(costs['total_analyses'], 1)
            st.markdown(f"""
            ### 💰 Maliyet Projeksiyonu
            | Analiz Sayısı | Tahmini Maliyet (USD) | Tahmini Maliyet (TRY) |
            |---------------|----------------------|----------------------|
            | 100 | ${avg_cost * 100:.2f} | ₺{avg_cost * 100 * USD_TO_TRY:.2f} |
            | 1,000 | ${avg_cost * 1000:.2f} | ₺{avg_cost * 1000 * USD_TO_TRY:.2f} |
            | 10,000 | ${avg_cost * 10000:.2f} | ₺{avg_cost * 10000 * USD_TO_TRY:.2f} |
            | 100,000 | ${avg_cost * 100000:.2f} | ₺{avg_cost * 100000 * USD_TO_TRY:.2f} |
            """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(f"🗑️ {t['BTN_PURGE']}", use_container_width=True):
            st.session_state['page'] = 'landing'
            st.session_state['user_data'] = {}
            st.session_state['analysis_result'] = None
            st.rerun()


# ==========================================
# 6. ROUTER
# ==========================================
PG = st.session_state['page']

if PG == 'landing':
    show_landing()
elif PG == 'quiz':
    show_quiz()
elif PG == 'paywall':
    show_paywall()
elif PG == 'result':
    show_result()