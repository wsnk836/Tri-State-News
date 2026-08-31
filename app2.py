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
                sessionStorage.setItem('tsn_synced', 'true');
                const defLat = '42.4006';
                const defLon = '-96.4001';
                const defLoc = 'Sioux City, IA';
                localStorage.setItem('tsn_lat', defLat);
                localStorage.setItem('tsn_lon', defLon);
                localStorage.setItem('tsn_loc_name', defLoc);
                const newUrl = window.location.pathname + `?lat=${defLat}&lon=${defLon}&loc_name=${encodeURIComponent(defLoc)}`;
                window.top.location.href = newUrl;
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
    .breaking-news-banner {
        background: linear-gradient(135deg, rgba(185, 28, 28, 0.25) 0%, rgba(18, 19, 26, 0.95) 100%);
        border: 1px solid rgba(239, 68, 68, 0.5);
        border-left: 6px solid #ef4444;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 25px;
        box-shadow: 0 6px 20px rgba(185, 28, 28, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .breaking-news-banner:hover {
        border-color: #ef4444;
        transform: translateY(-2px);
    }
    .breaking-news-link {
        color: #ffffff;
        text-decoration: none;
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
    }
    .breaking-news-link:hover {
        color: #fca5a5;
    }
    .broadcast-panel {
        background: rgba(18, 19, 26, 0.95);
        border: 1px solid #27272a;
        border-top: 3px solid #ef4444;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
