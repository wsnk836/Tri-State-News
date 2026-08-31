from datetime import datetime, timedelta
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
    "                   "
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
    .breaking-news-banner {
        background: linear-gradient(135deg, rgba(185,
