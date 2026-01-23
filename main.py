import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import json
import time
import httpx
from datetime import datetime
import base64

# ==========================================
# SUPABASE REST API FONKSİYONLARI
# ==========================================
def get_supabase_client():
    """Supabase bağlantı bilgilerini döner"""
    import os
    
    # 1. Streamlit Secrets dene
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["anon_key"]
        return url, key
    except Exception:
        pass
        
    # 2. Environment Variables dene (Render.com vb. için)
    url = os.getenv("SUPABASE_URL") or os.getenv("url")
    key = os.getenv("SUPABASE_KEY") or os.getenv("anon_key")
    
    if url and key:
        return url, key
        
    # 3. Fallback (Kesin Çözüm)
    # Render env variable okuyamazsa burası devreye girer
    url = "https://yrbahkcjifokglctohjz.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlyYmFoa2NqaWZva2dsY3RvaGp6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkxMzQzNjMsImV4cCI6MjA4NDcxMDM2M30.DkGYSaF9aHk1z4h6iXj8t0TH3SWk5S0ryy7psHW6JCo"
    
    return url, key

def save_score_to_leaderboard(username: str, iq_score: int, character_name: str = "", country: str = "", city: str = ""):
    """Kullanıcı skorunu Supabase'e kaydeder"""
    try:
        url, key = get_supabase_client()
        if not url or not key:
            return False, "Supabase bağlantısı yapılandırılmamış"
        
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        data = {
            "username": username,
            "iq_score": iq_score,
            "character_name": character_name,
            "country": country,
            "city": city,
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = httpx.post(
            f"{url}/rest/v1/leaderboard",
            headers=headers,
            json=data,
            timeout=10.0
        )
        
        if response.status_code in [200, 201, 204]:
            return True, "Skor kaydedildi"
        else:
            return False, f"Hata: {response.status_code}"
    except Exception as e:
        return False, str(e)

# ==========================================
# AUDIO PLAYER
# ==========================================
def init_audio():
    """Arka plan müziğini başlatır"""
    audio_file = "abstract-dramatic-atmosphere-145470.mp3"
    try:
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()
            
        audio_html = f"""
            <audio id="bg-audio" autoplay loop>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            <script>
                var audio = document.getElementById("bg-audio");
                audio.volume = 0.05;  // 5% Volume
                
                // Sayfa yenilendiğinde çalmaya devam etmesi için
                var playPromise = audio.play();
                if (playPromise !== undefined) {{
                    playPromise.then(_ => {{
                        // Autoplay başladı
                    }}).catch(error => {{
                        // Autoplay engellendi (kullanıcı etkileşimi lazım)
                    }});
                }}
            </script>
        """
        # Sadece bir kere ekle
        if 'audio_initialized' not in st.session_state:
            components.html(audio_html, height=0, width=0)
            st.session_state['audio_initialized'] = True
    except Exception as e:
        pass # Dosya yoksa sessizce geç

# ==========================================
# AUDIO PLAYER
# ==========================================
def init_audio():
    """Arka plan müziğini başlatır"""
    audio_file = "abstract-dramatic-atmosphere.mp3"
    try:
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()
            
        audio_html = f"""
            <audio id="bg-audio" autoplay loop>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            <script>
                var audio = document.getElementById("bg-audio");
                audio.volume = 0.05;  // 5% Volume
                
                // Sayfa yenilendiğinde çalmaya devam etmesi için
                var playPromise = audio.play();
                if (playPromise !== undefined) {{
                    playPromise.then(_ => {{
                        // Autoplay başladı
                    }}).catch(error => {{
                        // Autoplay engellendi (kullanıcı etkileşimi lazım)
                    }});
                }}
            </script>
        """
        # Sadece bir kere ekle
        if 'audio_initialized' not in st.session_state:
            components.html(audio_html, height=0, width=0)
            st.session_state['audio_initialized'] = True
    except Exception as e:
        pass # Dosya yoksa sessizce geç

# Müzik çaları başlat
init_audio()


def get_leaderboard(limit: int = 100):
    """Leaderboard'u getirir (en yüksek IQ skoruna göre sıralı)"""
    try:
        url, key = get_supabase_client()
        if not url or not key:
            return []
        
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        response = httpx.get(
            f"{url}/rest/v1/leaderboard?select=username,iq_score,character_name,created_at&order=iq_score.desc&limit={limit}",
            headers=headers,
            timeout=10.0
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception:
        return []

def save_user_analysis(username: str, analysis_data: dict):
    """Kullanıcının analiz sonuçlarını Supabase'e kaydeder (uyumluluk için)"""
    try:
        url, key = get_supabase_client()
        if not url or not key:
            return False, "Supabase bağlantısı yapılandırılmamış"
        
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal,resolution=merge-duplicates"
        }
        
        data = {
            "username": username.lower(),
            "iq_score": int(analysis_data.get('iq', 100)),
            "archetype": analysis_data.get('archetype', ''),
            "logic_score": int(analysis_data.get('logic_score', 50)),
            "empathy_score": int(analysis_data.get('empathy_score', 50)),
            "risk_level": analysis_data.get('risk_level', 'MEDIUM'),
            "neuroticism": analysis_data.get('neuroticism', 'Medium'),
            "stability": analysis_data.get('stability', 'Medium'),
            "pattern": analysis_data.get('pattern', 'Normal'),
            "character_match": analysis_data.get('character_match', ''),
            "character_match_reason": analysis_data.get('character_match_reason', ''),
            "shadow_trait": analysis_data.get('shadow_trait', ''),
            "detailed_analysis": analysis_data.get('detailed_analysis', ''),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Upsert - varsa güncelle, yoksa ekle
        response = httpx.post(
            f"{url}/rest/v1/user_analyses?on_conflict=username",
            headers=headers,
            json=data,
            timeout=10.0
        )
        
        if response.status_code in [200, 201, 204]:
            return True, "Analiz kaydedildi"
        else:
            return False, f"Hata: {response.status_code}"
    except Exception as e:
        return False, str(e)

def get_user_analysis(username: str):
    """Kullanıcının analiz sonuçlarını Supabase'den çeker (uyumluluk için)"""
    try:
        url, key = get_supabase_client()
        if not url or not key:
            return None
        
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        response = httpx.get(
            f"{url}/rest/v1/user_analyses?username=eq.{username.lower()}&select=*",
            headers=headers,
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
        return None
    except Exception:
        return None


def setup_background_music():
    """Arka plan müziğini ayarlar (Yerel Dosya - Persistent)"""
    music_file = "abstract-dramatic-atmosphere.mp3"
    
    try:
        with open(music_file, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        
        # Javascript Injection
        # Audio elementini window.parent (ana pencere) içine taşır
        # Button kontrolü ekler
        
        js_code = f"""
            <audio id="audio-source" style="display:none;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            
            <script>
                // 1. Audio Player Kurulumu
                var existingPlayer = window.parent.document.getElementById("project-zero-bg-music");
                var player;
                
                if (!existingPlayer) {{
                    player = document.createElement("audio");
                    player.id = "project-zero-bg-music";
                    player.loop = true;
                    player.volume = 0.05; // %5 ses seviyesi (İstek üzerine güncellendi)
                    
                    var source = document.getElementById("audio-source").querySelector("source");
                    player.appendChild(source.cloneNode(true));
                    
                    window.parent.document.body.appendChild(player);
                    
                    // Otomatik başlat
                    var playPromise = player.play();
                    if (playPromise !== undefined) {{
                        playPromise.catch(error => {{
                            console.log("Autoplay prevented");
                        }});
                    }}
                }} else {{
                    player = existingPlayer;
                }}

                // 2. Kontrol Butonu Kurulumu (Varsa silip yeniden ekle güncelleme için)
                var existingBtn = window.parent.document.getElementById("music-toggle-btn");
                if (existingBtn) {{
                    existingBtn.remove();
                }}
                
                var btn = document.createElement("div");
                btn.id = "music-toggle-btn";
                
                // Stil - Cyberpunk Tema
                btn.style.cssText = `
                    position: fixed;
                    bottom: 24px;
                    right: 24px;
                    z-index: 999999;
                    width: 44px;
                    height: 44px;
                    background: rgba(11, 14, 25, 0.85);
                    border: 1px solid rgba(0, 229, 255, 0.3);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    backdrop-filter: blur(8px);
                    box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
                `;
                
                // İkon Fonksiyonu
                function updateIcon(isPlaying) {{
                    if (isPlaying) {{
                        btn.innerHTML = '<span class="material-symbols-outlined" style="color: #00E5FF; font-size: 22px; filter: drop-shadow(0 0 5px rgba(0,229,255,0.5));">volume_up</span>';
                        btn.style.borderColor = "rgba(0, 229, 255, 0.5)";
                        btn.style.boxShadow = "0 0 20px rgba(0, 229, 255, 0.2)";
                        // Hafif dönüş animasyonu
                        btn.style.transform = "rotate(0deg)";
                    }} else {{
                        btn.innerHTML = '<span class="material-symbols-outlined" style="color: rgba(255, 255, 255, 0.4); font-size: 22px;">volume_off</span>';
                        btn.style.borderColor = "rgba(255, 255, 255, 0.1)";
                        btn.style.boxShadow = "none";
                    }}
                }}
                
                // İlk durum kontrolü
                updateIcon(!player.paused);
                
                // Tıklama Olayı
                btn.onclick = function() {{
                    if (player.paused) {{
                        player.play();
                        updateIcon(true);
                    }} else {{
                        player.pause();
                        updateIcon(false);
                    }}
                }};
                
                // Hover Efektleri
                btn.onmouseenter = function() {{ 
                    if (!player.paused) btn.style.transform = "scale(1.1) rotate(5deg)";
                    else btn.style.transform = "scale(1.1)";
                }};
                btn.onmouseleave = function() {{ 
                    btn.style.transform = "scale(1) rotate(0deg)";
                }};
                
                window.parent.document.body.appendChild(btn);
            </script>
        """
        components.html(js_code, height=0, width=0)
        
    except Exception as e:
        pass

# ==========================================
# 1. AYARLAR VE GÜVENLİK
# ==========================================
st.set_page_config(
    page_title="PROJECT ZERO",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Arka plan müziğini başlat
setup_background_music()

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
    
    /* HTML component iframe full width */
    .element-container,
    .stHtml,
    [data-testid="stIFrame"],
    iframe {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Remove all Streamlit default spacing */
    .css-1d391kg,
    .css-12oz5g7,
    .css-1lcbmhc {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Columns and rows - full width */
    [data-testid="column"],
    [data-testid="stHorizontalBlock"],
    .row-widget,
    .css-ocqkz7,
    div[data-testid="column"] > div {
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Mobil viewport ayarları */
    @viewport {
        width: device-width;
        zoom: 1.0;
    }
    
    /* Touch-friendly butonlar */
    /* Cyberpunk Button Styling */
    /* =========================================================================
       PROJECT ZERO CYBER-INTELLIGENCE BUTTON KIT
       ========================================================================= */
       
    /* 1. GLOBAL BUTTON STYLING (Neural Link - Primary) */
    /* Applies to ALL buttons by default to ensure premium look everywhere */
    .stButton > button {
        background: #0a141d !important; /* deep-navy from user config */
        border: 1px solid rgba(43, 205, 238, 0.3) !important;
        box-shadow: 0 0 20px rgba(43, 205, 238, 0.15) !important; 
        color: white !important;
        font-family: 'Epilogue', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.25em !important;
        text-transform: uppercase !important;
        border-radius: 2px !important; /* "rounded" in tailwind default is 0.25rem = 4px, user config says 0.125rem = 2px */
        min-height: 64px !important; /* Exactly 64px as requested */
        padding: 0 2rem !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Inner Gradient Effect and Glitch States via Pseudo-elements */
    .stButton > button::before {
        content: "" !important;
        position: absolute !important;
        inset: 0 !important;
        background: linear-gradient(90deg, rgba(43, 205, 238, 0.05), transparent) !important;
        z-index: 0 !important;
    }

    /* Hover State - Glitch & Glow */
    .stButton > button:hover {
        border-color: #2bcdee !important; /* primary color */
        box-shadow: 0 0 30px rgba(43, 205, 238, 0.25), inset 0 0 10px rgba(43, 205, 238, 0.1) !important;
        text-shadow: 2px 0 #ff00c1, -2px 0 #00fff9 !important;
        animation: glitch 0.3s infinite !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active {
        transform: scale(0.98) !important;
        background: #0d1a24 !important;
    }
    
    /* 2. SECONDARY / SMALLER BUTTONS (If explicitly type="secondary") */
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        border: 1px dashed rgba(43, 205, 238, 0.5) !important;
        box-shadow: none !important;
        min-height: 56px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
         background: rgba(43, 205, 238, 0.05) !important;
         border-style: solid !important;
         animation: none !important;
         text-shadow: none !important;
    }
    
    /* 3. DANGER ACTION (Critical Override) - Custom mapping (currently all secondary buttons are dashed, 
       but we can use this style for specific IDs if needed or map to form submit) */
       
    /* GLITCH ANIMATION KEYFRAMES */
    @keyframes glitch {
        0% { transform: translate(0); }
        20% { transform: translate(-2px, 2px); }
        40% { transform: translate(-2px, -2px); }
        60% { transform: translate(2px, 2px); }
        80% { transform: translate(2px, -2px); }
        100% { transform: translate(0); }
    }
    
    /* CORNER BRACKETS (Terminal Style) - Applied to small buttons or specific containers if needed */
    
    /* GLOBAL OVERRIDES */
    .stButton {
        width: 100% !important;
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
if 'ad_watched' not in st.session_state: st.session_state['ad_watched'] = False
if 'username' not in st.session_state: st.session_state['username'] = None
if 'username_error' not in st.session_state: st.session_state['username_error'] = None
if 'score_saved' not in st.session_state: st.session_state['score_saved'] = False
if 'user_country' not in st.session_state: st.session_state['user_country'] = None
if 'user_city' not in st.session_state: st.session_state['user_city'] = None
# Maliyet takip sistemi
if 'api_costs' not in st.session_state: st.session_state['api_costs'] = {
    'total_input_tokens': 0,
    'total_output_tokens': 0,
    'total_cost_usd': 0.0,
    'total_analyses': 0,
    'last_analysis_cost': None
}
# Uyumluluk karşılaştırma sistemi
if 'compatibility_partner' not in st.session_state: st.session_state['compatibility_partner'] = None
if 'compatibility_result' not in st.session_state: st.session_state['compatibility_result'] = None
if 'compatibility_error' not in st.session_state: st.session_state['compatibility_error'] = None


# ==========================================
# ÜLKE VE ŞEHİR VERİLERİ
# ==========================================
COUNTRIES_CITIES = {
    "🇹🇷 Türkiye": [
        "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", "Konya", 
        "Gaziantep", "Mersin", "Diyarbakır", "Kayseri", "Eskişehir", "Samsun",
        "Denizli", "Şanlıurfa", "Malatya", "Trabzon", "Erzurum", "Van", "Batman",
        "Elazığ", "Kocaeli", "Sakarya", "Balıkesir", "Manisa", "Aydın", "Muğla"
    ],
    "🇺🇸 USA": [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
        "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
        "San Francisco", "Seattle", "Denver", "Boston", "Las Vegas", "Miami",
        "Atlanta", "Portland", "Detroit", "Minneapolis", "Orlando", "Tampa"
    ],
    "🇬🇧 United Kingdom": [
        "London", "Birmingham", "Manchester", "Glasgow", "Liverpool", "Bristol",
        "Sheffield", "Leeds", "Edinburgh", "Leicester", "Cardiff", "Belfast"
    ],
    "🇩🇪 Germany": [
        "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt", "Stuttgart",
        "Düsseldorf", "Leipzig", "Dortmund", "Essen", "Bremen", "Dresden"
    ],
    "🇫🇷 France": [
        "Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes",
        "Strasbourg", "Montpellier", "Bordeaux", "Lille", "Rennes", "Reims"
    ],
    "🇮🇹 Italy": [
        "Rome", "Milan", "Naples", "Turin", "Palermo", "Genoa",
        "Bologna", "Florence", "Venice", "Verona", "Catania", "Bari"
    ],
    "🇪🇸 Spain": [
        "Madrid", "Barcelona", "Valencia", "Seville", "Zaragoza", "Málaga",
        "Murcia", "Palma", "Bilbao", "Alicante", "Córdoba", "Granada"
    ],
    "🇳🇱 Netherlands": [
        "Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven", "Tilburg"
    ],
    "🇧🇪 Belgium": [
        "Brussels", "Antwerp", "Ghent", "Bruges", "Liège", "Namur"
    ],
    "🇦🇹 Austria": [
        "Vienna", "Graz", "Linz", "Salzburg", "Innsbruck", "Klagenfurt"
    ],
    "🇨🇭 Switzerland": [
        "Zurich", "Geneva", "Basel", "Bern", "Lausanne", "Lucerne"
    ],
    "🇸🇪 Sweden": [
        "Stockholm", "Gothenburg", "Malmö", "Uppsala", "Västerås", "Örebro"
    ],
    "🇳🇴 Norway": [
        "Oslo", "Bergen", "Trondheim", "Stavanger", "Drammen", "Tromsø"
    ],
    "🇩🇰 Denmark": [
        "Copenhagen", "Aarhus", "Odense", "Aalborg", "Esbjerg", "Randers"
    ],
    "🇵🇱 Poland": [
        "Warsaw", "Kraków", "Łódź", "Wrocław", "Poznań", "Gdańsk"
    ],
    "🇨🇿 Czech Republic": [
        "Prague", "Brno", "Ostrava", "Plzeň", "Liberec", "Olomouc"
    ],
    "🇬🇷 Greece": [
        "Athens", "Thessaloniki", "Patras", "Heraklion", "Larissa", "Volos"
    ],
    "🇵🇹 Portugal": [
        "Lisbon", "Porto", "Braga", "Coimbra", "Funchal", "Setúbal"
    ],
    "🇮🇪 Ireland": [
        "Dublin", "Cork", "Limerick", "Galway", "Waterford", "Drogheda"
    ],
    "🇫🇮 Finland": [
        "Helsinki", "Espoo", "Tampere", "Vantaa", "Oulu", "Turku"
    ],
    "🇷🇴 Romania": [
        "Bucharest", "Cluj-Napoca", "Timișoara", "Iași", "Constanța", "Craiova"
    ],
    "🇭🇺 Hungary": [
        "Budapest", "Debrecen", "Szeged", "Miskolc", "Pécs", "Győr"
    ],
    "🌍 Other": [
        "Other City"
    ]
}

# ==========================================
# PROFANITY FILTER - Argo/Küfür Filtresi
# ==========================================
import re

# Leetspeak karakterleri
LEETSPEAK_MAP = {
    '0': 'o', '1': 'i', '2': 'z', '3': 'e', '4': 'a', '5': 's',
    '6': 'g', '7': 't', '8': 'b', '9': 'g', '@': 'a', '$': 's',
    '!': 'i', '(': 'c', ')': 'c', '{': 'c', '}': 'c', '[': 'c', ']': 'c',
    '<': 'c', '>': 'c', '|': 'l', '+': 't', '&': 'e', '%': 'x',
    '*': 'a', '^': 'a', '#': 'h'
}

# Yasaklı kelimeler listesi (Türkçe ve İngilizce)
BANNED_WORDS = [
    # Türkçe küfürler
    'amk', 'aq', 'amq', 'amina', 'amını', 'aminakoyim', 'aminakoydugum',
    'orospu', 'oruspu', 'oç', 'oc', 'piç', 'pic', 'pezevenk', 'gavat',
    'sikik', 'siktir', 'sikerim', 'sikeyim', 'sik', 'yarrak', 'yarak',
    'taşak', 'tasak', 'göt', 'got', 'ibne', 'top', 'am', 'meme',
    'kaltak', 'fahişe', 'fahise', 'sürtük', 'surtuk', 'kevaşe', 'kevase',
    'dangalak', 'salak', 'gerizekalı', 'gerizekali', 'aptal', 'mal',
    'bok', 'boktan', 'puşt', 'pust', 'kahpe', 'şerefsiz', 'serefsiz',
    'haysiyetsiz', 'namussuz', 'adi', 'alçak', 'alcak', 'köpek', 'kopek',
    'domuz', 'it', 'hıyar', 'hiyar', 'züppe', 'zuppe', 'kodumun', 'kodugumun',
    'koydum', 'koydugum', 'anani', 'ananı', 'bacini', 'bacını',
    # İngilizce küfürler
    'fuck', 'shit', 'bitch', 'ass', 'asshole', 'bastard', 'cunt',
    'dick', 'cock', 'pussy', 'whore', 'slut', 'nigger', 'nigga',
    'faggot', 'fag', 'retard', 'moron', 'idiot', 'dumb', 'stupid',
    'sex', 'porn', 'xxx', 'penis', 'vagina', 'boob', 'tit', 'nude',
    'naked', 'horny', 'hentai', 'milf', 'dildo', 'orgasm', 'cum',
    'jerk', 'wank', 'twat', 'prick', 'douche', 'scum', 'crap',
    'damn', 'hell', 'gay', 'lesbian', 'homo', 'queer', 'tranny',
    'nazi', 'hitler', 'rape', 'kill', 'murder', 'suicide', 'die',
    # Ek varyasyonlar
    'anan', 'bacin', 'sikim', 'gotten', 'yarram', 'tavsak', 'orosbu',
    'pice', 'pici', 'ibneler', 'pislik', 'zibidi'
]

def normalize_leetspeak(text):
    """Leetspeak karakterlerini normal harflere çevirir"""
    result = text.lower()
    for leet, normal in LEETSPEAK_MAP.items():
        result = result.replace(leet, normal)
    return result

def contains_profanity(username):
    """
    Kullanıcı adında küfür/argo olup olmadığını kontrol eder.
    Leetspeak varyasyonlarını da yakalar (örn: s3x, f*ck, sh1t)
    """
    if not username:
        return True, "empty"
    
    # Orijinal ve normalize edilmiş versiyonları kontrol et
    original = username.lower()
    normalized = normalize_leetspeak(username)
    
    # Boşlukları ve özel karakterleri kaldır
    clean_original = re.sub(r'[^a-zA-Z0-9ğüşıöçĞÜŞİÖÇ]', '', original)
    clean_normalized = re.sub(r'[^a-zA-Z0-9ğüşıöçĞÜŞİÖÇ]', '', normalized)
    
    for banned in BANNED_WORDS:
        banned_lower = banned.lower()
        # Direkt eşleşme
        if banned_lower in original or banned_lower in normalized:
            return True, banned
        # Temizlenmiş versiyonlarda eşleşme
        if banned_lower in clean_original or banned_lower in clean_normalized:
            return True, banned
        # Kelime içinde geçiyor mu (örn: fuck123, xxsexxx)
        if re.search(re.escape(banned_lower), clean_original) or re.search(re.escape(banned_lower), clean_normalized):
            return True, banned
    
    return False, None

def validate_username(username):
    """
    Kullanıcı adını doğrular. Geçerli ise (True, None), değilse (False, hata_mesajı) döner.
    """
    lang = st.session_state.get('language', 'TR')
    
    if not username or len(username.strip()) == 0:
        return False, "Kullanıcı adı boş olamaz." if lang == 'TR' else "Username cannot be empty."
    
    username = username.strip()
    
    # Uzunluk kontrolü
    if len(username) < 3:
        return False, "Kullanıcı adı en az 3 karakter olmalıdır." if lang == 'TR' else "Username must be at least 3 characters."
    
    if len(username) > 20:
        return False, "Kullanıcı adı en fazla 20 karakter olabilir." if lang == 'TR' else "Username must be at most 20 characters."
    
    # Geçerli karakterler kontrolü
    if not re.match(r'^[a-zA-Z0-9_ğüşıöçĞÜŞİÖÇ]+$', username):
        return False, "Kullanıcı adı sadece harf, rakam ve alt çizgi içerebilir." if lang == 'TR' else "Username can only contain letters, numbers, and underscores."
    
    # Küfür kontrolü
    has_profanity, matched_word = contains_profanity(username)
    if has_profanity:
        return False, "Bu kullanıcı adı uygun değil. Lütfen farklı bir isim seçin." if lang == 'TR' else "This username is not appropriate. Please choose a different name."
    
    return True, None

# ==========================================
# 4. İÇERİK VERİTABANI
# ==========================================
CONTENT = {
    "TR": {
        "LANDING": {"STATUS": "Sistem Hazır", "TITLE": "Zihninin derinliklerine dal", "SUBTITLE": "Nöro-Analitik Kimlik Raporu", "BTN": "SİSTEME GİRİŞ"},
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
        "LANDING": {"STATUS": "System Ready", "TITLE": "Dive into the depths of your mind", "SUBTITLE": "Neuro-Analytical Identity Report", "BTN": "ENTER SYSTEM"},
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
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-15px); }}
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .hero-container {{
            position: relative;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            width: 100%;
            background: #0b0e19;
            overflow: hidden;
            padding: 0 !important;
            margin: 0 !important;
        }}
        
        /* Background grid */
        .grid-bg {{
            position: absolute;
            inset: 0;
            opacity: 0.03;
            background-image: 
                linear-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
            background-size: 40px 40px;
        }}
        
        /* Vignette */
        .vignette {{
            position: absolute;
            inset: 0;
            background: radial-gradient(ellipse at center, transparent 0%, rgba(0,0,0,0.7) 100%);
            pointer-events: none;
        }}
        
        /* Status bar */
        .status-bar {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            display: flex;
            justify-content: space-between;
            padding: 20px 24px;
            font-size: 11px;
            color: rgba(255, 255, 255, 0.6);
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            z-index: 20;
            background: linear-gradient(
                180deg,
                rgba(11, 14, 25, 0.9) 0%,
                rgba(11, 14, 25, 0.7) 50%,
                transparent 100%
            );
            backdrop-filter: blur(8px);
        }}
        
        /* Brain icon section */
        .icon-section {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            z-index: 10;
            animation: float 6s ease-in-out infinite;
            padding-top: 80px;
        }}
        
        .brain-container {{
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 140px;
            height: 140px;
        }}
        
        .brain-glow {{
            position: absolute;
            inset: -20px;
            background: #00E5FF;
            border-radius: 50%;
            filter: blur(60px);
            opacity: 0.25;
            animation: breath 4s ease-in-out infinite;
        }}
        
        .brain-box {{
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 140px;
            height: 140px;
            border-radius: 20px;
            background: rgba(17, 30, 33, 0.5);
            border: 1px solid rgba(255,255,255,0.08);
            backdrop-filter: blur(8px);
            box-shadow: 0 0 30px rgba(0, 229, 255, 0.2);
        }}
        
        .brain-icon {{
            font-size: 72px;
            color: #00E5FF;
            filter: drop-shadow(0 0 12px rgba(0,229,255,0.6));
        }}
        
        .keyhole-icon {{
            position: absolute;
            font-size: 28px;
            color: #0b0e19;
            margin-top: 36px;
            margin-left: 4px;
        }}
        
        /* Title section */
        .title-section {{
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            z-index: 10;
            animation: fadeIn 1s ease-out 0.3s both;
            padding: 0 20px;
        }}
        
        .main-title {{
            color: white;
            font-family: 'Epilogue', sans-serif;
            font-weight: 900;
            font-size: clamp(36px, 8vw, 56px);
            letter-spacing: 0.25em;
            line-height: 1.2;
            margin: 0;
            text-shadow: 0 4px 8px rgba(0,0,0,0.5);
        }}
        
        .title-cyan {{
            color: rgba(0, 229, 255, 0.95);
        }}
        
        .subtitle {{
            color: #94a3b8;
            font-size: clamp(13px, 2.5vw, 16px);
            margin: 20px 0 0 0;
            letter-spacing: 0.08em;
            font-family: 'Manrope', sans-serif;
        }}
        
        .subtitle-divider {{
            display: inline-block;
            height: 1px;
            width: 32px;
            background: #334155;
            vertical-align: middle;
            margin: 0 12px;
        }}
        
        /* Button section */
        .button-section {{
            flex: 0.8;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-end;
            gap: 16px;
            padding: 0 20px 60px 20px;
            z-index: 10;
        }}
        
        /* Bottom line */
        .bottom-line {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(to right, transparent, #0a3f4d, transparent);
            opacity: 0.5;
        }}
        
        @media (max-width: 768px) {{
            .status-bar {{
                padding: 16px 16px;
                font-size: 10px;
            }}
            
            .icon-section {{
                padding-top: 60px;
            }}
            
            .brain-container,
            .brain-box {{
                width: 100px;
                height: 100px;
            }}
            
            .brain-icon {{
                font-size: 56px;
            }}
            
            .keyhole-icon {{
                font-size: 20px;
                margin-top: 26px;
            }}
            
            .main-title {{
                font-size: clamp(28px, 6vw, 40px);
                letter-spacing: 0.2em;
            }}
            
            .subtitle {{
                font-size: clamp(11px, 2vw, 14px);
            }}
            
            .button-section {{
                padding: 0 16px 40px 16px;
            }}
        }}
    </style>
    
    <div class="hero-container">
        <!-- Background layers -->
        <div class="grid-bg"></div>
        <div class="vignette"></div>
        
        <!-- Status bar -->
        <div class="status-bar">
            <span>{t['STATUS']}</span>
            <span>V 2.5.0</span>
        </div>
        
        <!-- Brain icon section (top) -->
        <div class="icon-section">
            <div class="brain-container">
                <div class="brain-glow"></div>
                <div class="brain-box">
                    <span class="material-symbols-outlined brain-icon">psychology</span>
                    <span class="material-symbols-outlined keyhole-icon">key_vertical</span>
                </div>
            </div>
        </div>
        
        <!-- Title section (middle) -->
        <div class="title-section">
            <h1 class="main-title">
                PROJECT<br/><span class="title-cyan">ZERO</span>
            </h1>
            <div style="margin-top: 20px;">
                <span class="subtitle-divider"></span>
                <span class="subtitle">{t['TITLE']}</span>
                <span class="subtitle-divider"></span>
            </div>
            <div style="margin-top: 10px; opacity: 0.9;">
                <span class="subtitle" style="display: block; color: rgba(0, 229, 255, 0.9); font-size: 0.85em; font-weight: 500; letter-spacing: 0.15em; text-transform: uppercase;">
                    {t['SUBTITLE']}
                </span>
            </div>
        </div>
        
        <!-- Empty space for buttons (bottom) -->
        <div class="button-section">
            <!-- Streamlit butonları buraya gelecek -->
        </div>
        
        <!-- Bottom line -->
        <div class="bottom-line"></div>
    </div>
    '''
    
    components.html(landing_html, height=900, scrolling=False)
    
    # ==========================================
    # LEADERBOARD - Top 100 IQ Scores
    # ==========================================
    leaderboard_title = "🏆 EN YÜKSEK IQ PUANLARI" if lang == 'TR' else "🏆 TOP IQ SCORES"
    leaderboard_data = [] # get_leaderboard(100) - KALDIRILDI
    
    if False and leaderboard_data and len(leaderboard_data) > 0:
        # Leaderboard için HTML
        leaderboard_rows = ""
        for i, entry in enumerate(leaderboard_data[:100]):
            rank = i + 1
            username = entry.get('username', 'Anonymous')[:15]
            iq_score = entry.get('iq_score', 0)
            character = entry.get('character_name', '')[:20]
            
            # Sıralama için özel stiller
            if rank == 1:
                rank_class = "rank-gold"
                rank_icon = "🥇"
            elif rank == 2:
                rank_class = "rank-silver"
                rank_icon = "🥈"
            elif rank == 3:
                rank_class = "rank-bronze"
                rank_icon = "🥉"
            else:
                rank_class = "rank-normal"
                rank_icon = f"#{rank}"
            
            leaderboard_rows += f'''
            <div class="lb-row {rank_class}">
                <div class="lb-rank">{rank_icon}</div>
                <div class="lb-user">{username}</div>
                <div class="lb-score">{iq_score}</div>
                <div class="lb-char">{character}</div>
            </div>
            '''
        
        leaderboard_html = f'''
        <style>
            .leaderboard-container {{
                background: rgba(11, 14, 25, 0.95);
                border: 1px solid rgba(0, 229, 255, 0.2);
                border-radius: 16px;
                padding: 20px;
                margin: 20px 0;
                max-height: 400px;
                overflow-y: auto;
            }}
            .lb-header {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 1px solid rgba(0, 229, 255, 0.2);
            }}
            .lb-title {{
                font-family: 'Epilogue', sans-serif;
                font-size: 18px;
                font-weight: 800;
                color: #00E5FF;
                letter-spacing: 0.1em;
            }}
            .lb-columns {{
                display: grid;
                grid-template-columns: 50px 1fr 80px 1fr;
                gap: 8px;
                padding: 8px 12px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 10px;
                color: rgba(255, 255, 255, 0.4);
                text-transform: uppercase;
                letter-spacing: 0.1em;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }}
            .lb-row {{
                display: grid;
                grid-template-columns: 50px 1fr 80px 1fr;
                gap: 8px;
                padding: 10px 12px;
                border-radius: 8px;
                transition: all 0.2s ease;
                font-family: 'Manrope', sans-serif;
            }}
            .lb-row:hover {{
                background: rgba(0, 229, 255, 0.05);
            }}
            .lb-rank {{
                font-size: 14px;
                font-weight: 700;
                display: flex;
                align-items: center;
            }}
            .lb-user {{
                color: #e2e8f0;
                font-size: 13px;
                font-weight: 500;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}
            .lb-score {{
                color: #00E5FF;
                font-size: 14px;
                font-weight: 700;
                font-family: 'JetBrains Mono', monospace;
            }}
            .lb-char {{
                color: rgba(255, 255, 255, 0.5);
                font-size: 11px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}
            .rank-gold .lb-rank {{ color: #FFD700; }}
            .rank-gold .lb-user {{ color: #FFD700; }}
            .rank-silver .lb-rank {{ color: #C0C0C0; }}
            .rank-silver .lb-user {{ color: #C0C0C0; }}
            .rank-bronze .lb-rank {{ color: #CD7F32; }}
            .rank-bronze .lb-user {{ color: #CD7F32; }}
            .rank-normal .lb-rank {{ color: rgba(255, 255, 255, 0.6); }}
            
            /* Scrollbar styling */
            .leaderboard-container::-webkit-scrollbar {{
                width: 6px;
            }}
            .leaderboard-container::-webkit-scrollbar-track {{
                background: rgba(0, 0, 0, 0.2);
                border-radius: 3px;
            }}
            .leaderboard-container::-webkit-scrollbar-thumb {{
                background: rgba(0, 229, 255, 0.3);
                border-radius: 3px;
            }}
            .leaderboard-container::-webkit-scrollbar-thumb:hover {{
                background: rgba(0, 229, 255, 0.5);
            }}
            
            @media (max-width: 600px) {{
                .lb-columns, .lb-row {{
                    grid-template-columns: 40px 1fr 60px;
                }}
                .lb-char {{
                    display: none;
                }}
                .lb-score {{
                    font-size: 12px;
                }}
            }}
        </style>
        
        <div class="leaderboard-container">
            <div class="lb-header">
                <span class="lb-title">{leaderboard_title}</span>
            </div>
            <div class="lb-columns">
                <span>{"SIRA" if lang == "TR" else "RANK"}</span>
                <span>{"KULLANICI" if lang == "TR" else "USER"}</span>
                <span>IQ</span>
                <span>{"KİŞİLİK" if lang == "TR" else "CHARACTER"}</span>
            </div>
            {leaderboard_rows}
        </div>
        '''
        components.html(leaderboard_html, height=450, scrolling=False)
    
    # Sponsor Banner - BDTCoin
    banner_html = '''
    <style>
        @keyframes goldShimmer {
            0% { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        .bdtcoin-banner {
            display: block;
            text-decoration: none;
            background: linear-gradient(135deg, #1a1205 0%, #0d0d0d 50%, #1a1205 100%);
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 12px;
            padding: 16px 20px;
            margin: 16px 0;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .bdtcoin-banner:hover {
            border-color: rgba(212, 175, 55, 0.6);
            box-shadow: 0 0 30px rgba(212, 175, 55, 0.2);
            transform: translateY(-2px);
        }
        .bdtcoin-banner::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.1), transparent);
            background-size: 200% 100%;
            animation: goldShimmer 3s ease-in-out infinite;
        }
        .banner-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
            z-index: 2;
        }
        .banner-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .coin-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #d4af37 0%, #b8860b 50%, #d4af37 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: 900;
            color: #0d0d0d;
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.4);
            font-family: 'Epilogue', sans-serif;
        }
        .banner-text {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .banner-title {
            font-family: 'Epilogue', sans-serif;
            font-size: 18px;
            font-weight: 800;
            background: linear-gradient(90deg, #d4af37, #f5d778, #d4af37);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: 0.05em;
        }
        .banner-subtitle {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: rgba(212, 175, 55, 0.7);
            text-transform: uppercase;
            letter-spacing: 0.15em;
        }
        .banner-cta {
            background: linear-gradient(135deg, #d4af37 0%, #b8860b 100%);
            color: #0d0d0d;
            padding: 10px 20px;
            border-radius: 6px;
            font-family: 'Epilogue', sans-serif;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
            transition: all 0.3s ease;
        }
        .bdtcoin-banner:hover .banner-cta {
            box-shadow: 0 6px 20px rgba(212, 175, 55, 0.5);
        }
        .sponsor-tag {
            position: absolute;
            top: 8px;
            right: 12px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 9px;
            color: rgba(255, 255, 255, 0.3);
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }
    </style>
    
    <a href="https://www.bdtcoin.co/" target="_blank" rel="noopener noreferrer" class="bdtcoin-banner">
        <span class="sponsor-tag">Sponsor</span>
        <div class="banner-content">
            <div class="banner-left">
                <div class="coin-icon">₿</div>
                <div class="banner-text">
                    <span class="banner-title">$BDTC - Value Anchored by Gold</span>
                    <span class="banner-subtitle">BDTCOIN • Next-Gen Cryptocurrency</span>
                </div>
            </div>
            <div class="banner-cta">Satın Al / Buy Now</div>
        </div>
    </a>
    '''
    components.html(banner_html, height=120, scrolling=False)
    
    # Sosyal Giriş Butonları (Google & Apple ile Bağlan)
    connect_label = "Hesabınızı Bağlayın" if st.session_state['language'] == 'TR' else "Connect Your Account"
    google_btn_text = "Google ile Bağlan" if st.session_state['language'] == 'TR' else "Connect with Google"
    apple_btn_text = "Apple ile Bağlan" if st.session_state['language'] == 'TR' else "Connect with Apple"
    
    social_login_html = f'''
    <style>
        .social-section {{
            margin-bottom: 20px;
            text-align: center;
        }}
        .social-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            color: rgba(255, 255, 255, 0.4);
            letter-spacing: 0.15em;
            text-transform: uppercase;
            margin-bottom: 14px;
        }}
        .social-buttons {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 320px;
            margin: 0 auto;
        }}
        .social-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 14px 24px;
            border-radius: 10px;
            text-decoration: none;
            font-family: 'Epilogue', sans-serif;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
        }}
        .google-btn {{
            background: #ffffff;
            color: #3c4043;
        }}
        .google-btn:hover {{
            background: #f7f7f7;
            box-shadow: 0 4px 15px rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }}
        .apple-btn {{
            background: #000000;
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .apple-btn:hover {{
            background: #1a1a1a;
            border-color: rgba(255, 255, 255, 0.4);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            transform: translateY(-2px);
        }}
        .social-icon {{
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .social-icon svg {{
            width: 100%;
            height: 100%;
        }}
        .divider-section {{
            display: flex;
            align-items: center;
            margin: 20px auto;
            max-width: 320px;
            gap: 16px;
        }}
        .divider-line {{
            flex: 1;
            height: 1px;
            background: rgba(255, 255, 255, 0.1);
        }}
        .divider-text {{
            font-family: 'Manrope', sans-serif;
            font-size: 11px;
            color: rgba(255, 255, 255, 0.3);
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        @media (max-width: 480px) {{
            .social-btn {{
                padding: 12px 20px;
                font-size: 13px;
            }}
        }}
    </style>
    
    <div class="social-section">
        <div class="social-label">{connect_label}</div>
        <div class="social-buttons">
            <!-- Google Button -->
            <a href="#" class="social-btn google-btn" onclick="return false;">
                <div class="social-icon">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                </div>
                {google_btn_text}
            </a>
            
            <!-- Apple Button -->
            <a href="#" class="social-btn apple-btn" onclick="return false;">
                <div class="social-icon">
                    <svg viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                        <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
                    </svg>
                </div>
                {apple_btn_text}
            </a>
        </div>
        
        <div class="divider-section">
            <div class="divider-line"></div>
            <span class="divider-text">{"veya" if st.session_state['language'] == 'TR' else "or"}</span>
            <div class="divider-line"></div>
        </div>
    </div>
    '''
    components.html(social_login_html, height=220, scrolling=False)
    
    # Native Streamlit butonları
    col1, col2, col3 = st.columns([0.1, 2, 0.1])
    with col2:
        if st.button(f"🔐 {t['BTN']}", use_container_width=True, type="primary"):
            st.session_state['page'] = 'username'
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
        
        # Liderlik Tablosu Butonu
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        if st.button("🏆 LİDERLİK TABLOSU", use_container_width=True):
            st.session_state['page'] = 'leaderboard'
            st.rerun()
        
        # App Store Butonları
        coming_soon_text = "Çok Yakında" if st.session_state['language'] == 'TR' else "Coming Soon"
        
        app_store_html = f'''
        <style>
            .app-store-section {{
                margin-top: 24px;
                text-align: center;
            }}
            .coming-soon-label {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                color: rgba(255, 255, 255, 0.5);
                letter-spacing: 0.2em;
                text-transform: uppercase;
                margin-bottom: 12px;
            }}
            .store-buttons {{
                display: flex;
                justify-content: center;
                gap: 12px;
                flex-wrap: wrap;
            }}
            .store-btn {{
                display: flex;
                align-items: center;
                gap: 10px;
                background: rgba(27, 34, 45, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px 18px;
                text-decoration: none;
                transition: all 0.3s ease;
                cursor: pointer;
                opacity: 0.7;
            }}
            .store-btn:hover {{
                border-color: rgba(0, 229, 255, 0.4);
                background: rgba(27, 34, 45, 1);
                opacity: 1;
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0, 229, 255, 0.15);
            }}
            .store-icon {{
                width: 28px;
                height: 28px;
            }}
            .store-icon svg {{
                width: 100%;
                height: 100%;
                fill: white;
            }}
            .store-text {{
                display: flex;
                flex-direction: column;
                align-items: flex-start;
            }}
            .store-text-small {{
                font-family: 'Manrope', sans-serif;
                font-size: 9px;
                color: rgba(255, 255, 255, 0.6);
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            .store-text-main {{
                font-family: 'Epilogue', sans-serif;
                font-size: 14px;
                font-weight: 600;
                color: white;
                letter-spacing: 0.02em;
            }}
            @media (max-width: 480px) {{
                .store-btn {{
                    padding: 8px 14px;
                }}
                .store-icon {{
                    width: 24px;
                    height: 24px;
                }}
                .store-text-main {{
                    font-size: 12px;
                }}
            }}
        </style>
        
        <div class="app-store-section">
            <div class="coming-soon-label">{coming_soon_text}</div>
            <div class="store-buttons">
                <!-- Google Play Button -->
                <a href="#" class="store-btn" onclick="return false;">
                    <div class="store-icon">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M3.609 1.814L13.792 12 3.609 22.186c-.181-.182-.292-.422-.292-.678V2.492c0-.256.111-.496.292-.678zM14.852 13.06l2.59 2.589-10.87 6.228 8.28-8.817zm3.778-2.12l2.094 1.199c.391.223.638.644.638 1.089 0 .445-.247.866-.638 1.09l-2.094 1.199-2.625-2.639 2.625-2.638zM6.572 3.123l10.87 6.228-2.59 2.59-8.28-8.818z"/>
                        </svg>
                    </div>
                    <div class="store-text">
                        <span class="store-text-small">GET IT ON</span>
                        <span class="store-text-main">Google Play</span>
                    </div>
                </a>
                
                <!-- App Store Button -->
                <a href="#" class="store-btn" onclick="return false;">
                    <div class="store-icon">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
                        </svg>
                    </div>
                    <div class="store-text">
                        <span class="store-text-small">Download on the</span>
                        <span class="store-text-main">App Store</span>
                    </div>
                </a>
            </div>
        </div>
        '''
        components.html(app_store_html, height=120, scrolling=False)


def show_username():
    """Kullanıcı adı seçme ekranı"""
    lang = st.session_state['language']
    
    # Dile göre metinler
    texts = {
        'TR': {
            'title': 'KULLANICI ADI BELİRLE',
            'subtitle': 'Profiliniz için benzersiz bir kullanıcı adı seçin',
            'placeholder': 'Kullanıcı adınızı girin...',
            'btn': 'DEVAM ET',
            'rules': [
                '• 3-20 karakter arası olmalı',
                '• Sadece harf, rakam ve alt çizgi (_) kullanılabilir',
                '• Uygunsuz kelimeler kullanılamaz'
            ],
            'back': 'GERİ DÖN'
        },
        'EN': {
            'title': 'CHOOSE USERNAME',
            'subtitle': 'Select a unique username for your profile',
            'placeholder': 'Enter your username...',
            'btn': 'CONTINUE',
            'rules': [
                '• Must be 3-20 characters',
                '• Only letters, numbers, and underscore (_) allowed',
                '• Inappropriate words are not allowed'
            ],
            'back': 'GO BACK'
        }
    }
    
    t = texts[lang]
    
    # CSS styling
    username_css = '''
    <style>
        .username-container {
            min-height: 100vh;
            background: #0b0e19;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .username-box {
            background: rgba(27, 34, 45, 0.6);
            border: 1px solid rgba(0, 229, 255, 0.2);
            border-radius: 16px;
            padding: 40px 32px;
            max-width: 420px;
            width: 100%;
            backdrop-filter: blur(10px);
        }
        .username-icon {
            text-align: center;
            margin-bottom: 24px;
        }
        .icon-circle {
            width: 80px;
            height: 80px;
            background: rgba(0, 229, 255, 0.1);
            border: 2px solid rgba(0, 229, 255, 0.3);
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
        }
        .username-title {
            font-family: 'Epilogue', sans-serif;
            font-size: 24px;
            font-weight: 800;
            color: #00E5FF;
            text-align: center;
            letter-spacing: 0.15em;
            margin-bottom: 8px;
        }
        .username-subtitle {
            font-family: 'Manrope', sans-serif;
            font-size: 14px;
            color: rgba(255, 255, 255, 0.6);
            text-align: center;
            margin-bottom: 32px;
        }
        .rules-box {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 16px;
            margin-top: 20px;
        }
        .rule-item {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: rgba(255, 255, 255, 0.5);
            line-height: 1.8;
        }
    </style>
    '''
    
    st.markdown(username_css, unsafe_allow_html=True)
    
    # Header HTML
    header_html = f'''
    <link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@400;500;600;700;800&family=Manrope:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
    
    <div style="text-align: center; padding: 60px 20px 30px 20px;">
        <div style="margin-bottom: 24px;">
            <div style="
                width: 80px;
                height: 80px;
                background: rgba(0, 229, 255, 0.1);
                border: 2px solid rgba(0, 229, 255, 0.3);
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 36px;
            ">👤</div>
        </div>
        <h1 style="
            font-family: 'Epilogue', sans-serif;
            font-size: 24px;
            font-weight: 800;
            color: #00E5FF;
            letter-spacing: 0.15em;
            margin-bottom: 8px;
        ">{t['title']}</h1>
        <p style="
            font-family: 'Manrope', sans-serif;
            font-size: 14px;
            color: rgba(255, 255, 255, 0.6);
        ">{t['subtitle']}</p>
    </div>
    '''
    components.html(header_html, height=260, scrolling=False)
    
    # Input alanı
    col1, col2, col3 = st.columns([0.1, 2, 0.1])
    with col2:
        username_input = st.text_input(
            label="Username",
            placeholder=t['placeholder'],
            label_visibility="collapsed",
            key="username_input"
        )
        
        # Ülke ve Şehir seçimi
        country_label = "🌍 Ülke Seçin" if lang == 'TR' else "🌍 Select Country"
        city_label = "🏙️ Şehir Seçin" if lang == 'TR' else "🏙️ Select City"
        
        # Ülke seçimi
        countries = list(COUNTRIES_CITIES.keys())
        selected_country = st.selectbox(
            country_label,
            options=[""] + countries,
            index=0,
            key="country_select"
        )
        
        # Şehir seçimi (ülkeye göre dinamik)
        if selected_country and selected_country != "":
            cities = COUNTRIES_CITIES.get(selected_country, [])
            selected_city = st.selectbox(
                city_label,
                options=[""] + cities,
                index=0,
                key="city_select"
            )
        else:
            selected_city = ""
            st.selectbox(
                city_label,
                options=[""],
                index=0,
                key="city_select_disabled",
                disabled=True
            )
        
        # Hata mesajı varsa göster
        if st.session_state.get('username_error'):
            st.markdown(f'''
            <div style="
                background: rgba(255, 82, 82, 0.1);
                border: 1px solid rgba(255, 82, 82, 0.3);
                border-radius: 8px;
                padding: 12px 16px;
                margin: 10px 0;
            ">
                <p style="
                    font-family: 'Manrope', sans-serif;
                    font-size: 13px;
                    color: #ff5252;
                    margin: 0;
                ">⚠️ {st.session_state['username_error']}</p>
            </div>
            ''', unsafe_allow_html=True)
        
        # Devam et butonu
        if st.button(f"✓ {t['btn']}", use_container_width=True, type="primary"):
            is_valid, error_msg = validate_username(username_input)
            
            # Ülke ve şehir kontrolü
            if not selected_country or selected_country == "":
                error_msg = "Lütfen ülke seçin." if lang == 'TR' else "Please select a country."
                is_valid = False
            elif not selected_city or selected_city == "":
                error_msg = "Lütfen şehir seçin." if lang == 'TR' else "Please select a city."
                is_valid = False
            
            if is_valid:
                st.session_state['username'] = username_input.strip()
                st.session_state['user_country'] = selected_country
                st.session_state['user_city'] = selected_city
                st.session_state['username_error'] = None
                st.session_state['page'] = 'quiz'
                st.session_state['quiz_start_time'] = time.time()
                st.rerun()
            else:
                st.session_state['username_error'] = error_msg
                st.rerun()
        
        # Geri dön butonu
        if st.button(f"← {t['back']}", use_container_width=True):
            st.session_state['username_error'] = None
            st.session_state['page'] = 'landing'
            st.rerun()
        
        # Kurallar
        rules_html = f'''
        <div style="
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 16px;
            margin-top: 20px;
        ">
            {''.join([f'<p style="font-family: JetBrains Mono, monospace; font-size: 11px; color: rgba(255,255,255,0.5); margin: 4px 0;">{rule}</p>' for rule in t['rules']])}
        </div>
        '''
        st.markdown(rules_html, unsafe_allow_html=True)


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
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
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
        
        /* Anti-Cheat: Metin Kopyalama Engeli */
        div[data-testid="stMarkdownContainer"] p, 
        div[data-testid="stMarkdownContainer"] h1, 
        div[data-testid="stMarkdownContainer"] h2, 
        div[data-testid="stMarkdownContainer"] h3,
        div[data-testid="stMarkdownContainer"] li,
        div[data-testid="stMarkdownContainer"] span {
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
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
            # Boş cevap kontrolü - max 2 boş soru hakkı
            empty_count = sum(1 for ans in user_answers.values() if not ans or str(ans).strip() == '')
            if empty_count > 2:
                st.error(f"⚠️ Çok fazla boş soru var ({empty_count} tane). Lütfen en az {len(user_answers) - 2} soruyu yanıtlayın.")
            else:
                # Süre hesabı
                start_t = st.session_state.get('quiz_start_time', time.time())
                duration = time.time() - start_t
                st.session_state['quiz_duration'] = duration
                
                st.session_state['user_data'] = user_answers
                st.session_state['page'] = 'loading'  # Önce yükleme ekranına git
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

def run_fbi_analysis(user_data, lang, duration=0):
    """AI analiz motoru - FBI Davranış Bilimcisi (Maliyet Takipli)"""
    
    # TROLL RANDOMIZER - Forces variety every time
    all_troll_chars = [
        "Patrick Star (Tembel)", "Peter Griffin (Sorumsuz)", "Homer Simpson (Düşüncesiz)", 
        "Beavis (Aptal)", "Ralph Wiggum (Saf)", "Jar Jar Binks (Yıkıcı)", "Wile E. Coyote (Başarısız)",
        "Scrappy-Doo (Sinir Bozucu)", "Gollum (Obsesif)", "Mr. Bean (Sakar)", "Nero (Umursamaz)", 
        "King Joffrey (Yeteneksiz)", "Commodus (Kibirli)", "Pennywise (Komik değil)", "Deadpool (Güçsüz)",
        "Don Quixote (Hayalperest)", "Ed (Salak)", "Billy (Grim Adventures)", "Stimpy (Ren & Stimpy)", 
        "Michael Scott (Farkındalıksız)", "Barney Stinson (Yüzeysel)", "Joey Tribbiani (Saf)",
        "Johnny Bravo (Narsisist)", "Gaston (Kibirli)", "Kronk (Yancı)", "Sid (Ice Age)"
    ]
    import random
    selected_trolls = list(random.sample(all_troll_chars, 6))
    troll_list_str = ", ".join(selected_trolls)
    
    prompt = f"""
    Sen, FBI Davranış Analizi Birimi'nde görevli üst düzey bir profil uzmanı ve davranış bilimcisisin.
    20 yıllık tecrübenle binlerce suçlu ve lider profilini analiz ettin.
    
    Görevin: Aşağıdaki kullanıcı verilerini derinlemesine analiz ederek kapsamlı bir psikolojik profil oluşturmak.
    
    DİL: {lang}. (Tüm yanıtları bu dilde ver).
    TEST SÜRESİ: {duration:.2f} saniye.
    
    HİLE VE SÜRE ANALİZİ (ÖNEMLİ):
    - < 60 saniye: İmkansız hız. Okumadan rastgele basılmış olabilir.
    - > 2400 saniye (40 dk): Çok uzun süre. Odak kaybı veya dış yardım (AI/Google) şüphesi. Skor penalizesi uygula (-10 puan).
    - Yapay zeka dili tespit edersen (ChatGPT stili cevaplar), kullanıcıyı uyar ve skoru düşür.

    ÇIKTI FORMATI (Sadece JSON, tüm alanları eksiksiz doldur):
    {{
        "iq": "Sayı (70-145 arası)",
        "archetype": "Kullanıcının kişiliğini tanımlayan profesyonel bir arketip. Aşağıdaki 60+ gerçekçi arketipten EN UYGUN olanı seç:
        
        JUNG ARKETİPLERİ (Klasik Psikoloji):
        The Mastermind (Beyincidar), The Strategist (Stratejist), The Architect (Mimar), The Visionary (Vizyoner), The Commander (Komutan), The Analyst (Analist), The Philosopher (Filozof), The Creator (Yaratıcı), The Ruler (Hükümdar), The Sage (Bilge), The Explorer (Kaşif), The Rebel (Asi), The Magician (Simyacı), The Hero (Kahraman), The Outlaw (Kanun Kaçağı), The Lover (Aşık), The Jester (Soytarı), The Caregiver (Koruyucu), The Innocent (Saf), The Everyman (Sıradan Adam)
        
        LİDERLİK TİPLERİ (İş/Yönetim Psikolojisi):
        The Executive (Yönetici), The Entrepreneur (Girişimci), The Diplomat (Diplomat), The Negotiator (Müzakereci), The Reformer (Reformcu), The Perfectionist (Mükemmeliyetçi), The Achiever (Başarı Odaklı), The Challenger (Meydan Okuyan), The Peacemaker (Barışçı), The Individualist (Bireyci)
        
        ANALİTİK TİPLER (Bilişsel Profiller):
        The Detective (Dedektif), The Scientist (Bilim İnsanı), The Logician (Mantıkçı), The Observer (Gözlemci), The Investigator (Araştırmacı), The Skeptic (Şüpheci), The Rationalist (Rasyonalist), The Theorist (Teorisyen), The Problem-Solver (Çözümcü), The Systems Thinker (Sistem Düşünürü)
        
        YARATICI TİPLER (Sanatsal/Vizyoner):
        The Artist (Sanatçı), The Inventor (Mucit), The Dreamer (Hayalperest), The Idealist (İdealist), The Romantic (Romantik), The Performer (Performansçı), The Composer (Besteci), The Writer (Yazar), The Designer (Tasarımcı), The Innovator (Yenilikçi)
        
        KARANLIK TRİAD (Dark Psychology - Dikkatli Kullan):
        The Machiavellian (Makyavelist), The Narcissist (Narsist), The Psychopath (Psikopat), The Manipulator (Manipülatör), The Schemer (Entrikacı), The Predator (Avcı), The Opportunist (Fırsatçı), The Puppet Master (Kukla Ustası), The Sociopath (Sosyopat), The Dark Empath (Karanlık Empatik)
        
        SOSYAL TİPLER (Kişilerarası Profiller):
        The Lone Wolf (Yalnız Kurt), The Alpha (Alfa), The Introvert (İçe Dönük), The Extrovert (Dışa Dönük), The Empath (Empatik), The Stoic (Stoacı), The Cynic (Sinik), The Optimist (İyimser), The Realist (Gerçekçi), The Pragmatist (Pragmatist)
        
        Seçim yaparken kullanıcının cevaplarına, düşünce yapısına ve değerlerine bak. Fantezi değil, gerçek psikoloji kullan!\",
        "logic_score": 0-100 arası sayı,
        "empathy_score": 0-100 arası sayı,
        "risk_level": "LOW / MEDIUM / HIGH",
        "neuroticism": "Low / Medium / High",
        "stability": "Low / Medium / High",
        "pattern": "Stable / Normal / Erratic / Volatile",
        
        "character_match": "Kullanıcının psikolojik profiliyle EN UYUMLU karakter. AYNI KARAKTERİ TEKRAR TEKRAR VERME! Listeden rastgele değil, kişiliğe göre seç.
        
        === TARİHİ FİGÜRLER (50+) ===
        
        KOMUTANLAR/STRATEJİSTLER:
        Sun Tzu, Napolyon Bonaparte, Julius Caesar, Hannibal Barca, Cengiz Han, İskender (Alexander), Otto von Bismarck, Erwin Rommel, George Patton, Saladin, Atatürk, Khalid ibn al-Walid, Frederick the Great, Suleiman the Magnificent, Tokugawa Ieyasu, Oda Nobunaga, Miyamoto Musashi, Spartacus, William Wallace, Boudicca
        
        LİDERLER/POLİTİKACILAR:
        Winston Churchill, Abraham Lincoln, Cleopatra, Elizabeth I, Catherine the Great, Theodore Roosevelt, Mahatma Gandhi, Nelson Mandela, JFK, Margaret Thatcher, Augustus Caesar, Charlemagne, Peter the Great, Queen Victoria, Charles de Gaulle, Benjamin Franklin, Thomas Jefferson, Marcus Aurelius (Filosof-İmparator)
        
        BİLİM İNSANLARI/MUCİTLER:
        Leonardo da Vinci, Nikola Tesla, Albert Einstein, Isaac Newton, Marie Curie, Galileo Galilei, Charles Darwin, Stephen Hawking, Richard Feynman, Carl Sagan, Ada Lovelace, Alan Turing, Archimedes, Copernicus, Thomas Edison, Alexander Graham Bell, James Watt, Wright Brothers
        
        FİLOZOFLAR/DÜŞÜNÜRLER:
        Nietzsche, Machiavelli, Socrates, Plato, Aristotle, Descartes, Voltaire, Kant, Hegel, Schopenhauer, Confucius, Lao Tzu, Seneca, Epictetus, Diogenes, Kierkegaard, Sartre, Camus, Spinoza, John Locke
        
        SANATÇILAR/YAZARLAR:
        Van Gogh, Beethoven, Mozart, Shakespeare, Oscar Wilde, Edgar Allan Poe, Michelangelo, Picasso, Dali, Frida Kahlo, Da Vinci, Rembrandt, Dostoevsky, Tolstoy, Kafka, Hemingway, Lord Byron, Mary Shelley, Virginia Woolf, Orwell
        
        KAŞIFLER/MACERACILAR:
        Marco Polo, Christopher Columbus, Magellan, Vasco da Gama, Neil Armstrong, Edmund Hillary, Amelia Earhart, Jacques Cousteau, Ibn Battuta, Zheng He
        
        === KURGUSAL KARAKTERLER (50+) ===
        
        DAHI STRATEJİSTLER:
        Professor (Money Heist), Light Yagami (Death Note), Lelouch vi Britannia (Code Geass), Erwin Smith (Attack on Titan), Aizen Sosuke (Bleach), Itachi Uchiha (Naruto), Shikamaru Nara (Naruto), Johan Liebert (Monster), Moriarty, Near (Death Note), Ozymandias (Watchmen), Petyr Baelish (GoT), Varys (GoT)
        
        KARİZMATİK LİDERLER:
        Thomas Shelby (Peaky Blinders), Don Vito Corleone (Godfather), Michael Corleone, Tony Soprano, Walter White (Breaking Bad), Gus Fring, Tony Montana, Jordan Belfort, Negan (TWD), Magneto, Daenerys Targaryen, Ragnar Lothbrok (Vikings), Rollo (Vikings)
        
        KARANLIK/ANTİ-KAHRAMANLAR:
        Hannibal Lecter, Joker, V (V for Vendetta), Tyler Durden (Fight Club), Alex DeLarge (Clockwork Orange), Dexter Morgan, Frank Underwood, Deadpool, Venom, Punisher, Rorschach, John Wick, Travis Bickle, Patrick Bateman
        
        DEDEKTİFLER/ANALİSTLER:
        Sherlock Holmes, L (Death Note), Dr. House, Patrick Jane (Mentalist), Rust Cohle (True Detective), Hercule Poirot, Miss Marple, Columbo, Will Graham (Hannibal), Spencer Reid (Criminal Minds), Benoit Blanc
        
        BİLGE MENTORLAR:
        Gandalf, Dumbledore, Morpheus (Matrix), Yoda, Uncle Iroh (Avatar), Obi-Wan Kenobi, Rafiki, Mr. Miyagi, Alfred Pennyworth, Master Splinter, Albus Percival
        
        SAVAŞÇI/KAHRAMAN:
        Aragorn, Jon Snow, Geralt of Rivia, Kratos, Batman, Wolverine, Captain America, Maximus (Gladiator), Achilles, Leonidas, Conan, Mad Max, John Wick, Neo, T-800
        
        ANİME/MANGA:
        Goku, Vegeta, Naruto, Sasuke, Eren Yeager, Levi Ackerman, Spike Spiegel (Cowboy Bebop), Edward Elric, Roy Mustang, Guts (Berserk), Saitama (One Punch Man), Gon Freecss, Killua, Hisoka, Meruem
        
        DİĞER İKONİK:
        Tony Stark (Iron Man), Bruce Wayne, Tyrion Lannister, Loki, Thanos, Darth Vader, Kylo Ren, Han Solo, Jack Sparrow, Indiana Jones, James Bond, Ethan Hunt, Jason Bourne, John Constantine, Lucifer Morningstar
        
        ⚠️ ÖNEMLİ: Yukarıdaki liste sadece ÖRNEK! Sen binlerce karakteri biliyorsun. Bu listeyle SINIRLI DEĞİLSİN!
        - Tüm tarihi figürleri kullanabilirsin (antik çağdan moderne)
        - Tüm anime/manga karakterlerini kullanabilirsin (One Piece, Hunter x Hunter, Jujutsu Kaisen, Demon Slayer, My Hero Academia, Dragon Ball, Berserk, Vinland Saga, vb.)
        - Tüm film/dizi karakterlerini kullanabilirsin (Marvel, DC, Star Wars, Lord of the Rings, Game of Thrones, Breaking Bad, vb.)
        - Tüm oyun karakterlerini kullanabilirsin (God of War, Witcher, Metal Gear, Final Fantasy, Dark Souls, Elden Ring, vb.)
        - Tüm kitap karakterlerini kullanabilirsin (Dune, 1984, Harry Potter, LOTR, vb.)
        
        ASLA aynı karakteri arka arkaya verme! Her kullanıcıya benzersiz bir karakter ver. Cevaplardaki düşünce yapısına, değerlere ve davranış kalıplarına göre seç!\",
        
        "character_match_reason": "Bu karakterle neden eşleştiğinin 2-3 cümlelik DETAYLI açıklaması. Ortak özellikleri, düşünce yapısını ve davranış kalıplarını kullanıcının VERDİĞİ CEVAPLARA referans vererek belirt.",
        
        "detailed_analysis": "5-6 cümlelik kapsamlı psikolojik analiz. Kullanıcının stratejik düşünce yapısını, karar alma mekanizmalarını, duygusal kalıplarını, liderlik potansiyelini, zayıf noktalarını ve benzersiz yeteneklerini detaylı açıkla. Profesyonel ve etkileyici bir dille yaz.",
        
        "shadow_trait": "Bastırılmış karanlık yön ve stres altındaki tehlikeli eğilimlerin detaylı açıklaması (3-4 cümle). Bu kişinin çöküş senaryosu ne olabilir? Hangi tetikleyiciler onu dengesizleştirebilir?"
    }}
    
    KRİTİK: IQ SKORLAMA VE GERÇEKÇİLİK KURALLARI (ÇOK KATI UYGULA):
    
    1.  **VARSAYILAN SKOR:** Eğer cevaplar "normal", "ortalama" veya "standart" ise, IQ skorunu KESİNLİKLE **95-105** aralığında ver.
    2.  **YÜKSEK SKOR ENGELİ:** 115 ve üzeri vermek için kullanıcının cevaplarında AÇIKÇA görülen kompleks strateji, çok katmanlı düşünme veya sıra dışı bağlantılar olmalı.
    3.  **ÇOK YÜKSEK SKOR (130+) YASAĞI:** Sadece "Ben bir deha gibi düşünüyorum" diyenlere değil, cevapların İÇERİĞİNDE bunu kanıtlayanlara ver. %98 ihtimalle skor 130'un ALTINDA olmalı.
    4.  **DAĞILIM HEDEFİ:**
        -   %50 İhtimalle: 90 - 105 (Ortalama)
        -   %30 İhtimalle: 105 - 115 (Ortalama Üstü)
        -   %15 İhtimalle: 115 - 125 (Zeki)
        -   %4 İhtimalle: 125 - 135 (Üstün)
        -   %1 İhtimalle: 135+ (Dahi)

    🚨 **TROLL / SPAM / BOŞ CEVAP FİLTRESİ (EN ÖNEMLİ KURAL - ÇOK KATI UYGULA):**
    
    AŞAĞIDAKİ DURUMLARDAN HERHANGİ BİRİ VARSA TROLL OLARAK DEĞERLENDİR:
    1. Cevapların %30'undan fazlası boş veya çok kısa (1-2 kelime)
    2. Anlamsız tuş kombinasyonları ("asdasd", "qweqwe", "sadsad", "aaa", "123", "..." vb.)
    3. Aynı cevabın tekrarı (copy-paste)
    4. Alakasız veya saçma yanıtlar (örn: matematik sorusuna "muz" yazmak)
    5. Gerçekdışı abartılı iddialar ("Ben Einstein'dan zekiyim", "IQ'm 200")
    6. Emoji spam veya tek karakter cevapları
    
    TROLL TESPİT EDİLDİĞİNDE:
    -   **IQ:** 55-70 arası ver (ASLA YÜKSEK VERME!).
    -   **Archetype:** "Dijital Parazit", "Sistem Çöpü", "Kaotik Hiçlik", "Dikkat Dilencisi" veya "Boşluk Lordu".
    -   **Risk Level:** HIGH.
    -   **Character Match:** TROLLER İÇİN KARAKTER LİSTESİ (BU LİSTEDEN SEÇ!):
        {troll_list_str}
        
        KESİNLİKLE Thomas Shelby, Walter White, Professor, Sherlock, Light Yagami gibi karizmatik/zeki karakterler VERME!
    -   **Character Match Reason:** Bu kişi testi ciddiye almadı, sistemi trollemeye çalıştı. Dikkat süresi ve odaklanma kapasitesi ciddi şekilde düşük. Sorumluluk almaktan kaçınan, kolay yolu seçen bir profil.
    -   **Detailed Analysis:** Acımasız ol. Bu kişinin neden başarısız olacağını, neden ciddiye alınmayacağını, odaklanma ve disiplin eksikliğini detaylı analiz et. "Bu test bile çok zor geldiyse gerçek hayatta ne yapacaksın?" tarzında sert yorumlar ekle. Motivasyon verme, eleştir.
    -   **Shadow Trait:** "Kronik Kaçış ve Yüzeysellik". Derinlikten korkan, her şeyi hafife alan, sonra başarısızlığı başkalarına yükleyen bir profil. Gerçek potansiyelini asla keşfedemeyecek çünkü çaba göstermiyor.
    -   **logic_score:** 10-25 arası
    -   **empathy_score:** 15-30 arası
    
    ⚠️ ASLA AMA ASLA TROLL BİRİNE "THOMAS SHELBY", "PROFESSOR", "WALTER WHITE", "SHERLOCK" GİBİ COOL KARAKTERLERİ VERME! Bu karakterler GERÇEKTEN düşünerek cevap verenler için.
    
    YAPAY ZEKA OLARAK SKORLARI ŞİŞİRME! GERÇEKÇİ VE HATTA BİRAZ "CİMRİ" OL. Müşteri memnuniyeti için yüksek puan vermek YASAKTIR. Doğru analiz yap.
    
    ÖNEMLİ: Analiz metni motive edici olabilir, ancak IQ sayısı matematiksel gerçekliğe dayanmalı. Eğer TROLL ise KELEPİRCE EZ.
    
    VERİLER: {user_data}
    """
    
    try:
        # API Key alma (Önce secrets.toml, yoksa Environment Variable)
        import os
        api_key = None
        try:
            if "gemini_api_key" in st.secrets:
                api_key = st.secrets["gemini_api_key"]
        except Exception:
            pass
        
        if not api_key:
            api_key = os.getenv("gemini_api_key")
            
        if api_key:
            genai.configure(api_key=api_key)
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


def run_compatibility_analysis(user1_data: dict, user2_data: dict, lang: str):
    """İki kullanıcı arasındaki uyumluluk analizi - Özel Prompt"""
    prompt = f"""
    Sen, ilişki psikolojisi ve kişilik uyumu konusunda uzmanlaşmış bir terapist ve ilişki danışmanısın.
    İki kişinin psikolojik profillerini karşılaştırarak detaylı bir uyum analizi yapacaksın.
    
    DİL: {lang}. (Tüm yanıtları bu dilde ver).
    
    KİŞİ 1 (SEN) PROFİLİ:
    - IQ: {user1_data.get('iq_score', user1_data.get('iq', 100))}
    - Arketip: {user1_data.get('archetype', 'Bilinmiyor')}
    - Mantık Skoru: {user1_data.get('logic_score', 50)}
    - Empati Skoru: {user1_data.get('empathy_score', 50)}
    - Risk Seviyesi: {user1_data.get('risk_level', 'MEDIUM')}
    - Nevrotizm: {user1_data.get('neuroticism', 'Medium')}
    - Stabilite: {user1_data.get('stability', 'Medium')}
    - Karakter Eşleşmesi: {user1_data.get('character_match', 'Bilinmiyor')}
    - Gölge Kişilik: {user1_data.get('shadow_trait', 'Bilinmiyor')}
    
    KİŞİ 2 (PARTNER) PROFİLİ:
    - IQ: {user2_data.get('iq_score', user2_data.get('iq', 100))}
    - Arketip: {user2_data.get('archetype', 'Bilinmiyor')}
    - Mantık Skoru: {user2_data.get('logic_score', 50)}
    - Empati Skoru: {user2_data.get('empathy_score', 50)}
    - Risk Seviyesi: {user2_data.get('risk_level', 'MEDIUM')}
    - Nevrotizm: {user2_data.get('neuroticism', 'Medium')}
    - Stabilite: {user2_data.get('stability', 'Medium')}
    - Karakter Eşleşmesi: {user2_data.get('character_match', 'Bilinmiyor')}
    - Gölge Kişilik: {user2_data.get('shadow_trait', 'Bilinmiyor')}
    
    ÇIKTI FORMATI (Sadece JSON, tüm alanları eksiksiz doldur):
    {{
        "compatibility_score": "0-100 arası sayı (gerçekçi ol, %85+ çok nadir olmalı, ortalama %50-70)",
        
        "relationship_type": "Romantik Partner / Yakın Arkadaş / İş Ortağı / Entelektüel Yoldaş / Dikkatli Ol",
        
        "harmony_areas": [
            "İki kişinin doğal olarak uyumlu olduğu 3 alan (spesifik ve kişiye özel)"
        ],
        
        "user1_completes_user2": [
            "Kişi 1'in (SEN) Kişi 2'nin eksiklerini kapattığı 2-3 alan"
        ],
        
        "user2_completes_user1": [
            "Kişi 2'nin (PARTNER) Kişi 1'in eksiklerini kapattığı 2-3 alan"
        ],
        
        "recommended_activities": [
            "Birlikte yapmaları gereken 4-5 GERÇEKÇİ aktivite",
            "YASAK: 'Ada satın almak', 'Şirket kurmak', 'Dünyayı gezmek' gibi abartılar",
            "ÖRNEK: 'Strateji oyunları', 'Sessiz kafede kitap okumak', 'Doğa yürüyüşü', 'Yemek pişirmek', 'Film/dizi maratonu', 'Spor aktiviteleri', 'Podcast tartışmaları'"
        ],
        
        "avoid_topics": [
            "Uzak durmaları gereken 3-4 konu veya aktivite (ilişkiye zarar verebilecek)"
        ],
        
        "warning_signs": [
            "İlişkide dikkat edilmesi gereken 2-3 uyarı işareti"
        ],
        
        "long_term_advice": "İlişkinin uzun vadede sağlıklı kalması için 2-3 cümlelik tavsiye",
        
        "chemistry_breakdown": {{
            "intellectual": 0-100,
            "emotional": 0-100,
            "lifestyle": 0-100,
            "communication": 0-100
        }}
    }}
    
    KRİTİK KURALLAR:
    1. GERÇEKÇİ OL - Herkes %90 uyumlu değil. Normal dağılım: %45-70 arası uyum en yaygın.
    2. AKTİVİTELER ULAŞILABILIR OLMALI - Normal gelirli insanların yapabileceği şeyler.
    3. OLUMSUZ YÖNLER DE BELİRT - Sadece olumlu değil, potansiyel sorunları da söyle.
    4. SPESİFİK OL - Profillere özgü öneriler ver, genel laflar etme.
    5. YAPISAL SORUNLARI GÖR - İki yüksek ego, iki düşük stabilite gibi durumları tespit et.
    """
    
    try:
        import os
        api_key = None
        try:
            if "gemini_api_key" in st.secrets:
                api_key = st.secrets["gemini_api_key"]
        except Exception:
            pass
        
        if not api_key:
            api_key = os.getenv("gemini_api_key")
            
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_json)
            return result
        else:
            # Demo mod
            time.sleep(2)
            result = {
                "compatibility_score": "67",
                "relationship_type": "Yakın Arkadaş",
                "harmony_areas": [
                    "İkiniz de analitik düşünmeyi seviyorsunuz",
                    "Yalnız kaliteli zaman geçirme ihtiyacınız benzer",
                    "Problem çözme yaklaşımlarınız birbirini tamamlıyor"
                ],
                "user1_completes_user2": [
                    "Senin mantıksal yaklaşımın, onun duygusal kararlarında denge sağlıyor",
                    "Sakin yapın, onun stresli anlarında yatıştırıcı etki yaratıyor"
                ],
                "user2_completes_user1": [
                    "Onun sosyal enerjisi, senin içe dönük yapını dengeliyor",
                    "Spontan kararları, senin aşırı planlamacı yapını gevşetiyor"
                ],
                "recommended_activities": [
                    "Birlikte strateji oyunları oynamak (satranç, bilgisayar oyunları)",
                    "Sessiz bir kafede yan yana kitap okumak",
                    "Doğa yürüyüşleri ve piknik",
                    "Belgesel/film maratonu gecesi",
                    "Birlikte yemek pişirme denemeleri"
                ],
                "avoid_topics": [
                    "Rekabetçi oyunlar - ikiniz de kaybetmeyi zor kaldırıyorsunuz",
                    "Finansal kararları birlikte almak - farklı risk toleransları",
                    "Birbirinizin sosyal çevresine müdahale",
                    "Ani seyahat planları - biri plancı, diğeri spontan"
                ],
                "warning_signs": [
                    "İkinizin de yüksek kontrol ihtiyacı güç savaşlarına yol açabilir",
                    "Duygusal ifade farklılıkları iletişim kopukluğu yaratabilir"
                ],
                "long_term_advice": "Birbirinize alan tanımayı öğrenin. Her karar birlikte alınmak zorunda değil. Farklılıklarınızı tehdit olarak değil, zenginlik olarak görün.",
                "chemistry_breakdown": {
                    "intellectual": 78,
                    "emotional": 55,
                    "lifestyle": 62,
                    "communication": 71
                }
            }
            return result
    except Exception as e:
        err_msg = str(e)
        display_msg = f"Teknik Hata: {err_msg}"
        
        # JSON hatası ise daha anlaşılır mesaj göster
        if "Expecting" in err_msg or "JSON" in err_msg or "Extra data" in err_msg:
            display_msg = "Yapay zeka yanıtı çözümleyemedi. Rastgele veya anlamsız veri girişi yapmış olabilirsiniz."
            
        return {
            "compatibility_score": "0",
            "relationship_type": "Analiz Başarısız",
            "harmony_areas": ["Veri kalitesi yetersiz"],
            "user1_completes_user2": ["Anlaşılamadı"],
            "user2_completes_user1": ["Anlaşılamadı"],
            "recommended_activities": ["Testi anlamlı cevaplarla tekrar çözün"],
            "avoid_topics": ["Rastgele tuşlara basmak"],
            "warning_signs": [display_msg],
            "long_term_advice": "Lütfen testi tekrar, dürüst ve anlamlı cevaplarla çözün.",
            "chemistry_breakdown": {"intellectual": 0, "emotional": 0, "lifestyle": 0, "communication": 0}
        }


def show_loading():
    """Analiz sırasında gösterilen yükleme ekranı"""
    lang = st.session_state.get('language', 'TR')
    
    # Dil bazlı metinler
    texts = {
        'TR': {
            'title': 'Analiz Devam Ediyor',
            'subtitle': 'Güvenli Sunucu 0-9 // Nöral Bağlantı Şifreli',
            'progress_title': 'Bilişsel Haritalama',
            'layer': 'Katman {} / 5 İşleniyor',
            'logs': [
                'Nöral el sıkışma başlatılıyor...',
                'Psikolojik temel veriler alınıyor...',
                '> BİLİŞSEL ÖRÜNTÜLER ÇÖZÜMLÜYOR...',
                '> DAVRANIŞSAL ARKETİPLER HARİTALANIYOR...',
                '> FBI DOSYASI OLUŞTURULUYOR...'
            ]
        },
        'EN': {
            'title': 'Analysis In Progress',
            'subtitle': 'Secure Server 0-9 // Neural Link Encrypted',
            'progress_title': 'Cognitive Mapping',
            'layer': 'Processing Layer {} of 5',
            'logs': [
                'Initializing neural handshake...',
                'Fetching psychological baseline...',
                '> DECRYPTING COGNITIVE PATTERNS...',
                '> MAPPING BEHAVIORAL ARCHETYPES...',
                '> FBI DOSSIER GENERATION IN PROGRESS...'
            ]
        }
    }
    t = texts.get(lang, texts['TR'])
    
    loading_html = f'''
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    
    <script>
        // Scroll to top immediately
        window.parent.scrollTo(0, 0);
        try {{ window.parent.document.querySelector('.main').scrollTo(0, 0); }} catch(e) {{}}
        try {{ window.parent.document.querySelector('[data-testid="stAppViewContainer"]').scrollTo(0, 0); }} catch(e) {{}}
        
        // Remove existing overlay if any
        var existingOverlay = window.parent.document.getElementById("pz-loading-overlay");
        if (existingOverlay) {{ existingOverlay.remove(); }}
        
        // Create full-page overlay in PARENT document
        var overlay = document.createElement("div");
        overlay.id = "pz-loading-overlay";
        overlay.innerHTML = `
            <style>
                #pz-loading-overlay {{
                    font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
                    background-color: #050a0b;
                    color: white;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    height: 100vh;
                    z-index: 9999999;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                }}
                #pz-loading-overlay .grid-bg {{
                    background-image: linear-gradient(to right, rgba(43, 205, 238, 0.05) 1px, transparent 1px),
                                      linear-gradient(to bottom, rgba(43, 205, 238, 0.05) 1px, transparent 1px);
                    background-size: 30px 30px;
                    position: absolute;
                    inset: 0;
                    pointer-events: none;
                }}
                #pz-loading-overlay .primary {{ color: #2bcdee; }}
                @keyframes pz-pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
                @keyframes pz-float {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-10px); }} }}
                @keyframes pz-progress {{ 0% {{ width: 0%; }} 100% {{ width: 100%; }} }}
                @keyframes pz-scanline {{ 0% {{ top: -100%; }} 100% {{ top: 100%; }} }}
                @keyframes pz-blink {{ 50% {{ border-color: transparent; }} }}
                @keyframes pz-fadeIn {{ to {{ opacity: 1; }} }}
                #pz-loading-overlay .animate-pulse {{ animation: pz-pulse 2s infinite; }}
                #pz-loading-overlay .animate-float {{ animation: pz-float 3s ease-in-out infinite; }}
                #pz-loading-overlay .scanline {{
                    position: absolute;
                    width: 100%;
                    height: 2px;
                    background: linear-gradient(to right, transparent, rgba(43, 205, 238, 0.3), transparent);
                    animation: pz-scanline 2s linear infinite;
                }}
                #pz-loading-overlay .brain-glow {{
                    width: 120px;
                    height: 120px;
                    background: radial-gradient(circle, rgba(43, 205, 238, 0.3) 0%, transparent 70%);
                    border-radius: 50%;
                    filter: blur(20px);
                    animation: pz-pulse 2s ease-in-out infinite;
                }}
                #pz-loading-overlay .terminal-log p {{
                    margin: 4px 0;
                    opacity: 0;
                    animation: pz-fadeIn 0.5s forwards;
                }}
                #pz-loading-overlay .terminal-log p:nth-child(1) {{ animation-delay: 0.5s; }}
                #pz-loading-overlay .terminal-log p:nth-child(2) {{ animation-delay: 1.5s; }}
                #pz-loading-overlay .terminal-log p:nth-child(3) {{ animation-delay: 2.5s; }}
                #pz-loading-overlay .terminal-log p:nth-child(4) {{ animation-delay: 3.5s; }}
                #pz-loading-overlay .terminal-log p:nth-child(5) {{ animation-delay: 4.5s; }}
                #pz-loading-overlay .progress-bar {{
                    height: 6px;
                    background: rgba(255,255,255,0.05);
                    border-radius: 3px;
                    overflow: hidden;
                }}
                #pz-loading-overlay .progress-fill {{
                    height: 100%;
                    background: #2bcdee;
                    box-shadow: 0 0 10px #2bcdee;
                    animation: pz-progress 5s ease-out forwards;
                }}
                #pz-loading-overlay .cursor-blink {{
                    display: inline-block;
                    width: 8px;
                    height: 16px;
                    background: #2bcdee;
                    animation: pz-blink 1s step-end infinite;
                }}
            </style>
            
            <div class="grid-bg"></div>
            <div class="scanline"></div>
            
            <!-- Top Bar -->
            <div style="display: flex; align-items: center; padding: 16px; justify-content: space-between;">
                <span class="material-symbols-outlined primary" style="font-size: 24px;">shield_lock</span>
                <span style="font-size: 10px; letter-spacing: 0.4em; opacity: 0.8; text-transform: uppercase;">Project Zero</span>
                <span class="material-symbols-outlined primary" style="font-size: 24px;">memory</span>
            </div>
            
            <!-- Main Content -->
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; flex-grow: 1;">
                
                <!-- Brain Visual -->
                <div style="position: relative; width: 200px; height: 200px; margin-bottom: 32px;">
                    <div style="position: absolute; inset: 0; border: 1px solid rgba(43, 205, 238, 0.2); border-radius: 50%;" class="animate-pulse"></div>
                    <div style="position: absolute; inset: 20px; border: 1px solid rgba(43, 205, 238, 0.15); border-radius: 50%;" class="animate-pulse"></div>
                    <div style="display: flex; align-items: center; justify-content: center; width: 100%; height: 100%;">
                        <div class="brain-glow"></div>
                        <span class="material-symbols-outlined animate-float" style="position: absolute; font-size: 80px; color: #2bcdee;">psychology</span>
                    </div>
                    <div style="position: absolute; top: -10px; left: 50%; transform: translateX(-50%); background: rgba(43, 205, 238, 0.2); border: 1px solid rgba(43, 205, 238, 0.4); border-radius: 4px; padding: 4px 8px; font-size: 9px; color: #2bcdee; font-family: monospace; letter-spacing: 0.1em;">
                        SYNAPSE_LINK: STABLE
                    </div>
                </div>
                
                <!-- Title -->
                <h2 style="color: #2bcdee; letter-spacing: 0.2em; font-size: 20px; font-weight: 700; text-transform: uppercase; margin: 0 0 4px 0;">{t['title']}</h2>
                <p style="color: rgba(157, 180, 185, 0.6); font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; margin: 0 0 32px 0;">{t['subtitle']}</p>
                
                <!-- Terminal Log -->
                <div style="width: 100%; max-width: 400px; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 16px; margin-bottom: 32px; font-family: 'JetBrains Mono', monospace; font-size: 11px; line-height: 1.6;" class="terminal-log">
                    <p style="color: rgba(255,255,255,0.4); font-style: italic;">{t['logs'][0]}</p>
                    <p style="color: rgba(255,255,255,0.4);">{t['logs'][1]}</p>
                    <p style="color: rgba(43, 205, 238, 0.8);">{t['logs'][2]}</p>
                    <p style="color: rgba(43, 205, 238, 0.8);">{t['logs'][3]}</p>
                    <p style="color: rgba(255,255,255,0.9);">{t['logs'][4]}</p>
                    <div style="display: flex; align-items: center; gap: 4px; margin-top: 8px;">
                        <span style="color: #2bcdee;">&gt;</span>
                        <span class="cursor-blink"></span>
                    </div>
                </div>
                
                <!-- Progress Section -->
                <div style="width: 100%; max-width: 400px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 12px;">
                        <div>
                            <p style="color: white; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin: 0;">{t['progress_title']}</p>
                            <p style="color: rgba(43, 205, 238, 0.6); font-size: 10px; text-transform: uppercase; margin: 4px 0 0 0;">{t['layer'].format(4)}</p>
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 9px; color: rgba(255,255,255,0.3); text-transform: uppercase; letter-spacing: 0.05em;">
                        <span>Alpha State: 14.2Hz</span>
                        <span>Buffer: 1024kbps</span>
                        <span>Nodes: 4,092</span>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="padding: 16px; display: flex; justify-content: space-between; align-items: center; opacity: 0.3; border-top: 1px solid rgba(255,255,255,0.05);">
                <span style="font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 700;">Project Zero UI v4.0.2</span>
                <div style="display: flex; gap: 16px;">
                    <span class="material-symbols-outlined" style="font-size: 14px;">fingerprint</span>
                    <span class="material-symbols-outlined" style="font-size: 14px;">distance</span>
                </div>
            </div>
        `;
        
        window.parent.document.body.appendChild(overlay);
    </script>
    '''
    
    # Yükleme ekranını göster (sadece JS çalıştırmak için, görünür içerik yok)
    components.html(loading_html, height=0, width=0)
    
    # Analizi başlat
    dur = st.session_state.get('quiz_duration', 0)
    st.session_state['analysis_result'] = run_fbi_analysis(st.session_state['user_data'], st.session_state['language'], dur)
    
    # Analiz tamamlandı, sonuç sayfasına yönlendir
    st.session_state['page'] = 'result'
    st.rerun()


def show_result():
    """Sonuç ekranı - Detaylı FBI Raporu (Video izleme kaldırıldı)"""
    t = CONTENT[st.session_state['language']]['RESULT']
    
    # Loading overlay'ı temizle (varsa)
    cleanup_js = """
    <script>
        var overlay = window.parent.document.getElementById("pz-loading-overlay");
        if (overlay) { overlay.remove(); }
    </script>
    """
    components.html(cleanup_js, height=0, width=0)
    
    # Video izleme zorunluluğu kaldırıldı - direkt sonuç göster
    
    # Analiz yap
    if st.session_state['analysis_result'] is None:
        with st.spinner("🧠 NÖRAL DESENLER ÇÖZÜMLENİYOR..."):
            dur = st.session_state.get('quiz_duration', 0)
            st.session_state['analysis_result'] = run_fbi_analysis(st.session_state['user_data'], st.session_state['language'], dur)
    
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
    
    # Skoru leaderboard'a kaydet (sadece bir kez)
    if not st.session_state.get('score_saved', False):
        username = st.session_state.get('username', 'Anonymous')
        country = st.session_state.get('user_country', '')
        city = st.session_state.get('user_city', '')
        try:
            iq_int = int(iq)
            save_score_to_leaderboard(username, iq_int, character_match, country, city)
            # Uyumluluk analizi için tam veriyi kaydet
            try: save_user_analysis(username, res)
            except: pass
            
            st.session_state['score_saved'] = True
        except:
            pass
    
    # Kullanıcının sıralamasını hesapla
    user_rank = None
    total_users = 0
    try:
        leaderboard = get_leaderboard(1000)  # Tüm kullanıcıları al
        total_users = len(leaderboard)
        if total_users > 0:
            iq_int = int(iq)
            # Kullanıcıdan yüksek skorlu kaç kişi var
            higher_scores = sum(1 for entry in leaderboard if entry.get('iq_score', 0) > iq_int)
            user_rank = higher_scores + 1
    except:
        pass
    
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
                    
                    <!-- Ranking Card -->
                    <div style="background: linear-gradient(135deg, #1a2a15 0%, #1c2426 100%); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative;">
                        <div style="position: absolute; right: -20px; top: -20px; width: 80px; height: 80px; background: rgba(34, 197, 94, 0.1); border-radius: 50%; filter: blur(25px);"></div>
                        <span class="material-symbols-outlined" style="color: #22c55e; font-size: 32px; margin-bottom: 8px;">leaderboard</span>
                        <span style="font-size: 10px; color: #9eb2b7; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; letter-spacing: 0.1em;">DÜNYA SIRALAMAN</span>
                        <div style="display: flex; align-items: baseline; gap: 4px; margin-top: 8px;">
                            <span style="font-size: 36px; font-weight: 800; color: #22c55e;">#{user_rank if user_rank else '?'}</span>
                            <span style="font-size: 14px; color: #9eb2b7; font-family: 'JetBrains Mono', monospace;">/ {total_users if total_users else '?'}</span>
                        </div>
                        <p style="font-size: 10px; color: #9eb2b7; font-family: 'JetBrains Mono', monospace; margin-top: 8px; text-align: center;">
                            📍 {st.session_state.get('user_city', '')}
                        </p>
                    </div>
                </div>
                
                <!-- Metrics Row -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                    
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
    try:
        is_admin = st.secrets.get("admin_mode", False)
    except Exception:
        is_admin = False
    
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
        # Uyumluluk Testi Butonu
        if st.button("❤️ UYUMLULUK TESTİ", use_container_width=True, type="primary"):
            st.session_state['page'] = 'compatibility_menu'
            st.rerun()
            
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        if st.button(f"🗑️ {t['BTN_PURGE']}", use_container_width=True):
            st.session_state['page'] = 'landing'
            st.session_state['user_data'] = {}
            st.session_state['analysis_result'] = None
            st.rerun()


def show_compatibility_menu():
    """Uyumluluk menüsü - Partner kullanıcı adı girme"""
    st.markdown("""
    <style>
        .compat-container {
            min-height: 100vh;
            background: #0b0e19;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .profile-card {
            background: rgba(28, 36, 38, 0.6);
            border: 1px solid rgba(0, 229, 255, 0.2);
            border-radius: 12px;
            padding: 24px;
            width: 100%;
            max-width: 400px;
            margin-bottom: 24px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    components.html("""
    <link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@700;900&family=JetBrains+Mono&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <div style="text-align: center; font-family: 'Epilogue', sans-serif; padding: 40px 20px;">
        <div style="display: inline-flex; align-items: center; gap: 12px; margin-bottom: 16px;">
            <span class="material-symbols-outlined" style="color: #00E5FF; font-size: 32px; filter: drop-shadow(0 0 8px rgba(0, 229, 255, 0.5));">sync_alt</span>
        </div>
        <h1 style="color: #00E5FF; font-size: 22px; margin: 0; text-transform: uppercase; letter-spacing: 0.2em; font-weight: 900;">Nöral Senkronizasyon</h1>
        <p style="color: rgba(255,255,255,0.5); font-size: 11px; margin: 12px 0 0 0; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.1em; text-transform: uppercase;">// İki zihin arasındaki bağlantıyı analiz et</p>
    </div>
    """, height=140)

    # Kullanıcının kendi profili
    username = st.session_state.get('username', 'Bilinmiyor')
    
    col1, col2, col3 = st.columns([0.1, 2, 0.1])
    with col2:
        # Kendi kartı
        st.markdown(f"""
        <div class="profile-card">
            <div style="font-size: 10px; color: #00E5FF; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">Senin Profilin</div>
            <div style="font-size: 18px; color: white; font-weight: bold;">@{username}</div>
            <div style="font-size: 11px; color: rgba(255,255,255,0.5);">Verilerin analiz sisteminde yüklü</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin: 20px 0; position: relative;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 80px; height: 80px; background: rgba(0, 229, 255, 0.1); border: 2px solid rgba(0, 229, 255, 0.3); border-radius: 50%; position: relative;">
                <span class="material-symbols-outlined" style="color: #00E5FF; font-size: 36px; filter: drop-shadow(0 0 10px rgba(0, 229, 255, 0.5)); animation: linkPulse 2s infinite;">link</span>
                <div style="position: absolute; inset: -8px; border: 1px dashed rgba(0, 229, 255, 0.2); border-radius: 50%; animation: spin 10s linear infinite;"></div>
            </div>
            <div style="margin-top: 12px; font-family: 'JetBrains Mono', monospace; font-size: 10px; color: rgba(0, 229, 255, 0.6); text-transform: uppercase; letter-spacing: 0.15em;">Neural Sync Ready</div>
        </div>
        <style>
            @keyframes linkPulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.1); opacity: 0.8; } }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
        """, unsafe_allow_html=True)
        
        # Partner girişi
        partner_username = st.text_input("Partnerin Kullanıcı Adı", placeholder="Partnerinin kullanıcı adını gir...", help="Partnerin de bu testi kendi cihazında çözmüş ve kullanıcı adını kaydetmiş olmalı.")
        
        if st.session_state.get('compatibility_error'):
            st.error(st.session_state['compatibility_error'])
        
        if st.button("🧬 ANALİZİ BAŞLAT", type="primary", use_container_width=True):
            if not partner_username:
                st.session_state['compatibility_error'] = "Lütfen bir kullanıcı adı girin."
                st.rerun()
            elif partner_username.lower() == str(username).lower():
                st.session_state['compatibility_error'] = "Kendinle uyumluluk testi yapamazsın :)"
                st.rerun()
            else:
                st.session_state['compatibility_error'] = None
                with st.spinner("Partner verileri aranıyor..."):
                    partner_data = get_user_analysis(partner_username)
                    
                    if partner_data:
                        st.session_state['compatibility_partner'] = partner_data
                        # Analizi çalıştır
                        with st.spinner("İlişki dinamikleri hesaplanıyor..."):
                            user_data = st.session_state.get('analysis_result', {})
                            # Eğer sonuç yoksa DB'den çek
                            if not user_data or not user_data.get('iq'): 
                                user_data = get_user_analysis(username)
                            
                            if user_data:
                                comp_result = run_compatibility_analysis(user_data, partner_data, st.session_state['language'])
                                st.session_state['compatibility_result'] = comp_result
                                st.session_state['page'] = 'compatibility_result'
                                st.rerun()
                            else:
                                st.error("Senin verilerine ulaşılamadı. Lütfen önce testi tamamla.")
                    else:
                        st.session_state['compatibility_error'] = f"'{partner_username}' kullanıcısı bulunamadı. Testi çözüp sonuç ekranına geldiğinden emin ol."
                        st.rerun()
                        
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        if st.button("← Geri Dön", use_container_width=True):
            st.session_state['page'] = 'result'
            st.rerun()

def show_compatibility_result():
    """Uyumluluk Testi Sonuç Ekranı"""
    res = st.session_state.get('compatibility_result')
    if not res:
        st.session_state['page'] = 'compatibility_menu'
        st.rerun()
        return

    # Değerler
    score = res.get('compatibility_score', 50)
    try: score = int(score) 
    except: score = 50
    
    score_color = "#22c55e" if score > 75 else ("#f59e0b" if score > 50 else "#ef4444")
    
    # CSS
    st.markdown(f"""
    <style>
        .compat-score {{
            font-size: 64px;
            font-weight: 800;
            color: {score_color};
            text-shadow: 0 0 20px {score_color}40;
            line-height: 1;
        }}
        .compat-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: rgba(255,255,255,0.5);
            letter-spacing: 0.2em;
            text-transform: uppercase;
        }}
        .compat-card {{
            background: rgba(17, 30, 33, 0.8);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
        }}
        .section-title {{
            font-family: 'Epilogue', sans-serif;
            font-size: 16px;
            color: #00E5FF;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 12px;
            border-bottom: 1px solid rgba(0,229,255,0.2);
            padding-bottom: 8px;
        }}
        .list-item {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 8px;
            font-size: 14px;
            color: #e2e8f0;
            font-family: 'Manrope', sans-serif;
        }}
        .marker {{
            color: #00E5FF;
            font-weight: bold;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 30px 0;">
        <div class="compat-label">ANALİZ TAMAMLANDI</div>
        <h1 style="font-family: 'Epilogue', sans-serif; font-size: 24px; margin: 8px 0;">UYUMLULUK RAPORU</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Skor
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <div class="compat-score">{score}%</div>
            <div style="font-size: 18px; color: {score_color}; font-weight: bold; margin-top: 8px;">{res.get('relationship_type', 'ANALİZ EDİLİYOR')}</div>
        </div>
        """, unsafe_allow_html=True)

    # Detaylar
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.markdown(f"""
        <div class="compat-card">
            <div class="section-title">🌱 BİRLİKTE GÜÇLÜSÜNÜZ</div>
            {''.join([f'<div class="list-item"><span class="marker">✓</span>{item}</div>' for item in res.get('harmony_areas', [])])}
        </div>
        
        <div class="compat-card">
            <div class="section-title">🧩 SEN ONU NASIL TAMAMLARSIN</div>
            {''.join([f'<div class="list-item"><span class="marker">•</span>{item}</div>' for item in res.get('user1_completes_user2', [])])}
        </div>
        
        <div class="compat-card" style="border-color: rgba(34, 197, 94, 0.3);">
            <div class="section-title" style="color: #22c55e; border-color: rgba(34, 197, 94, 0.3);">✅ BİRLİKTE YAPIN</div>
            {''.join([f'<div class="list-item"><span class="marker" style="color: #22c55e;">+</span>{item}</div>' for item in res.get('recommended_activities', [])])}
        </div>
        """, unsafe_allow_html=True)
        
    with col_r:
        st.markdown(f"""
        <div class="compat-card">
            <div class="section-title">⚠️ DİKKAT EDİN</div>
             {''.join([f'<div class="list-item"><span class="marker" style="color: #f59e0b;">!</span>{item}</div>' for item in res.get('warning_signs', [])])}
        </div>
        
        <div class="compat-card">
            <div class="section-title">🧩 O SENİ NASIL TAMAMLAR</div>
             {''.join([f'<div class="list-item"><span class="marker">•</span>{item}</div>' for item in res.get('user2_completes_user1', [])])}
        </div>
        
        <div class="compat-card" style="border-color: rgba(239, 68, 68, 0.3);">
            <div class="section-title" style="color: #ef4444; border-color: rgba(239, 68, 68, 0.3);">⛔ UZAK DURUN</div>
            {''.join([f'<div class="list-item"><span class="marker" style="color: #ef4444;">x</span>{item}</div>' for item in res.get('avoid_topics', [])])}
        </div>
        """, unsafe_allow_html=True)
        
    # Kimya (Progress Bar)
    chem = res.get('chemistry_breakdown', {})
    st.markdown("""
    <div class="compat-card">
        <div class="section-title">⚗️ KİMYA ANALİZİ</div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Entelektüel", f"{chem.get('intellectual', 50)}%")
    c1.progress(chem.get('intellectual', 50) / 100)
    
    c2.metric("Duygusal", f"{chem.get('emotional', 50)}%")
    c2.progress(chem.get('emotional', 50) / 100)
    
    c3.metric("Yaşam Tarzı", f"{chem.get('lifestyle', 50)}%")
    c3.progress(chem.get('lifestyle', 50) / 100)
    
    c4.metric("İletişim", f"{chem.get('communication', 50)}%")
    c4.progress(chem.get('communication', 50) / 100)
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    if st.button("← Ana Ekrana Dön", use_container_width=True):
        st.session_state['page'] = 'landing'
        st.session_state['compatibility_result'] = None
        st.session_state['analysis_result'] = None
        st.session_state['user_data'] = {}
        st.rerun()


def show_leaderboard():
    """Şık Leaderboard Sayfası"""
    lang = st.session_state.get('language', 'TR')
    
    # Metinler
    txt = {
        'back': "← Geri" if lang == 'TR' else "← Back",
        'title': "🏆 LİDERLİK TABLOSU" if lang == 'TR' else "🏆 LEADERBOARD",
        'sub': "En Zeki 20 Zihin" if lang == 'TR' else "Top 20 Minds",
        'load': "Sıralama yükleniyor..." if lang == 'TR' else "Loading rank...",
        'empty': "Henüz veri yok." if lang == 'TR' else "No data yet.",
        'you': "(SEN)" if lang == 'TR' else "(YOU)"
    }
    
    st.markdown("""
    <style>
        .lb-container {
            max-width: 600px;
            margin: 0 auto;
        }
        .lb-header {
            text-align: center;
            padding: 40px 0 20px 0;
        }
        .lb-title {
            font-family: 'Epilogue', sans-serif;
            font-size: 24px;
            color: #FFD700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 8px;
            text-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
        }
        .lb-row {
            display: flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            transition: all 0.3s ease;
        }
        .lb-row:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.1);
        }
        .lb-rank {
            font-family: 'JetBrains Mono', monospace;
            font-size: 18px;
            font-weight: bold;
            color: rgba(255, 255, 255, 0.4);
            width: 40px;
            text-align: center;
        }
        .rank-1 { color: #FFD700; text-shadow: 0 0 10px rgba(255,215,0,0.5); font-size: 24px; }
        .rank-2 { color: #C0C0C0; text-shadow: 0 0 10px rgba(192,192,192,0.5); font-size: 22px; }
        .rank-3 { color: #CD7F32; text-shadow: 0 0 10px rgba(205,127,50,0.5); font-size: 20px; }
        
        .lb-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #00E5FF, #2979FF);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            margin: 0 16px;
            font-size: 18px;
        }
        .lb-info {
            flex-grow: 1;
        }
        .lb-name {
            color: white;
            font-weight: 600;
            font-size: 16px;
        }
        .lb-char {
            color: rgba(255, 255, 255, 0.5);
            font-size: 12px;
        }
        .lb-score {
            font-family: 'JetBrains Mono', monospace;
            font-size: 20px;
            font-weight: 800;
            color: #00E5FF;
        }
        .user-row {
            border-color: #00E5FF;
            background: rgba(0, 229, 255, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Geri Dön Butonu (Üstte)
    if st.button(txt['back'], key="lb_back_top"):
        st.session_state['page'] = 'landing'
        st.rerun()

    st.markdown(f"""
    <div class='lb-header'>
        <div class='lb-title'>{txt['title']}</div>
        <div style='color: rgba(255,255,255,0.6); font-size: 14px;'>{txt['sub']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner(txt['load']):
        data = get_leaderboard(limit=20)
        
        if not data:
            st.info(txt['empty'])
        else:
            st.markdown("<div class='lb-container'>", unsafe_allow_html=True)
            
            for i, entry in enumerate(data):
                rank = i + 1
                rank_class = f"rank-{rank}" if rank <= 3 else ""
                rank_display = ["🥇", "🥈", "🥉"][i] if rank <= 3 else f"#{rank}"
                
                username = str(entry.get('username', 'Anonymous'))[:20]
                initial = username[0].upper() if username else "?"
                score = entry.get('iq_score', 0)
                character = entry.get('character_name', '')
                
                # Mevcut kullanıcıyı işaretle
                username_val = st.session_state.get('username')
                current_user = str(username_val).lower() if username_val else ""
                is_me = username.lower() == current_user if current_user else False
                row_class = "user-row" if is_me else ""
                
                html = f"""
                <div class='lb-row {row_class}'>
                    <div class='lb-rank {rank_class}'>{rank_display}</div>
                    <div class='lb-avatar'>{initial}</div>
                    <div class='lb-info'>
                        <div class='lb-name'>{username} {" " + txt['you'] if is_me else ""}</div>
                        <div class='lb-char'>{character}</div>
                    </div>
                    <div class='lb-score'>{score}</div>
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)
            
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)


# ==========================================
# 6. ROUTER
# ==========================================
PG = st.session_state['page']

if PG == 'landing':
    show_landing()
elif PG == 'username':
    show_username()
elif PG == 'quiz':
    show_quiz()
elif PG == 'paywall':
    show_paywall()
elif PG == 'loading':
    show_loading()
elif PG == 'result':
    show_result()
elif PG == 'compatibility_menu':
    show_compatibility_menu()
elif PG == 'compatibility_result':
    show_compatibility_result()
elif PG == 'leaderboard':
    show_leaderboard()