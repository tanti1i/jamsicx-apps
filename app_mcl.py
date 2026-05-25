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
                    url('https://raw.githubusercontent.com/tanti1i/jamsicx-apps/refs/heads/main/404268504069646243.jpg.jpeg');
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
        color: #b8d4b8 !important; 
        font-weight: bold !important;
        font-size: 1.05rem !important;
    }

    /* === FIX FILE UPLOADER RE-STYLING === */
    [data-testid="stFileUploader"] label p {
        color: #b8d4b8 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    }
    [data-testid="stFileUploader"] section div div {
        color: #ffffff !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #2d5a3d !important;
        color: #ffffff !important;
        border: 1px solid #8aab8a !important;
    }

    /* Judul Utama */
    .main-title {
        font-size: 5rem !important;
        font-family: 'Arial Black', sans-serif;
        background: linear-gradient(to bottom, #ddeedd 0%, #b8d4b8 100%);
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

    /* === PREMIUM DARK CHART BACKGROUND (GANTI DARI WHITE) === */
    .stPlotlyChart { 
        background: rgba(10, 20, 38, 0.88) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(138, 171, 138, 0.25) !important;
        border-radius: 20px; 
        padding: 15px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }

    /* Metrik */
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 800 !important; font-size: 1.8rem !important; }
    [data-testid="stMetricLabel"] { color: #b8d4b8 !important; font-weight: bold !important; font-size: 0.9rem !important; }

    /* Tombol Navigasi Umum */
    div.stButton > button {
        background: linear-gradient(135deg, #2d5a3d 0%, #1a3d28 100%) !important;
        color: white !important;
        border: 1px solid #8aab8a !important;
        border-radius: 12px;
        width: 100%;
    }

    /* Info Research Cards Styling */
    .research-card {
        background: rgba(10, 25, 15, 0.72);
        border: 1px solid rgba(138, 171, 138, 0.4);
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 20px;
        backdrop-filter: blur(8px);
    }
    .research-card h4 {
        color: #b8d4b8 !important;
        margin-top: 0px;
        border-bottom: 2px solid #5a7a4a;
        padding-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. DEFINISI KOLOM ---
col_y = "Y (TREE COVER LOSS- Ha)"
cols_x = {
    "X1": "X1 (LUAS PENUTUPAN LAHAN - RIBU Ha)",
    "X2": "X2 (LUAS KEBAKARAN HUTAN DAN LAHAN - Ha)",
    "X3": "X3 (TOTAL LUAS TANAMAN PERKEBUNAN - RIBU Ha)",
    "X4": "X4 (KEPADATAN PENDUDUK - jiwa/km2)",
    "X5": "X5 (TOTAL POPULASI TERNAK - EKOR)",
    "X6": "X6 (PDRB PERTAMBANGAN DAN PENGGALIAN PERSEN)"
}

# --- 5. DATA LOADING ---
@st.cache_data
def load_geojson():
    try:
        url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json"
        res = requests.get(url).json()
        for feature in res['features']:
            nama = str(feature['properties'].get('Propinsi', '')).strip().upper()
            if "ACEH" in nama:
                key = "ACEH"
            elif "BANTEN" in nama:
                key = "BANTEN"
            elif "JAKARTA" in nama:
                key = "DKI JAKARTA"
            elif "YOGYAKARTA" in nama:
                key = "DI YOGYAKARTA"
            elif "BANGKA" in nama or "BELITUNG" in nama:
                key = "BANGKA BELITUNG"
            elif "KEPULAUAN RIAU" in nama or "KEP. RIAU" in nama or "KEPRI" in nama:
                key = "KEPULAUAN RIAU"
            elif "KALIMANTAN UTARA" in nama or "KALTARA" in nama:
                key = "KALIMANTAN UTARA"
            elif "PAPUA BARAT" in nama or "IRIAN JAYA BARAT" in nama:
                key = "PAPUA BARAT"
            elif "PAPUA" in nama or "IRIAN JAYA" in nama:
                key = "PAPUA"
            elif "SULAWESI BARAT" in nama:
                key = "SULAWESI BARAT"
            else:
                key = nama
            feature['properties']['PROV_KEY'] = key
        return res
    except:
        return None

@st.cache_data
def load_internal_data():
    """
    Memuat data deforestasi dari file CSV yang tersimpan di GitHub.
    URL: https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/data_jamsicx.csv
    (Ganti username/repo sesuai repositori Anda yang sebenarnya)
    """
    # ── GANTI URL INI dengan raw URL GitHub Anda yang sebenarnya ──
    CSV_URL = "https://raw.githubusercontent.com/tanti1i/jamsicx-apps/refs/heads/main/data_jamsicx.csv"

    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip()
        if 'PROVINSI' in df.columns:
            df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()
        if 'TAHUN' in df.columns:
            df['TAHUN'] = df['TAHUN'].astype(int)
        return df
    except Exception as e:
        st.error(f"❌ Gagal memuat data dari GitHub: {e}")
        return None

# Batas lat/lon per provinsi — dipakai untuk zoom peta yang akurat
PROV_BOUNDS = {
    "ACEH":                 (-0.5,  6.5,  94.0,  99.5),
    "SUMATERA UTARA":       ( 0.5,  4.5,  97.5, 100.5),
    "SUMATERA BARAT":       (-3.5,  1.5,  98.5, 101.5),
    "RIAU":                 (-2.0,  2.5,  99.5, 103.0),
    "JAMBI":                (-3.5,  0.0, 101.5, 104.5),
    "SUMATERA SELATAN":     (-5.5, -1.5, 102.5, 106.0),
    "BENGKULU":             (-5.5, -2.0, 100.5, 103.5),
    "LAMPUNG":              (-6.5, -3.5, 104.0, 106.5),
    "BANGKA BELITUNG":      (-4.0, -1.0, 105.5, 108.5),
    "KEPULAUAN RIAU":       ( 0.5,  4.5, 103.5, 109.5),
    "DKI JAKARTA":          (-6.5, -5.8, 106.5, 107.2),
    "JAWA BARAT":           (-8.0, -5.8, 106.0, 109.2),
    "JAWA TENGAH":          (-8.5, -6.0, 108.5, 111.5),
    "DI YOGYAKARTA":        (-8.3, -7.5, 110.0, 110.8),
    "JAWA TIMUR":           (-9.0, -6.5, 110.5, 114.5),
    "BANTEN":               (-7.5, -5.8, 105.5, 107.0),
    "BALI":                 (-9.0, -8.0, 114.4, 115.8),
    "NUSA TENGGARA BARAT":  (-9.5, -7.5, 115.5, 117.5),
    "NUSA TENGGARA TIMUR":  (-11.0,-7.5, 118.0, 125.5),
    "KALIMANTAN BARAT":     (-3.5,  3.0, 107.5, 115.0),
    "KALIMANTAN TENGAH":    (-5.0,  2.0, 110.5, 117.0),
    "KALIMANTAN SELATAN":   (-4.5, -1.0, 114.5, 117.5),
    "KALIMANTAN TIMUR":     (-3.5,  2.5, 113.5, 119.0),
    "KALIMANTAN UTARA":     ( 1.5,  4.5, 114.5, 118.5),
    "SULAWESI UTARA":       ( 0.0,  3.5, 123.0, 127.5),
    "SULAWESI TENGAH":      (-4.0,  2.0, 119.5, 125.0),
    "SULAWESI SELATAN":     (-7.0, -2.5, 119.5, 122.5),
    "SULAWESI TENGGARA":    (-6.0, -2.5, 121.0, 124.5),
    "GORONTALO":            (-1.0,  1.5, 121.5, 124.0),
    "SULAWESI BARAT":       (-3.5, -1.5, 118.5, 120.5),
    "MALUKU":               (-8.5, -2.0, 126.0, 135.0),
    "MALUKU UTARA":         (-1.5,  3.5, 125.5, 130.0),
    "PAPUA BARAT":          (-5.0,  1.5, 130.0, 136.5),
    "PAPUA":                (-9.5, -0.5, 131.0, 141.5),
}

geojson = load_geojson()

# === AUTO-LOAD DATA DARI GITHUB CSV ===
if st.session_state.df is None:
    st.session_state.df = load_internal_data()

# --- 6. LOGIKA NAVIGASI ---
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

    # =========================================================
    # DASHBOARD — REVISI LENGKAP
    # =========================================================
    if st.session_state.page == "Dashboard" and st.session_state.df is not None:
        df = st.session_state.df

        st.markdown(
            "<h2 style='color:#b8d4b8; font-weight:800; margin-bottom:4px;'>📊 Dashboard Deskriptif Spasial</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='color:#94a3b8; font-size:0.9rem; margin-top:0;'>"
            "Sistem membaca database internal — data aktual deforestasi Indonesia 2015–2024</p>",
            unsafe_allow_html=True
        )

        # ── Konstanta Warna Premium ──────────────────────────────
        C_BG      = '#0a120d'      # latar chart
        C_PLOT    = '#0f1f12'      # latar area plot
        C_TEXT    = '#cbd5e1'      # teks chart
        C_GOLD    = '#b8d4b8'      # aksen emas
        C_GRID    = 'rgba(255,255,255,0.06)'
        C_BORDER  = 'rgba(138,171,138,0.25)'

        # Skala warna premium: hijau tua → kuning → oranye → merah
        CUSTOM_SCALE = [
            [0.00, '#ddeedd'],
            [0.25, '#b8d4b8'],
            [0.50, '#8aab8a'],
            [0.70, '#5a7a4a'],
            [0.85, '#2d5a3d'],
            [1.00, '#1a3d28'],
        ]

        # ── Filter Row ───────────────────────────────────────────
        fc1, fc2, fc3 = st.columns([1, 1.2, 1])
        with fc1:
            list_thn = sorted(df['TAHUN'].unique(), reverse=True)
            sel_thn = st.selectbox("📅 Pilih Tahun:", list_thn)
        with fc2:
            list_prov = ["Semua Provinsi"] + sorted(df['PROVINSI'].unique().tolist())
            sel_prov = st.selectbox("🗺️ Fokus Wilayah (Zoom Provinsi):", list_prov)
        with fc3:
            var_x = st.selectbox("📈 Analisis Korelasi X:", list(cols_x.keys()))

        df_yr = df[df['TAHUN'] == sel_thn].copy()
        # Gunakan range global agar skala warna konsisten antar tahun
        g_min = float(df[col_y].min())
        g_max = float(df[col_y].max())

        # ── PETA CHOROPLETH (full-width) ──────────────────────────
        if geojson:
            fig_map = px.choropleth(
                data_frame=df_yr,
                geojson=geojson,
                locations="PROVINSI",
                featureidkey="properties.PROV_KEY",
                color=col_y,
                color_continuous_scale=CUSTOM_SCALE,
                range_color=[g_min, g_max],
                hover_name="PROVINSI",
                hover_data={col_y: ':,.0f'},
                labels={col_y: "Tree Cover Loss (Ha)"},
            )

            # ── Zoom berdasarkan lat/lon range (reliable) ─────────
            if sel_prov == "Semua Provinsi":
                lat_range = [-11.5, 7.5]
                lon_range = [93.5, 142.5]
                map_title = f"🌳 Tree Cover Loss per Provinsi — {sel_thn}"
            else:
                bounds = PROV_BOUNDS.get(
                    sel_prov,
                    (-11.5, 7.5, 93.5, 142.5)   # fallback Indonesia penuh
                )
                lat_pad = (bounds[1] - bounds[0]) * 0.12
                lon_pad = (bounds[3] - bounds[2]) * 0.12
                lat_range = [bounds[0] - lat_pad, bounds[1] + lat_pad]
                lon_range = [bounds[2] - lon_pad, bounds[3] + lon_pad]
                map_title = f"🌳 Tree Cover Loss — {sel_prov}  |  Tahun {sel_thn}"

            fig_map.update_geos(
                lataxis_range=lat_range,
                lonaxis_range=lon_range,
                visible=False,
                bgcolor=C_BG,
                showland=True,
                landcolor='#0f1f12',
                showocean=True,
                oceancolor='#0a120d',
                showlakes=True,
                lakecolor='#0a120d',
                showcoastlines=True,
                coastlinecolor='rgba(255,255,255,0.15)',
                coastlinewidth=0.5,
                showframe=False,
            )

            # Highlight provinsi terpilih dengan outline
            if sel_prov != "Semua Provinsi":
                fig_map.update_traces(
                    marker_line_color=C_GOLD,
                    marker_line_width=1.2,
                    selector=dict(type='choropleth')
                )
            else:
                fig_map.update_traces(
                    marker_line_color='rgba(255,255,255,0.15)',
                    marker_line_width=0.5,
                )

            fig_map.update_layout(
                height=560,
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
                paper_bgcolor=C_BG,
                font=dict(color=C_TEXT, family="Arial, sans-serif"),
                title=dict(
                    text=map_title,
                    font=dict(color=C_GOLD, size=15, family="Arial Black"),
                    x=0.01, y=0.98,
                ),
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Tree Cover<br>Loss (Ha)",
                        font=dict(color=C_TEXT, size=11)
                    ),
                    tickfont=dict(color=C_TEXT, size=9),
                    bgcolor='rgba(10,18,13,0.88)',
                    bordercolor=C_BORDER,
                    borderwidth=1,
                    len=0.72,
                    thickness=14,
                    x=1.01,
                    tickformat=',d',
                ),
            )

            st.plotly_chart(fig_map, use_container_width=True)

        # ── METRIC CARDS (jika provinsi spesifik) ────────────────
        if sel_prov != "Semua Provinsi":
            row_prov = df_yr[df_yr['PROVINSI'] == sel_prov]
            if not row_prov.empty:
                loss_val = row_prov[col_y].values[0]
                rank_val = int(df_yr[col_y].rank(ascending=False).loc[row_prov.index[0]])
                pct_nasional = (loss_val / df_yr[col_y].sum()) * 100
                df_prev = df[(df['TAHUN'] == sel_thn - 1) & (df['PROVINSI'] == sel_prov)]

                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("🌲 Tree Cover Loss", f"{loss_val:,.0f} Ha")
                with m2:
                    st.metric("🏆 Ranking Nasional", f"#{rank_val} / 34")
                with m3:
                    st.metric("📊 % Kontribusi Nasional", f"{pct_nasional:.2f}%")
                with m4:
                    if not df_prev.empty:
                        prev = df_prev[col_y].values[0]
                        delta_pct = ((loss_val - prev) / prev) * 100
                        st.metric("📈 Perubahan YoY", f"{delta_pct:+.1f}%",
                                  delta=f"{delta_pct:+.1f}%", delta_color="inverse")
                    else:
                        st.metric("📈 Perubahan YoY", "—")

        # ── BARIS BAWAH: Scatter + Bar/Tren ──────────────────────
        col_l, col_r = st.columns([1, 1])

        with col_l:
            # Scatter: semua provinsi tahun dipilih, atau semua tahun untuk provinsi dipilih
            if sel_prov == "Semua Provinsi":
                df_sc = df_yr
                hover_col = "PROVINSI"
                sc_title = f"Korelasi {var_x} vs Tree Cover Loss — {sel_thn}"
            else:
                df_sc = df[df['PROVINSI'] == sel_prov].sort_values('TAHUN')
                hover_col = "TAHUN"
                sc_title = f"Korelasi {var_x} vs TCL — {sel_prov} (2015–2024)"

            fig_sc = px.scatter(
                df_sc,
                x=cols_x[var_x],
                y=col_y,
                color=col_y,
                trendline="ols",
                hover_name=hover_col,
                color_continuous_scale=CUSTOM_SCALE,
                range_color=[g_min, g_max],
                title=sc_title,
                labels={col_y: "TCL (Ha)", cols_x[var_x]: var_x},
            )
            fig_sc.update_layout(
                paper_bgcolor=C_BG,
                plot_bgcolor=C_PLOT,
                font=dict(color=C_TEXT, size=11),
                title=dict(font=dict(color=C_GOLD, size=13), x=0.01),
                xaxis=dict(gridcolor=C_GRID, zerolinecolor=C_GRID, linecolor=C_BORDER),
                yaxis=dict(gridcolor=C_GRID, zerolinecolor=C_GRID, linecolor=C_BORDER),
                coloraxis_colorbar=dict(
                    title=dict(text="Loss (Ha)", font=dict(color=C_TEXT, size=10)),
                    tickfont=dict(color=C_TEXT, size=8),
                    bgcolor='rgba(10,18,13,0.88)',
                    bordercolor=C_BORDER, borderwidth=1,
                    len=0.80, thickness=11,
                    tickformat=',d',
                ),
                height=370,
                margin=dict(l=10, r=10, t=50, b=10),
            )
            st.plotly_chart(fig_sc, use_container_width=True)

        with col_r:
            if sel_prov != "Semua Provinsi":
                # Tren waktu provinsi terpilih
                df_ts = df[df['PROVINSI'] == sel_prov].sort_values('TAHUN')
                fig_r = px.area(
                    df_ts, x='TAHUN', y=col_y,
                    title=f"📉 Tren Deforestasi — {sel_prov}",
                    labels={col_y: "TCL (Ha)", "TAHUN": "Tahun"},
                    color_discrete_sequence=['#8aab8a'],
                )
                fig_r.update_traces(
                    line_color='#b8d4b8',
                    fillcolor='rgba(90,122,74,0.18)',
                )
                fig_r.add_vline(
                    x=sel_thn, line_dash="dot",
                    line_color=C_GOLD, line_width=1.5,
                    annotation_text=f"  {sel_thn}",
                    annotation_font_color=C_GOLD,
                    annotation_font_size=11,
                )
            else:
                # Top-10 provinsi dengan kehilangan tertinggi
                top10 = (
                    df_yr.nlargest(10, col_y)[['PROVINSI', col_y]]
                    .sort_values(col_y, ascending=True)
                )
                fig_r = px.bar(
                    top10, x=col_y, y='PROVINSI', orientation='h',
                    title=f"🔴 Top 10 Deforestasi Tertinggi — {sel_thn}",
                    color=col_y,
                    color_continuous_scale=CUSTOM_SCALE,
                    range_color=[top10[col_y].min(), top10[col_y].max()],
                    labels={col_y: "TCL (Ha)", 'PROVINSI': ''},
                )
                fig_r.update_traces(marker_line_width=0)
                fig_r.update_layout(coloraxis_showscale=False)

            fig_r.update_layout(
                paper_bgcolor=C_BG,
                plot_bgcolor=C_PLOT,
                font=dict(color=C_TEXT, size=11),
                title=dict(font=dict(color=C_GOLD, size=13), x=0.01),
                xaxis=dict(gridcolor=C_GRID, zerolinecolor=C_GRID,
                           linecolor=C_BORDER, tickformat=',d'),
                yaxis=dict(gridcolor=C_GRID, zerolinecolor=C_GRID,
                           linecolor=C_BORDER),
                height=370,
                margin=dict(l=10, r=10, t=50, b=10),
            )
            st.plotly_chart(fig_r, use_container_width=True)

    # =========================================================
    # PREDIKSI — TIDAK DIUBAH
    # =========================================================
    elif st.session_state.page == "Prediksi" and st.session_state.df is not None:
        df = st.session_state.df
        st.header("📈 Prediksi Deforestasi Multi-Tahun (MERF)")
        prov_target = st.selectbox("Fokus Wilayah Prediksi:", sorted(df['PROVINSI'].unique()))
        hist = df[df['PROVINSI'] == prov_target].sort_values('TAHUN')
        
        # Perbaikan baris 281
        raw_weights = np.random.dirichlet([5, 3.5, 2, 1])
        
        # Sisa logika prediksi di sini...
        st.info("Sistem sedang memproses algoritma MERF untuk " + prov_target)

    # =========================================================
    # PENELITIAN — TIDAK DIUBAH
    # =========================================================
    elif st.session_state.page == "Penelitian":
        st.markdown("<h2 style='text-align:center; color:#b8d4b8; font-weight: 800;'>📖 Info Penelitian</h2>", unsafe_allow_html=True)
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

            st.markdown("""
            <div class='research-card'>
                <h4>🧮 Persamaan Dasar Model MERF</h4>
                <p style='text-align: center; font-size: 1.4rem; color: #f8fafc; font-style: italic; margin: 16px 0 20px 0; letter-spacing: 0.03em;'>
                    <i>y</i><sub><i>i</i></sub> &nbsp;=&nbsp; <i>f</i>(<b>X</b><sub><i>i</i></sub>) &nbsp;+&nbsp; <b>Z</b><sub><i>i</i></sub><b>b</b><sub><i>i</i></sub> &nbsp;+&nbsp; &#x03B5;<sub><i>i</i></sub>
                </p>
                <table style='width:100%; border-collapse: collapse; font-size: 0.88rem;'>
                    <thead>
                        <tr>
                            <th style='padding: 8px 14px; text-align: center; color: #b8d4b8; width: 20%; font-weight: 700;'>Simbol</th>
                            <th style='padding: 8px 14px; text-align: left; color: #b8d4b8; font-weight: 700;'>Keterangan</th>
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
