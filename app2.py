from datetime import datetime, timedelta
import time
from zoneinfo import ZoneInfo
import requests
import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Tri-State News | TSN Live",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- PWA STATIC MANIFEST INJECTION ---
pwa_manifest_code = """
<script>
    let link = document.createElement('link');
    link.rel = 'manifest';
    link.href = './app/static/manifest.json';
    document.head.appendChild(link);
</script>
"""
components.html(pwa_manifest_code, height=0)
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
    }
    /* Modern, Sleek Neon Radar Window Frame */
    .radar-wrapper {
        background: linear-gradient(180deg, #12131c 0%, #090a0f 100%);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.7), 0 0 20px rgba(239, 68, 68, 0.08);
        position: relative;
        overflow: hidden;
    }
    .radar-screen-inner {
        position: relative;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #27272a;
        background: #050508;
    }
    /* Scanline visual overlay effect */
    .radar-screen-inner::after {
        content: " ";
        display: block;
        position: absolute;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
        z-index: 10;
        background-size: 100% 4px, 6px 100%;
        pointer-events: none;
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
    /* Force Streamlit columns to stay horizontal and prevent stacking on desktop for all layouts */
    [data-testid="column"] {
        flex: 1 !important;
        min-width: 0 !important;
    }
    /* Ensure button text stays inline horizontally instead of wrapping vertically letter by letter */
    div[data-testid="column"] button p {
        white-space: nowrap !important;
    }
    div[data-testid="column"] button {
        font-size: 0.78rem !important;
        padding-left: 2px !important;
        padding-right: 2px !important;
        writing-mode: horizontal-tb !important;
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
  st.image(
      "777468448_1567274085055308_6458077729241826651_n_2.jpg", width=110
  )
except Exception:
  st.markdown(
      "<h3 style='color: #ef4444; margin:0;'>TSN</h3>",
      unsafe_allow_html=True,
  )

col_title, col_badge = st.columns([3.5, 1.2], vertical_alignment="bottom")

with col_title:
  st.markdown(
      """
        <h1 style="color: #ffffff; margin: 0; font-size: 2.2rem; font-weight: 900; letter-spacing: -0.03em; line-height: 1.1;">
            TSN <span style="color: #ef4444;">NEWS NETWORK</span>
        </h1>
        <p style="color: #a1a1aa; margin: 2px 0 0 0; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;">
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
            <div style="color: #d4d4d8; font-size: 0.8rem; font-weight: 700; margin-top: 6px;">
                TARGET GRID: <span style="color: #ef4444;">{location_name}</span>
            </div>
        </div>
        """,
      unsafe_allow_html=True,
  )

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# --- BREAKING NEWS BANNER ---
st.markdown(
    """
<div class="breaking-news-banner">
    <a href="https://www.facebook.com/p/Tri-State-News-100078393567762/" target="_blank" class="breaking-news-link">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span class="tsn-live-badge">BREAKING NEWS</span>
            <span style="font-size: 1.05rem; font-weight: 800; letter-spacing: -0.01em;">Body found in Riverside Park</span>
        </div>
        <div style="font-size: 0.85rem; color: #a1a1aa; font-weight: 600; display: flex; align-items: center; gap: 4px;">
            <span>Read Update on Facebook</span> &rarr;
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
        }
    ]

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
            "#ef4444" if severity in ["Extreme", "Severe"] else "#f87171"
        )

        st.markdown(
            f"""
                <div class="alert-severe" style="border-left-color: {status_color};">
                    <strong style="color: {status_color};">🚨 TSN BULLETIN: {event}</strong><br/>
                    <span style="color: #f4f4f5; font-size: 0.92rem; margin-top: 4px; display: block;">{headline}</span>
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
                🟢 <strong>TSN STATUS:</strong> All clear. No active severe warnings for {loc_label}.
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
                <span style="width: 8px; height: 8px; background-color: #22c55e; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #22c55e;"></span>
                <h3 style="margin: 0; color: #f4f4f5; font-size: 1.1rem; font-weight: 800; letter-spacing: -0.01em;">LIVE DOPPLER • <span style="color: #ef4444;">{radar_station}</span></h3>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">HD VECTOR</span>
                <span style="background: rgba(24, 25, 32, 0.9); color: #a1a1aa; border: 1px solid #27272a; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">60S REFRESH</span>
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
            <h3 style="color: #f87171; margin-top: 0; font-size: 1.2rem;">📊 METEOROLOGICAL DESK</h3>
            <p style="color: #d4d4d8; font-size: 0.9rem; line-height: 1.5; margin-bottom: 15px;">
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
      date_str = current_date.strftime("%m/%d")  # e.g. "08/31"

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
        "<h4 style='color: #fafafa; font-size: 1rem; margin-bottom: 8px;'>📅"
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
        <div style="background: rgba(18, 19, 26, 0.95); border: 1px solid #27272a; border-left: 3px solid #ef4444; border-radius: 8px; padding: 14px; margin-top: 12px;">
            <div style="font-weight: 700; color: #f87171; font-size: 0.95rem; margin-bottom: 6px;">
                📋 REPORT • {selected_record['day']}
            </div>
            {f'<div style="font-size: 0.85rem; color: #f4f4f5; margin-bottom: 6px;"><strong>Day:</strong> {selected_record["detailed"]}</div>' if selected_record['detailed'] else ''}
            {f'<div style="font-size: 0.85rem; color: #d4d4d8; margin-bottom: 8px;"><strong>Night:</strong> {selected_record["low_detailed"]}</div>' if selected_record['low_detailed'] else ''}
            <div style="display: flex; gap: 15px; font-size: 0.8rem; color: #a1a1aa; border-top: 1px solid #27272a; padding-top: 6px;">
                <div>High: <strong style="color: #fafafa;">{selected_record['high']}</strong></div>
                <div>Low: <strong style="color: #fafafa;">{selected_record['low']}</strong></div>
                <div>Wind: <strong style="color: #fafafa;">{selected_record['wind_speed']}</strong></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ==========================================
    # --- COMMUNITY ANNOUNCEMENTS AREA ---
    # ==========================================
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background: rgba(18, 19, 26, 0.95); border: 1px solid #27272a; border-top: 3px solid #ef4444; border-radius: 12px; padding: 18px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);">
            <h3 style="color: #f87171; margin-top: 0; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                📢 COMMUNITY ANNOUNCEMENTS BOARD
            </h3>
            <p style="color: #a1a1aa; font-size: 0.85rem; margin-bottom: 15px;">
                View live regional notices or post your own public announcements below.
            </p>
        """,
        unsafe_allow_html=True,
    )

    # Display existing announcements
    for ann in st.session_state.community_announcements:
      st.markdown(
          f"""
            <div style="background: #0f1015; border: 1px solid #27272a; border-left: 3px solid #ef4444; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <strong style="color: #fafafa; font-size: 0.9rem;">{ann['title']}</strong>
                    <span style="color: #71717a; font-size: 0.75rem;">{ann['time']}</span>
                </div>
                <p style="color: #d4d4d8; font-size: 0.85rem; margin: 0 0 6px 0; line-height: 1.4;">{ann['text']}</p>
                <div style="color: #a1a1aa; font-size: 0.75rem; font-style: italic;">Posted by: {ann['author']}</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    # Submission form inside an expander to keep layout clean
    with st.expander("➕ Post New Community Announcement"):
      with st.form("community_announcement_form"):
        ann_author = st.text_input("Your Name / Organization *")
        ann_title = st.text_input("Announcement Title *")
        ann_text = st.text_area("Announcement Details *")
        ann_submitted = st.form_submit_button(
            "Publish Announcement", use_container_width=True
        )

        if ann_submitted:
          if not ann_author.strip() or not ann_title.strip() or not ann_text.strip():
            st.error("Please fill in all required announcement fields.")
          else:
            current_timestamp = datetime.now(ZoneInfo("America/Chicago")).strftime(
                "%b %d, %I:%M %p"
            )
            st.session_state.community_announcements.insert(
                0,
                {
                    "author": ann_author.strip(),
                    "title": ann_title.strip(),
                    "text": ann_text.strip(),
                    "time": current_timestamp,
                },
            )
            st.success("Announcement published successfully!")
            time.sleep(0.3)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


render_tsn_broadcast_center(ACTIVE_LAT, ACTIVE_LON, location_name)

# ==========================================
# --- COMMUNITY FEEDBACK DESK (CLIENT-SIDE JS) ---
# ==========================================
st.markdown("<div style='margin: 30px 0 10px 0;'></div>", unsafe_allow_html=True)

st.markdown(
    """
<div style="background: rgba(18, 19, 26, 0.95); border: 1px solid #27272a; border-top: 3px solid #ef4444; border-radius: 12px; padding: 20px; font-family: system-ui, -apple-system, sans-serif; color: #f4f4f5; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);">
    <h3 style="color: #f87171; margin-top: 0; font-size: 1.2rem;">💬 TSN VIEWER & COMMUNITY FEEDBACK DESK</h3>
    <p style="color: #a1a1aa; font-size: 0.9rem; margin-bottom: 15px;">
        Have news tips, weather updates, or suggestions for the network? Send your message directly to the TSN desk at <strong style="color: #fafafa;">wsnk836@gmail.com</strong>.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

with st.form("tsn_feedback_form"):
  fb_name = st.text_input("Viewer Name *", placeholder="Your Name")
  fb_loc = st.text_input("Your Location / Grid (Optional)", placeholder="City or ZIP")
  fb_msg = st.text_area(
      "Feedback or News Tip *",
      placeholder="Enter your message, news tip, or suggestion here...",
  )
  submit_feedback = st.form_submit_button(
      "Transmit Feedback to Desk", use_container_width=True
  )

  if submit_feedback:
    if not fb_name.strip() or not fb_msg.strip():
      st.error(
          "⚠️ Transmission error: Please provide both your name and message."
      )
    else:
      safe_name = fb_name.strip().replace("'", "\\'")
      safe_loc = (
          fb_loc.strip().replace("'", "\\'") if fb_loc else "Not provided"
      )
      safe_msg = fb_msg.strip().replace("'", "\\'").replace("\n", " ")

      client_js = f"""
            <script>
            async function sendFeedback() {{
                const payload = {{
                    access_key: "6f59571f-f519-4655-9b50-095eed178152",
                    subject: "💡 Community Feedback and Suggestions from TSN News Network",
                    name: "{safe_name}",
                    location: "{safe_loc}",
                    message: "{safe_msg}"
                }};
                
                try {{
                    let response = await fetch("https://api.web3forms.com/submit", {{
                        method: "POST",
                        headers: {{
                            "Content-Type": "application/json",
                            "Accept": "application/json"
                        }},
                        body: JSON.stringify(payload)
                    }});
                    let data = await response.json();
                    if (data.success) {{
                        console.log("Feedback sent successfully");
                    }} else {{
                        console.error("Submission failed:", data.message);
                    }}
                }} catch (err) {{
                    console.error("Network error:", err);
                }}
            }}
            sendFeedback();
            </script>
            """
      components.html(client_js, height=0)
      st.success(
          "✅ Feedback successfully transmitted directly to wsnk836@gmail.com!"
      )

# --- NETWORK FOOTER ---
st.markdown(
    """
<div style="text-align: center; color: #71717a; font-size: 0.82rem; margin-top: 40px; padding-bottom: 20px;">
    <hr style="border: none; border-top: 1px solid #27272a; margin-bottom: 15px;">
    <strong>TSN NEWS NETWORK</strong> • Tri-State Broadcast Operations & Meteorological Telemetry<br>
    Powered by NWS Meteorological Data Servers
</div>
""",
    unsafe_allow_html=True,
)
