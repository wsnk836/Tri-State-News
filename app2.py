from datetime import datetime
import time
from zoneinfo import ZoneInfo
import requests
import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="TSN Live | Tri-State News Network",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- BROWSER LOCALSTORAGE & DEVICE GEOLOCATION BRIDGE ---
geolocation_bridge_code = """
<script>
    const urlParams = new URLSearchParams(window.location.search);
    const hasParams = urlParams.has('lat');

    if (hasParams) {
        if (urlParams.has('lat')) localStorage.setItem('tsn_lat', urlParams.get('lat'));
        if (urlParams.has('lon')) localStorage.setItem('tsn_lon', urlParams.get('lon'));
        if (urlParams.has('loc_name')) localStorage.setItem('tsn_loc_name', urlParams.get('loc_name'));
        sessionStorage.setItem('tsn_synced', 'true');
    } else {
        const alreadySynced = sessionStorage.getItem('tsn_synced');
        
        if (!alreadySynced) {
            const savedLat = localStorage.getItem('tsn_lat');
            const savedLon = localStorage.getItem('tsn_lon');
            const savedLoc = localStorage.getItem('tsn_loc_name');

            if (savedLat) {
                sessionStorage.setItem('tsn_synced', 'true');
                const newUrl = window.location.pathname + `?lat=${savedLat}&lon=${savedLon}&loc_name=${encodeURIComponent(savedLoc)}`;
                if (window.top && window.top.history && window.top.history.replaceState) {
                    window.top.history.replaceState(null, '', newUrl);
                    window.top.location.href = newUrl;
                }
            } else {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        async (position) => {
                            const lat = position.coords.latitude;
                            const lon = position.coords.longitude;
                            sessionStorage.setItem('tsn_synced', 'true');
                            
                            try {
                                const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
                                const data = await res.json();
                                const city = data.address.city || data.address.town || data.address.village || data.address.county || 'Local Area';
                                const state = data.address.state_code || data.address.state || '';
                                const locName = `${city}, ${state}`.trim();
                                
                                localStorage.setItem('tsn_lat', lat);
                                localStorage.setItem('tsn_lon', lon);
                                localStorage.setItem('tsn_loc_name', locName);
                                
                                const newUrl = window.location.pathname + `?lat=${lat}&lon=${lon}&loc_name=${encodeURIComponent(locName)}`;
                                window.top.location.href = newUrl;
                            } catch (e) {
                                localStorage.setItem('tsn_lat', lat);
                                localStorage.setItem('tsn_lon', lon);
                                localStorage.setItem('tsn_loc_name', 'GPS Location');
                                const newUrl = window.location.pathname + `?lat=${lat}&lon=${lon}&loc_name=${encodeURIComponent('GPS Location')}`;
                                window.top.location.href = newUrl;
                            }
                        },
                        (error) => {
                            sessionStorage.setItem('tsn_synced', 'true');
                            const defLat = '41.8781';
                            const defLon = '-87.6298';
                            const defLoc = 'Chicago, IL';
                            localStorage.setItem('tsn_lat', defLat);
                            localStorage.setItem('tsn_lon', defLon);
                            localStorage.setItem('tsn_loc_name', defLoc);
                            const newUrl = window.location.pathname + `?lat=${defLat}&lon=${defLon}&loc_name=${encodeURIComponent(defLoc)}`;
                            window.top.location.href = newUrl;
                        },
                        { timeout: 10000 }
                    );
                }
            }
        }
    }
</script>
"""
components.html(geolocation_bridge_code, height=0)

# --- PROFESSIONAL TSN BROADCAST NETWORK STYLING ---
st.markdown(
    """
<style>
    .stApp {
        background-color: #08090c;
        color: #f4f4f5;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .tsn-header-bar {
        background: linear-gradient(90deg, #b91c1c 0%, #ef4444 50%, #181922 100%);
        padding: 4px 0;
        margin-bottom: 20px;
        border-radius: 6px;
        box-shadow: 0 4px 20px rgba(185, 28, 28, 0.4);
    }
    .tsn-ticker {
        background: #0f1015;
        border-top: 1px solid #ef4444;
        border-bottom: 1px solid #27272a;
        color: #fca5a5;
        padding: 8px 16px;
        font-weight: 700;
        font-size: 0.88rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 12px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    .tsn-live-badge {
        background: #ef4444;
        color: #ffffff;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 900;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .broadcast-panel {
        background: rgba(18, 19, 26, 0.95);
        border: 1px solid #27272a;
        border-top: 3px solid #ef4444;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
    }
    .radar-container {
        background: rgba(12, 13, 18, 0.98);
        border: 2px solid #3f3f46;
        border-radius: 14px;
        padding: 12px;
        box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.8), 0 10px 30px rgba(0, 0, 0, 0.7);
    }
    .alert-severe {
        background: rgba(239, 68, 68, 0.18);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-left: 5px solid #ef4444;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .alert-clear {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-left: 5px solid #10b981;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #d1fae5;
    }
    [data-testid="stMetric"] {
        background: rgba(24, 25, 32, 0.9) !important;
        border: 1px solid #27272a;
        border-radius: 10px;
        padding: 12px 16px;
    }
    [data-testid="stMetricLabel"] {
        color: #a1a1aa !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"] {
        color: #fafafa !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        background-color: #181922;
        border: 1px solid #27272a;
        color: #a1a1aa;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: #ef4444 !important;
        color: #ffffff !important;
        border-color: #ef4444 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- QUERY PARAMS RESOLUTION ---
query_params = st.query_params
default_lat = "41.8781"
default_lon = "-87.6298"

lat_str = query_params.get("lat", default_lat)
lon_str = query_params.get("lon", default_lon)
location_name = query_params.get("loc_name", "Detecting Location...")

try:
  ACTIVE_LAT = round(float(lat_str), 4)
  ACTIVE_LON = round(float(lon_str), 4)
except ValueError:
  ACTIVE_LAT = float(default_lat)
  ACTIVE_LON = float(default_lon)
  location_name = "Chicago, IL"

# --- NETWORK HEADER ---
st.markdown(
    """
<div class="tsn-header-bar"></div>
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 15px;">
    <div>
        <h1 style="color: #ffffff; margin: 0; font-size: 2.4rem; font-weight: 900; letter-spacing: -0.03em;">
            TSN <span style="color: #ef4444;">NEWS NETWORK</span>
        </h1>
        <p style="color: #a1a1aa; margin: 4px 0 0 0; font-size: 0.95rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;">
            Tri-State Weather Center & Live Telemetry
        </p>
    </div>
    <div style="text-align: right;">
        <span class="tsn-live-badge">LIVE DESK</span>
        <div style="color: #d4d4d8; font-size: 0.85rem; font-weight: 700; margin-top: 6px;">
            TARGET GRID: <span style="color: #ef4444;">%s</span>
        </div>
    </div>
</div>
"""
    % location_name,
    unsafe_allow_html=True,
)

# --- NEWS TICKER ---
cst_time = datetime.now(ZoneInfo
