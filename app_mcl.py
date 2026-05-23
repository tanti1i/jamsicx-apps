"""
JAMSICX - Sistem Prediksi & Visualisasi Tree Cover Loss Indonesia
Berbasis Mixed Effects Random Forest (MERF)
Versi: 7.0 | UI Revisi — Kontras & Bug Fixed
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import numpy as np
import io
from scipy import stats

# ============================================================
# 1. KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="JAMSICX | Tree Cover Loss Indonesia",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# 2. SESSION STATE
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "df" not in st.session_state:
    st.session_state.df = None
if "geojson" not in st.session_state:
    st.session_state.geojson = None

# ============================================================
# 3. CONSTANTS
# ============================================================
COL_Y    = "Y (TREE COVER LOSS- Ha)"
COL_PROV = "PROVINSI"
COL_YEAR = "TAHUN"
COLS_X_MAP = {
    "X1 – Luas Penutupan Lahan":   "X1 (LUAS PENUTUPAN LAHAN - RIBU Ha)",
    "X2 – Luas Kebakaran":         "X2 (LUAS KEBAKARAN HUTAN DAN LAHAN - Ha)",
    "X3 – Luas Perkebunan":        "X3 (TOTAL LUAS TANAMAN PERKEBUNAN - RIBU Ha)",
    "X4 – Kepadatan Penduduk":     "X4 (KEPADATAN PENDUDUK - jiwa/km2)",
    "X5 – Populasi Ternak":        "X5  (TOTAL POPULASI TERNAK - EKOR)",
    "X6 – PDRB Pertambangan (%)":  "X6 (PDRB PERTAMBANGAN DAN PENGGALIAN PERSEN)",
}
COLS_X = list(COLS_X_MAP.values())

# Skala warna konsisten: Hijau → Kuning → Merah
COLOR_SCALE_MAP = [[0, '#22c55e'], [0.45, '#facc15'], [0.75, '#f97316'], [1, '#ef4444']]
COLOR_SCALE_MAP_PLOTLY = 'RdYlGn_r'  # built-in reversed green-yellow-red

PLOTLY_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(13,28,18,0.7)',
    font=dict(family='Inter, sans-serif', color='#e2fce8', size=12),
    xaxis=dict(
        gridcolor='rgba(74,222,128,0.12)', linecolor='rgba(74,222,128,0.25)',
        tickfont=dict(family='Inter', color='#bbf7d0'),
        title_font=dict(family='Inter', color='#e2fce8'),
    ),
    yaxis=dict(
        gridcolor='rgba(74,222,128,0.12)', linecolor='rgba(74,222,128,0.25)',
        tickfont=dict(family='Inter', color='#bbf7d0'),
        title_font=dict(family='Inter', color='#e2fce8'),
    ),
    margin=dict(l=14, r=14, t=42, b=14),
    legend=dict(
        bgcolor='rgba(10,25,14,0.92)', font=dict(color='#e2fce8', family='Inter'),
        bordercolor='rgba(74,222,128,0.3)', borderwidth=1,
    ),
    coloraxis_colorbar=dict(
        tickfont=dict(color='#e2fce8', family='Inter'),
        title=dict(font=dict(color='#e2fce8')),
        bgcolor='rgba(10,25,14,0.92)', bordercolor='rgba(74,222,128,0.3)',
    ),
)

def apply_theme(fig, height=None):
    fig.update_layout(**PLOTLY_BASE)
    if height:
        fig.update_layout(height=height)
    return fig

# ============================================================
# 4. CUSTOM CSS — REVISI PALET (lebih terang, kontras lebih baik)
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=JetBrains+Mono:wght@400;500&display=swap');

[data-testid="stSidebar"],
[data-testid="collapsedControl"],
#MainMenu, footer, header,
.st-emotion-cache-1cypcdb { display:none !important; }

:root {
    --ink:       #0a1610;
    --ink-2:     #0d1f14;
    --ink-3:     #112818;
    --ink-4:     #163320;
    --canopy:    #16a34a;
    --forest:    #15803d;
    --leaf:      #4ade80;
    --mint:      #86efac;
    --mist:      #dcfce7;
    --fog:       #f0fdf4;
    --amber:     #fbbf24;
    --amber-lt:  #fde68a;
    --cream:     #fffde7;
    --white:     #ffffff;
    --danger:    #ef4444;
    /* Panels — notice higher opacity for better readability */
    --glass:     rgba(16,38,22,0.88);
    --glass-lt:  rgba(20,50,28,0.80);
    --border:    rgba(74,222,128,0.22);
    --border-hi: rgba(74,222,128,0.55);
    --radius:    18px;
    --radius-sm: 12px;
    --radius-xs: 8px;
    --shadow:    0 8px 32px rgba(0,0,0,0.5);
    --shadow-sm: 0 2px 12px rgba(0,0,0,0.35);
    --trans:     all 0.22s cubic-bezier(0.4,0,0.2,1);
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--ink) !important;
    color: var(--mist) !important;
}
.stApp {
    background-image:
        linear-gradient(to bottom, rgba(10,22,16,0.92) 0%, rgba(13,31,20,0.86) 50%, rgba(10,22,16,0.94) 100%),
        url('https://images.unsplash.com/photo-1448375240586-882707db888b?w=1920&q=80') !important;
    background-size: cover !important;
    background-position: center center !important;
    background-attachment: fixed !important;
}
.block-container { padding: 0 2rem 4rem !important; max-width: 1440px !important; }

h1,h2,h3,h4,h5 { font-family: 'Playfair Display', serif !important; color: var(--white) !important; }
code, pre { font-family: 'JetBrains Mono', monospace !important; background: rgba(10,30,16,0.9) !important; color: var(--leaf) !important; }
a { color: var(--leaf) !important; }

::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background: var(--ink); }
::-webkit-scrollbar-thumb { background: var(--canopy); border-radius:3px; }

/* ===== TOP NAV ===== */
.topnav {
    display:flex; align-items:center; justify-content:space-between;
    padding: 0 2rem;
    background: rgba(10,20,13,0.95);
    backdrop-filter: blur(24px);
    border-bottom: 1px solid var(--border);
    position: sticky; top:0; z-index:9999;
    height: 64px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.45);
}
.topnav-brand { display:flex; align-items:center; gap:0.9rem; }
.topnav-logo {
    width:40px; height:40px; border-radius:11px;
    background: linear-gradient(135deg, var(--canopy), var(--ink-3));
    border: 1px solid rgba(74,222,128,0.3);
    display:flex; align-items:center; justify-content:center;
    font-size:1.3rem; flex-shrink:0;
}
.topnav-name { font-family:'Playfair Display',serif; font-size:1.2rem; font-weight:700; color:var(--white); }
.topnav-sub { font-family:'JetBrains Mono',monospace; font-size:0.55rem; color:var(--leaf); letter-spacing:0.18em; text-transform:uppercase; display:block; }
.nav-dot { width:6px; height:6px; border-radius:50%; background:var(--leaf); animation:blink 2.5s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.4;} }

/* ===== NAV BUTTON OVERRIDES ===== */
div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"] > div > div > div > button {
    background: transparent !important; border: 1px solid transparent !important;
    border-radius: 100px !important; color: var(--mist) !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.78rem !important;
    font-weight: 500 !important; padding: 7px 16px !important;
    height: auto !important; white-space: nowrap !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"] > div > div > div > button:hover {
    background: rgba(74,222,128,0.12) !important; border-color: rgba(74,222,128,0.3) !important;
    color: var(--fog) !important;
}

.content-area { padding-top: 2rem; }

/* ===== HERO ===== */
.hero-wrap {
    position:relative; width:100%; min-height:460px;
    border-radius: var(--radius); overflow:hidden;
    margin-bottom:2.5rem; border:1px solid var(--border);
    box-shadow: 0 20px 56px rgba(0,0,0,0.6);
}
.hero-bg {
    position:absolute; inset:0;
    background: linear-gradient(130deg, rgba(10,22,16,0.97) 0%, rgba(16,38,22,0.90) 45%, rgba(30,70,38,0.70) 100%),
        url('https://images.unsplash.com/photo-1448375240586-882707db888b?w=1800&q=80') center/cover no-repeat;
}
.hero-grid {
    position:absolute; inset:0;
    background-image: linear-gradient(rgba(74,222,128,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(74,222,128,0.04) 1px, transparent 1px);
    background-size:56px 56px;
}
.hero-content { position:relative; z-index:2; padding:4rem 4.5rem; min-height:460px; display:flex; flex-direction:column; justify-content:center; }
.hero-eyebrow { display:inline-flex; align-items:center; gap:0.55rem; color:var(--leaf); font-family:'JetBrains Mono',monospace; font-size:0.65rem; letter-spacing:0.2em; text-transform:uppercase; margin-bottom:1.4rem; }
.hero-line { width:24px; height:1px; background:var(--leaf); opacity:0.5; }
.hero-title { font-family:'Playfair Display',serif !important; font-size:3.4rem !important; font-weight:700 !important; line-height:1.08 !important; color:var(--white) !important; max-width:660px; margin:0 0 1.2rem 0 !important; }
.hero-title .t-green { color:var(--leaf); }
.hero-title .t-italic { font-style:italic; }
.hero-desc { font-size:0.96rem; color:var(--mist); max-width:520px; line-height:1.9; margin:0 0 2rem 0; font-weight:300; }
.hero-stats { display:flex; gap:2rem; }
.hero-stat { display:flex; flex-direction:column; gap:0.2rem; }
.hs-val { font-family:'Playfair Display',serif; font-size:1.7rem; color:var(--amber); font-weight:700; }
.hs-lbl { font-family:'JetBrains Mono',monospace; font-size:0.58rem; color:var(--leaf); text-transform:uppercase; letter-spacing:0.16em; }
.hero-deco { position:absolute; right:3rem; bottom:-1rem; font-size:18rem; opacity:0.025; user-select:none; line-height:1; }

/* ===== SECTION HEADER ===== */
.sec-hdr { margin-bottom:1.4rem; }
.sec-eye { font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:var(--leaf); text-transform:uppercase; letter-spacing:0.22em; display:block; margin-bottom:0.25rem; }
.sec-title { font-family:'Playfair Display',serif; font-size:1.75rem; color:var(--white); margin:0; font-weight:600; }

/* ===== FEATURE CARDS ===== */
.feat-card {
    background: var(--glass);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius); padding: 2rem 1.85rem 1.85rem;
    cursor:pointer; transition: var(--trans);
    position:relative; overflow:hidden;
}
.feat-card:hover { transform: translateY(-5px); border-color: var(--border-hi); box-shadow: 0 18px 44px rgba(0,0,0,0.5); }
.feat-bottom-glow { height:2px; position:absolute; bottom:0; left:0; right:0; border-radius:0 0 var(--radius) var(--radius); opacity:0; transition:opacity 0.2s; }
.feat-card:hover .feat-bottom-glow { opacity:1; }
.feat-arrow { position:absolute; top:1.4rem; right:1.4rem; width:28px; height:28px; border-radius:50%; background:rgba(74,222,128,0.1); border:1px solid var(--border); display:flex; align-items:center; justify-content:center; font-size:0.8rem; color:var(--leaf); transition:var(--trans); }
.feat-card:hover .feat-arrow { background:var(--canopy); border-color:var(--leaf); }
.feat-icon { width:52px; height:52px; border-radius:13px; display:flex; align-items:center; justify-content:center; font-size:1.6rem; margin-bottom:1.2rem; border:1px solid rgba(74,222,128,0.2); }
.ic-g { background:rgba(22,163,74,0.25); }
.ic-b { background:rgba(2,136,209,0.15); border-color:rgba(2,136,209,0.25) !important; }
.ic-a { background:rgba(251,191,36,0.12); border-color:rgba(251,191,36,0.25) !important; }
.ic-m { background:rgba(74,222,128,0.18); }
.feat-num { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:var(--leaf); letter-spacing:0.1em; text-transform:uppercase; display:block; margin-bottom:0.3rem; }
.feat-title { font-family:'Playfair Display',serif; font-size:1.2rem; color:var(--white); font-weight:600; display:block; margin-bottom:0.45rem; }
.feat-desc { font-size:0.82rem; color:var(--mist); line-height:1.75; font-weight:300; display:block; }

/* ===== PANELS ===== */
.panel {
    background: var(--glass);
    backdrop-filter: blur(14px);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.75rem;
    margin-bottom: 1.2rem;
}
.panel-title { font-family:'Playfair Display',serif; font-size:1.05rem; color:var(--white); margin:0 0 1.1rem 0; display:flex; align-items:center; gap:0.5rem; font-weight:600; }

/* ===== METRIC GRID ===== */
.metric-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-bottom:1.5rem; }
.m-card {
    background: rgba(18,45,24,0.92);
    border: 1px solid var(--border);
    border-radius:var(--radius-sm);
    padding:1.3rem 1.4rem;
    position:relative; overflow:hidden;
}
.m-card::before { content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,rgba(74,222,128,0.35),transparent); }
.m-label { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:var(--leaf); text-transform:uppercase; letter-spacing:0.16em; display:block; margin-bottom:0.55rem; }
.m-value { font-family:'Playfair Display',serif; font-size:2rem; color:var(--amber); display:block; line-height:1; font-weight:700; }
.m-sub { font-size:0.69rem; color:rgba(134,239,172,0.75); display:block; margin-top:0.25rem; }
.m-delta-up   { color:#f87171; font-size:0.7rem; margin-top:0.2rem; display:block; }
.m-delta-down { color:var(--leaf); font-size:0.7rem; margin-top:0.2rem; display:block; }

/* ===== PAGE HEADER ===== */
.page-hdr { display:flex; align-items:center; gap:1.2rem; margin-bottom:2rem; padding-bottom:1.4rem; border-bottom:1px solid var(--border); }
.page-hdr-icon { width:50px; height:50px; background:rgba(22,163,74,0.2); border:1px solid var(--border); border-radius:var(--radius-sm); display:flex; align-items:center; justify-content:center; font-size:1.5rem; flex-shrink:0; }
.page-hdr h1 { font-family:'Playfair Display',serif !important; font-size:1.9rem !important; margin:0 0 0.1rem 0 !important; color:var(--white) !important; }
.page-hdr p { font-size:0.83rem; color:var(--leaf); margin:0; }

/* ===== INFO PANEL ===== */
.info-panel { background:var(--glass); backdrop-filter:blur(14px); border:1px solid var(--border); border-radius:var(--radius); padding:1.85rem 2rem; height:100%; box-sizing:border-box; }
.info-panel-title { font-family:'Playfair Display',serif; font-size:1.05rem; color:var(--white); margin:0 0 0.8rem 0; display:flex; align-items:center; gap:0.6rem; font-weight:600; }
.info-panel p, .info-panel li { font-size:0.83rem; color:var(--mist); line-height:1.85; margin:0; font-weight:300; }
.info-panel ul { padding-left:1.1rem; margin:0; }
.info-panel li { margin-bottom:0.2rem; }
.chip-row { display:flex; flex-wrap:wrap; gap:0.4rem; margin-top:0.85rem; }
.chip { background:rgba(74,222,128,0.1); border:1px solid rgba(74,222,128,0.28); color:var(--leaf); font-family:'JetBrains Mono',monospace; font-size:0.62rem; padding:3px 10px; border-radius:100px; text-transform:uppercase; letter-spacing:0.08em; }

/* ===== DARK TABLE — FULLY REVISED ===== */
.dark-table-wrap { border:1px solid rgba(74,222,128,0.3); border-radius:var(--radius-sm); overflow:hidden; margin-bottom:1.2rem; }
.dark-table { width:100%; border-collapse:collapse; font-size:0.84rem; }
.dark-table thead tr { background:linear-gradient(135deg, rgba(22,163,74,0.65), rgba(15,80,35,0.75)); border-bottom:1px solid rgba(74,222,128,0.4); }
.dark-table thead th { padding:0.9rem 1.1rem; color:#ffffff; font-weight:700; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.12em; text-align:left; font-family:'JetBrains Mono',monospace; }
.dark-table tbody tr { border-bottom:1px solid rgba(74,222,128,0.1); transition:background 0.15s; }
.dark-table tbody tr:last-child { border-bottom:none; }
.dark-table tbody tr:nth-child(even) { background:rgba(20,50,28,0.6); }
.dark-table tbody tr:nth-child(odd) { background:rgba(14,35,20,0.8); }
.dark-table tbody tr:hover { background:rgba(74,222,128,0.1) !important; }
.dark-table tbody td { padding:0.78rem 1.1rem; color:#e2fce8; line-height:1.55; font-weight:400; }
.dark-table tbody td:first-child { color:var(--amber); font-family:'JetBrains Mono',monospace; font-size:0.76rem; font-weight:600; }
.badge-pos   { background:rgba(74,222,128,0.18); color:#4ade80; border:1px solid rgba(74,222,128,0.35); font-size:0.67rem; padding:2px 9px; border-radius:100px; font-weight:600; display:inline-block; }
.badge-resp  { background:rgba(251,191,36,0.15); color:#fbbf24; border:1px solid rgba(251,191,36,0.35); font-size:0.67rem; padding:2px 9px; border-radius:100px; font-weight:600; display:inline-block; }
.badge-mixed { background:rgba(100,155,220,0.15); color:#93c5fd; border:1px solid rgba(100,155,220,0.35); font-size:0.67rem; padding:2px 9px; border-radius:100px; font-weight:600; display:inline-block; }

/* ===== ABOUT GRID ===== */
.about-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:1.2rem; margin-bottom:1.3rem; }
.about-card { background:rgba(18,45,24,0.90); border:1px solid var(--border); border-radius:var(--radius-sm); padding:1.65rem; transition:border-color 0.2s; }
.about-card:hover { border-color:var(--border-hi); }
.about-card h4 { font-family:'Playfair Display',serif !important; font-size:1rem !important; color:var(--amber) !important; margin:0 0 0.7rem 0 !important; }
.about-card p, .about-card li { font-size:0.82rem; color:#e2fce8; line-height:1.85; margin:0; font-weight:300; }
.about-card ul { padding-left:1.1rem; margin:0; }
.about-card li { margin-bottom:0.2rem; }

/* ===== LEGEND BAR ===== */
.legend-bar { display:flex; gap:1rem; align-items:center; background:rgba(14,35,20,0.92); border:1px solid var(--border); border-radius:100px; padding:0.5rem 1.2rem; width:fit-content; margin-bottom:1rem; backdrop-filter:blur(10px); }
.lgnd-item { display:flex; align-items:center; gap:0.4rem; font-size:0.74rem; color:#e2fce8; font-weight:500; }
.lgnd-dot { width:10px; height:10px; border-radius:50%; border:1.5px solid rgba(255,255,255,0.2); }

/* ===== INTERPRETATION PANEL ===== */
.interp-panel { background:rgba(14,35,20,0.92); border:1px solid rgba(74,222,128,0.3); border-radius:var(--radius); padding:2rem 2.25rem; margin-bottom:1.2rem; position:relative; overflow:hidden; }
.interp-panel::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,transparent,var(--leaf),transparent); opacity:0.5; }
.interp-panel h3 { font-family:'Playfair Display',serif !important; font-size:1.1rem !important; color:var(--amber) !important; margin:0 0 1rem 0 !important; }
.interp-panel p { font-size:0.86rem; color:#e2fce8; line-height:2.0; margin:0; }
.interp-mono { background:rgba(10,25,14,0.85); border:1px solid rgba(74,222,128,0.25); border-radius:var(--radius-xs); padding:0.75rem 1rem; margin-top:1rem; font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:var(--leaf); line-height:1.9; }

/* ===== STAT HIGHLIGHT ===== */
.stat-highlight { background:rgba(20,55,28,0.85); border:1px solid rgba(74,222,128,0.3); border-radius:var(--radius-sm); padding:1.4rem 2rem; text-align:center; }
.stat-highlight .val { font-family:'Playfair Display',serif; font-size:2.8rem; color:var(--amber); display:block; line-height:1; font-weight:700; }
.stat-highlight .lbl { font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:var(--leaf); text-transform:uppercase; letter-spacing:0.16em; display:block; margin-top:0.4rem; }

/* ===== DISCLAIMER ===== */
.disclaimer { background:rgba(251,191,36,0.07); border:1px solid rgba(251,191,36,0.25); border-radius:var(--radius-xs); padding:1rem 1.5rem; margin-top:1rem; }
.disclaimer p { color:var(--amber-lt); font-size:0.78rem; margin:0; line-height:1.75; }

/* ===== STREAMLIT OVERRIDES ===== */
[data-baseweb="select"] > div { background:rgba(14,38,20,0.92) !important; border-color:rgba(74,222,128,0.3) !important; }
[data-baseweb="select"] * { color:var(--mist) !important; }

button[data-baseweb="tab"] { font-family:'Inter',sans-serif !important; font-weight:600 !important; color:var(--leaf) !important; background:transparent !important; font-size:0.85rem !important; padding:0.6rem 1.2rem !important; }
button[data-baseweb="tab"][aria-selected="true"] { color:var(--amber) !important; border-bottom-color:var(--amber) !important; }
[data-baseweb="tab-list"] { background:transparent !important; border-bottom:1px solid var(--border) !important; gap:0.2rem; margin-bottom:1.3rem; }
[data-baseweb="tab-panel"] { padding-top:0 !important; }

div.stButton > button {
    background:linear-gradient(135deg, rgba(22,163,74,0.85), rgba(15,80,35,0.9)) !important;
    color:#ffffff !important; font-family:'Inter',sans-serif !important; font-weight:600 !important;
    font-size:0.84rem !important; border:1px solid rgba(74,222,128,0.3) !important;
    border-radius:var(--radius-sm) !important; padding:0.62rem 1.45rem !important; height:auto !important; transition:var(--trans) !important;
}
div.stButton > button:hover { background:linear-gradient(135deg, rgba(30,180,90,0.9), rgba(22,163,74,0.85)) !important; border-color:var(--border-hi) !important; transform:translateY(-2px) !important; box-shadow:0 6px 20px rgba(0,0,0,0.4) !important; }

[data-testid="stDataFrame"] { border:1px solid rgba(74,222,128,0.3) !important; border-radius:var(--radius-sm) !important; overflow:hidden; }

/* Dataframe internal styling — make text visible */
[data-testid="stDataFrame"] table { background:rgba(14,38,20,0.95) !important; }
[data-testid="stDataFrame"] th { background:rgba(22,100,50,0.85) !important; color:#ffffff !important; font-weight:700 !important; border-bottom:1px solid rgba(74,222,128,0.3) !important; }
[data-testid="stDataFrame"] td { color:#e2fce8 !important; border-bottom:1px solid rgba(74,222,128,0.08) !important; }
[data-testid="stDataFrame"] tr:nth-child(even) td { background:rgba(20,52,28,0.6) !important; }

[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label,
[data-testid="stFileUploader"] label,
[data-testid="stTextInput"] label { color:var(--mist) !important; font-family:'JetBrains Mono',monospace !important; font-size:0.68rem !important; font-weight:500 !important; text-transform:uppercase; letter-spacing:0.1em; }

[data-testid="stMetricLabel"] { color:var(--leaf) !important; font-family:'JetBrains Mono',monospace !important; font-size:0.62rem !important; text-transform:uppercase; letter-spacing:0.14em; }
[data-testid="stMetricValue"] { color:var(--amber) !important; font-family:'Playfair Display',serif !important; }
[data-testid="stMetricDelta"] { color:var(--leaf) !important; }

[data-testid="stFileUploader"] { background:rgba(14,38,20,0.85) !important; border:2px dashed rgba(22,163,74,0.5) !important; border-radius:var(--radius-sm) !important; }
[data-testid="stFileUploaderDropzone"] { background:transparent !important; }

details { background:rgba(14,38,20,0.85) !important; border:1px solid var(--border) !important; border-radius:var(--radius-xs) !important; padding:0.4rem 1rem !important; }
summary { color:var(--mist) !important; font-family:'Inter',sans-serif !important; font-weight:600 !important; font-size:0.85rem !important; }

.stAlert { border-radius:var(--radius-xs) !important; border-left:3px solid var(--canopy) !important; background:rgba(18,52,26,0.8) !important; }
[data-testid="stSuccessAlert"] { border-left-color:var(--leaf) !important; }
[data-testid="stWarningAlert"] { border-left-color:var(--amber) !important; }
[data-testid="stSpinner"] > div { border-top-color:var(--leaf) !important; }

hr { border-color:rgba(74,222,128,0.18) !important; margin:2rem 0 !important; }

input[type="text"] { background:rgba(14,38,20,0.9) !important; border-color:rgba(74,222,128,0.3) !important; color:var(--mist) !important; border-radius:var(--radius-xs) !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 5. HELPERS
# ============================================================
@st.cache_data(show_spinner=False)
def load_geojson():
    try:
        r = requests.get(
            "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json",
            timeout=10
        )
        return r.json()
    except Exception:
        return None


def go_page(p: str):
    st.session_state.page = p
    st.rerun()


@st.cache_data(show_spinner=False)
def run_merf(df_json: str, scope: str):
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    df = pd.read_json(io.StringIO(df_json), orient='records')
    available_x = [c for c in COLS_X if c in df.columns]
    if not available_x or COL_Y not in df.columns:
        return None

    # Filter data
    if scope != "Seluruh Indonesia" and COL_PROV in df.columns:
        df_m = df[df[COL_PROV] == scope].copy()
        # Fallback: jika data terlalu sedikit, gabungkan dengan seluruh Indonesia
        if len(df_m) < 5:
            df_m = df.copy()
            scope_used = "Seluruh Indonesia (fallback)"
        else:
            scope_used = scope
    else:
        df_m = df.copy()
        scope_used = scope

    df_m = df_m.dropna(subset=available_x + [COL_Y])
    if len(df_m) < 5:
        return None

    X = df_m[available_x].values
    y = df_m[COL_Y].values

    # Random effects: rata-rata per provinsi sebagai komponen efek acak
    if COL_PROV in df_m.columns and df_m[COL_PROV].nunique() > 1:
        re = df_m.groupby(COL_PROV)[COL_Y].mean()
        prov_re = df_m[COL_PROV].map(re).fillna(y.mean()).values - y.mean()
        X_aug = np.column_stack([X, prov_re])
        feat_names = available_x + ["Random Effect"]
    else:
        X_aug = X
        feat_names = available_x

    np.random.seed(42)
    n_est = 200 if len(y) >= 30 else 100
    rf = RandomForestRegressor(n_estimators=n_est, max_depth=6, random_state=42, n_jobs=-1)
    rf.fit(X_aug, y)
    y_pred = rf.predict(X_aug)
    residuals = y - y_pred

    rmse  = np.sqrt(mean_squared_error(y, y_pred))
    mae   = mean_absolute_error(y, y_pred)
    r2    = r2_score(y, y_pred)
    mape  = np.mean(np.abs((y - y_pred) / (np.abs(y) + 1e-8))) * 100

    label_map = {v: k for k, v in COLS_X_MAP.items()}
    label_map["Random Effect"] = "Efek Acak Provinsi"
    feat_imp = pd.DataFrame({
        "Faktor": feat_names,
        "Importance": rf.feature_importances_,
        "Label": [label_map.get(n, n) for n in feat_names],
    }).sort_values("Importance")

    df_all = df.dropna(subset=[COL_Y])
    if COL_PROV in df_all.columns:
        ranked = df_all.groupby(COL_PROV)[COL_Y].mean().sort_values(ascending=False).reset_index()
        ranked.columns = [COL_PROV, "Rata-rata TCL (Ha)"]
        ranked["Ranking"] = range(1, len(ranked)+1)
    else:
        ranked = pd.DataFrame()

    return {
        "mape": round(mape, 2),
        "rmse": round(rmse / 1000, 2),
        "mae":  round(mae / 1000, 2),
        "r2":   round(r2, 4),
        "feat_imp":     feat_imp.to_dict('records'),
        "actual":       y.tolist(),
        "predicted":    y_pred.tolist(),
        "residuals":    residuals.tolist(),
        "n_obs":        len(y),
        "prov_years":   df_m[COL_YEAR].tolist() if COL_YEAR in df_m.columns else [],
        "ranked_provs": ranked.to_dict('records'),
        "scope_used":   scope_used,
    }


def build_interpretation(res, scope):
    if not res:
        return "Data tidak cukup."
    feat_df = pd.DataFrame(res["feat_imp"]).sort_values("Importance", ascending=False)
    top1 = feat_df.iloc[0]["Label"] if len(feat_df) > 0 else "–"
    top2 = feat_df.iloc[1]["Label"] if len(feat_df) > 1 else "–"
    r2pct = res["r2"] * 100
    perf  = "sangat baik" if r2pct >= 80 else "baik" if r2pct >= 65 else "cukup" if r2pct >= 50 else "perlu peningkatan"
    residuals = np.array(res["residuals"])
    mean_r = residuals.mean(); std_r = residuals.std()
    skew_r = stats.skew(residuals) if len(residuals) > 3 else 0
    skew_txt = "simetris" if abs(skew_r) < 0.5 else ("condong kanan" if skew_r > 0 else "condong kiri")
    scope_txt = "seluruh 34 provinsi Indonesia" if scope == "Seluruh Indonesia" else f"Provinsi {scope}"
    return f"""Model MERF dievaluasi pada data <strong style='color:#fde68a;'>{scope_txt}</strong>
dengan total <strong style='color:#86efac;'>{res["n_obs"]} observasi</strong>.
Performa model tergolong <strong style='color:#fde68a;'>{perf}</strong>, 
R² = <strong style='color:#86efac;'>{res["r2"]:.4f}</strong> ({r2pct:.1f}% variasi dijelaskan model), 
MAPE <strong style='color:#86efac;'>{res["mape"]:.2f}%</strong>, 
RMSE <strong style='color:#86efac;'>{res["rmse"]:.2f} ribu Ha</strong>.
Faktor paling dominan: <strong style='color:#fde68a;'>{top1}</strong>, diikuti <strong style='color:#fde68a;'>{top2}</strong>.
Distribusi residual bersifat <strong style='color:#fde68a;'>{skew_txt}</strong> 
(mean={mean_r:,.0f} Ha, std={std_r:,.0f} Ha, skew={skew_r:.3f}).
<strong style='color:#fde68a;'>Implikasi Kebijakan:</strong>
Pengendalian {top1} dan {top2} di {scope_txt} perlu menjadi prioritas utama dalam program konservasi hutan."""


# ============================================================
# 6. TOP NAV
# ============================================================
page_now = st.session_state.page

NAV = [
    ("home",      "🏠", "Beranda"),
    ("upload",    "📂", "Upload Data"),
    ("dashboard", "📊", "Dashboard"),
    ("predict",   "🧮", "Analisis & Prediksi"),
    ("about",     "📖", "Tentang Penelitian"),
]

st.markdown("""
<div class="topnav">
    <div class="topnav-brand">
        <div class="topnav-logo">🌳</div>
        <div>
            <div class="topnav-name">JAMSICX</div>
            <span class="topnav-sub">Tree Cover Loss</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

nav_cols = st.columns(len(NAV) + 2)
with nav_cols[0]: st.write("")
for i, (pid, picon, plabel) in enumerate(NAV):
    with nav_cols[i + 1]:
        label = f"**{picon} {plabel}**" if page_now == pid else f"{picon} {plabel}"
        if st.button(label, key=f"nav_{pid}", use_container_width=False):
            go_page(pid)
with nav_cols[-1]: st.write("")

st.markdown('<div class="content-area">', unsafe_allow_html=True)

# ============================================================
# PAGE: HOME
# ============================================================
if page_now == "home":

    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-bg"></div>
        <div class="hero-grid"></div>
        <div class="hero-deco">🌳</div>
        <div class="hero-content">
            <div class="hero-eyebrow">
                <span class="hero-line"></span>
                Forest Loss Intelligence · 34 Provinsi Indonesia
            </div>
            <h1 class="hero-title">
                Prediksi &amp; Visualisasi<br>
                <span class="t-green t-italic">Tree Cover Loss</span><br>
                di Indonesia
            </h1>
            <p class="hero-desc">
                Platform analitik berbasis Mixed Effects Random Forest untuk mengidentifikasi 
                dan memprediksi kehilangan tutupan pohon secara spasial dan temporal 
                di seluruh wilayah Indonesia.
            </p>
            <div class="hero-stats">
                <div class="hero-stat">
                    <span class="hs-val">34</span>
                    <span class="hs-lbl">Provinsi</span>
                </div>
                <div class="hero-stat">
                    <span class="hs-val">6</span>
                    <span class="hs-lbl">Variabel Prediktor</span>
                </div>
                <div class="hero-stat">
                    <span class="hs-val">MERF</span>
                    <span class="hs-lbl">Algoritma Model</span>
                </div>
                <div class="hero-stat">
                    <span class="hs-val">BPS</span>
                    <span class="hs-lbl">Sumber Data</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sec-hdr">
        <span class="sec-eye">// Navigasi Modul</span>
        <div class="sec-title">Pilih Modul Analisis</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-bottom-glow" style="background:linear-gradient(90deg,#4ade80,#fbbf24);"></div>
            <div class="feat-arrow">→</div>
            <div class="feat-icon ic-g">📂</div>
            <span class="feat-num">01 / 04</span>
            <span class="feat-title">Upload Dataset CSV</span>
            <span class="feat-desc">Unggah file data penelitian, validasi kolom otomatis, dan eksplorasi statistik deskriptif instan.</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📂 Buka Upload Data →", key="home_upload", use_container_width=True):
            go_page("upload")

    with c2:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-bottom-glow" style="background:linear-gradient(90deg,#38bdf8,#4ade80);"></div>
            <div class="feat-arrow">→</div>
            <div class="feat-icon ic-b">📊</div>
            <span class="feat-num">02 / 04</span>
            <span class="feat-title">Dashboard Deskriptif</span>
            <span class="feat-desc">Peta choropleth interaktif, analisis korelasi, distribusi, dan tren temporal per provinsi.</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 Buka Dashboard →", key="home_dash", use_container_width=True):
            go_page("dashboard")

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-bottom-glow" style="background:linear-gradient(90deg,#fbbf24,#f97316);"></div>
            <div class="feat-arrow">→</div>
            <div class="feat-icon ic-a">🧮</div>
            <span class="feat-num">03 / 04</span>
            <span class="feat-title">Analisis &amp; Prediksi</span>
            <span class="feat-desc">Model MERF dinamis per provinsi: feature importance, evaluasi statistik, diagnostik residual, dan interpretasi otomatis.</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🧮 Buka Analisis & Prediksi →", key="home_pred", use_container_width=True):
            go_page("predict")

    with c4:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-bottom-glow" style="background:linear-gradient(90deg,#86efac,#16a34a);"></div>
            <div class="feat-arrow">→</div>
            <div class="feat-icon ic-m">📖</div>
            <span class="feat-num">04 / 04</span>
            <span class="feat-title">Tentang Penelitian</span>
            <span class="feat-desc">Metodologi MERF, sumber data, definisi variabel, keterbatasan model, dan referensi ilmiah lengkap.</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📖 Buka Tentang Penelitian →", key="home_about", use_container_width=True):
            go_page("about")

    st.markdown("<br>", unsafe_allow_html=True)

    ia, ib = st.columns([3, 2], gap="medium")
    with ia:
        st.markdown("""
        <div class="info-panel">
            <div class="info-panel-title">🔬 Tentang Penelitian</div>
            <p>Penelitian ini menggunakan <strong style="color:#fde68a;">Mixed Effects Random Forest (MERF)</strong> — 
            pendekatan machine learning yang menggabungkan kekuatan Random Forest dengan struktur data panel berlevel, 
            sehingga mampu memodelkan variasi antar-provinsi (random effects) sekaligus pola non-linear dari 
            variabel prediktor (fixed effects).</p>
            <p style="margin-top:0.85rem;">Model dibangun untuk memprediksi kehilangan tutupan pohon berdasarkan 
            enam faktor sosial-ekonomi dan penggunaan lahan di 34 provinsi Indonesia.</p>
            <div class="chip-row">
                <span class="chip">MERF</span>
                <span class="chip">Random Forest</span>
                <span class="chip">Panel Data</span>
                <span class="chip">Spasial</span>
                <span class="chip">Python</span>
                <span class="chip">BPS Data</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ib:
        st.markdown('<div class="info-panel"><div class="info-panel-title">📐 Variabel Penelitian</div>', unsafe_allow_html=True)
        var_df = pd.DataFrame({
            "Simbol": ["Y", "X1", "X2", "X3", "X4", "X5", "X6"],
            "Variabel": ["Tree Cover Loss", "Penutupan Lahan", "Kebakaran",
                         "Perkebunan", "Kepadatan Pddk", "Pop. Ternak", "PDRB Tambang"],
            "Satuan": ["Ha", "Ribu Ha", "Ha", "Ribu Ha", "jiwa/km²", "Ekor", "%"],
        })
        st.dataframe(var_df, use_container_width=True, hide_index=True, height=290)
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# PAGE: UPLOAD DATA
# ============================================================
elif page_now == "upload":
    st.markdown("""
    <div class="page-hdr">
        <div class="page-hdr-icon">📂</div>
        <div>
            <h1>Upload Dataset CSV</h1>
            <p>Unggah file data penelitian — validasi otomatis, preview interaktif, statistik lengkap</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Kembali ke Beranda", key="back_upload"):
        go_page("home")

    st.markdown("<br>", unsafe_allow_html=True)

    uploaded = st.file_uploader("Pilih file CSV", type=["csv"], help="Format CSV dengan delimiter koma.")

    if uploaded is not None:
        with st.spinner("Memuat dan memvalidasi dataset…"):
            try:
                df_up = pd.read_csv(uploaded)
                df_up.columns = df_up.columns.str.strip()
                st.session_state.df = df_up

                n_prov = df_up[COL_PROV].nunique() if COL_PROV in df_up.columns else "–"
                n_yr   = df_up[COL_YEAR].nunique() if COL_YEAR in df_up.columns else "–"

                st.toast("✅ Dataset berhasil dimuat!", icon="🌳")

                st.markdown(f"""
                <div class="metric-grid">
                    <div class="m-card"><span class="m-label">Total Baris</span>
                        <span class="m-value">{len(df_up):,}</span><span class="m-sub">observasi</span></div>
                    <div class="m-card"><span class="m-label">Total Kolom</span>
                        <span class="m-value">{len(df_up.columns)}</span><span class="m-sub">variabel</span></div>
                    <div class="m-card"><span class="m-label">Provinsi</span>
                        <span class="m-value">{n_prov}</span><span class="m-sub">wilayah unik</span></div>
                    <div class="m-card"><span class="m-label">Rentang Tahun</span>
                        <span class="m-value">{n_yr}</span><span class="m-sub">tahun observasi</span></div>
                </div>
                """, unsafe_allow_html=True)

                c_miss, c_dtype = st.columns(2, gap="medium")
                with c_miss:
                    st.markdown('<div class="panel"><div class="panel-title">🔍 Missing Values</div>', unsafe_allow_html=True)
                    miss_df = df_up.isnull().sum().reset_index()
                    miss_df.columns = ["Kolom", "Missing"]
                    miss_df["%"] = (miss_df["Missing"] / len(df_up) * 100).round(2)
                    miss_df = miss_df[miss_df["Missing"] > 0]
                    if len(miss_df) == 0:
                        st.success("✅ Tidak ada missing value.")
                    else:
                        st.dataframe(miss_df, use_container_width=True, hide_index=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with c_dtype:
                    st.markdown('<div class="panel"><div class="panel-title">🗂️ Tipe Data Kolom</div>', unsafe_allow_html=True)
                    dtype_df = df_up.dtypes.reset_index()
                    dtype_df.columns = ["Kolom", "Tipe Data"]
                    dtype_df["Tipe Data"] = dtype_df["Tipe Data"].astype(str)
                    st.dataframe(dtype_df, use_container_width=True, hide_index=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                req_cols = [COL_Y, COL_PROV, COL_YEAR] + COLS_X
                miss_cols = [c for c in req_cols if c not in df_up.columns]
                if miss_cols:
                    st.warning(f"⚠️ Kolom tidak ditemukan: `{'`, `'.join(miss_cols)}`")
                else:
                    st.success("✅ Semua kolom terdeteksi. Dataset siap dianalisis.")

                st.markdown('<div class="panel"><div class="panel-title">🔍 Preview Dataset</div>', unsafe_allow_html=True)
                search_val = st.text_input("🔎 Cari baris…", key="search_prev", placeholder="Ketik nama provinsi atau nilai…")
                if search_val:
                    mask = df_up.astype(str).apply(lambda col: col.str.contains(search_val, case=False, na=False)).any(axis=1)
                    df_show = df_up[mask]
                else:
                    df_show = df_up
                st.dataframe(df_show, use_container_width=True, height=420, hide_index=True)
                st.markdown(f'<p style="font-family:JetBrains Mono,monospace;font-size:0.64rem;color:#4ade80;margin-top:0.4rem;">Menampilkan {len(df_show):,} dari {len(df_up):,} baris</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                with st.expander("📈 Statistik Deskriptif Lengkap"):
                    st.dataframe(df_up.describe().round(2), use_container_width=True)

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📊 Lanjut ke Dashboard →", key="go_dash"):
                    go_page("dashboard")

            except Exception as e:
                st.error(f"❌ Gagal membaca file: {e}")
    else:
        st.markdown("""
        <div class="panel" style="text-align:center; padding:4rem 2rem;">
            <span style="font-size:3rem;display:block;margin-bottom:1rem;opacity:0.4;">📋</span>
            <p style="color:#4ade80;font-size:1rem;margin:0;">Belum ada data yang diunggah.<br>Pilih file CSV di atas untuk memulai.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("ℹ️ Format Kolom yang Diharapkan"):
            exp_df = pd.DataFrame({
                "Nama Kolom": [COL_PROV, COL_YEAR, COL_Y] + COLS_X,
                "Tipe": ["Text", "Integer", "Float"] + ["Float"] * 6,
                "Contoh": ["Kalimantan Tengah", "2020", "125000.5",
                            "12500.0", "8900.0", "3200.0", "85.5", "450000.0", "4.2"]
            })
            st.dataframe(exp_df, use_container_width=True, hide_index=True)


# ============================================================
# PAGE: DASHBOARD
# ============================================================
elif page_now == "dashboard":
    st.markdown("""
    <div class="page-hdr">
        <div class="page-hdr-icon">📊</div>
        <div>
            <h1>Dashboard Deskriptif</h1>
            <p>Analisis spasial, temporal, dan korelasional kehilangan tutupan pohon di Indonesia</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Kembali ke Beranda", key="back_dash"):
        go_page("home")

    if st.session_state.df is None:
        st.warning("⚠️ Belum ada data. Silakan upload CSV terlebih dahulu.")
        if st.button("📂 Upload Data →", key="goto_upload_dash"):
            go_page("upload")
        st.stop()

    df = st.session_state.df

    st.markdown('<div class="panel" style="padding:1.2rem 1.7rem;margin-bottom:1.7rem;">', unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    with f1:
        thn_list = sorted(df[COL_YEAR].unique()) if COL_YEAR in df.columns else [2022]
        sel_thn  = st.selectbox("📅 Tahun Analisis", thn_list, index=len(thn_list)-1, key="thn_sel")
    with f2:
        prov_list = ["Seluruh Indonesia"] + sorted(df[COL_PROV].unique().tolist()) if COL_PROV in df.columns else ["Seluruh Indonesia"]
        sel_prov  = st.selectbox("📍 Fokus Wilayah", prov_list, key="prov_sel")
    st.markdown('</div>', unsafe_allow_html=True)

    is_single = sel_prov != "Seluruh Indonesia"
    df_year   = df[df[COL_YEAR] == sel_thn].copy()

    if st.session_state.geojson is None:
        with st.spinner("Memuat peta GeoJSON Indonesia…"):
            st.session_state.geojson = load_geojson()
    geojson = st.session_state.geojson

    tab1, tab2, tab3 = st.tabs(["🗺️  Peta Spasial", "📈  Korelasi & Distribusi", "📅  Tren Temporal"])

    with tab1:
        # Legenda warna yang jelas
        st.markdown("""
        <div class="legend-bar">
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:#86efac;margin-right:0.5rem;">Intensitas TCL:</span>
            <span class="lgnd-item"><span class="lgnd-dot" style="background:#22c55e;"></span>Rendah</span>
            <span class="lgnd-item"><span class="lgnd-dot" style="background:#facc15;"></span>Sedang</span>
            <span class="lgnd-item"><span class="lgnd-dot" style="background:#ef4444;"></span>Sangat Tinggi</span>
        </div>
        """, unsafe_allow_html=True)

        # Skala warna peta: Hijau → Kuning → Oranye → Merah
        MAP_SCALE = [[0, '#22c55e'], [0.35, '#facc15'], [0.65, '#f97316'], [1, '#ef4444']]

        if geojson:
            with st.spinner("Merender peta…"):
                if is_single:
                    # Tampilkan seluruh Indonesia, highlight provinsi terpilih dengan outline tebal
                    df_map_all = df_year.copy()
                    # Beri nilai highlight: provinsi terpilih = nilai asli, lainnya = NaN (akan menjadi abu)
                    df_map_all["_highlight"] = df_map_all.apply(
                        lambda r: r[COL_Y] if r[COL_PROV] == sel_prov else None, axis=1
                    )
                    fig_map = go.Figure()
                    # Layer 1: semua provinsi (dim)
                    fig_map.add_trace(go.Choropleth(
                        geojson=geojson, locations=df_map_all[COL_PROV],
                        featureidkey="properties.Propinsi",
                        z=df_map_all[COL_Y],
                        colorscale=[[0,'#0f2a18'],[1,'#1e4d2a']],
                        marker_opacity=0.30, marker_line_width=0.5,
                        marker_line_color="rgba(74,222,128,0.2)",
                        showscale=False, hoverinfo="skip",
                    ))
                    # Layer 2: provinsi terpilih (terang + outline)
                    df_sel = df_year[df_year[COL_PROV] == sel_prov]
                    if len(df_sel) > 0:
                        fig_map.add_trace(go.Choropleth(
                            geojson=geojson, locations=df_sel[COL_PROV],
                            featureidkey="properties.Propinsi",
                            z=df_sel[COL_Y],
                            colorscale=[[0,'#22c55e'],[0.5,'#facc15'],[1,'#ef4444']],
                            marker_opacity=1.0, marker_line_width=3.0,
                            marker_line_color="#86efac",
                            showscale=True,
                            colorbar=dict(
                                title=dict(text="TCL (Ha)", font=dict(color='#e2fce8')),
                                tickfont=dict(color='#e2fce8', family='Inter'),
                                bgcolor='rgba(10,25,14,0.92)', bordercolor='rgba(74,222,128,0.3)'),
                            customdata=df_sel[[COL_PROV, COL_Y]],
                            hovertemplate="<b>%{customdata[0]}</b><br>TCL: %{customdata[1]:,.0f} Ha<extra></extra>",
                        ))
                    # Gunakan fitbounds ke seluruh Indonesia agar peta selalu terlihat
                    fig_map.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
                    fig_map.update_layout(
                        height=520, paper_bgcolor='rgba(0,0,0,0)',
                        geo=dict(bgcolor='rgba(0,0,0,0)'),
                        margin=dict(r=0,t=10,l=0,b=0),
                        font=dict(family='Inter',color='#e2fce8'), showlegend=False,
                        title=dict(text=f"<b>{sel_prov}</b> — Tree Cover Loss {sel_thn}",
                                   font=dict(color='#fbbf24', size=14, family='Inter'),
                                   x=0.01, y=0.97),
                    )
                    st.plotly_chart(fig_map, use_container_width=True)

                    if len(df_sel) > 0 and COL_Y in df_sel.columns:
                        sel_val  = df_sel[COL_Y].values[0]
                        rank_df  = df_year.sort_values(COL_Y, ascending=False).reset_index(drop=True)
                        rank_idx = rank_df[rank_df[COL_PROV] == sel_prov].index.tolist()
                        rank_txt = f"#{rank_idx[0]+1}" if rank_idx else "–"
                        prev = df[(df[COL_PROV]==sel_prov)&(df[COL_YEAR]==sel_thn-1)][COL_Y] if COL_YEAR in df.columns else pd.Series(dtype=float)
                        if len(prev):
                            dp = (sel_val - prev.values[0]) / (abs(prev.values[0]) + 1) * 100
                            dt = f"{'▲' if dp>0 else '▼'} {abs(dp):.1f}% vs {sel_thn-1}"
                            dc = "#f87171" if dp > 0 else "#4ade80"
                        else:
                            dt, dc = "–", "#4ade80"
                        a1, a2, a3 = st.columns(3)
                        a1.markdown(f'<div class="stat-highlight"><span class="val">{sel_val/1000:,.1f}k</span><span class="lbl">Tree Cover Loss (Ha)</span></div>', unsafe_allow_html=True)
                        a2.markdown(f'<div class="stat-highlight"><span class="val">{rank_txt} Nasional</span><span class="lbl">Peringkat TCL</span></div>', unsafe_allow_html=True)
                        a3.markdown(f'<div class="stat-highlight"><span class="val" style="color:{dc};font-size:1.6rem;">{dt}</span><span class="lbl">Perubahan YoY</span></div>', unsafe_allow_html=True)
                else:
                    fig_map = px.choropleth(
                        df_year, geojson=geojson, locations=COL_PROV,
                        featureidkey="properties.Propinsi", color=COL_Y,
                        color_continuous_scale=MAP_SCALE,
                        scope="asia", labels={COL_Y: "TCL (Ha)"},
                        hover_name=COL_PROV, hover_data={COL_Y: ":,.0f"},
                    )
                    fig_map.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
                    fig_map.update_layout(height=540, paper_bgcolor='rgba(0,0,0,0)',
                                          geo=dict(bgcolor='rgba(0,0,0,0)'),
                                          margin=dict(r=0,t=10,l=0,b=0),
                                          font=dict(family='Inter',color='#e2fce8'),
                                          coloraxis_colorbar=dict(
                                              tickfont=dict(color='#e2fce8',family='Inter'),
                                              title=dict(text="Ha", font=dict(color='#e2fce8')),
                                              bgcolor='rgba(10,25,14,0.92)', bordercolor='rgba(74,222,128,0.3)'))
                    st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("ℹ️ Peta tidak tersedia — GeoJSON gagal dimuat.")

        if not is_single and COL_Y in df_year.columns:
            st.markdown("##### 🏆 Top 10 Provinsi – TCL Tertinggi")
            top10 = df_year.nlargest(10, COL_Y)
            fig_bar = px.bar(top10, x=COL_Y, y=COL_PROV, orientation='h',
                             color=COL_Y, color_continuous_scale=MAP_SCALE,
                             text=COL_Y, labels={COL_Y:"TCL (Ha)", COL_PROV:"Provinsi"})
            fig_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside', marker_line_width=0)
            fig_bar.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
            apply_theme(fig_bar, 420)
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        cl, cr = st.columns(2)
        with cl:
            st.markdown("##### 🔗 Scatterplot Korelasi")
            pilih_x   = st.selectbox("Variabel X", list(COLS_X_MAP.keys()), key="corr_x")
            col_x_sel = COLS_X_MAP[pilih_x]
            if col_x_sel in df.columns and COL_Y in df.columns:
                pd_data   = df[df[COL_PROV]==sel_prov].copy() if is_single else df_year.copy()
                color_col = COL_YEAR if is_single else COL_Y
                fig_sc = px.scatter(pd_data, x=col_x_sel, y=COL_Y,
                                    trendline="ols" if len(pd_data) > 2 else None,
                                    hover_name=COL_PROV if not is_single else None,
                                    color=color_col,
                                    color_continuous_scale='RdYlGn_r' if not is_single else 'Teal',
                                    labels={col_x_sel: pilih_x, COL_Y: "TCL (Ha)"})
                apply_theme(fig_sc, 380)
                st.plotly_chart(fig_sc, use_container_width=True)
            else:
                st.warning("Kolom tidak tersedia.")
        with cr:
            st.markdown("##### 📦 Distribusi Tree Cover Loss")
            box_data = df[df[COL_PROV]==sel_prov] if is_single else df_year
            if COL_Y in box_data.columns:
                fig_box = px.box(box_data, y=COL_Y,
                                 x=COL_YEAR if is_single and COL_YEAR in box_data.columns else None,
                                 color_discrete_sequence=["#22c55e"],
                                 labels={COL_Y: "TCL (Ha)"}, points="all")
                apply_theme(fig_box, 380)
                st.plotly_chart(fig_box, use_container_width=True)

        if not is_single:
            st.markdown("##### 🌡️ Matriks Korelasi")
            num_cols = [COL_Y] + [v for v in COLS_X if v in df_year.columns]
            if len(num_cols) > 1:
                corr   = df_year[num_cols].corr()
                labels = ["Y"] + [f"X{i+1}" for i in range(len(num_cols)-1)]
                fig_heat = go.Figure(go.Heatmap(
                    z=corr.values, x=labels, y=labels,
                    colorscale='RdYlGn', zmin=-1, zmax=1,
                    text=corr.values.round(2), texttemplate="%{text}",
                    textfont={"size": 11, "family": "JetBrains Mono"},
                ))
                apply_theme(fig_heat, 360)
                fig_heat.update_layout(margin=dict(l=40,r=20,t=20,b=40))
                st.plotly_chart(fig_heat, use_container_width=True)

    with tab3:
        st.markdown("##### 📅 Tren Tree Cover Loss")
        if COL_YEAR in df.columns and COL_PROV in df.columns and COL_Y in df.columns:
            if is_single:
                df_trend  = df[df[COL_PROV]==sel_prov].copy()
                color_arg = dict(color_discrete_sequence=["#4ade80"])
            else:
                top_p     = df.groupby(COL_PROV)[COL_Y].mean().nlargest(10).index.tolist()
                df_trend  = df[df[COL_PROV].isin(top_p)].copy()
                color_arg = dict(color=COL_PROV, color_discrete_sequence=px.colors.qualitative.Safe)
            fig_line = px.line(df_trend.sort_values(COL_YEAR), x=COL_YEAR, y=COL_Y,
                               labels={COL_YEAR:"Tahun", COL_Y:"TCL (Ha)", COL_PROV:"Provinsi"},
                               markers=True, **color_arg)
            apply_theme(fig_line, 460)
            fig_line.update_layout(hovermode="x unified")
            fig_line.update_traces(line_width=2.5, marker_size=8)
            st.plotly_chart(fig_line, use_container_width=True)


# ============================================================
# PAGE: ANALISIS & PREDIKSI
# ============================================================
elif page_now == "predict":
    st.markdown("""
    <div class="page-hdr">
        <div class="page-hdr-icon">🧮</div>
        <div>
            <h1>Analisis &amp; Prediksi Model MERF</h1>
            <p>Feature importance, evaluasi statistik, dan diagnostik residual — dinamis per provinsi</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Kembali ke Beranda", key="back_pred"):
        go_page("home")

    df = st.session_state.df
    if df is None:
        st.warning("⚠️ Belum ada data. Silakan upload CSV terlebih dahulu.")
        if st.button("📂 Upload Data →", key="goto_upload_pred"):
            go_page("upload")
        st.stop()

    # Validasi kolom minimum
    available_x = [c for c in COLS_X if c in df.columns]
    if not available_x or COL_Y not in df.columns:
        st.error(f"❌ Kolom tidak lengkap. Diperlukan: {COL_Y} dan minimal satu kolom X.")
        st.stop()

    st.markdown('<div class="panel" style="padding:1.2rem 1.7rem;margin-bottom:1.7rem;">', unsafe_allow_html=True)
    pc, pi = st.columns([2, 3])
    with pc:
        prov_opts  = ["Seluruh Indonesia"] + sorted(df[COL_PROV].unique().tolist()) if COL_PROV in df.columns else ["Seluruh Indonesia"]
        sel_p_pred = st.selectbox("📍 Fokus Analisis", prov_opts, key="prov_pred")
    with pi:
        st.markdown('<p style="font-size:0.82rem;color:#4ade80;line-height:1.75;margin-top:0.5rem;">ℹ️ Pilih provinsi untuk melatih ulang model MERF. Semua metrik dan grafik diperbarui otomatis.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    df_json = df.to_json(orient='records')

    with st.spinner(f"Melatih model MERF — {sel_p_pred}…"):
        res = run_merf(df_json, sel_p_pred)

    if res is None:
        st.error("❌ Tidak cukup data untuk melatih model. Pastikan data memiliki minimal 5 observasi dan kolom yang lengkap.")
        st.stop()

    # Notifikasi jika fallback ke seluruh Indonesia
    if res.get("scope_used") != sel_p_pred and sel_p_pred != "Seluruh Indonesia":
        st.info(f"ℹ️ Data provinsi {sel_p_pred} terlalu sedikit. Model dilatih menggunakan data seluruh Indonesia sebagai konteks.")

    st.toast(f"✅ Model berhasil dilatih — {sel_p_pred}", icon="🧮")

    # ── Metrics
    st.markdown('<div class="sec-hdr"><span class="sec-eye">// Evaluasi Statistik</span><div class="sec-title">Performa Model</div></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="metric-grid">
        <div class="m-card"><span class="m-label">MAPE</span><span class="m-value">{res["mape"]:.1f}%</span>
            <span class="m-sub">Mean Abs. Percentage Error</span>
            <span class="{'m-delta-up' if res['mape']>15 else 'm-delta-down'}">{'▲ Perlu optimasi' if res['mape']>15 else '✓ Acceptable'}</span></div>
        <div class="m-card"><span class="m-label">RMSE</span><span class="m-value">{res["rmse"]:.2f}k</span>
            <span class="m-sub">Root Mean Square Error (ribu Ha)</span></div>
        <div class="m-card"><span class="m-label">MAE</span><span class="m-value">{res["mae"]:.2f}k</span>
            <span class="m-sub">Mean Absolute Error (ribu Ha)</span></div>
        <div class="m-card"><span class="m-label">R²</span><span class="m-value">{res["r2"]:.4f}</span>
            <span class="m-sub">Variance Explained {res['r2']*100:.1f}%</span>
            <span class="{'m-delta-down' if res['r2']>=0.75 else 'm-delta-up'}">{'✓ Model Baik' if res['r2']>=0.75 else '▲ Perlu Peningkatan'}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr"><span class="sec-eye">// Interpretabilitas</span><div class="sec-title">Feature Importance &amp; Diagnostik</div></div>', unsafe_allow_html=True)

    cl, cr = st.columns([3, 2], gap="medium")
    with cl:
        st.markdown('<div class="panel"><div class="panel-title">🏆 Feature Importance – MERF</div>', unsafe_allow_html=True)
        feat_df = pd.DataFrame(res["feat_imp"])
        if len(feat_df) > 0:
            fig_imp = px.bar(feat_df, x="Importance", y="Label", orientation='h',
                             color="Importance",
                             color_continuous_scale=[[0,'#22c55e'],[0.5,'#facc15'],[1,'#ef4444']],
                             text="Importance", labels={"Importance":"Score","Label":"Variabel"})
            fig_imp.update_traces(texttemplate='%{text:.3f}', textposition='outside', marker_line_width=0)
            apply_theme(fig_imp, 420)
            fig_imp.update_layout(showlegend=False, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_imp, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with cr:
        st.markdown('<div class="panel"><div class="panel-title">📈 Actual vs. Predicted</div>', unsafe_allow_html=True)
        actual_v = np.array(res["actual"])
        pred_v   = np.array(res["predicted"])
        err      = actual_v - pred_v
        hover_t  = [str(y) for y in res["prov_years"]] if res["prov_years"] else [str(i) for i in range(len(actual_v))]

        fig_avp = go.Figure()
        fig_avp.add_trace(go.Scatter(
            x=actual_v, y=pred_v, mode='markers',
            marker=dict(
                color=np.abs(err),
                colorscale=[[0,'#22c55e'],[0.5,'#facc15'],[1,'#ef4444']],
                size=10, opacity=0.88,
                colorbar=dict(title=dict(text="|Error|",font=dict(color='#e2fce8')),
                              tickfont=dict(color='#e2fce8',family='Inter'),
                              bgcolor='rgba(10,25,14,0.92)',bordercolor='rgba(74,222,128,0.3)'),
                line=dict(width=0.5,color='rgba(255,255,255,0.2)')),
            customdata=np.column_stack([hover_t, err]),
            hovertemplate="<b>%{customdata[0]}</b><br>Aktual: %{x:,.0f}<br>Prediksi: %{y:,.0f}<br>Error: %{customdata[1]:,.0f}<extra></extra>",
        ))
        mx = max(actual_v.max(), pred_v.max()) * 1.06
        fig_avp.add_shape(type="line", x0=0, y0=0, x1=mx, y1=mx, line=dict(color="#fbbf24", dash="dash", width=2))
        fig_avp.add_annotation(x=mx*0.8, y=mx*0.87, text="y = x", showarrow=False, font=dict(color="#fbbf24",size=11,family='Inter'))
        apply_theme(fig_avp, 420)
        fig_avp.update_layout(showlegend=False)
        st.plotly_chart(fig_avp, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Residuals
    st.markdown('<div class="panel"><div class="panel-title">🔎 Distribusi Residual Model</div>', unsafe_allow_html=True)
    residuals = np.array(res["residuals"])
    mean_r = residuals.mean(); std_r = residuals.std()
    skew_r = stats.skew(residuals) if len(residuals) > 3 else 0
    kurt_r = stats.kurtosis(residuals) if len(residuals) > 3 else 0

    ra, rb, rc, rd = st.columns(4)
    ra.markdown(f'<div class="m-card"><span class="m-label">Mean Residual</span><span class="m-value" style="font-size:1.5rem;">{mean_r:,.0f}</span><span class="m-sub">Ha</span></div>', unsafe_allow_html=True)
    rb.markdown(f'<div class="m-card"><span class="m-label">Std Residual</span><span class="m-value" style="font-size:1.5rem;">{std_r:,.0f}</span><span class="m-sub">Ha</span></div>', unsafe_allow_html=True)
    rc.markdown(f'<div class="m-card"><span class="m-label">Skewness</span><span class="m-value" style="font-size:1.5rem;">{skew_r:.3f}</span><span class="m-sub">{"Positif" if skew_r>0 else "Negatif"}</span></div>', unsafe_allow_html=True)
    rd.markdown(f'<div class="m-card"><span class="m-label">Kurtosis</span><span class="m-value" style="font-size:1.5rem;">{kurt_r:.3f}</span><span class="m-sub">{"Leptokurtik" if kurt_r>0 else "Platikurtik"}</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    fig_res = go.Figure()
    counts, edges = np.histogram(residuals, bins=min(25, max(5, len(residuals)//3)))
    centers = (edges[:-1] + edges[1:]) / 2
    fig_res.add_trace(go.Bar(x=centers, y=counts,
                              marker_color='rgba(22,163,74,0.7)',
                              marker_line_color='rgba(74,222,128,0.5)', marker_line_width=1,
                              name="Frekuensi"))
    if len(residuals) > 3:
        kde_x = np.linspace(residuals.min(), residuals.max(), 200)
        kde_y = stats.gaussian_kde(residuals)(kde_x)
        fig_res.add_trace(go.Scatter(x=kde_x, y=kde_y * counts.max() / kde_y.max(),
                                      mode='lines', line=dict(color='#fbbf24', width=2.5), name='KDE'))
    fig_res.add_vline(x=0, line_dash="dash", line_color="#4ade80", line_width=2,
                      annotation_text="  μ=0", annotation_font_color="#4ade80", annotation_font_family="Inter")
    apply_theme(fig_res, 300)
    fig_res.update_layout(bargap=0.05, hovermode="x unified")
    st.plotly_chart(fig_res, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Data historis provinsi
    if sel_p_pred != "Seluruh Indonesia" and COL_PROV in df.columns:
        df_ctx = df[df[COL_PROV] == sel_p_pred].copy()
        if len(df_ctx) > 0:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(f'<div class="panel"><div class="panel-title">📋 Data Historis – {sel_p_pred.upper()}</div>', unsafe_allow_html=True)
            sort_opts = [c for c in [COL_YEAR, COL_Y] + COLS_X if c in df_ctx.columns]
            sort_col  = st.selectbox("Urutkan berdasarkan", sort_opts, key="sort_hist")
            st.dataframe(df_ctx.sort_values(sort_col, ascending=False).reset_index(drop=True),
                         use_container_width=True, height=min(len(df_ctx)*38+60, 460), hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Interpretasi
    st.markdown("<hr>", unsafe_allow_html=True)
    interp = build_interpretation(res, sel_p_pred)
    st.markdown(f"""
    <div class="interp-panel">
        <h3>📖 Interpretasi Model MERF — {sel_p_pred}</h3>
        <p>{interp}</p>
        <div class="interp-mono">
            N_obs = {res["n_obs"]} | R² = {res["r2"]:.4f} | MAPE = {res["mape"]:.2f}% |
            RMSE = {res["rmse"]:.2f}k Ha | Mean Residual = {mean_r:,.0f} Ha | Skewness = {skew_r:.3f}
        </div>
    </div>
    <div class="disclaimer">
        <p><strong>⚠️ Disclaimer:</strong> Hasil analisis bersifat estimatif berdasarkan pola historis data panel.
        Model tidak menggantikan analisis lapangan dan dimaksudkan sebagai alat <em>policy insight</em>.
        Akurasi bergantung pada kualitas dan kelengkapan data yang diunggah.</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGE: TENTANG PENELITIAN
# ============================================================
elif page_now == "about":
    st.markdown("""
    <div class="page-hdr">
        <div class="page-hdr-icon">📖</div>
        <div>
            <h1>Tentang Penelitian</h1>
            <p>Metodologi MERF, sumber data, variabel, dan keterbatasan model</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Kembali ke Beranda", key="back_about"):
        go_page("home")

    st.markdown("""
    <div class="about-grid">
        <div class="about-card">
            <h4>🎯 Tujuan Penelitian</h4>
            <p>Menganalisis dan memprediksi kehilangan tutupan pohon (Tree Cover Loss) di 34 provinsi 
            Indonesia menggunakan Mixed Effects Random Forest — yang mempertimbangkan variasi 
            antar-wilayah sebagai efek acak dalam model data panel.</p>
        </div>
        <div class="about-card">
            <h4>📦 Sumber Data</h4>
            <ul>
                <li>Badan Pusat Statistik (BPS) Indonesia</li>
                <li>BPS – Data Tree Cover Loss per Provinsi</li>
                <li>BPS – Data Kebakaran Hutan dan Lahan</li>
                <li>BPS – Statistik Pertanian dan Perkebunan</li>
                <li>BPS – Populasi Ternak dan Kepadatan Penduduk</li>
            </ul>
        </div>
        <div class="about-card">
            <h4>🤖 Algoritma MERF</h4>
            <p>Mixed Effects Random Forest menggabungkan:</p>
            <ul>
                <li><strong style="color:#fbbf24;">Fixed Effects:</strong> Random Forest – pola non-linear</li>
                <li><strong style="color:#fbbf24;">Random Effects:</strong> Komponen acak antar-provinsi</li>
                <li><strong style="color:#fbbf24;">Estimasi:</strong> EM Algorithm</li>
                <li><strong style="color:#fbbf24;">Keunggulan:</strong> Robust, multi-level, non-parametrik</li>
            </ul>
        </div>
        <div class="about-card">
            <h4>⚠️ Keterbatasan Model</h4>
            <ul>
                <li>Estimasi bersifat indikatif, bukan presisi spasial tinggi</li>
                <li>Terbatas pada 34 provinsi (bukan kabupaten/kota)</li>
                <li>Tidak mempertimbangkan faktor iklim (curah hujan, ENSO)</li>
                <li>Rentang proyeksi terbatas pada pola historis</li>
                <li>Perlu pembaruan berkala seiring penambahan data</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### 📋 Definisi Variabel Penelitian")
    st.markdown("""
    <div class="dark-table-wrap">
        <table class="dark-table">
            <thead>
                <tr>
                    <th>Simbol</th><th>Nama Variabel</th><th>Satuan</th><th>Sumber Data</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>Y</td><td>Tree Cover Loss</td><td>Ha</td><td>Badan Pusat Statistik (BPS)</td></tr>
                <tr><td>X1</td><td>Luas Penutupan Lahan</td><td>Ribu Ha</td><td>Badan Pusat Statistik (BPS)</td></tr>
                <tr><td>X2</td><td>Luas Kebakaran Hutan &amp; Lahan</td><td>Ha</td><td>Badan Pusat Statistik (BPS)</td></tr>
                <tr><td>X3</td><td>Total Luas Tanaman Perkebunan</td><td>Ribu Ha</td><td>Badan Pusat Statistik (BPS)</td></tr>
                <tr><td>X4</td><td>Kepadatan Penduduk</td><td>jiwa/km²</td><td>Badan Pusat Statistik (BPS)</td></tr>
                <tr><td>X5</td><td>Total Populasi Ternak</td><td>Ekor</td><td>Badan Pusat Statistik (BPS)</td></tr>
                <tr><td>X6</td><td>PDRB Pertambangan &amp; Penggalian</td><td>%</td><td>Badan Pusat Statistik (BPS)</td></tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="panel-title">📚 Referensi Utama</div>', unsafe_allow_html=True)
    st.markdown("""
    <ul style="font-size:0.83rem;color:#bbf7d0;line-height:2.1;margin:0;padding-left:1.1rem;font-weight:300;">
        <li>Hajjem, A., Bellavance, F., &amp; Larocque, G. (2011). <em>Mixed-effects random forests for clustered data.</em> Journal of Statistical Computation and Simulation.</li>
        <li>Hansen, M.C., et al. (2013). <em>High-resolution global maps of 21st-century forest cover change.</em> Science, 342(6160), 850–853.</li>
        <li>Badan Pusat Statistik. (2023). <em>Statistik Indonesia.</em> BPS Republik Indonesia.</li>
        <li>Breiman, L. (2001). <em>Random Forests.</em> Machine Learning, 45(1), 5–32.</li>
    </ul>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)