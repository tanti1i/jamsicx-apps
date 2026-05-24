import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="I-JAMCSIIX - Eco Intelligence", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "Portal"
if 'df' not in st.session_state:
    st.session_state.df = None

def set_page(name):
    st.session_state.page = name

# --- 3. CSS CUSTOM (FIX KONTRAS WARNA & READABILITY) ---
st.markdown("""
<style>
    /* Background Imersif */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                    url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #ffffff;
    }

    /* === FIX DROPDOWN (SELECTBOX) RE-STYLING === */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 10px;
    }
    .stSelectbox div[data-baseweb="select"] div {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    .stSelectbox label p {
        color: #facc15 !important; 
        font-weight: bold !important;
        font-size: 1.05rem !important;
    }

    /* === FIX FILE UPLOADER RE-STYLING === */
    [data-testid="stFileUploader"] label p {
        color: #facc15 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    }
    [data-testid="stFileUploader"] section div div {
        color: #ffffff !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #15803d !important;
        color: #ffffff !important;
        border: 1px solid #facc15 !important;
    }

    /* Judul Utama */
    .main-title {
        font-size: 5rem !important;
        font-family: 'Arial Black', sans-serif;
        background: linear-gradient(to bottom, #facc15 0%, #fbbf24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 900 !important;
        filter: drop-shadow(0px 5px 15px rgba(0,0,0,0.9));
    }

    /* Glassmorphism Card */
    .menu-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 30px;
        padding: 40px;
        text-align: center;
        height: 350px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* White Background untuk Chart agar Teks Grafik Jelas */
    .stPlotlyChart { 
        background-color: white !important; 
        border-radius: 20px; 
        padding: 15px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Metrik */
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 800 !important; font-size: 1.8rem !important; }
    [data-testid="stMetricLabel"] { color: #facc15 !important; font-weight: bold !important; font-size: 0.9rem !important; }

    /* Tombol Navigasi Umum */
    div.stButton > button {
        background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important;
        color: white !important;
        border: 1px solid #facc15 !important;
        border-radius: 12px;
        width: 100%;
    }

    /* Info Research Cards Styling */
    .research-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(250, 191, 36, 0.3);
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 20px;
        backdrop-filter: blur(8px);
    }
    .research-card h4 {
        color: #facc15 !important;
        margin-top: 0px;
        border-bottom: 2px solid #15803d;
        padding-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. DATA LOADING ---
@st.cache_data
def load_geojson():
    try:
        url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json"
        res = requests.get(url).json()
        for feature in res['features']:
            nama_geojson = str(feature['properties'].get('Propinsi', '')).strip().upper()
            if "ACEH" in nama_geojson: feature['properties']['PROV_KEY'] = "ACEH"
            elif "BANTEN" in nama_geojson: feature['properties']['PROV_KEY'] = "BANTEN"
            elif "JAKARTA" in nama_geojson: feature['properties']['PROV_KEY'] = "DKI JAKARTA"
            elif "YOGYAKARTA" in nama_geojson: feature['properties']['PROV_KEY'] = "DI YOGYAKARTA"
            else: feature['properties']['PROV_KEY'] = nama_geojson
        return res
    except: return None

geojson = load_geojson()
col_y = "Y (TREE COVER LOSS- Ha)"
cols_x = {
    "X1": "X1 (LUAS PENUTUPAN LAHAN - RIBU Ha)",
    "X2": "X2 (LUAS KEBAKARAN HUTAN DAN LAHAN - Ha)",
    "X3": "X3 (TOTAL LUAS TANAMAN PERKEBUNAN - RIBU Ha)",
    "X4": "X4 (KEPADATAN PENDUDUK - jiwa/km2)",
    "X5": "X5 (TOTAL POPULASI TERNAK - EKOR)",
    "X6": "X6 (PDRB PERTAMBANGAN DAN PENGGALIAN PERSEN)"
}

# --- 5. LOGIKA NAVIGASI ---
if st.session_state.page == "Portal":
    st.markdown("<br><br><h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#dcfce7; letter-spacing:2px;'>SISTEM MONITORING DEFORESTASI DINAMIS</p>", unsafe_allow_html=True)
    
    c_up1, c_up2, c_up3 = st.columns([1, 2, 1])
    with c_up2:
        up_file = st.file_uploader("📥 Unggah Dataset Deforestasi (CSV)", type=["csv"])
        if up_file is not None:
            raw_df = pd.read_csv(up_file)
            raw_df.columns = raw_df.columns.str.strip()
            if 'PROVINSI' in raw_df.columns:
                raw_df['PROVINSI'] = raw_df['PROVINSI'].astype(str).str.strip().str.upper()
            st.session_state.df = raw_df
            st.success("🌲 Data Terintegrasi Sempurna!")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    is_locked = st.session_state.df is None

    with c1:
        st.markdown("<div class='menu-card'><h1>🛰️</h1><h3>Dashboard Spasial</h3></div>", unsafe_allow_html=True)
        if st.button("Buka Dashboard", disabled=is_locked): set_page("Dashboard"); st.rerun()
    with c2:
        st.markdown("<div class='menu-card'><h1>🧪</h1><h3>Prediksi MERF</h3></div>", unsafe_allow_html=True)
        if st.button("Mulai Prediksi", disabled=is_locked): set_page("Prediksi"); st.rerun()
    with c3:
        st.markdown("<div class='menu-card'><h1>📖</h1><h3>Info Penelitian</h3></div>", unsafe_allow_html=True)
        if st.button("Lihat Penelitian"): set_page("Penelitian"); st.rerun()

else:
    if st.button("⬅️ KEMBALI KE PORTAL"):
        set_page("Portal"); st.rerun()
    st.markdown("---")

    if st.session_state.page == "Dashboard" and st.session_state.df is not None:
        df = st.session_state.df
        st.header("📊 Dashboard Deskriptif Spasial")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            list_thn = sorted(df['TAHUN'].unique(), reverse=True)
            sel_thn = st.selectbox("Pilih Tahun:", list_thn)
        with col_f2:
            list_prov = ["Semua Provinsi"] + sorted(df['PROVINSI'].unique().tolist())
            sel_prov = st.selectbox("Fokus Wilayah (Zoom Provinsi):", list_prov)
        
        df_filt_year = df[df['TAHUN'] == sel_thn]
        min_val = float(df_filt_year[col_y].min())
        max_val = float(df_filt_year[col_y].max())
        
        cl, cr = st.columns([1.1, 0.9])
        with cl:
            if geojson:
                data_peta = df_filt_year if sel_prov == "Semua Provinsi" else df_filt_year[df_filt_year['PROVINSI'] == sel_prov]
                fitur_fit = "locations" if sel_prov != "Semua Provinsi" else False
                fig = px.choropleth(data_frame=data_peta, geojson=geojson, locations="PROVINSI", featureidkey="properties.PROV_KEY", color=col_y, color_continuous_scale="RdYlGn_r", range_color=[min_val, max_val], hover_name="PROVINSI")
                if fitur_fit: fig.update_geos(fitbounds=fitur_fit, visible=False)
                else: fig.update_geos(projection_type="mercator", center={"lat": -2.5, "lon": 118.0}, visible=False)
                fig.update_layout(height=450, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='white')
                st.plotly_chart(fig, use_container_width=True)
        with cr:
            var_x = st.selectbox("Analisis Korelasi X:", list(cols_x.keys()))
            fig2 = px.scatter(df_filt_year, x=cols_x[var_x], y=col_y, color=col_y, trendline="ols", hover_name="PROVINSI", color_continuous_scale="RdYlGn_r", range_color=[min_val, max_val])
            fig2.update_layout(paper_bgcolor='white')
            st.plotly_chart(fig2, use_container_width=True)

    elif st.session_state.page == "Prediksi" and st.session_state.df is not None:
        df = st.session_state.df
        st.header("📈 Prediksi Deforestasi Multi-Tahun (MERF)")
        prov_target = st.selectbox("Fokus Wilayah Prediksi:", sorted(df['PROVINSI'].unique()))
        hist = df[df['PROVINSI'] == prov_target].sort_values('TAHUN')
        
        # Perbaikan baris 281
        raw_weights = np.random.dirichlet([5, 3.5, 2, 1])
        
        # Sisa logika prediksi di sini...
        st.info("Sistem sedang memproses algoritma MERF untuk " + prov_target)

    elif st.session_state.page == "Penelitian":
        st.markdown("<h2 style='text-align:center; color:#facc15; font-weight: 800;'>📖 Info Penelitian</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("""
            <div class='research-card'>
                <h4>🎯 Tujuan Penelitian</h4>
                <ul style='color: #f8fafc; padding-left: 20px; line-height: 1.6;'>
                    <li>Menerapkan pendekatan data longitudinal dan model hibrida Mixed Effects Random Forest (MERF) untuk menangkap tren perubahan waktu sekaligus karakteristik spasial.</li>
                    <li>Membangun aplikasi web interaktif ForestGuard sebagai media visualisasi spasial-temporal (Choropleth Map) dan sistem prediksi risiko deforestasi yang praktis dan mudah dipahami oleh pemangku kebijakan serta masyarakat umum.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class='research-card'>
                <h4>📊 Sumber Data Penelitian</h4>
                <ul style='color: #f8fafc; padding-left: 20px; line-height: 1.6;'>
                    <li><b>BPS (Badan Pusat Statistik):</b> Data sosio-ekonomi agregat tahunan meliputi kepadatan penduduk sektoral dan persentase kontribusi PDRB lapangan usaha.</li>
                    <li><b>KLHK (Kementerian Lingkungan Hidup dan Kehutanan):</b> Rekapitulasi luasan area kebakaran hutan (Karhutla) serta pemantauan status fungsi kawasan hutan.</li>
                    <li><b>Global Forest Watch (GFW):</b> Metrik target historis <i>Tree Cover Loss</i> (Y) yang dihitung dalam satuan Hektar (Ha).</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with rc2:
            st.markdown("""
            <div class='research-card'>
                <h4>🤖 Metode MERF (Mixed-Effects Random Forest)</h4>
                <p style='color: #f8fafc; text-align: justify; line-height: 1.6; margin-bottom: 10px;'>
                    <b>Mixed-Effects Random Forest (MERF)</b> merupakan algoritma lanjut yang memadukan keunggulan non-linearitas dari <i>Random Forest</i> dengan kemampuan menangani data panel berhirarki milik <i>Linear Mixed Models</i>.
                </p>
                <p style='color: #f8fafc; text-align: justify; line-height: 1.6;'>
                    Setiap provinsi memiliki karakteristik dasar lingkungan yang berbeda (efek acak) yang tidak bisa disamaratakan oleh model regresi biasa standar. MERF mengisolasi efek kontekstual wilayah ini sehingga tingkat akurasi prediksi meningkat tajam secara lokal.
                </p>
            </div>
            """, unsafe_allow_html=True)

            # =====================================================================
            # BAGIAN YANG DIREVISI: 🧮 Persamaan Dasar Model MERF
            # =====================================================================
            st.markdown("""
            <div class='research-card'>
                <h4>🧮 Persamaan Dasar Model MERF</h4>
                <p style='text-align: center; font-size: 1.4rem; color: #f8fafc; font-style: italic; margin: 16px 0 20px 0; letter-spacing: 0.03em;'>
                    <i>y</i><sub><i>i</i></sub> &nbsp;=&nbsp; <i>f</i>(<b>X</b><sub><i>i</i></sub>) &nbsp;+&nbsp; <b>Z</b><sub><i>i</i></sub><b>b</b><sub><i>i</i></sub> &nbsp;+&nbsp; &#x03B5;<sub><i>i</i></sub>
                </p>
                <table style='width:100%; border-collapse: collapse; font-size: 0.88rem;'>
                    <thead>
                        <tr>
                            <th style='padding: 8px 14px; text-align: center; color: #facc15; width: 20%; font-weight: 700;'>Simbol</th>
                            <th style='padding: 8px 14px; text-align: left; color: #facc15; font-weight: 700;'>Keterangan</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style='padding: 8px 14px; text-align: center; color: #fde68a; font-style: italic;'><i>y</i><sub><i>i</i></sub></td>
                            <td style='padding: 8px 14px; color: #f8fafc;'>Vektor nilai variabel respon (<i>Tree Cover Loss</i>) untuk subjek provinsi ke-<i>i</i></td>
                        </tr>
                        <tr>
                            <td style='padding: 8px 14px; text-align: center; color: #fde68a; font-style: italic;'><i>f</i>(<b>X</b><sub><i>i</i></sub>)</td>
                            <td style='padding: 8px 14px; color: #f8fafc;'>Fungsi non-linear <i>fixed effects</i> yang diestimasi menggunakan algoritma <b>Random Forest</b> berdasarkan matriks prediktor <b>X</b><sub><i>i</i></sub></td>
                        </tr>
                        <tr>
                            <td style='padding: 8px 14px; text-align: center; color: #fde68a;'><b>Z</b><sub><i>i</i></sub></td>
                            <td style='padding: 8px 14px; color: #f8fafc;'>Matriks desain untuk komponen <i>random effects</i> (konstanta intercept untuk tiap provinsi)</td>
                        </tr>
                        <tr>
                            <td style='padding: 8px 14px; text-align: center; color: #fde68a;'><b>b</b><sub><i>i</i></sub></td>
                            <td style='padding: 8px 14px; color: #f8fafc;'>Vektor penyimpangan acak (<i>random effects</i>) untuk provinsi ke-<i>i</i>, dimana <b>b</b><sub><i>i</i></sub> &#x223C; <i>N</i>(0, <b>D</b>)</td>
                        </tr>
                        <tr>
                            <td style='padding: 8px 14px; text-align: center; color: #fde68a;'>&#x03B5;<sub><i>i</i></sub></td>
                            <td style='padding: 8px 14px; color: #f8fafc;'>Vektor <i>error</i> acak sisaan (<i>residual error</i>), dimana &#x03B5;<sub><i>i</i></sub> &#x223C; <i>N</i>(0, <b>R</b><sub><i>i</i></sub>) dengan <b>R</b><sub><i>i</i></sub> = &#x03C3;&#xB2;<b>I</b><sub><i>n</i><sub><i>i</i></sub></sub></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)
            # =====================================================================

        st.markdown("""
        <div style='background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); padding: 25px; border-radius: 15px; border: 1px solid #ef4444; margin-top: 10px;'>
            <h5 style='margin: 0 0 10px 0; color: #fca5a5; font-weight: bold;'>⚠️ Batasan Penelitian & Disclaimer Model</h5>
            <ul style='color: #ffeeee; font-size: 0.9rem; line-height: 1.5;'>
                <li><b>Ketergantungan Data Historis:</b> Model memprediksi berdasarkan tren masa lalu, sehingga tidak bisa membaca perubahan mendadak seperti kebijakan hukum baru atau penegakan hukum di lapangan.</li>
                <li><b>Optimal Jangka Pendek:</b> Estimasi paling akurat untuk masa depan terdekat. Prediksi terlalu jauh ke depan berisiko memperbesar akumulasi kesalahan (error propagation).</li>
                <li><b>Efek Wilayah Baru:</b> Jika ada provinsi hasil pemekaran baru, model akan mengabaikan efek acak wilayah (b_i = 0) dan murni menggunakan prediksi rata-rata global.</li>
                <li><b>Cakupan Variabel Makro:</b> Tidak memperhitungkan faktor pemicu eksternal mendadak (exogenous shocks) di luar variabel terdata.</li>
                <li><b>Resolusi Spasial Makro:</b> Dirancang untuk memetakan estimasi risiko di tingkat provinsi, bukan untuk mendeteksi penebangan pohon secara real-time di tingkat koordinat petak hutan.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
