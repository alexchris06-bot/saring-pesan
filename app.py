import joblib
import re
import streamlit as st


# Helper function untuk merender HTML
def render_html(html_str):
  clean_html = re.sub(r'\s+', ' ', html_str).strip()
  st.markdown(clean_html, unsafe_allow_html=True)


# ==========================================
# 1. Konfigurasi Halaman & CSS RETRO SYNTHWAVE
# ==========================================
st.set_page_config(
    page_title='SARINGPESAN // GX-CYBER', page_icon='👾', layout='centered'
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Silkscreen:wght@400;700&display=swap');

    @keyframes moveStarfield {
        0% { background-position: 0 0, 0 0, 0 0, 0 0; }
        100% { background-position: 400px 400px, -300px 600px, 200px -400px, 0 100%; }
    }

    .stApp {
        background-color: #0d0714 !important;
        background-image: 
            radial-gradient(2px 2px at 20px 30px, #ff007f, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 80px 120px, #a855f7, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 150px 60px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 220px 180px, #e0aaff, rgba(0,0,0,0));
        background-repeat: repeat;
        background-size: 300px 300px;
        animation: moveStarfield 25s linear infinite;
        font-family: 'Silkscreen', cursive, sans-serif;
        color: #d8b4fe;
    }

    .main {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 100vh !important;
    }

    .block-container {
        max-width: 720px !important;
        padding: 2rem !important;
        margin: auto !important;
        background: #1a0f2b !important;
        border: 3px solid #ff007f !important;
        border-radius: 0px !important;
        box-shadow: 6px 6px 0px #7b2cbf, -2px -2px 0px #06030a !important;
        position: relative !important;
        z-index: 10 !important;
    }

    h1 {
        color: #ff007f !important;
        font-family: 'Press Start 2P', cursive !important;
        font-size: 2.2rem !important;
        text-transform: uppercase;
        text-align: center;
        letter-spacing: -1px;
        margin-bottom: 8px !important;
        text-shadow: 3px 3px 0px #7b2cbf;
    }

    .subtitle {
        color: #c77dff;
        font-family: 'Silkscreen', cursive;
        text-align: center;
        font-size: 0.85rem;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }

    .stTextArea label, .stTextArea label p, div[data-testid="stWidgetLabel"] p {
        font-family: 'Press Start 2P', cursive !important;
        color: #ff007f !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.5px !important;
        line-height: 1.5 !important;
    }

    .stTextArea textarea {
        background-color: #0a0512 !important;
        color: #e0aaff !important;
        border: 2px solid #a855f7 !important;
        border-radius: 0px !important;
        font-family: 'Silkscreen', cursive !important;
        font-size: 0.95rem !important;
        box-shadow: inset 3px 3px 0px rgba(0, 0, 0, 0.8);
    }
    .stTextArea textarea:focus {
        border-color: #ff007f !important;
        box-shadow: inset 3px 3px 0px rgba(0, 0, 0, 0.8), 0 0 8px rgba(255, 0, 127, 0.5) !important;
    }

    .stButton > button {
        width: 100% !important;
        background: #ff007f !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 0px !important;
        padding: 16px 20px !important;
        box-shadow: 4px 4px 0px #7b2cbf !important;
        margin-top: 15px;
        transition: all 0.1s ease !important;
    }

    .stButton > button, .stButton > button p, .stButton > button span, .stButton > button div {
        font-family: 'Press Start 2P', cursive !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        color: #ffffff !important;
    }

    .stButton > button:hover, .stButton > button:hover p, .stButton > button:hover span {
        background: #9d4edd !important;
        color: #ffffff !important;
        box-shadow: 4px 4px 0px #ff007f !important;
        cursor: pointer;
    }

    .cyber-card-danger {
        background-color: #2a081a;
        border: 2px solid #ff007f;
        box-shadow: 4px 4px 0px #7b2cbf;
        padding: 18px;
        margin-top: 20px;
        color: #ff80bf;
        font-family: 'Silkscreen', cursive;
    }

    .cyber-card-safe {
        background-color: #0f1c24;
        border: 2px solid #00f5d4;
        box-shadow: 4px 4px 0px #7b2cbf;
        padding: 18px;
        margin-top: 20px;
        color: #80ffe8;
        font-family: 'Silkscreen', cursive;
    }

    hr {
        border: none;
        border-top: 2px dashed #a855f7 !important;
        margin: 20px 0;
        opacity: 0.5;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. Whitelist Domain & Normalisasi Teks
# ==========================================
DOMAIN_RESMI = [
    'tsel.me',
    'telkomsel.com',
    'telkomsel.co.id',
    'isat.me',
    'indosatooredoo.com',
    'xl.co.id',
    'axis.co.id',
    'tri.co.id',
    'smartfren.com',
    'bca.co.id',
    'bri.co.id',
    'mandiri.co.id',
    'bni.co.id',
    'cimbniaga.co.id',
    'gojek.com',
    'grab.com',
    'tokopedia.com',
    'shopee.co.id',
    'bukalapak.com',
    'wingstop.co.id',
]


def normalisasi_leetspeak(teks):
  # Translasi angka kamuflase menjadi huruf (leetspeak -> kata baku)
  leet_map = {
      '0': 'o',
      '1': 'i',
      '3': 'e',
      '4': 'a',
      '5': 's',
      '7': 't',
      '8': 'b',
  }
  kata_kata = teks.split()
  hasil = []

  for kata in kata_kata:
    # Jika kata mengandung percampuran angka & huruf (contoh: s1tus, jud1, g4cor)
    if any(c.isdigit() for c in kata) and any(c.isalpha() for c in kata):
      kata_baru = ''.join(leet_map.get(c, c) for c in kata)
      hasil.append(kata_baru)
    else:
      hasil.append(kata)

  return ' '.join(hasil)


def bersihkan_teks(teks):
  teks_awal = str(teks).lower()

  # Deteksi file berbahaya (.apk)
  ada_apk = bool(re.search(r'\b\S+\.apk\b', teks_awal))

  # Extract URL & Whitelist Check
  urls = re.findall(
      r'https?://\S+|www\.\S+|\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/[^\s]*', teks_awal
  )
  ada_link_resmi = any(
      any(domain in url for domain in DOMAIN_RESMI) for url in urls
  )

  # Normalisasi Leetspeak (angka kamuflase)
  teks_norm = normalisasi_leetspeak(teks_awal)

  # Preprocessing teks untuk Machine Learning
  teks_bersih = re.sub(r'[^a-zA-Z\s]', ' ', teks_norm)
  teks_bersih = re.sub(r'\s+', ' ', teks_bersih).strip()

  return teks_bersih, ada_apk, ada_link_resmi


# ==========================================
# 3. Load Model AI
# ==========================================
@st.cache_resource
def load_model():
  model = joblib.load('model_naive_bayes.pkl')
  vectorizer = joblib.load('vectorizer_tfidf.pkl')
  return model, vectorizer


try:
  model, vectorizer = load_model()
except Exception:
  st.error(
      '❌ [SYSTEM ERROR] Model gagal dimuat. Jalankan `python train.py` dulu!'
  )
  st.stop()

# ==========================================
# 4. Antarmuka UI
# ==========================================
st.markdown('<h1>SARINGPESAN</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">[ SISTEM KLASIFIKASI ANCAMAN PESAN PENIPUAN ]</div>',
    unsafe_allow_html=True,
)

pesan_input = st.text_area(
    'INPUT PESAN MENCURIGAKAN:',
    height=130,
    placeholder='TEMPELKAN PESAN YANG INGIN DIANALISIS DI SINI...',
)

if st.button('MULAI PEMINDAIAN'):
  if not pesan_input.strip():
    st.warning('⚠️ INPUT EMPTY! Masukkan pesan terlebih dahulu.')
  else:
    pesan_bersih, punya_apk, punya_link_resmi = bersihkan_teks(pesan_input)

    # Layer 1: Rule-Based Khusus APK & Whitelist Domain Utama
    if punya_apk:
      prediksi = 'penipuan'
      prob_penipuan = 99.99
      prob_aman = 0.01
      alasan_rule = 'Terdeteksi lampiran file berbahaya (.apk)'
    elif punya_link_resmi:
      prediksi = 'aman'
      prob_aman = 99.85
      prob_penipuan = 0.15
      alasan_rule = 'Terdeteksi tautan domain resmi terverifikasi'
    # Layer 2: Machine Learning Model (Untuk Semua Teks Biasa & Link Umum)
    else:
      alasan_rule = 'Klasifikasi Murni Machine Learning (Naive Bayes)'
      X_input = vectorizer.transform([pesan_bersih])
      probabilitas = model.predict_proba(X_input)[0]

      kelas_model = [str(c).lower() for c in list(model.classes_)]

      idx_aman = 0
      idx_penipuan = 1

      for i, c in enumerate(kelas_model):
        if c in ['aman', 'ham', 'normal', '0', '0.0']:
          idx_aman = i
        elif c in ['penipuan', 'spam', '1', '1.0', 'phishing']:
          idx_penipuan = i

      prob_aman = probabilitas[idx_aman] * 100
      prob_penipuan = probabilitas[idx_penipuan] * 100

      if prob_penipuan > prob_aman:
        prediksi = 'penipuan'
      else:
        prediksi = 'aman'

    skor_keyakinan = prob_penipuan if prediksi == 'penipuan' else prob_aman

    st.markdown('<hr>', unsafe_allow_html=True)

    # GRAFIK PROGRESS BAR
    html_chart = f"""
        <div style="background-color: #0a0512; border: 2px solid #a855f7; padding: 15px; margin-top: 15px; font-family: 'Silkscreen', cursive;">
            <div style="color: #ff007f; font-weight: bold; margin-bottom: 15px; font-size: 0.85rem;">>>> SKOR PROBABILITAS:</div>
            
            <div style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 6px; color: #00f5d4;">
                    <span>🛡️ AMAN / RESMI</span>
                    <span>{prob_aman:.2f}%</span>
                </div>
                <div style="background-color: #1a0f2b; border: 2px solid #00f5d4; height: 18px; padding: 2px;">
                    <div style="background-color: #00f5d4; width: {prob_aman}%; height: 100%;"></div>
                </div>
            </div>

            <div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 6px; color: #ff007f;">
                    <span>🚨 PENIPUAN / PHISHING</span>
                    <span>{prob_penipuan:.2f}%</span>
                </div>
                <div style="background-color: #1a0f2b; border: 2px solid #ff007f; height: 18px; padding: 2px;">
                    <div style="background-color: #ff007f; width: {prob_penipuan}%; height: 100%;"></div>
                </div>
            </div>
        </div>
        """
    render_html(html_chart)

    # KARTU HASIL
    if prediksi == 'penipuan':
      html_card = f"""
            <div class="cyber-card-danger">
                <h3 style="color: #ff007f; margin-top: 0; font-family: 'Press Start 2P', cursive; font-size: 0.85rem; line-height: 1.5;">🚨 TERDETEKSI ANCAMAN: PENIPUAN</h3>
                <p style="font-size: 0.85rem;">TINGKAT KEYAKINAN: <b style="color: #ff007f; font-size: 1rem;">{skor_keyakinan:.2f}%</b></p>
                <hr>
                <p style="font-size: 0.8rem;"><b>TINDAKAN YANG DISARANKAN:</b></p>
                <ul style="font-size: 0.8rem; padding-left: 20px;">
                    <li>Jangan klik link apapun!</li>
                    <li>Blokir pengirim pesan.</li>
                    <li>Jangan unduh file (.apk).</li>
                </ul>
            </div>
            """
    else:
      html_card = f"""
            <div class="cyber-card-safe">
                <h3 style="color: #00f5d4; margin-top: 0; font-family: 'Press Start 2P', cursive; font-size: 0.85rem; line-height: 1.5;">🛡️ STAGE CLEAR: PESAN AMAN</h3>
                <p style="font-size: 0.85rem;">TINGKAT KEYAKINAN: <b style="color: #00f5d4; font-size: 1rem;">{skor_keyakinan:.2f}%</b></p>
                <hr>
                <p style="font-size: 0.8rem;">Pesan terdeteksi resmi / aman dari ancaman penipuan.</p>
            </div>
            """

    render_html(html_card)

    # DEBUG DIAGNOSTICS
    with st.expander('🔍 SYSTEM DIAGNOSTICS'):
      st.write('**Teks Hasil Normalisasi (ML Input):**', pesan_bersih)
      st.write('**Status Layer Deteksi:**', alasan_rule)