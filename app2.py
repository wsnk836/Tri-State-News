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
    .stTabs [data-basew
