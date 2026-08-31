from datetime import datetime, timedelta
import time
import urllib.parse
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
        "https://www.facebook.com/p/Tri-State-News-100078393567762/"
    )

if "community_announcements" not in st.session_state:
    st.session_state.community_announcements = [
        {
            "author": "TSN Desk",
            "title": "Welcome to Tri-State Announcements",
            "text": (
                "Use the submission form below to broadcast local notices,"
                " community events, or missing item alerts."
            ),
            "time": datetime.now(ZoneInfo("America/Chicago")).strftime(
                "%b %d, %I:%M %p"
            ),
        },
    ]

# --- BREAKING NEWS BANNER ---
st.markdown(
    f"""
<div class="breaking-news-banner">
    <a href="{st.session_state.breaking_news_link}" target="_blank" class="breaking-news-link">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span class="tsn-live-badge">BREAKING NEWS</span>
            <span style="font-size: 1.05rem; font-weight: 800; color: #0f172a; letter-spacing: -0.01em;">{st.session_state.breaking_news_title}</span>
        </div>
        <div style="font-size: 0.85rem; color: #dc2626; font-weight: 700; display: flex; align-items: center; gap: 4px;">
            <span>Read Update</span> &rarr;
        </div>
    </a>
</div>
""",
    unsafe_allow_html=True,
)

# --- NEWS TICKER ---
cst_time = datetime.now(ZoneInfo("America/Chicago")).strftime(
    "%I:%M:%S %p %Z"
)
st.markdown(
    f"""
<div class="tsn-ticker">
    <span class="tsn-live-badge">UPDATE</span>
    <span>Law enforcement on scene at Riverside Park • NWS KSFD Doppler radar telemetry online • System time: {cst_time}</span>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# --- US ZIP CODE LOCATION OVERRIDE PANEL ---
# ==========================================
with st.expander(
    "🇺🇸 Enter US ZIP Code for Regional Override", expanded=False
):
    with st.form("zip_override_form"):
        zip_input = st.text_input(
            "US ZIP Code", placeholder="e.g. 51101 or 60601", max_chars=5
        )
        zip_submitted = st.form_submit_button("Lock ZIP Grid")

        if zip_submitted and zip_input.strip():
            if len(zip_input.strip()) == 5 and zip_input.strip().isdigit():
                try:
                    geo_url = f"https://nominatim.openstreetmap.org/search?postalcode={zip_input.strip()}&country=us&format=json&limit=1"
                    geo_resp = requests.get(
                        geo_url, headers={"User-Agent": "TSNNetworkApp"}, timeout=5
                    ).json()

                    if geo_resp:
                        new_lat = geo_resp[0]["lat"]
                        new_lon = geo_resp[0]["lon"]
                        raw_name = geo_resp[0].get("display_name")
                        if raw_name:
                            display_name = raw_name.split(",")[0]
                        else:
                            display_name = "ZIP " + zip_input.strip()
                        loc_label = f"{display_name}, US ({zip_input.strip()})"

                        st.query_params["lat"] = new_lat
                        st.query_params["lon"] = new_lon
                        st.query_params["loc_name"] = loc_label

                        update_js = f"""
                            <script>
                                localStorage.setItem('tsn_lat', '{new_lat}');
                                localStorage.setItem('tsn_lon', '{new_lon}');
                                localStorage.setItem('tsn_loc_name', '{loc_label}');
                                sessionStorage.setItem('tsn_synced', 'true');
                                window.location.reload();
                            </script>
                            """
                        components.html(update_js, height=0)
                        st.success(f"Grid updated successfully to ZIP {zip_input}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("ZIP code not found in US database. Please verify.")
                except Exception as e:
                    st.error(f"Geocoding connection error: {e}")
            else:
                st.error("Please enter a valid 5-digit US ZIP code.")


# ==========================================
# --- LIVE FRAGMENT: RADAR & WEATHER OUTLOOK ---
# ==========================================
@st.fragment(run_every=60)
def render_tsn_broadcast_center(lat, lon, loc_label):
    headers = {
        "User-Agent": "TSNNetworkApp (wsnk836@gmail.com)",
        "Accept": "application/geo+json",
    }

    if "selected_forecast_day" not in st.session_state:
        st.session_state.selected_forecast_day = None

    # --- ACTIVE WEATHER ALERTS ---
    try:
        alerts_url = f"https://api.weather.gov/alerts/active?point={lat},{lon}"
        alerts_response = requests.get(alerts_url, headers=headers, timeout=10).json()
        alerts = alerts_response.get("features", [])

        if len(alerts) > 0:
            for alert in alerts:
                props = alert.get("properties", {})
                event = props.get("event", "Weather Alert")
                headline = props.get("headline", "Severe weather advisory issued.")
                description = props.get("description", "No details provided.")
                severity = props.get("severity", "Unknown")
                status_color = (
                    "#dc2626" if severity in ["Extreme", "Severe"] else "#ea580c"
                )

                st.markdown(
                    f"""
                    <div class="alert-severe" style="border-left-color: {status_color};">
                        <strong style="color: {status_color}; font-size: 1rem;">🚨 TSN BULLETIN: {event}</strong><br/>
                        <span style="color: #1e293b; font-size: 0.95rem; font-weight: 600; margin-top: 4px; display: block;">{headline}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander("📄 View Full Emergency Statement"):
                    st.write(description)
        else:
            st.markdown(
                f"""
                <div class="alert-clear">
                    🟢 <strong style="color: #14532d;">TSN STATUS:</strong> All clear. No active severe warnings for {loc_label}.
                </div>
                """,
                unsafe_allow_html=True,
            )
    except Exception as e:
        st.error(f"Alert telemetry feed unreachable: {e}")

    # --- FETCH NWS POINTS & FORECAST ---
    try:
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        points_res = requests.get(points_url, headers=headers, timeout=10)

        if points_res.status_code != 200:
            st.error(
                "NWS Grid Server error. Coordinates may fall outside US jurisdiction."
            )
            return

        points_data = points_res.json()
        radar_station = points_data["properties"].get("radarStation", "KSFD")
        forecast_url = points_data["properties"].get("forecast")

        forecast_res = requests.get(forecast_url, headers=headers, timeout=10)
        forecast_data = forecast_res.json()
        periods = forecast_data["properties"]["periods"]
        current = periods[0]

    except Exception as e:
        st.error(f"Error establishing NWS data link: {e}")
        return

    # --- LAYOUT: MODERN RADAR & OUTLOOK ---
    col_radar, col_outlook = st.columns([1.5, 1], gap="large")

    with col_radar:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="width: 10px; height: 10px; background-color: #16a34a; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #16a34a;"></span>
                    <h3 style="margin: 0; color: #0f172a; font-size: 1.1rem; font-weight: 800; letter-spacing: -0.01em;">LIVE DOPPLER • <span style="color: #dc2626;">{radar_station}</span></h3>
                </div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">HD VECTOR</span>
                    <span style="background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">60S REFRESH</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        radar_url = f"https://radar.weather.gov/ridge/standard/{radar_station}_loop.gif?t={int(time.time())}"

        st.markdown(
            '<div class="radar-wrapper"><div class="radar-screen-inner">',
            unsafe_allow_html=True,
        )
        st.image(radar_url, use_container_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(
                "🌡️ Temp", f"{current['temperature']}°{current['temperatureUnit']}"
            )
        with m2:
            st.metric("💨 Wind", f"{current['windSpeed']}")
        with m3:
            st.metric("☁️ Conditions", current["shortForecast"])

    with col_outlook:
        st.markdown(
            f"""
            <div class="broadcast-panel" style="margin-top: 0;">
                <h3 style="color: #dc2626; margin-top: 0; font-size: 1.2rem; font-weight: 800;">📊 METEOROLOGICAL DESK</h3>
                <p style="color: #334155; font-size: 0.95rem; font-weight: 500; line-height: 1.6; margin-bottom: 15px;">
                    {current['detailedForecast']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        daily_forecasts = []
        i = 0
        base_date = datetime.now(ZoneInfo("America/Chicago"))
        day_counter = 0

        while i < len(periods) and day_counter < 7:
            p = periods[i]
            current_date = base_date + timedelta(days=day_counter)
            date_str = current_date.strftime("%m/%d")

            if p["isDaytime"]:
                day_detailed = p["detailedForecast"]
                high_temp = f"{p['temperature']}°{p['temperatureUnit']}"
                wind_speed = p["windSpeed"]
                wind_dir = p.get("windDirection", "")
                low_temp = "N/A"
                night_detailed = ""

                if i + 1 < len(periods) and not periods[i + 1]["isDaytime"]:
                    night_p = periods[i + 1]
                    low_temp = f"{night_p['temperature']}°{night_p['temperatureUnit']}"
                    night_detailed = night_p["detailedForecast"]
                    i += 1

                daily_forecasts.append({
                    "day": date_str,
                    "high": high_temp,
                    "low": low_temp,
                    "detailed": day_detailed,
                    "low_detailed": night_detailed,
                    "wind_speed": wind_speed,
                    "wind_dir": wind_dir,
                })
            else:
                low_temp = f"{p['temperature']}°{p['temperatureUnit']}"
                night_detailed = p["detailedForecast"]
                wind_speed = p["windSpeed"]
                wind_dir = p.get("windDirection", "")
                high_temp = "N/A"
                day_detailed = ""

                if i + 1 < len(periods) and periods[i + 1]["isDaytime"]:
                    day_p = periods[i + 1]
                    high_temp = f"{day_p['temperature']}°{day_p['temperatureUnit']}"
                    day_detailed = day_p["detailedForecast"]
                    i += 1

                daily_forecasts.append({
                    "day": date_str,
                    "high": high_temp,
                    "low": low_temp,
                    "detailed": day_detailed,
                    "low_detailed": night_detailed,
                    "wind_speed": wind_speed,
                    "wind_dir": wind_dir,
                })
            i += 1
            day_counter += 1

        if (
            not st.session_state.selected_forecast_day
            or st.session_state.selected_forecast_day
            not in [d["day"] for d in daily_forecasts]
        ):
            st.session_state.selected_forecast_day = daily_forecasts[0]["day"]

        st.markdown(
            "<h4 style='color: #0f172a; font-size: 1rem; font-weight: 800; margin-bottom: 8px;'>📅"
            " 7-Day Regional Outlook</h4>",
            unsafe_allow_html=True,
        )
        tab3, tab7 = st.tabs(["3-Day Grid", "Full 7-Day Grid"])

        with tab3:
            days_3 = daily_forecasts[:3]
            cols3 = st.columns(len(days_3), gap="small")
            for idx, d_item in enumerate(days_3):
                with cols3[idx]:
                    is_selected = d_item["day"] == st.session_state.selected_forecast_day
                    btn_label = f"📍 {d_item['day']}" if is_selected else d_item["day"]
                    if st.button(
                        btn_label, key=f"btn_3_{idx}_{d_item['day']}", use_container_width=True
                    ):
                        st.session_state.selected_forecast_day = d_item["day"]
                        st.rerun()

        with tab7:
            days_7 = daily_forecasts[:7]
            cols7 = st.columns(len(days_7), gap="small")
            for idx, d_item in enumerate(days_7):
                with cols7[idx]:
                    is_selected = d_item["day"] == st.session_state.selected_forecast_day
                    btn_label = f"📍 {d_item['day']}" if is_selected else d_item["day"]
                    if st.button(
                        btn_label, key=f"btn_7_{idx}_{d_item['day']}", use_container_width=True
                    ):
                        st.session_state.selected_forecast_day = d_item["day"]
                        st.rerun()

        selected_record = next(
            (
                d
                for d in daily_forecasts
                if d["day"] == st.session_state.selected_forecast_day
            ),
            daily_forecasts[0],
        )

        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #cbd5e1; border-left: 4px solid #dc2626; border-radius: 8px; padding: 14px; margin-top: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                <div style="font-weight: 800; color: #dc2626; font-size: 0.95rem; margin-bottom: 6px;">
                    📋 REPORT • {selected_record['day']}
                </div>
                {f'<div style="font-size: 0.9rem; color: #1e293b; font-weight: 500; margin-bottom: 6px;"><strong>Day:</strong> {selected_record["detailed"]}</div>' if selected_record['detailed'] else ''}
                {f'<div style="font-size: 0.9rem; color: #334155; font-weight: 500; margin-bottom: 8px;"><strong>Night:</strong> {selected_record["low_detailed"]}</div>' if selected_record['low_detailed'] else ''}
                <div style="display: flex; gap: 15px; font-size: 0.85rem; color: #475569; border-top: 1px solid #e2e8f0; padding-top: 8px;">
                    <div>High: <strong style="color: #0f172a;">{selected_record['high']}</strong></div>
                    <div>Low: <strong style="color: #0f172a;">{selected_record['low']}</strong></div>
                    <div>Wind: <strong style="color: #0f172a;">{selected_record['wind_speed']}</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ==========================================
        # --- EXPANDED COMMUNITY ANNOUNCEMENTS AREA ---
        # ==========================================
        st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #cbd5e1; border-top: 4px solid #dc2626; border-radius: 14px; padding: 24px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); margin-bottom: 25px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h2 style="color: #0f172a; margin: 0; font-size: 1.4rem; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                        📢 TRI-STATE COMMUNITY ANNOUNCEMENTS DESK
                    </h2>
                    <span style="background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; padding: 3px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">PUBLIC BULLETIN BOARD</span>
                </div>
                <p style="color: #334155; font-size: 0.95rem; font-weight: 500; margin-bottom: 20px; line-height: 1.6;">
                    Your direct broadcast channel for regional public notices, community gatherings, missing item alerts, and local organization updates across the tri-state area.
                </p>
            """,
            unsafe_allow_html=True,
        )

        if len(st.session_state.community_announcements) == 0:
            st.info("No active community announcements on the board.")
        else:
            for idx, ann in enumerate(st.session_state.community_announcements):
                st.markdown(
                    f"""
                    <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-left: 6px solid #dc2626; border-radius: 12px; padding: 22px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <strong style="color: #0f172a; font-size: 1.25rem; font-weight: 800; letter-spacing: -0.01em;">{ann['title']}</strong>
                            <span style="color: #475569; font-size: 0.85rem; background: #e2e8f0; padding: 4px 10px; border-radius: 6px; font-weight: 700;">{ann['time']}</span>
                        </div>
                        <p style="color: #1e293b; font-size: 1.05rem; font-weight: 500; margin: 0 0 16px 0; line-height: 1.6;">{ann['text']}</p>
                        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #e2e8f0; padding-top: 10px;">
                            <div style="color: #475569; font-size: 0.9rem; font-style: italic;">
                                Broadcasted by: <strong style="color: #334155;">{ann['author']}</strong>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # ==========================================
        # --- DIRECT DESK FEEDBACK & SUBMISSION FORM ---
        # ==========================================
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        with st.expander("✉️ Send Community Announcement or Feedback to TSN Desk", expanded=False):
            st.markdown(
                """
                <p style="color: #334155; font-size: 0.9rem; margin-bottom: 15px;">
                    Have a local news tip, a community announcement, or app feedback? Click below to instantly open your email client pre-addressed to <strong>wsnk836@gmail.com</strong> and <strong>news@tsnnet.org</strong>.
                </p>
                """,
                unsafe_allow_html=True
            )
            
            with st.form("tsn_feedback_form"):
                fb_name = st.text_input("Your Name / Organization", placeholder="e.g. Jane Doe or Riverside Community Club")
                fb_type = st.selectbox("Submission Type", ["Community Announcement", "News Tip / Scoop", "App Feedback / Bug Report"])
                fb_title = st.text_input("Headline / Subject", placeholder="e.g. Annual Community Food Drive at City Park")
                fb_message = st.text_area("Message Details", placeholder="Provide all relevant details, times, locations, or feedback notes here...")
                
                submitted = st.form_submit_button("Open Email Client to Send")
                
                if submitted:
                    if not fb_name.strip() or not fb_title.strip() or not fb_message.strip():
                        st.error("Please fill out all required fields before sending.")
                    else:
                        recipients = "wsnk836@gmail.com,news@tsnnet.org"
                        subject = urllib.parse.quote(f"[{fb_type}] {fb_title}")
                        body = urllib.parse.quote(f"Name/Org: {fb_name}\nType: {fb_type}\n\nDetails:\n{fb_message}")
                        
                        mailto_url = f"mailto:{recipients}?subject={subject}&body={body}"
                        
                        email_trigger_html = f"""
                        <script>
                            window.location.href = "{mailto_url}";
                        </script>
                        """
                        components.html(email_trigger_html, height=0)
                        
                        st.success("Preparing your email client! If your device didn't open it automatically, click the secure link below:")
                        st.markdown(f'<a href="{mailto_url}" target="_blank" style="background-color: #dc2626; color: white; padding: 10px 16px; border-radius: 6px; text-decoration: none; font-weight: 800; display: inline-block; margin-top: 10px;">✉️ Click Here to Launch Email Client</a>', unsafe_allow_html=True)
                        
                        # If it's a community announcement, also push it to the live board state
                        if fb_type == "Community Announcement":
                            new_item = {
                                "author": fb_name.strip(),
                                "title": fb_title.strip(),
                                "text": fb_message.strip(),
                                "time": datetime.now(ZoneInfo("America/Chicago")).strftime("%b %d, %I:%M %p")
                            }
                            st.session_state.community_announcements.insert(0, new_item)

        st.markdown("</div>", unsafe_allow_html=True)

# Run Main Fragment Loop
render_tsn_broadcast_center(ACTIVE_LAT, ACTIVE_LON, location_name)
