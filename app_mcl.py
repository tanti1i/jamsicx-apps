import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np
import io

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
        background-color: transparent !important; 
        border-radius: 20px; 
        padding: 0px; 
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

    /* Dashboard Premium Styles */
    .dash-header { 
        font-size: 1.9rem; font-weight: 800; color: #facc15;
        letter-spacing: 1px; margin-bottom: 6px;
        text-shadow: 0 2px 10px rgba(250,204,21,0.4);
    }
    .legend-bar {
        background: rgba(10, 25, 41, 0.75);
        border: 1px solid rgba(250, 204, 21, 0.35);
        border-radius: 14px; padding: 12px 24px;
        display: flex; align-items: center; gap: 14px;
        backdrop-filter: blur(10px); margin-bottom: 18px;
    }
    .legend-label { color: #f1f5f9; font-size: 0.88rem; font-weight: 600; }
    .metric-glass {
        background: rgba(10, 25, 41, 0.72);
        border: 1px solid rgba(250,204,21,0.25);
        border-radius: 16px; padding: 16px 20px;
        backdrop-filter: blur(12px);
        text-align: center;
        margin-bottom: 14px;
    }
    .metric-glass .val { font-size: 1.6rem; font-weight: 800; color: #ffffff; }
    .metric-glass .lbl { font-size: 0.78rem; color: #facc15; font-weight: 600; margin-top: 2px; }
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

# --- 4b. EMBEDDED RESEARCH DATA ---
@st.cache_data
def get_embedded_data():
    csv_raw = """ID PROVINSI,PROVINSI,TAHUN,X1 (LUAS PENUTUPAN LAHAN - RIBU Ha),X2 (LUAS KEBAKARAN HUTAN DAN LAHAN - Ha),X3 (TOTAL LUAS TANAMAN PERKEBUNAN - RIBU Ha),X4 (KEPADATAN PENDUDUK - jiwa/km2),X5  (TOTAL POPULASI TERNAK - EKOR),X6 (PDRB PERTAMBANGAN DAN PENGGALIAN PERSEN) ,Y (TREE COVER LOSS- Ha)
P01,ACEH,2015,3161.9,913.27,14978.1,86,1460012.63,5.69,33969
P01,ACEH,2016,3270.9,9158.45,819.8,88,1541017,4.67,50074
P01,ACEH,2017,3120.2,3885.16,882.4,90,1511575,4.64,45813
P01,ACEH,2018,3110.2,1284.7,919.2,91,1155974,4.99,46111
P01,ACEH,2019,3155.6,730,915.4,93,1204409,4.82,28562
P01,ACEH,2020,3126.2,1078,917.4,91,1280377,4.45,30225
P01,ACEH,2021,3135.9,1267,910.9,92,1323270,6.65,31786
P01,ACEH,2022,3144.9,3716,888.6,95,1438218,9.12,29785
P01,ACEH,2023,3151.1,1936.86,853.25,96,466405,7.47,38983
P01,ACEH,2024,3119.16,7257.35,860.99,98,1066153,7.05,46071
P02,SUMATERA UTARA,2015,1759.9,6010.92,2973.5,191,3348981,1.34,53040
P02,SUMATERA UTARA,2016,1813.1,33028.62,2045.3,193,3433195,1.35,79282
P02,SUMATERA UTARA,2017,1785.9,767.98,2180.3,195,3581707,1.3,74551
P02,SUMATERA UTARA,2018,1778.4,3678.79,2232,198,3881936,1.29,66196
P02,SUMATERA UTARA,2019,1853.4,2514,2050.5,200,3651387,1.27,51889
P02,SUMATERA UTARA,2020,1899.5,3744,1995.2,203,2702862,1.28,50234
P02,SUMATERA UTARA,2021,1885.1,4078,1951.1,205,2632771,1.25,59204
P02,SUMATERA UTARA,2022,1910.7,7516,2015.9,209,2608034,1.21,49218
P02,SUMATERA UTARA,2023,1945.9,2113.75,1972.93,212,668925,1.17,65335
P02,SUMATERA UTARA,2024,1932.68,7032.27,1965.18,215,1847763,1.16,64259
P03,SUMATERA BARAT,2015,1934.7,3940.14,2910.2,124,835490.95,4.84,22500
P03,SUMATERA BARAT,2016,1924.1,2629.82,796.7,125,836203,4.53,39172
P03,SUMATERA BARAT,2017,1936.6,2227.43,786.3,127,792575,4.27,51512
P03,SUMATERA BARAT,2018,1931,2421.9,754.9,128,763653,4.27,37400
P03,SUMATERA BARAT,2019,1907.1,2133,742.7,130,776407,4.3,30977
P03,SUMATERA BARAT,2020,1912.8,1573,725.1,132,783239,4.28,30395
P03,SUMATERA BARAT,2021,1891,2068,747.4,133,806189,4.19,35801
P03,SUMATERA BARAT,2022,1907.3,9832,752.3,134,772206,4.09,35602
P03,SUMATERA BARAT,2023,1891.1,4885.13,728.55,137,288192,4.08,35180
P03,SUMATERA BARAT,2024,1879.08,3052.2,733.3,139,764141,3.88,32209
P04,RIAU,2015,2350,183808.59,4085.7,73,520389,30.63,90762
P04,RIAU,2016,2617.6,85219.51,2882.4,75,503342,28.16,147085
P04,RIAU,2017,2304.3,6866.09,2991.9,77,534192,25.92,123675
P04,RIAU,2018,2260.5,37236.27,3469,78,467332,27.87,101107
P04,RIAU,2019,2459.2,90550,3502,80,538951,24.25,102819
P04,RIAU,2020,2665.7,15442,3618.9,73,539188,17.73,94605
P04,RIAU,2021,2580.9,8970,3640.5,75,571851,19.68,95679
P04,RIAU,2022,2577,4915,3559.5,74,556897,22.7,86882
P04,RIAU,2023,2561.9,7267.03,4075.23,74,413130,19.78,115270
P04,RIAU,2024,2515.6,11027.96,4050.29,75,530517,18.5,100670
P05,JAMBI,2015,1341.3,115634.34,4519.7,68,744926.13,19,60611
P05,JAMBI,2016,1385.6,8281.25,1189.2,69,762008,16.54,157246
P05,JAMBI,2017,1283.4,109.17,1297.4,70,778878,17.79,86203
P05,JAMBI,2018,1274.2,1577.75,1572.9,71,750952,19.84,69978
P05,JAMBI,2019,1253.2,56593,1580.5,72,682215,18.44,67673
P05,JAMBI,2020,1345.3,1002,1626.5,71,683130,12.28,78387
P05,JAMBI,2021,1328.5,540,1646.1,72,701170,14.2,73131
P05,JAMBI,2022,1360.1,918,1633.3,74,674071,19.23,75657
P05,JAMBI,2023,1483.5,6539.68,1478.75,75,250429,15.31,93816
P05,JAMBI,2024,1464.94,5636.69,1485.25,76,266659,13.41,91324
P06,SUMATERA SELATAN,2015,1200.6,646298.8,3386,88,751629,21.84,169040
P06,SUMATERA SELATAN,2016,1536.4,8784.91,2101.4,89,765222,19.71,275754
P06,SUMATERA SELATAN,2017,1144.4,3625.66,2218.1,90,711327,19.24,124661
P06,SUMATERA SELATAN,2018,1141,16226.6,2347.1,91,762146,20.17,125458
P06,SUMATERA SELATAN,2019,1445,336798,2405.2,92,769938,20.33,102590
P06,SUMATERA SELATAN,2020,1549.8,950,2422.6,92,799625,18.32,108366
P06,SUMATERA SELATAN,2021,1506.8,5245,2311.5,93,815407,21.03,77866
P06,SUMATERA SELATAN,2022,1540.3,3723,2367.2,100,797557,27.71,87810
P06,SUMATERA SELATAN,2023,1566.2,132082.86,2391.48,101,624025,26.6,139240
P06,SUMATERA SELATAN,2024,1553.63,15422.48,2434.7,102,804492,24.6,120445
P07,BENGKULU,2015,688.9,931.76,2643,94,386582,3.97,20197
P07,BENGKULU,2016,681.5,1000.39,495.1,96,419799,3.74,24378
P07,BENGKULU,2017,685.1,131.04,545.6,97,446619,3.56,27232
P07,BENGKULU,2018,677.2,8.82,521.9,99,393011,3.44,24624
P07,BENGKULU,2019,674.6,11,520.7,100,395234,3.34,18200
P07,BENGKULU,2020,191.9,221,533.6,101,402029,3.26,16311
P07,BENGKULU,2021,654.2,93,533.5,102,407138,4.96,14326
P07,BENGKULU,2022,651.3,1620,627,102,429001,7.45,23800
P07,BENGKULU,2023,647.4,75.94,613.99,104,221702,5.71,29912
P07,BENGKULU,2024,638.81,355.05,621.8,105,229869,4.2,20998
P08,LAMPUNG,2015,339.1,71326.49,1318.6,234,2081711,5.67,14132
P08,LAMPUNG,2016,354.9,3201.24,821.7,237,2128972,5.49,16242
P08,LAMPUNG,2017,334.4,6177.79,839.7,239,2174044,5.65,11761
P08,LAMPUNG,2018,333.1,15156.22,810.4,242,2401743,5.74,10337
P08,LAMPUNG,2019,335.9,35546,819.6,244,2458177,5.55,13177
P08,LAMPUNG,2020,665,1358,822.8,260,2467227,5.01,9472
P08,LAMPUNG,2021,322.3,5411,829.2,262,2668600,5.6,7605
P08,LAMPUNG,2022,330.4,7989,696.8,273,2696007,5.89,7023
P08,LAMPUNG,2023,332,6506.67,802.28,277,2571682,5.25,21635
P08,LAMPUNG,2024,328.93,13242.01,788.86,281,2942565,5.11,12943
P09,KEP. BANGKA BELITUNG,2015,233.3,19770.81,1086.6,84,46877,12.69,41281
P09,KEP. BANGKA BELITUNG,2016,229.7,0,289.9,85,43217,11.9,58203
P09,KEP. BANGKA BELITUNG,2017,221.8,0,298.6,87,49942,11.71,25558
P09,KEP. BANGKA BELITUNG,2018,218.1,2055.67,282,89,48369,10.61,22426
P09,KEP. BANGKA BELITUNG,2019,192.1,4778,283.7,91,46056,9.51,25529
P09,KEP. BANGKA BELITUNG,2020,344.2,576,298.6,89,43740,8.57,24628
P09,KEP. BANGKA BELITUNG,2021,205,385,298.1,90,32422,9.55,31006
P09,KEP. BANGKA BELITUNG,2022,209.1,328,306.6,90,28778,8.63,34052
P09,KEP. BANGKA BELITUNG,2023,238.1,4752.98,302.16,91,26657,7.58,50388
P09,KEP. BANGKA BELITUNG,2024,227.93,2915.46,310.87,92,35023,7.55,31059
P10,KEP. RIAU,2015,245,0,346.6,241,342224,15.74,5869
P10,KEP. RIAU,2016,268.7,67.36,66.8,247,367757,15.29,13058
P10,KEP. RIAU,2017,268.8,19.61,67.2,254,414654,14.08,7993
P10,KEP. RIAU,2018,269.1,320.96,63.5,260,407925,14.13,6266
P10,KEP. RIAU,2019,271.6,6134,63.6,267,332875,13.06,8888
P10,KEP. RIAU,2020,284.1,8805,64.2,252,412026,11.16,8779
P10,KEP. RIAU,2021,286.8,1588,63.9,258,311500,12.59,4391
P10,KEP. RIAU,2022,322.6,23,64.2,264,287378,12.58,2845
P10,KEP. RIAU,2023,330.3,724.26,61.58,260,15183,11.17,3343
P10,KEP. RIAU,2024,329.14,1498.66,62.03,264,45536,9.72,2623
P11,DKI JAKARTA,2015,0.3,0,77.8,15328,11509,0.25,0
P11,DKI JAKARTA,2016,0.3,0,0,15478,12198,0.24,0
P11,DKI JAKARTA,2017,0.3,0,0,15624,10669,0.24,1
P11,DKI JAKARTA,2018,0.3,0,0,15764,11084,0.25,0
P11,DKI JAKARTA,2019,0.3,0,0,15900,11668,0.22,0
P11,DKI JAKARTA,2020,152.9,0,0,15907,10978,0.17,0
P11,DKI JAKARTA,2021,1.1,0,0,15978,10932,0.22,1
P11,DKI JAKARTA,2022,1.1,0,0,16158,9043,0.25,0
P11,DKI JAKARTA,2023,1.1,0,0,16146,16849,0.17,0
P11,DKI JAKARTA,2024,1.1,0.51,0,16165,9210,0.16,0
P12,JAWA BARAT,2015,634.7,2886.03,404.1,1320,14862991,1.71,3502
P12,JAWA BARAT,2016,650,0,363.1,1339,11933008,1.53,3657
P12,JAWA BARAT,2017,648.1,648.11,387.5,1358,13321699,1.43,5646
P12,JAWA BARAT,2018,639.8,4104.51,371.9,1376,13803293,1.36,4509
P12,JAWA BARAT,2019,797.2,9552,374.6,1394,14197050,1.25,6974
P12,JAWA BARAT,2020,0.9,2344,370.5,1365,13978714,1.11,3459
P12,JAWA BARAT,2021,686.5,1299,358.8,1379,12075475,1.16,2568
P12,JAWA BARAT,2022,680.8,2005,334.5,1334,10402475,1.15,2575
P12,JAWA BARAT,2023,681.1,11524.8,353.48,1346,359109,0.99,5561
P12,JAWA BARAT,2024,669.98,4548.58,353.04,1359,6759857,0.97,4421
P13,JAWA TENGAH,2015,1019.5,2747.7,782.1,1030,8351292.13,2.27,1808
P13,JAWA TENGAH,2016,787.3,0,360.9,1037,8417355,2.53,2285
P13,JAWA TENGAH,2017,1019.7,6028.48,352.4,1044,8536724,2.55,3457
P13,JAWA TENGAH,2018,1019,331.67,348.2,1052,8415144,2.55,2573
P13,JAWA TENGAH,2019,1023,7882,348.6,1060,8610218,2.44,3819
P13,JAWA TENGAH,2020,1031.4,3131,348.4,1063,8615148,2.35,2161
P13,JAWA TENGAH,2021,1015.9,868,318.6,1068,8620965,2.43,2036
P13,JAWA TENGAH,2022,1012.4,7424,327.9,1066,8583424,2.41,1756
P13,JAWA TENGAH,2023,1014.2,12047.78,327.53,1068,3090038,2.3,3390
P13,JAWA TENGAH,2024,1004.89,11186.23,326.76,1071,5025019,2.27,2820
P14,DI YOGYAKARTA,2015,22.8,0,0,1213,717148,0.5,251
P14,DI YOGYAKARTA,2016,22.8,0,0,1231,730534,0.49,139
P14,DI YOGYAKARTA,2017,22.8,0,0,1249,736521,0.49,167
P14,DI YOGYAKARTA,2018,22.8,0,0,1265,741427,0.47,156
P14,DI YOGYAKARTA,2019,22.8,0,0,1282,747880,0.48,208
P14,DI YOGYAKARTA,2020,22.8,0,0,1268,737533,0.46,193
P14,DI YOGYAKARTA,2021,22.8,0,0,1276,715413,0.44,180
P14,DI YOGYAKARTA,2022,22.8,59,0,1292,701200,0.45,203
P14,DI YOGYAKARTA,2023,22.8,56.45,0,1303,252040,0.43,377
P14,DI YOGYAKARTA,2024,22.58,39.31,0,1316,373561,0.42,238
P15,JAWA TIMUR,2015,1239.5,5820.76,1272.4,817,35011223,2.85,4804
P15,JAWA TIMUR,2016,1209.4,0,572.7,821,36275925,2.78,4804
P15,JAWA TIMUR,2017,1195.5,7741.88,578.9,826,37393455,2.74,4702
P15,JAWA TIMUR,2018,1190.8,12244.22,580.3,831,37750083,2.69,4498
P15,JAWA TIMUR,2019,1226.5,45887,597.5,835,39085665,2.62,5088
P15,JAWA TIMUR,2020,1234.5,2551,599.5,819,38474131,2.5,3174
P15,JAWA TIMUR,2021,1207.7,2773,582.5,824,37912987,2.61,2614
P15,JAWA TIMUR,2022,1211.1,2671,589.8,837,38197960,2.65,2918
P15,JAWA TIMUR,2023,1218.5,9929.31,590.88,840,13800477,2.52,4823
P15,JAWA TIMUR,2024,1210.2,6613.63,591.21,845,18955768,2.48,3705
P16,BANTEN,2015,200.1,0,138.6,1318,2157060,0.35,1155
P16,BANTEN,2016,186.8,0,47.5,1342,2251710,0.35,1254
P16,BANTEN,2017,188.1,0,45.9,1366,2337750,0.35,1218
P16,BANTEN,2018,185.7,0,45.4,1390,2283459,0.35,1003
P16,BANTEN,2019,185.4,247,44.2,1414,2297095,0.34,959
P16,BANTEN,2020,185.3,0,42.4,1398,2281918,0.3,709
P16,BANTEN,2021,185.2,0,39.6,1413,2246843,0.32,683
P16,BANTEN,2022,184.5,0,38.2,1433,2136700,0.33,685
P16,BANTEN,2023,184.3,1090.91,37.5,1449,827226,0.32,882
P16,BANTEN,2024,182.41,318.7,36.89,1464,1183413,0.31,699
P17,BALI,2015,126.6,0,82.7,721,993892,0.58,627
P17,BALI,2016,127,0,28.8,729,1025350,0.56,492
P17,BALI,2017,126.7,0,28,737,1066459,0.53,613
P17,BALI,2018,125.9,0,28,745,1046219,0.52,532
P17,BALI,2019,125.6,0,27.4,753,1043726,0.5,518
P17,BALI,2020,125.3,0,27.4,731,1039073,0.5,386
P17,BALI,2021,125.3,0,27.3,739,1048680,0.51,349
P17,BALI,2022,125.3,1543,27.3,747,1049673,0.52,378
P17,BALI,2023,125.3,2.36,27.35,757,366561,0.5,459
P17,BALI,2024,124.51,2.01,27.19,765,487756,0.47,326
P18,NUSA TENGGARA BARAT,2015,620.3,1155.04,564.8,262,1438555,1.42,10427
P18,NUSA TENGGARA BARAT,2016,619.9,0,199.4,265,1516490,1.45,10249
P18,NUSA TENGGARA BARAT,2017,625.6,1441.33,199.3,268,1568505,1.4,6897
P18,NUSA TENGGARA BARAT,2018,609.7,42706.44,194.3,271,1564050,1.37,9107
P18,NUSA TENGGARA BARAT,2019,619.8,42673,192.8,274,1602337,1.26,13199
P18,NUSA TENGGARA BARAT,2020,619.3,9985,196.2,277,1623800,1.29,6985
P18,NUSA TENGGARA BARAT,2021,618.4,28855,199.5,279,1668826,1.41,5481
P18,NUSA TENGGARA BARAT,2022,619.6,7803,208.8,281,1679344,1.58,7263
P18,NUSA TENGGARA BARAT,2023,619.4,18625.14,211.51,284,607337,1.55,8986
P18,NUSA TENGGARA BARAT,2024,616.36,15248.46,214.06,287,688474,1.47,6547
P19,NUSA TENGGARA TIMUR,2015,1840.4,12820.2,1186.4,100,3373756,0.74,27609
P19,NUSA TENGGARA TIMUR,2016,1887,0,480.4,101,3586840,0.73,14428
P19,NUSA TENGGARA TIMUR,2017,1871.8,4.55,492.3,103,3799090,0.73,10547
P19,NUSA TENGGARA TIMUR,2018,1863.5,3153.03,483.1,104,3951068,0.76,10218
P19,NUSA TENGGARA TIMUR,2019,1860.3,26007,482.9,106,4176826,0.75,12716
P19,NUSA TENGGARA TIMUR,2020,1860.1,19406,480.6,107,4280459,0.76,9286
P19,NUSA TENGGARA TIMUR,2021,1861.5,96928,484.1,108,4456316,0.8,7969
P19,NUSA TENGGARA TIMUR,2022,1861,118249,480.7,110,4625200,0.8,8892
P19,NUSA TENGGARA TIMUR,2023,1860.7,27551.72,481.35,112,1622099,0.79,15016
P19,NUSA TENGGARA TIMUR,2024,1849.87,24929.98,483.23,113,2207296,0.77,7880
P20,KALIMANTAN BARAT,2015,7736.5,147034.7,1781.9,31,416879,1.75,136534
P20,KALIMANTAN BARAT,2016,8183.9,27428.53,1172.3,31,394073,1.73,201208
P20,KALIMANTAN BARAT,2017,8134.6,13.05,1288.5,32,413547,1.69,84882
P20,KALIMANTAN BARAT,2018,8113.9,17099.42,1477.1,33,428434,1.78,69558
P20,KALIMANTAN BARAT,2019,8064.1,133826,1477.8,34,444199,1.74,116869
P20,KALIMANTAN BARAT,2020,8005.2,5296,1550.5,34,447344,1.72,81000
P20,KALIMANTAN BARAT,2021,7893.3,4754,1562.6,35,466862,1.83,67454
P20,KALIMANTAN BARAT,2022,7928.4,1023,1583.8,36,455484,2.09,67010
P20,KALIMANTAN BARAT,2023,7882.2,12278.62,1618.29,36,166918,2.0,107534
P20,KALIMANTAN BARAT,2024,7825.08,13882.06,1582.11,37,327244,1.87,92499
P21,KALIMANTAN TENGAH,2015,8734.4,542340.57,1299.1,16,337234,18.06,168424
P21,KALIMANTAN TENGAH,2016,8818.1,162099.54,820.7,16,344660,17.1,253742
P21,KALIMANTAN TENGAH,2017,8738.5,166.62,890.5,17,364481,17.64,118095
P21,KALIMANTAN TENGAH,2018,8671.5,35440.34,1201.6,17,367620,18.63,139028
P21,KALIMANTAN TENGAH,2019,8622.3,1209000,1275.5,17,376688,18.35,101386
P21,KALIMANTAN TENGAH,2020,8571.6,25009,1346.1,17,382551,17.25,73234
P21,KALIMANTAN TENGAH,2021,8476.8,12590,1374.6,17,395040,18.59,49040
P21,KALIMANTAN TENGAH,2022,8505.4,2428,1378.9,17,392855,24.56,58072
P21,KALIMANTAN TENGAH,2023,8535.5,199699.35,1350.4,17,146178,23.06,114386
P21,KALIMANTAN TENGAH,2024,8481.59,53283.96,1341.86,17,310268,21.88,103327
P22,KALIMANTAN SELATAN,2015,702.3,4280.95,741.7,103,258026,22.96,32073
P22,KALIMANTAN SELATAN,2016,703.7,3827.77,525.6,104,255285,20.85,35461
P22,KALIMANTAN SELATAN,2017,705.2,28.11,534.1,105,264083,20.85,17428
P22,KALIMANTAN SELATAN,2018,709.3,74006.45,537.1,106,258706,21.79,25430
P22,KALIMANTAN SELATAN,2019,716.7,62741,543.3,107,261618,19.22,33817
P22,KALIMANTAN SELATAN,2020,731.1,4017,741.9,105,253798,18.28,21000
P22,KALIMANTAN SELATAN,2021,926,8625,730.4,106,273311,21.46,21668
P22,KALIMANTAN SELATAN,2022,943.1,429,766,113,258921,32.08,17769
P22,KALIMANTAN SELATAN,2023,953,190394.58,692.11,114,110240,30.84,51434
P22,KALIMANTAN SELATAN,2024,944.86,4993.88,703.54,115,177003,29.47,27839
P23,KALIMANTAN TIMUR,2015,9071.3,692352.96,1609.5,27,244724,45.16,183872
P23,KALIMANTAN TIMUR,2016,8358,43136.76,1114.5,27,259610,43.19,313958
P23,KALIMANTAN TIMUR,2017,8318.3,676.38,1183.6,28,273932,46.6,134297
P23,KALIMANTAN TIMUR,2018,8272,27893.2,1532.8,28,265246,46.69,147742
P23,KALIMANTAN TIMUR,2019,8232,68524,1354.4,29,276900,45.6,132059
P23,KALIMANTAN TIMUR,2020,8167.4,5221,1416.4,29,279303,41.27,91821
P23,KALIMANTAN TIMUR,2021,7758,3029,1470.9,30,274031,45.1,74061
P23,KALIMANTAN TIMUR,2022,7906.2,373,1476,30,220299,53.18,61563
P23,KALIMANTAN TIMUR,2023,7924,39494.41,1587.04,31,78686,43.18,134307
P23,KALIMANTAN TIMUR,2024,7886.09,22570.5,1543.2,32,149256,38.38,110376
P24,KALIMANTAN UTARA,2015,6136.8,14506.2,1123,9,73519,28.04,47844
P24,KALIMANTAN UTARA,2016,5923.4,2107.21,62,9,74388,24.84,38488
P24,KALIMANTAN UTARA,2017,5918.8,82.22,75,9,72805,27.37,33775
P24,KALIMANTAN UTARA,2018,5911.1,627.71,162.2,9,68635,27.42,36813
P24,KALIMANTAN UTARA,2019,5904.7,8559,162.6,10,69033,26.95,29326
P24,KALIMANTAN UTARA,2020,5897.2,1721,165.2,9,68654,25.46,24481
P24,KALIMANTAN UTARA,2021,5778.2,1678,222.5,9,64078,27.26,19260
P24,KALIMANTAN UTARA,2022,5798.3,370,244.4,10,51817,36.2,17636
P24,KALIMANTAN UTARA,2023,5940.9,796.36,244.86,10,24334,34.18,26441
P24,KALIMANTAN UTARA,2024,5917.93,2429.21,241.18,11,45156,28.72,19954
P25,SULAWESI UTARA,2015,560.1,4861.31,472.4,174,584458,4.75,15596
P25,SULAWESI UTARA,2016,555.3,2240.47,301.9,176,599816,4.82,8782
P25,SULAWESI UTARA,2017,557.1,103.04,305.7,178,606286,4.84,5777
P25,SULAWESI UTARA,2018,553.2,326.39,299.3,179,589196,4.96,7455
P25,SULAWESI UTARA,2019,555.4,4574,300.4,181,599838,5.07,8921
P25,SULAWESI UTARA,2020,1891.2,177,301.6,189,608699,5.41,3124
P25,SULAWESI UTARA,2021,549.5,579,302.6,190,573582,5.43,2824
P25,SULAWESI UTARA,2022,552.7,469,298,183,584966,5.21,2731
P25,SULAWESI UTARA,2023,557.3,2531.44,296.94,185,206236,4.95,5793
P25,SULAWESI UTARA,2024,556.74,651.68,293.84,186,149811,4.89,3474
P26,SULAWESI TENGAH,2015,3907.9,31679.88,970.8,47,1071132,10.25,91932
P26,SULAWESI TENGAH,2016,3854.3,11744.4,676.5,47,935683,11.8,74262
P26,SULAWESI TENGAH,2017,3846.5,1310.19,692.7,48,1042080,12.83,36947
P26,SULAWESI TENGAH,2018,3825.1,4147.28,653.8,49,1081571,12.84,37525
P26,SULAWESI TENGAH,2019,3816.3,11551,652.6,49,1157469,13.39,45513
P26,SULAWESI TENGAH,2020,837.6,2555,661.3,48,1201663,13.4,26788
P26,SULAWESI TENGAH,2021,3760.2,3133,653.6,49,1267348,14.11,22583
P26,SULAWESI TENGAH,2022,3759.9,3704,652.7,50,1325812,15.34,24645
P26,SULAWESI TENGAH,2023,3790.4,10844.28,643.87,50,288172,15.3,43093
P26,SULAWESI TENGAH,2024,3775.02,4920.7,645.88,51,404695,14.64,28744
P27,SULAWESI SELATAN,2015,1433.6,10074.32,1165.2,182,2947872,6.32,28080
P27,SULAWESI SELATAN,2016,1415.4,438.4,502.1,184,3131695,5.19,30886
P27,SULAWESI SELATAN,2017,1404.4,1035.51,498,186,3247357,4.91,24051
P27,SULAWESI SELATAN,2018,1409.8,1741.27,471.7,188,3143110,4.8,19442
P27,SULAWESI SELATAN,2019,1457.8,15697,452.7,189,3228058,4.62,22925
P27,SULAWESI SELATAN,2020,1534.4,1902,440.4,194,3440009,4.67,14268
P27,SULAWESI SELATAN,2021,1479.9,916,429.1,196,3521533,4.75,10243
P27,SULAWESI SELATAN,2022,1511.2,997,409.4,204,3483201,5.1,15943
P27,SULAWESI SELATAN,2023,1493.3,6489.26,418.47,207,1325404,5.13,26949
P27,SULAWESI SELATAN,2024,1480.64,3522.91,426.14,209,1683557,4.55,9599
P28,SULAWESI TENGGARA,2015,1914.4,31763.54,868.6,66,500905,20.89,43540
P28,SULAWESI TENGGARA,2016,1896.8,72.42,397,67,552646,19.38,38445
P28,SULAWESI TENGGARA,2017,1877,3313.68,397.8,68,620576,20.68,27135
P28,SULAWESI TENGGARA,2018,1846.6,8594.67,398.4,70,568377,20.83,24214
P28,SULAWESI TENGGARA,2019,1861.4,16929,378.3,71,607754,21.04,34956
P28,SULAWESI TENGGARA,2020,97.5,3206,427,69,657848,19.79,18920
P28,SULAWESI TENGGARA,2021,1883,2124,397.2,70,708699,19.35,12405
P28,SULAWESI TENGGARA,2022,1884,3098,373.7,75,747282,20.25,13369
P28,SULAWESI TENGGARA,2023,1880.4,18736.47,355.23,76,223070,21.44,34164
P28,SULAWESI TENGGARA,2024,1860.34,1629.74,352.26,77,390501,21.13,16908
P29,GORONTALO,2015,707.5,5225.89,478.8,101,297638,1.32,13286
P29,GORONTALO,2016,692.7,737.91,101.8,102,317558,1.2,10910
P29,GORONTALO,2017,709.9,0,105.3,104,336979,1.16,7869
P29,GORONTALO,2018,710.3,158.65,108.5,105,343325,1.11,8007
P29,GORONTALO,2019,717.6,1909,110.4,107,362561,1.1,10959
P29,GORONTALO,2020,869.6,80,111.1,104,372351,1.12,3030
P29,GORONTALO,2021,709.8,163,113.3,105,381529,1.1,2199
P29,GORONTALO,2022,709,101,105.1,99,389678,1.09,2819
P29,GORONTALO,2023,705.9,666.33,108.63,101,155164,1.09,8242
P29,GORONTALO,2024,703.38,767.03,107.55,102,179777,1.12,4643
P30,SULAWESI BARAT,2015,822.1,4989.38,424.4,76,456908.11,2.21,22500
P30,SULAWESI BARAT,2016,823.2,4133.98,356.9,78,395188,2.32,39172
P30,SULAWESI BARAT,2017,817.4,188.13,366.6,79,429699,2.25,51512
P30,SULAWESI BARAT,2018,815.6,978.38,370.9,81,435889,2.23,37400
P30,SULAWESI BARAT,2019,823.3,3029,359.3,82,477583,2.24,30977
P30,SULAWESI BARAT,2020,1725.4,569,359,85,489717,2.17,30395
P30,SULAWESI BARAT,2021,811.5,886,347.7,86,495151,2.2,35801
P30,SULAWESI BARAT,2022,811.7,488,349.2,88,496077,2.15,35602
P30,SULAWESI BARAT,2023,825.1,2132.31,348.25,89,133969,2.2,35180
P30,SULAWESI BARAT,2024,816.27,994.74,347.26,91,274152,2.21,32209
P31,MALUKU,2015,3016.8,43231.45,471.2,36,306232,2.44,48979
P31,MALUKU,2016,3030,7834.54,155.6,37,304005,2.03,27623
P31,MALUKU,2017,3011.8,3191.12,159.2,37,316319,2.29,7333
P31,MALUKU,2018,3007.8,14906.44,159.4,38,302871,2.56,11187
P31,MALUKU,2019,3012.6,27211,158,38,321343,2.29,17179
P31,MALUKU,2020,2023.2,20270,156.2,39,328434,2.2,5660
P31,MALUKU,2021,3077.9,11807,153,40,343275,2.41,3727
P31,MALUKU,2022,3096.8,14954,157.2,41,387026,2.61,5059
P31,MALUKU,2023,3103.9,45999.39,156.2,42,93324,1.85,14304
P31,MALUKU,2024,3078.89,13404.83,156.93,42,170433,1.68,5198
P32,MALUKU UTARA,2015,2070.9,2132.51,405.9,36,264832,8.77,45451
P32,MALUKU UTARA,2016,1946.8,103.11,251.4,37,279940,8.39,26859
P32,MALUKU UTARA,2017,2019,31.1,253.3,38,286472,9.18,10589
P32,MALUKU UTARA,2018,2009.3,69.54,226.7,39,265717,10.84,12375
P32,MALUKU UTARA,2019,2014.1,2781,232.2,39,333573,10.75,14166
P32,MALUKU UTARA,2020,3075.5,59,232.2,40,354699,11.56,7423
P32,MALUKU UTARA,2021,2033.2,108,231.6,41,357691,14.64,6041
P32,MALUKU UTARA,2022,2038.7,171,232.3,40,367469,17.55,6358
P32,MALUKU UTARA,2023,2060.7,542.18,232.57,41,56784,20.1,11895
P32,MALUKU UTARA,2024,2056.73,102.57,232.52,41,74535,18.52,7303
P33,PAPUA BARAT,2015,8790,7964.41,416.1,9,193148,19.49,42462
P33,PAPUA BARAT,2016,8821.6,542.09,92.1,9,198008,19.13,26815
P33,PAPUA BARAT,2017,8750.9,1156.03,95.4,9,167737,17.97,15891
P33,PAPUA BARAT,2018,8751.1,509.5,86.6,9,155313,17.98,20511
P33,PAPUA BARAT,2019,8874.9,1533,85.2,9,160768,17.44,16558
P33,PAPUA BARAT,2020,25396.6,5716,88.6,11,171924,17.3,16318
P33,PAPUA BARAT,2021,9087,77,94.8,11,155180,17.69,12209
P33,PAPUA BARAT,2022,9131.6,1738,108,12,153451,18.25,13752
P33,PAPUA BARAT,2023,9122.6,763.27,110.7,12,41957,33.7,16565
P33,PAPUA BARAT,2024,13208.34,227.27,118.83,26,83200,35.39,12150
P34,PAPUA,2015,25088.4,350015.3,258.6,10,858595.17,32.41,82032
P34,PAPUA,2016,25082.6,186571.6,265.8,10,928582,34.08,83052
P34,PAPUA,2017,25076.9,28767.38,257.2,10,983867,35.19,49615
P34,PAPUA,2018,24993.6,88626.84,232.8,10,827076,36.64,34778
P34,PAPUA,2019,25168.7,108110,250.3,11,1105355,23.56,34560
P34,PAPUA,2020,8967.3,28277,237.1,13,1151411,28.21,29911
P34,PAPUA,2021,25241.3,15979,261.1,14,1170919,36.82,26341
P34,PAPUA,2022,25321.9,8336,227.6,14,1197900,38.6,28605
P34,PAPUA,2023,25153.5,154798.37,226.72,14,607951,78.27,22967
P34,PAPUA,2024,20867.47,28291.96,233.22,71,762756,79.99,22586"""
    df = pd.read_csv(io.StringIO(csv_raw))
    df.columns = df.columns.str.strip()
    df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()
    return df

geojson = load_geojson()
col_y = "Y (TREE COVER LOSS- Ha)"
cols_x = {
    "X1": "X1 (LUAS PENUTUPAN LAHAN - RIBU Ha)",
    "X2": "X2 (LUAS KEBAKARAN HUTAN DAN LAHAN - Ha)",
    "X3": "X3 (TOTAL LUAS TANAMAN PERKEBUNAN - RIBU Ha)",
    "X4": "X4 (KEPADATAN PENDUDUK - jiwa/km2)",
    "X5": "X5  (TOTAL POPULASI TERNAK - EKOR)",
    "X6": "X6 (PDRB PERTAMBANGAN DAN PENGGALIAN PERSEN) "
}

# KOORDINAT PUSAT PER PROVINSI
PROV_COORDS = {
    "ACEH": (4.6, 96.7), "SUMATERA UTARA": (2.1, 99.5), "SUMATERA BARAT": (-0.7, 100.4),
    "RIAU": (0.5, 101.4), "JAMBI": (-1.6, 103.6), "SUMATERA SELATAN": (-3.3, 104.0),
    "BENGKULU": (-3.8, 102.3), "LAMPUNG": (-4.6, 105.4), "KEP. BANGKA BELITUNG": (-2.7, 106.4),
    "KEP. RIAU": (3.9, 108.1), "DKI JAKARTA": (-6.2, 106.8), "JAWA BARAT": (-6.9, 107.6),
    "JAWA TENGAH": (-7.2, 110.4), "DI YOGYAKARTA": (-7.8, 110.4), "JAWA TIMUR": (-7.5, 112.2),
    "BANTEN": (-6.4, 106.1), "BALI": (-8.4, 115.2), "NUSA TENGGARA BARAT": (-8.7, 117.4),
    "NUSA TENGGARA TIMUR": (-8.8, 121.7), "KALIMANTAN BARAT": (0.0, 109.3),
    "KALIMANTAN TENGAH": (-1.7, 113.9), "KALIMANTAN SELATAN": (-3.1, 115.3),
    "KALIMANTAN TIMUR": (0.5, 116.4), "KALIMANTAN UTARA": (3.1, 116.1),
    "SULAWESI UTARA": (1.5, 124.8), "SULAWESI TENGAH": (-1.4, 121.4),
    "SULAWESI SELATAN": (-3.7, 120.0), "SULAWESI TENGGARA": (-3.9, 122.5),
    "GORONTALO": (0.6, 122.5), "SULAWESI BARAT": (-2.8, 119.3),
    "MALUKU": (-3.2, 130.1), "MALUKU UTARA": (1.6, 127.8),
    "PAPUA BARAT": (-1.3, 133.2), "PAPUA": (-4.3, 138.1),
}

# --- 5. AUTO-LOAD DATA EMBEDDED ---
if st.session_state.df is None:
    st.session_state.df = get_embedded_data()

# --- 6. LOGIKA NAVIGASI ---
if st.session_state.page == "Portal":
    st.markdown("<br><br><h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#dcfce7; letter-spacing:2px;'>SISTEM MONITORING DEFORESTASI DINAMIS</p>", unsafe_allow_html=True)

    c_up1, c_up2, c_up3 = st.columns([1, 2, 1])
    with c_up2:
        up_file = st.file_uploader("📥 Unggah Dataset Deforestasi (CSV) — opsional, data penelitian sudah tersedia", type=["csv"])
        if up_file is not None:
            raw_df = pd.read_csv(up_file)
            raw_df.columns = raw_df.columns.str.strip()
            if 'PROVINSI' in raw_df.columns:
                raw_df['PROVINSI'] = raw_df['PROVINSI'].astype(str).str.strip().str.upper()
            st.session_state.df = raw_df
            st.success("🌲 Data Terintegrasi Sempurna!")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("<div class='menu-card'><h1>🛰️</h1><h3>Dashboard Spasial</h3></div>", unsafe_allow_html=True)
        if st.button("Buka Dashboard"): set_page("Dashboard"); st.rerun()
    with c2:
        st.markdown("<div class='menu-card'><h1>🧪</h1><h3>Prediksi MERF</h3></div>", unsafe_allow_html=True)
        if st.button("Mulai Prediksi"): set_page("Prediksi"); st.rerun()
    with c3:
        st.markdown("<div class='menu-card'><h1>📖</h1><h3>Info Penelitian</h3></div>", unsafe_allow_html=True)
        if st.button("Lihat Penelitian"): set_page("Penelitian"); st.rerun()

else:
    if st.button("⬅️ KEMBALI KE PORTAL"):
        set_page("Portal"); st.rerun()
    st.markdown("---")

    # =====================================================================
    # BAGIAN DASHBOARD DESKRIPTIF SPASIAL — REVISI PREMIUM
    # =====================================================================
    if st.session_state.page == "Dashboard" and st.session_state.df is not None:
        df = st.session_state.df

        st.markdown("<div class='dash-header'>📊 Dashboard Deskriptif Spasial</div>", unsafe_allow_html=True)

        # Legenda warna
        st.markdown("""
        <div class='legend-bar'>
            <span class='legend-label'>Legenda Tingkat Kehilangan Tutupan Pohon:</span>
            <span style='display:inline-flex;align-items:center;gap:6px;'>
                <span style='width:13px;height:13px;border-radius:50%;background:#22c55e;display:inline-block;'></span>
                <span style='color:#dcfce7;font-size:0.85rem;'>Rendah (Hijau)</span>
            </span>
            <span style='color:#475569;font-size:1rem;'>→</span>
            <span style='display:inline-flex;align-items:center;gap:6px;'>
                <span style='width:13px;height:13px;border-radius:50%;background:#eab308;display:inline-block;'></span>
                <span style='color:#fef9c3;font-size:0.85rem;'>Sedang (Kuning)</span>
            </span>
            <span style='color:#475569;font-size:1rem;'>→</span>
            <span style='display:inline-flex;align-items:center;gap:6px;'>
                <span style='width:13px;height:13px;border-radius:50%;background:#ef4444;display:inline-block;'></span>
                <span style='color:#fee2e2;font-size:0.85rem;'>Tinggi (Merah)</span>
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Filter tahun & provinsi
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown("<p style='color:#facc15;font-weight:bold;margin-bottom:4px;font-size:1.05rem;'>Pilih Tahun:</p>", unsafe_allow_html=True)
            list_thn = sorted(df['TAHUN'].unique(), reverse=True)
            sel_thn = st.selectbox("", list_thn, key="sel_tahun_dash", label_visibility="collapsed")
        with col_f2:
            st.markdown("<p style='color:#facc15;font-weight:bold;margin-bottom:4px;font-size:1.05rem;'>Fokus Wilayah (Zoom Provinsi):</p>", unsafe_allow_html=True)
            list_prov = ["Semua Provinsi"] + sorted(df['PROVINSI'].unique().tolist())
            sel_prov = st.selectbox("", list_prov, key="sel_prov_dash", label_visibility="collapsed")

        df_filt_year = df[df['TAHUN'] == sel_thn].copy()
        min_val = float(df[col_y].min())
        max_val = float(df[col_y].max())

        # Kartu metrik ringkasan
        total_loss = int(df_filt_year[col_y].sum())
        avg_loss = int(df_filt_year[col_y].mean()) if not df_filt_year.empty else 0
        prov_tertinggi = df_filt_year.loc[df_filt_year[col_y].idxmax(), 'PROVINSI'] if not df_filt_year.empty else "-"
        val_tertinggi = int(df_filt_year[col_y].max()) if not df_filt_year.empty else 0

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class='metric-glass'>
                <div class='val'>{total_loss:,} Ha</div>
                <div class='lbl'>🌍 Total Tree Cover Loss {sel_thn}</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class='metric-glass'>
                <div class='val'>{avg_loss:,} Ha</div>
                <div class='lbl'>📊 Rata-rata per Provinsi</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class='metric-glass'>
                <div class='val' style='font-size:1.15rem;'>{prov_tertinggi}</div>
                <div class='lbl'>🔴 Provinsi Tertinggi ({val_tertinggi:,} Ha)</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Warna premium map
        PREMIUM_COLORSCALE = [
            [0.00, "#052e16"], [0.15, "#14532d"], [0.30, "#16a34a"],
            [0.45, "#4ade80"], [0.55, "#fde047"], [0.68, "#f97316"],
            [0.82, "#dc2626"], [1.00, "#450a0a"]
        ]

        cl, cr = st.columns([1.15, 0.85])

        with cl:
            if geojson:
                if sel_prov == "Semua Provinsi":
                    data_peta = df_filt_year
                    use_fitbounds = False
                    geo_center = {"lat": -2.5, "lon": 118.0}
                    geo_scale = 3.5
                else:
                    # Untuk provinsi tunggal: tampilkan semua data tapi highlight
                    data_peta = df_filt_year
                    use_fitbounds = "locations"
                    coords = PROV_COORDS.get(sel_prov, (-2.5, 118.0))
                    geo_center = {"lat": coords[0], "lon": coords[1]}
                    geo_scale = 5.5

                fig = px.choropleth(
                    data_frame=data_peta,
                    geojson=geojson,
                    locations="PROVINSI",
                    featureidkey="properties.PROV_KEY",
                    color=col_y,
                    color_continuous_scale=PREMIUM_COLORSCALE,
                    range_color=[min_val, max_val],
                    hover_name="PROVINSI",
                    hover_data={col_y: ":.0f"},
                )

                if sel_prov == "Semua Provinsi":
                    fig.update_geos(
                        projection_type="mercator",
                        center=geo_center,
                        projection_scale=geo_scale,
                        visible=False,
                        bgcolor="#0d1b2a",
                        showocean=True, oceancolor="#0a2540",
                        showland=True, landcolor="#1a3a2a",
                        showlakes=True, lakecolor="#0a2540",
                        showcoastlines=True, coastlinecolor="#1e4d3a",
                        showframe=False,
                    )
                else:
                    fig.update_geos(
                        projection_type="mercator",
                        center=geo_center,
                        projection_scale=geo_scale,
                        visible=False,
                        bgcolor="#0d1b2a",
                        showocean=True, oceancolor="#0a2540",
                        showland=True, landcolor="#1a3a2a",
                        showlakes=True, lakecolor="#0a2540",
                        showcoastlines=True, coastlinecolor="#1e4d3a",
                        showframe=False,
                    )

                fig.update_layout(
                    height=530,
                    margin={"r": 0, "t": 10, "l": 0, "b": 0},
                    paper_bgcolor="#0d1b2a",
                    plot_bgcolor="#0d1b2a",
                    font=dict(color="#f1f5f9", family="Arial"),
                    coloraxis_colorbar=dict(
                        title=dict(text="Tree Cover Loss (Ha)", font=dict(color="#facc15", size=11)),
                        tickfont=dict(color="#cbd5e1", size=10),
                        bgcolor="rgba(13,27,42,0.85)",
                        bordercolor="rgba(250,204,21,0.3)",
                        borderwidth=1,
                        thickness=14,
                        len=0.75,
                    ),
                    geo=dict(bgcolor="#0d1b2a"),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ GeoJSON Indonesia tidak dapat dimuat. Periksa koneksi internet.")

        with cr:
            st.markdown("<p style='color:#facc15;font-weight:bold;margin-bottom:4px;font-size:1.05rem;'>Analisis Korelasi X:</p>", unsafe_allow_html=True)
            var_x = st.selectbox("", list(cols_x.keys()), key="sel_varx_dash", label_visibility="collapsed")

            # Scatter: semua provinsi tahun terpilih, atau filter satu provinsi jika terpilih
            if sel_prov == "Semua Provinsi":
                data_scatter = df_filt_year
            else:
                data_scatter = df_filt_year[df_filt_year['PROVINSI'] == sel_prov]
                if len(data_scatter) < 2:
                    # fallback: tampilkan tren historis provinsi tersebut lintas tahun
                    data_scatter = df[df['PROVINSI'] == sel_prov].sort_values('TAHUN')

            fig2 = px.scatter(
                data_scatter,
                x=cols_x[var_x],
                y=col_y,
                color=col_y,
                trendline="ols",
                hover_name="PROVINSI",
                color_continuous_scale=PREMIUM_COLORSCALE,
                range_color=[min_val, max_val],
                labels={
                    col_y: "Tree Cover Loss (Ha)",
                    cols_x[var_x]: var_x
                },
            )
            fig2.update_traces(
                marker=dict(size=10, line=dict(width=1.2, color="#0d1b2a"), opacity=0.92),
                selector=dict(mode="markers")
            )
            fig2.update_layout(
                height=530,
                paper_bgcolor="#0d1b2a",
                plot_bgcolor="#0f2235",
                font=dict(color="#f1f5f9", family="Arial"),
                margin={"r": 10, "t": 24, "l": 10, "b": 10},
                xaxis=dict(
                    gridcolor="rgba(255,255,255,0.06)",
                    zerolinecolor="rgba(255,255,255,0.1)",
                    tickfont=dict(color="#94a3b8", size=10),
                    title_font=dict(color="#facc15", size=11),
                ),
                yaxis=dict(
                    gridcolor="rgba(255,255,255,0.06)",
                    zerolinecolor="rgba(255,255,255,0.1)",
                    tickfont=dict(color="#94a3b8", size=10),
                    title_font=dict(color="#facc15", size=11),
                ),
                coloraxis_colorbar=dict(
                    title=dict(text="Loss (Ha)", font=dict(color="#facc15", size=10)),
                    tickfont=dict(color="#cbd5e1", size=9),
                    bgcolor="rgba(13,27,42,0.85)",
                    bordercolor="rgba(250,204,21,0.3)",
                    borderwidth=1,
                    thickness=12,
                    len=0.7,
                ),
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Tabel data bawah
        with st.expander("📋 Lihat Tabel Data Lengkap"):
            display_cols = ['PROVINSI', 'TAHUN', col_y] + list(cols_x.values())
            available_cols = [c for c in display_cols if c in df_filt_year.columns]
            tbl = df_filt_year[available_cols].sort_values(col_y, ascending=False).reset_index(drop=True)
            st.dataframe(tbl, use_container_width=True, height=320)

    # =====================================================================
    # AKHIR BAGIAN DASHBOARD
    # =====================================================================

    elif st.session_state.page == "Prediksi" and st.session_state.df is not None:
        df = st.session_state.df
        st.header("📈 Prediksi Deforestasi Multi-Tahun (MERF)")
        prov_target = st.selectbox("Fokus Wilayah Prediksi:", sorted(df['PROVINSI'].unique()))
        hist = df[df['PROVINSI'] == prov_target].sort_values('TAHUN')

        raw_weights = np.random.dirichlet([5, 3.5, 2, 1])

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
