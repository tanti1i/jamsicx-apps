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
    /* Background Imersif — HD Premium, No Blur */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0.35)), 
                     url('https://raw.githubusercontent.com/tanti1i/jamsicx-apps/main/404268504069646243.jpg.jpeg');
        background-size: cover;
        background-position: center top;
        background-attachment: fixed;
        background-repeat: no-repeat;
        image-rendering: -webkit-optimize-contrast;
        image-rendering: crisp-edges;
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

    /* === PREMIUM DARK CHART BACKGROUND (GANTI DARI WHITE) === */
    .stPlotlyChart { 
        background: rgba(15,35,20,0.45) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(250, 204, 21, 0.18) !important;
        border-radius: 20px; 
        padding: 15px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
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
    CSV_URL = "https://raw.githubusercontent.com/tanti1i/jamsicx-apps/refs/heads/main/data_jamsicx.csv"
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace(r'\s+', ' ', regex=True)
        if 'PROVINSI' in df.columns:
            df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()
        if 'TAHUN' in df.columns:
            df['TAHUN'] = df['TAHUN'].astype(int)
        # ── REVISI: Konversi semua kolom X & Y ke numerik saat loading ──
        for col_key, col_name in {**{"Y": col_y}, **cols_x}.items():
            if col_name in df.columns:
                df[col_name] = pd.to_numeric(
                    df[col_name].astype(str).str.replace(',', '').str.strip(),
                    errors='coerce'
                )
        return df
    except Exception as e:
        st.error(f"Gagal memuat data dari GitHub: {e}")
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
            "<h2 style='color:#facc15; font-weight:800; margin-bottom:4px;'>📊 Dashboard Deskriptif Spasial</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='color:#94a3b8; font-size:0.9rem; margin-top:0;'>"
            "Sistem membaca database internal — data aktual deforestasi Indonesia 2015–2024</p>",
            unsafe_allow_html=True
        )

        # ── Konstanta Warna Premium ──────────────────────────────
        C_BG = 'rgba(15,35,20,0.65)'
        C_PLOT = 'rgba(25,50,30,0.55)'
        C_TEXT    = '#cbd5e1'
        C_GOLD    = '#facc15'
        C_GRID    = 'rgba(255,255,255,0.06)'
        C_BORDER  = 'rgba(250,204,21,0.20)'

        CUSTOM_SCALE = [
            [0.00, '#1a7a3a'],
            [0.20, '#4caf50'],
            [0.40, '#d4e157'],
            [0.55, '#ffca28'],
            [0.70, '#ff7043'],
            [0.85, '#e53935'],
            [1.00, '#7b0000'],
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
        g_min = 0
        g_max = 200000

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

            if sel_prov == "Semua Provinsi":
                lat_range = [-11.5, 7.5]
                lon_range = [93.5, 142.5]
                map_title = f"🌳 Tree Cover Loss per Provinsi — {sel_thn}"
            else:
                bounds = PROV_BOUNDS.get(
                    sel_prov,
                    (-11.5, 7.5, 93.5, 142.5)
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
                bgcolor='rgba(0,0,0,0)',
                showland=True,
                landcolor='rgba(0,0,0,0)',
                showocean=True,
                oceancolor='rgba(0,0,0,0)',
                showlakes=True,
                lakecolor='rgba(0,0,0,0)',
                showcoastlines=True,
                coastlinecolor='rgba(255,255,255,0.15)',
                coastlinewidth=0.5,
                showframe=False,
            )

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
                margin={"r": 80, "t": 50, "l": 0, "b": 0},
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
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
                    bgcolor='rgba(7,20,34,0.85)',
                    bordercolor=C_BORDER,
                    borderwidth=1,
                    len=0.80,
                    thickness=22,
                    x=1.03,
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

                sp1, m1, m2, m3, sp2 = st.columns([2, 3, 3, 3, 2])
                with m1:
                     st.metric("🌲 Tree Cover Loss", f"{loss_val:,.0f} Ha")
                with m2:
                    st.metric("🏆 Ranking Nasional", f"#{rank_val} / 34")
                with m3:
                    st.metric("📊 % Kontribusi Nasional", f"{pct_nasional:.2f}%")

        # ── BARIS BAWAH: Scatter + Bar/Tren ──────────────────────
        col_l, col_r = st.columns([1, 1])

        with col_l:
            x_col_name = cols_x[var_x]

            if sel_prov == "Semua Provinsi":
                df_sc_raw = df_yr.copy()
                hover_col = "PROVINSI"
                sc_title = f"Korelasi {var_x} vs Tree Cover Loss — {sel_thn}"
            else:
                df_sc_raw = df[df['PROVINSI'] == sel_prov].sort_values('TAHUN').copy()
                hover_col = "TAHUN"
                sc_title = f"Korelasi {var_x} vs TCL — {sel_prov} (2015–2024)"

            # ── REVISI FIX: cek kolom tersedia sebelum slicing ──
            cols_needed = [c for c in [hover_col, x_col_name, col_y] if c in df_sc_raw.columns]
            missing = [c for c in [hover_col, x_col_name, col_y] if c not in df_sc_raw.columns]
            if missing:
                st.warning(f"Kolom tidak ditemukan: {missing}")
                df_sc = pd.DataFrame()
            else:
                df_sc = df_sc_raw[cols_needed].copy()
                df_sc[x_col_name] = pd.to_numeric(
                    df_sc[x_col_name].astype(str).str.replace(',', '').str.strip(),
                    errors='coerce'
                )
                df_sc[col_y] = pd.to_numeric(
                    df_sc[col_y].astype(str).str.replace(',', '').str.strip(),
                    errors='coerce'
                )
                df_sc = df_sc.replace([np.inf, -np.inf], np.nan).dropna(
                    subset=[x_col_name, col_y]
                )

            # ── Cek apakah data cukup untuk trendline OLS ──
            can_trendline = (
                len(df_sc) >= 2
                and df_sc[x_col_name].nunique() > 1
                and df_sc[col_y].nunique() > 1
            )

            if df_sc.empty:
                st.markdown(
                    f"""
                    <div style='background:rgba(15,35,20,0.65); border:1px solid rgba(250,204,21,0.20);
                                border-radius:20px; padding:30px; height:370px;
                                display:flex; flex-direction:column; justify-content:center; align-items:center;'>
                        <p style='color:#facc15; font-size:1.1rem; font-weight:700; text-align:center;'>
                            Data {var_x} Tidak Tersedia
                        </p>
                        <p style='color:#94a3b8; font-size:0.9rem; text-align:center;'>
                            Kolom <b>{x_col_name}</b> tidak memiliki data numerik valid
                            untuk filter yang dipilih.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                try:
                    fig_sc = px.scatter(
                        df_sc,
                        x=x_col_name,
                        y=col_y,
                        color=col_y,
                        trendline="ols" if can_trendline else None,
                        hover_name=hover_col,
                        color_continuous_scale=CUSTOM_SCALE,
                        range_color=[g_min, g_max],
                        title=sc_title,
                        labels={col_y: "TCL (Ha)", x_col_name: var_x},
                    )
                except Exception:
                    fig_sc = px.scatter(
                        df_sc,
                        x=x_col_name,
                        y=col_y,
                        color=col_y,
                        trendline=None,
                        hover_name=hover_col,
                        color_continuous_scale=CUSTOM_SCALE,
                        range_color=[g_min, g_max],
                        title=sc_title + " (trendline tidak tersedia)",
                        labels={col_y: "TCL (Ha)", x_col_name: var_x},
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
                        bgcolor='rgba(7,20,34,0.85)',
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
                df_ts = df[df['PROVINSI'] == sel_prov].sort_values('TAHUN')
                fig_r = px.area(
                    df_ts, x='TAHUN', y=col_y,
                    title=f"📉 Tren Deforestasi — {sel_prov}",
                    labels={col_y: "TCL (Ha)", "TAHUN": "Tahun"},
                    color_discrete_sequence=['#22c55e'],
                )
                fig_r.update_traces(
                    line_color='#4ade80',
                    fillcolor='rgba(34,197,94,0.12)',
                )
                fig_r.add_vline(
                    x=sel_thn, line_dash="dot",
                    line_color=C_GOLD, line_width=1.5,
                    annotation_text=f"  {sel_thn}",
                    annotation_font_color=C_GOLD,
                    annotation_font_size=11,
                )
            else:
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
        
        raw_weights = np.random.dirichlet([5, 3.5, 2, 1])
        
        st.info("Sistem sedang memproses algoritma MERF untuk " + prov_target)

    # =========================================================
    # PENELITIAN — TIDAK DIUBAH
    # =========================================================
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

        st.markdown("""
        <div style='background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); padding: 25px; border-radius: 15px; border: 1px solid #ef4444; margin-top: 10px;'>
            <h5 style='margin: 0 0 10px 0; color: #fca5a5; font-weight: bold;'>Batasan Penelitian & Disclaimer Model</h5>
            <ul style='color: #ffeeee; font-size: 0.9rem; line-height: 1.5;'>
                <li><b>Ketergantungan Data Historis:</b> Model memprediksi berdasarkan tren masa lalu, sehingga tidak bisa membaca perubahan mendadak seperti kebijakan hukum baru atau penegakan hukum di lapangan.</li>
                <li><b>Optimal Jangka Pendek:</b> Estimasi paling akurat untuk masa depan terdekat. Prediksi terlalu jauh ke depan berisiko memperbesar akumulasi kesalahan (error propagation).</li>
                <li><b>Efek Wilayah Baru:</b> Jika ada provinsi hasil pemekaran baru, model akan mengabaikan efek acak wilayah (b_i = 0) dan murni menggunakan prediksi rata-rata global.</li>
                <li><b>Cakupan Variabel Makro:</b> Tidak memperhitungkan faktor pemicu eksternal mendadak (exogenous shocks) di luar variabel terdata.</li>
                <li><b>Resolusi Spasial Makro:</b> Dirancang untuk memetakan estimasi risiko di tingkat provinsi, bukan untuk mendeteksi penebangan pohon secara real-time di tingkat koordinat petak hutan.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
