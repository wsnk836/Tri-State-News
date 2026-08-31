from datetime import datetime, timedelta
import time
from zoneinfo import ZoneInfo
import requests
import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="Tri-State News | TSN Live",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- PWA STATIC MANIFEST INCORPORATION ---
pwa_manifest_code = """
<script>
    let link = document.createElement('link');
    link.rel = 'manifest';
    link.href = './app/static/manifest.json';
    document.head.appendChild(link);
</script>
"""
components.html(pwa_manifest_code, height=0)

# --- BROWSER LOCALSTORAGE & DEVICE GEOLOCATION BRIDGE ---
geolocation_bridge_code = (
    "<script>\n"
    "    const urlParams = new URLSearchParams(window.location.search);\n"
    "    const hasParams = urlParams.has('lat');\n\n"
    "    if (hasParams) {\n"
    "        if (urlParams.has('lat'))"
    " localStorage.setItem('tsn_lat', urlParams.get('lat'));\n"
    "        if (urlParams.has('lon'))"
    " localStorage.setItem('tsn_lon', urlParams.get('lon'));\n"
    "        if (urlParams.has('loc_name'))"
    " localStorage.setItem('tsn_loc_name', urlParams.get('loc_name'));\n"
    "        sessionStorage.setItem('tsn_synced', 'true');\n"
    "    } else {\n"
    "        const alreadySynced = sessionStorage.getItem('tsn_synced');\n\n"
    "        if (!alreadySynced) {\n"
    "            const savedLat = localStorage.getItem('tsn_lat');\n"
    "            const savedLon = localStorage.getItem('tsn_lon');\n"
    "            const savedLoc = localStorage.getItem('tsn_loc_name');\n\n"
    "            if (savedLat) {\n"
    "                sessionStorage.setItem('tsn_synced', 'true');\n"
    "                const newUrl = window.location.pathname +"
    " `?lat=${savedLat}&lon=${savedLon}&loc_name=${encodeURIComponent(savedLoc)}`;\n"
    "                if (window.top && window.top.history &&"
    " window.top.history.replaceState) {\n"
    "                    "
    " window.top.history.replaceState(null, '', newUrl);\n"
    "                    window.top.location.href = newUrl;\n"
    "                }\n"
    "            } else {\n"
    "                sessionStorage.setItem('tsn_synced', 'true');\n"
    "                const defLat = '42.4006';\n"
    "                const defLon = '-96.4001';\n"
    "                const defLoc = 'Sioux City, IA';\n"
    "                localStorage.setItem('tsn_lat', defLat);\n"
    "                localStorage.setItem('tsn_lon', defLon);\n"
    "                localStorage.setItem('tsn_loc_name', defLoc);\n"
    "                const newUrl = window.location.pathname +"
    " `?lat=${defLat}&lon=${defLon}&loc_name=${encodeURIComponent(defLoc)}`;\n"
    "                window.top.location.href = newUrl;\n"
    "            }\n"
    "        }\n"
    "    }\n"
    "</script>"
)
components.html(geolocation_bridge_code, height=0)

# --- PROFESSIONAL TSN BROADCAST NETWORK STYLING (HIGH CONTRAST THEME) ---
st.markdown(
    """
<style>
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .tsn-header-bar {
        background: linear-gradient(90deg, #dc2626 0%, #ef4444 50%, #1e293b 100%);
        padding: 4px 0;
        margin-bottom: 20px;
        border-radius: 6px;
        box-shadow: 0 4px 20px rgba(220, 38, 38, 0.25);
    }
    .tsn-ticker {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 5px solid #dc2626;
        color: #0f172a;
        padding: 10px 16px;
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 0.03em;
        display: flex;
        align-items: center;
        gap: 12px;
        border-radius: 6px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    .tsn-live-badge {
        background: #dc2626;
        color: #ffffff;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 900;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    .breaking-news-banner {
        background: #ffffff;
        border: 2px solid #fca5a5;
        border-left: 6px solid #dc2626;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 25px;
        box-shadow: 0 6px 20px rgba(220, 38, 38, 0.12);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .breaking-news-banner:hover {
        border-color: #dc2626;
        transform: translateY(-2px);
    }
    .breaking-news-link {
        color: #0f172a;
        text-decoration: none;
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
    }
    .breaking-news-link:hover {
        color: #dc2626;
    }
    .broadcast-panel {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-top: 4px solid #dc2626;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
    }
    .radar-wrapper {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 12px 40px rgba(15, 23, 42, 0.08);
        position: relative;
        overflow: hidden;
    }
    .radar-screen-inner {
        position: relative;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #94a3b8;
        background: #000000;
    }
    .alert-severe {
        background: #fef2f2;
        border: 1px solid #fca5a5;
        border-left: 6px solid #dc2626;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #7f1d1d;
    }
    .alert-clear {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 6px solid #16a34a;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #14532d;
    }
    [data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px;
        padding: 12px 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    [data-testid="stMetricLabel"] {
        color: #475569 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        font-weight: 700 !important;
    }
    [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
    }
    input, textarea, [data-baseweb="input"] input, [data-baseweb="textarea"] textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
    }
    input::placeholder, textarea::placeholder {
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        background-color: #e2e8f0;
        border: 1px solid #cbd5e1;
        color: #334155;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: #dc2626 !important;
        color: #ffffff !important;
        border-color: #dc2626 !important;
    }
    [data-testid="column"] {
        flex: 1 !important;
        min-width: 0 !important;
    }
    div[data-testid="column"] button p {
        white-space: nowrap !important;
    }
    div[data-testid="column"] button {
        font-size: 0.78rem !important;
        padding-left: 2px !important;
        padding-right: 2px !important;
        writing-mode: horizontal-tb !important;
    }
    div[data-testid="column"] button[kind="secondary"], 
    .stButton button {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        font-weight: 800 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    div[data-testid="column"] button[kind="secondary"]:hover, 
    .stButton button:hover {
        background-color: #dc2626 !important;
        color: #ffffff !important;
        border-color: #dc2626 !important;
    }
    .stFormSubmitButton button {
        background-color: #dc2626 !important;
        color: #ffffff !important;
        border: 1px solid #b91c1c !important;
        font-weight: 900 !important;
        letter-spacing: 0.02em;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
    }
    .stFormSubmitButton button:hover {
        background-color: #b91c1c !important;
        color: #ffffff !important;
        border-color: #991b1b !important;
        box-shadow: 0 6px 16px rgba(220, 38, 38, 0.4);
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- QUERY PARAMS RESOLUTION ---
query_params = st.query_params
default_lat = "42.4006"
default_lon = "-96.4001"

lat_str = query_params.get("lat", default_lat)
lon_str = query_params.get("lon", default_lon)
location_name = query_params.get("loc_name", "Sioux City, IA")

try:
    ACTIVE_LAT = round(float(lat_str), 4)
    ACTIVE_LON = round(float(lon_str), 4)
except ValueError:
    ACTIVE_LAT = float(default_lat)
    ACTIVE_LON = float(default_lon)
    location_name = "Sioux City, IA"

# --- NETWORK HEADER WITH EMBEDDED LOGO ---
st.markdown('<div class="tsn-header-bar"></div>', unsafe_allow_html=True)

try:
    st.image("favicon_512.png", width=110)
except Exception:
    st.markdown(
        "<h3 style='color: #dc2626; margin:0;'>TSN</h3>",
        unsafe_allow_html=True,
    )

col_title, col_badge = st.columns([3.5, 1.2], vertical_alignment="bottom")

with col_title:
    st.markdown(
        """
        <h1 style="color: #0f172a; margin: 0; font-size: 2.2rem; font-weight: 900; letter-spacing: -0.03em; line-height: 1.1;">
            TSN <span style="color: #dc2626;">NEWS NETWORK</span>
        </h1>
        <p style="color: #475569; margin: 2px 0 0 0; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;">
            Tri-State Weather Center & Live Telemetry
        </p>
        """,
        unsafe_allow_html=True,
    )

with col_badge:
    st.markdown(
        f"""
        <div style="text-align: right;">
            <span class="tsn-live-badge">LIVE DESK</span>
            <div style="color: #334155; font-size: 0.8rem; font-weight: 800; margin-top: 6px;">
                TARGET GRID: <span style="color: #dc2626;">{location_name}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# ==========================================
# --- INSTALL APP INSTRUCTIONS EXPANDER ---
# ==========================================
with st.expander(
    "📲 How to Install & Rename Tri-State News on Your Device", expanded=False
):
    st.markdown(
        """
Want quick one-tap access to Tri-State News like a native mobile app? Follow the steps below for your specific device (you can also **rename the app** during this process):

### 🍎 iPhone / iPad (Safari)
1. Open this link in **Safari**.
2. Tap the **Share** icon (the square with an upward arrow at the bottom of the screen).
3. Scroll down the menu and select **"Add to Home Screen"**.
4. **Rename the app:** Tap on the default title text box, clear it, and type **"TSN"** or **"Tri-State News"**.
5. Tap **Add** in the top right corner.

### 🤖 Android (Chrome)
1. Open this link in **Google Chrome**.
2. Tap the **three vertical dots** (menu) in the top-right corner of the browser.
3. Select **"Add to home screen"** or **"Install app"**.
4. **Rename the app:** A prompt will appear showing the app title. Tap inside the title field to edit it, change it to **"TSN"** or **"Tri-State News"**, and confirm.
5. Tap **Add** or **Install** on the prompt.

### 💻 Desktop (Chrome / Edge / Safari)
1. Open this app in **Google Chrome**, **Microsoft Edge**, or **Brave**.
2. Look for the **install icon** (a small monitor with a down arrow or a plus sign) located on the right side of your browser address/URL bar.
3. Click **Install**. 
4. *(Note: On desktop, you can usually right-click the installed app shortcut on your desktop or applications folder later to rename it to whatever you prefer).*
        """
    )

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "breaking_news_title" not in st.session_state:
    st.session_state.breaking_news_title = "Body found in Riverside Park"

if "breaking_news_link" not in st.session_state:
    st.session_state.breaking_news_link = (
        "
