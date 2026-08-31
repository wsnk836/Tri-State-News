from datetime import datetime
import time
from zoneinfo import ZoneInfo
import requests
import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="Tri State News",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- BROWSER LOCALSTORAGE BRIDGE ---
localStorage_sync_code = """
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
                const lat = savedLat || '42.8242';
                const lon = savedLon || '-95.7994';
                const loc = savedLoc || 'Marcus, IA';
                
                sessionStorage.setItem('tsn_synced', 'true');
                
                const newUrl = window.location.pathname + `?lat=${lat}&lon=${lon}&loc_name=${encodeURIComponent(loc)}`;
                
                if (window.top && window.top.history && window.top.history.replaceState) {
                    window.top.history.replaceState(null, '', newUrl);
                    window.top.location.href = newUrl;
                }
            } else {
                sessionStorage.setItem('tsn_synced', 'true');
            }
        }
    }
</script>
"""
components.html(localStorage_sync_code, height=0)

# --- TACTICAL CRIMSON & CARBON CSS ---
st.markdown(
    """
<style>
    .stApp {
        background-color: #0c0d10;
        color: #f4f4f5;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .hero-banner {
        background: linear-gradient(145deg, #18191f 0%, #0e0f12 100%);
        border: 1px solid #27272a;
        border-top: 3px solid #ef4444;
        border-radius: 14px;
        padding: 22px 28px;
        margin-bottom: 16px;
        box-shadow: 0 10px 25px -10px rgba(0, 0, 0, 0.7);
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        color: #f87171;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        color: #a1a1aa;
        font-size: 0.92rem;
        margin-top: 6px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-weight: 500;
    }
    .command-card {
        background: #121316;
        border: 1px solid #27272a;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
        color: #e4e4e7;
        font-size: 0.96rem;
        line-height: 1.5;
    }
    .welcome-card { border-left: 4px solid #ef4444; }
    .news-card {
        background: rgba(239, 68, 68, 0.05);
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-left: 4px solid #f87171;
        color: #fee2e2;
    }
    .install-card { border-left: 4px solid #38bdf8; color: #d4d4d8; font-size: 0.9rem; }
    .alert-card-severe {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-left: 4px solid #ef4444;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .alert-card-clear {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-left: 4px solid #10b981;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #d1fae5;
    }
    [data-testid="stMetric"] {
        background: #121316;
        border: 1px solid #27272a;
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #a1a1aa !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #fafafa !important;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 4px 12px;
        background-color: #121316;
        border: 1px solid #27272a;
        color: #a1a1aa;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: #ef4444 !important;
        color: #0c0d10 !important;
        border-color: #ef4444 !important;
        font-weight: 700 !important;
    }
    @media (max-width: 768px) {
        .block-container { padding: 1rem 0.75rem !important; }
        .hero-title { font-size: 1.4rem; }
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- RESOLVE & PERSIST QUERY PARAMS ---
query_params = st.query_params
default_lat = "42.8242"
default_lon = "-95.7994"

lat_str = query_params.get("lat", default_lat)
lon_str = query_params.get("lon", default_lon)
location_name = query_params.get("loc_name", "Marcus, IA")

try:
  ACTIVE_LAT = round(float(lat_str), 4)
  ACTIVE_LON = round(float(lon_str), 4)
except ValueError:
  ACTIVE_LAT = float(default_lat)
  ACTIVE_LON = float(default_lon)
  location_name = "Marcus, IA"

# --- HERO HEADER ---
st.markdown(
    """
<div class="hero-banner">
    <div class="hero-title">📡 Tri State News</div>
    <div class="hero-subtitle">Real-time NWS Telemetry & Regional Operations</div>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# --- ZIP CODE & LOCATION SELECTOR PANEL ---
# ==========================================
with st.expander("📍 Change Location (Enter ZIP Code or City Name)", expanded=False):
  with st.form("zip_search_form"):
    loc_input = st.text_input(
        "ZIP Code or City",
        placeholder="e.g. 51035 or Cherokee, IA",
        value="" if location_name == "Marcus, IA" else location_name,
    )
    submitted = st.form_submit_button("Update Location Grid")

    if submitted and loc_input.strip():
      try:
        geo_url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(loc_input)}&format=json&countrycodes=us&limit=1"
        geo_resp = requests.get(
            geo_url, headers={"User-Agent": "TriStateNewsApp"}, timeout=5
        ).json()

        if geo_resp:
          new_lat = geo_resp[0]["lat"]
          new_lon = geo_resp[0]["lon"]
          new_name = geo_resp[0].get("display_name", loc_input).split(",")[0]

          st.query_params["lat"] = new_lat
          st.query_params["lon"] = new_lon
          st.query_params["loc_name"] = new_name

          update_js = f"""
                    <script>
                        localStorage.setItem('tsn_lat', '{new_lat}');
                        localStorage.setItem('tsn_lon', '{new_lon}');
                        localStorage.setItem('tsn_loc_name', '{new_name}');
                        sessionStorage.setItem('tsn_synced', 'true');
                    </script>
                    """
          components.html(update_js, height=0)

          st.success(f"Location locked to: {geo_resp[0].get('display_name')}")
          time.sleep(0.5)
          st.rerun()
        else:
          st.error(
              "Location not found. Please try a valid US ZIP code or city name."
          )
      except Exception as e:
        st.error(f"Geocoding connection error: {e}")


# ==========================================
# --- CONTINUOUSLY REFRESHING FRAGMENT ---
# ==========================================
@st.fragment(run_every=60)
def load_live_weather(lat, lon, loc_label):
  headers = {
      "User-Agent": "TriStateNewsApp (wsnk836@gmail.com)",
      "Accept": "application/geo+json",
  }

  if "selected_forecast_day" not in st.session_state:
    st.session_state.selected_forecast_day = None

  radar_station = "KFSD"

  # --- ACTIVE SEVERE WEATHER ALERTS ---
  st.subheader(f"⚠️ Active NWS Weather Alerts ({loc_label})")

  try:
    alerts_url = f"https://api.weather.gov/alerts/active?point={lat},{lon}"
    alerts_response = requests.get(alerts_url, headers=headers, timeout=10).json()
    alerts = alerts_response.get("features", [])

    if len(alerts) > 0:
      for alert in alerts:
        props = alert.get("properties", {})
        event = props.get("event", "Weather Alert")
        headline = props.get("headline", "Severe weather alert issued.")
        description = props.get("description", "No description provided.")
        severity = props.get("severity", "Unknown")
        status_color = (
            "#ef4444" if severity in ["Extreme", "Severe"] else "#f87171"
        )

        st.markdown(
            f"""
                <div class="alert-card-severe" style="border-left-color: {status_color};">
                    <strong style="color: {status_color};">🚨 {event}</strong><br/>
                    <span style="color: #f4f4f5; font-size: 0.9rem; margin-top: 4px; display: block;">{headline}</span>
                </div>
                """,
            unsafe_allow_html=True,
        )

        with st.expander("📄 View Full Warning Statement"):
          st.write(description)
    else:
      st.markdown(
          f"""
            <div class="alert-card-clear">
                🟢 <strong>All Clear:</strong> No active warnings or advisories for {loc_label}.
            </div>
            """,
          unsafe_allow_html=True,
      )

  except Exception as e:
    st.error(f"Could not reach NWS alert servers: {e}")

  st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)

  # --- TWO-COLUMN DASHBOARD LAYOUT ---
  col_left, col_right = st.columns([1.1, 1], gap="large")

  with col_left:
    # --- CURRENT CONDITIONS & METRICS ---
    st.subheader(f"🌦️ Current Conditions ({loc_label})")
    try:
      points_url = f"https://api.weather.gov/points/{lat},{lon}"
      points_res = requests.get(points_url, headers=headers, timeout=10)

      if points_res.status_code != 200:
        st.error(
            f"NWS Grid Server error (Code {points_res.status_code}). Try a"
            " nearby ZIP code."
        )
        return

      points_response = points_res.json()
      if "properties" not in points_response:
        st.error("Received malformed data telemetry from NWS servers.")
        return

      radar_station = points_response["properties"].get("radarStation", "KFSD")

      forecast_url = points_response["properties"].get("forecast")
      if not forecast_url:
        st.error("Could not resolve forecast URL for this specific coordinate zone.")
        return

      forecast_res = requests.get(forecast_url, headers=headers, timeout=10)
      if forecast_res.status_code != 200:
        st.error("Could not reach NWS forecast servers.")
        return

      forecast_response = forecast_res.json()
      if "properties" not in forecast_response:
        st.error("Forecast data stream currently unavailable.")
        return

      periods = forecast_response["properties"]["periods"]
      current = periods[0]

      m1, m2, m3 = st.columns(3)
      with m1:
        st.metric(
            "🌡️ Temp", f"{current['temperature']}°{current['temperatureUnit']}"
        )
      with m2:
        st.metric("💨 Wind", f"{current['windSpeed']}")
      with m3:
        st.metric("☁️ Sky", current["shortForecast"])

      st.markdown(
          f"""
            <div style="background: #121316; border: 1px solid #27272a; border-radius: 10px; padding: 10px 14px; margin: 10px 0 15px 0; color: #d4d4d8; font-size: 0.88rem;">
                <strong>📋 Summary:</strong> {current['detailedForecast']}
            </div>
            """,
          unsafe_allow_html=True,
      )

      daily_forecasts = []
      i = 0
      while i < len(periods):
        p = periods[i]
        if p["isDaytime"]:
          day_name = p["name"]
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
              "day": day_name,
              "high": high_temp,
              "low": low_temp,
              "detailed": day_detailed,
              "low_detailed": night_detailed,
              "wind_speed": wind_speed,
              "wind_dir": wind_dir,
          })
        else:
          night_name = p["name"]
          day_label = (
              "Today"
              if night_name.lower() == "tonight"
              else night_name.replace(" Night", "").strip()
          )

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
              "day": day_label,
              "high": high_temp,
              "low": low_temp,
              "detailed": day_detailed,
              "low_detailed": night_detailed,
              "wind_speed": wind_speed,
              "wind_dir": wind_dir,
          })
        i += 1

      if (
          not st.session_state.selected_forecast_day
          or st.session_state.selected_forecast_day
          not in [d["day"] for d in daily_forecasts]
      ):
        st.session_state.selected_forecast_day = daily_forecasts[0]["day"]

      st.subheader("📅 Outlook")
      tab3, tab7 = st.tabs(["3-Day", "7-Day"])

      with tab3:
        days_to_show_3 = daily_forecasts[:3]
        cols3 = st.columns(len(days_to_show_3))
        for idx, d_item in enumerate(days_to_show_3):
          with cols3[idx]:
            is_selected = d_item["day"] == st.session_state.selected_forecast_day
            btn_label = f"📍 {d_item['day']}" if is_selected else d_item["day"]
            if st.button(
                btn_label, key=f"btn_3d_{idx}_{d_item['day']}", use_container_width=True
            ):
              st.session_state.selected_forecast_day = d_item["day"]
              st.rerun()

      with tab7:
        days_to_show_7 = daily_forecasts[:7]
        cols7 = st.columns(len(days_to_show_7))
        for idx, d_item in enumerate(days_to_show_7):
          with cols7[idx]:
            is_selected = d_item["day"] == st.session_state.selected_forecast_day
            btn_label = f"📍 {d_item['day']}" if is_selected else d_item["day"]
            if st.button(
                btn_label, key=f"btn_7d_{idx}_{d_item['day']}", use_container_width=True
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

      display_high = selected_record["high"]
      display_low = selected_record["low"]
      current_temp_str = f"{current['temperature']}°{current['temperatureUnit']}"
      if display_high == "N/A":
        display_high = current_temp_str
      if display_low == "N/A":
        display_low = current_temp_str

      st.markdown(
          f"""
            <div style="background: #18191f; border: 1px solid #27272a; border-left: 3px solid #ef4444; border-radius: 10px; padding: 18px 20px; margin-top: 15px;">
                <div style="font-weight: 700; color: #f87171; font-size: 1.05rem; margin-bottom: 10px;">
                    🏛️ Full NWS Forecast Report • {selected_record['day']}
                </div>
                {f'<div style="font-size: 0.92rem; color: #f4f4f5; margin-bottom: 8px; line-height: 1.6;"><strong>Daytime Forecast:</strong> {selected_record["detailed"]}</div>' if selected_record['detailed'] else ''}
                {f'<div style="font-size: 0.92rem; color: #d4d4d8; margin-bottom: 12px; line-height: 1.6;"><strong>Nighttime Forecast:</strong> {selected_record["low_detailed"]}</div>' if selected_record['low_detailed'] else ''}
                <div style="display: flex; flex-wrap: wrap; gap: 18px; margin-top: 12px; font-size: 0.85rem; color: #a1a1aa; border-top: 1px solid #27272a; padding-top: 10px;">
                    <div>🌡️ High: <strong style="color: #fafafa;">{display_high}</strong></div>
                    <div>🌡️ Low: <strong style="color: #fafafa;">{display_low}</strong></div>
                    <div>💨 Wind: <strong style="color: #fafafa;">{selected_record['wind_speed']} ({selected_record['wind_dir']})</strong></div>
                </div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    except Exception as e:
      st.error(f"Could not load NWS forecast telemetry: {e}")

    st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)

    # --- LIVE RADAR LOOP ---
    st.subheader(f"📡 Live Doppler Radar Loop ({radar_station})")
    cst_time = datetime.now(ZoneInfo("America/Chicago")).strftime(
        "%I:%M:%S %p %Z"
    )
    st.caption(f"🔄 Sync active • {cst_time} • Station: {radar_station}")
    radar_url = f"https://radar.weather.gov/ridge/standard/{radar_station}_loop.gif?t={int(time.time())}"
    with st.container(border=True):
      st.image(radar_url, use_container_width=True)

  with col_right:
    st.markdown(
        f"""
        <div class="command-card welcome-card">
            👋 <strong>Welcome to Tri State News.</strong> Currently monitoring regional grid coordinates <strong>{loc_label}</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("📻 Community News")
    st.markdown(
        """
        <div class="command-card news-card">
            <strong>LOCAL COMMUNITY UPDATE:</strong> Stay tuned here for regional announcements, weather advisories, and local updates across the tri-state area.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("📲 Install")
    st.markdown(
        """
        <div class="command-card install-card">
            <strong>Add to Home Screen:</strong><br/>
            • <strong>iOS (Safari):</strong> Tap <strong>Share</strong> ➔ <strong>"Add to Home Screen"</strong>.<br/>
            • <strong>Android (Chrome):</strong> Tap <strong>Menu (⋮)</strong> ➔ <strong>"Add to Home screen"</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )


load_live_weather(ACTIVE_LAT, ACTIVE_LON, location_name)

# ==========================================
# --- NATIVE STREAMLIT FEEDBACK FORM ---
# ==========================================
st.markdown("<div style='margin: 20px 0 10px 0;'></div>", unsafe_allow_html=True)
st.subheader("💬 Community Feedback and Suggestions")

with st.form("native_feedback_form"):
  fb_name = st.text_input("Name *", placeholder="Your Name")
  fb_loc = st.text_input("Location / Grid (Optional)", placeholder="Marcus, IA")
  fb_msg = st.text_area(
      "Your Feedback and Suggestions *",
      placeholder="Enter your feedback or suggestions here...",
  )
  fb_submitted = st.form_submit_button(
      "Send Feedback", use_container_width=True
  )

  if fb_submitted:
    name_val = fb_name if isinstance(fb_name, str) else ""
    if not name_val.strip() or not fb_msg.strip():
      st.error("Please fill out both your name and message before submitting.")
    else:
      try:
        payload = {
            "access_key": "6f59571f-f519-4655-9b50-095eed178152",
            "subject": (
                "💡 Community Feedback and Suggestions from Tri State News"
            ),
            "name": name_val,
            "location": fb_loc,
            "message": fb_msg,
        }
        res = requests.post(
            "https://api.web3forms.com/submit", json=payload, timeout=5
        )
        if res.status_code == 200:
          st.success(
              "✅ Feedback and suggestions sent directly to wsnk836@gmail.com!"
          )
        else:
          st.error("Server responded with an error. Please try again later.")
      except Exception as e:
        st.error(f"Network connection error: {e}")

# --- GITHUB REPOSITORY LINK FOOTER ---
st.markdown(
    """
<div style="text-align: center; color: #71717a; font-size: 0.88rem; padding-top: 20px; padding-bottom: 15px;">
    <hr style="border: none; border-top: 1px solid #27272a; margin-bottom: 15px;">
    💻 Source code available on 
    <a href="https://github.com/wsnk836/marcus-weather-app" target="_blank" style="color: #f87171; text-decoration: none; font-weight: 600;">
        GitHub
    </a>
</div>
""",
    unsafe_allow_html=True,
)
