# app.py
import json
import requests
import streamlit as st
import time
from plyer import notification

# -------------------------
# Config & Load data
# -------------------------
st.set_page_config(page_title="🌤 Live Weather - Fun UI", layout="centered")

# Original background / basic styles (keeps app look you had)
# Theme toggle
theme_choice = st.radio("Theme Mode", ["Light", "Dark"], horizontal=True)

if theme_choice == "Light":
    st.markdown(
        """
        <style>
            /* App background */
            .stApp {
                background: linear-gradient(to bottom, #87CEEB, #ffffff);
                color: #222222;
            }

            /* Titles */
            h1, h2, h3, h4, h5, h6 { color: #1a1a1a !important; }

            /* Dropdowns */
            div[data-baseweb="select"] > div {
                background-color: #ffffff !important;
                color: #000000 !important;
                border-radius: 12px !important;
                border: 1px solid #cccccc !important;
            }

            /* Buttons */
            .stButton>button {
                background: linear-gradient(90deg, #4facfe, #00f2fe);
                color: white;
                font-weight: 600;
                border-radius: 12px;
                padding: 0.6em 1.2em;
                border: none;
            }
            .stButton>button:hover {
                background: linear-gradient(90deg, #00f2fe, #4facfe);
            }

            /* Metrics - frosted glass look */
            div[data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.6);
                border-radius: 15px;
                padding: 15px;
                margin: 10px 0;
                backdrop-filter: blur(8px);
                border: 1px solid rgba(200, 200, 200, 0.5);
                box-shadow: 2px 4px 12px rgba(0,0,0,0.1);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

else:  # Dark mode
    st.markdown(
        """
        <style>
            /* App background */
            .stApp {
                background: linear-gradient(to bottom, #1e3c72, #2a5298);
                color: #f5f5f5;
            }

            /* Titles */
            h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }

            /* Dropdowns */
            div[data-baseweb="select"] > div {
                background-color: #2a2a2a !important;
                color: #f5f5f5 !important;
                border-radius: 12px !important;
                border: 1px solid #666666 !important;
            }

            /* Buttons */
            .stButton>button {
                background: linear-gradient(90deg, #ff7e5f, #feb47b);
                color: #1a1a1a;
                font-weight: 600;
                border-radius: 12px;
                padding: 0.6em 1.2em;
                border: none;
            }
            .stButton>button:hover {
                background: linear-gradient(90deg, #feb47b, #ff7e5f);
            }

            /* Metrics - neon glow */
            div[data-testid="stMetric"] {
                background: #111111;
                border-radius: 15px;
                padding: 15px;
                margin: 10px 0;
                border: 1px solid #00e5ff;
                box-shadow: 0px 0px 15px #00e5ff, 0px 0px 30px #00e5ff55;
                color: #00e5ff !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Load countries and cities data

with open("countries_cities.json", "r", encoding="utf-8") as f:
    CITIES_BY_COUNTRY = json.load(f)

# -------------------------
# Weather maps & GIFs
# -------------------------
WC_MAP = {
    0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Light snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Light rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 99: "Severe thunderstorm"
}

WEATHER_ICONS = {
    "Clear": "☀️", "Mainly clear": "🌤", "Partly cloudy": "⛅️", "Overcast": "☁️",
    "Fog": "🌫", "Light drizzle": "🌦", "Moderate drizzle": "🌦", "Dense drizzle": "🌧",
    "Slight rain": "🌧", "Moderate rain": "🌧", "Heavy rain": "🌧🌧",
    "Light snow": "🌨", "Moderate snow": "🌨❄️", "Heavy snow": "❄️❄️",
    "Thunderstorm": "⛈", "Severe thunderstorm": "🌩"
}

WEATHER_GIFS = {
    "Clear": "gifs/sunny.gif",
    "Mainly clear": "gifs/sunny.gif",
    "Partly cloudy": "gifs/cloudy.gif",
    "Overcast": "gifs/cloudy.gif",
    "Fog": "gifs/cloudy.gif",
    "Light drizzle": "gifs/rain.gif",
    "Moderate drizzle": "gifs/rain.gif",
    "Dense drizzle": "gifs/rain.gif",
    "Slight rain": "gifs/rain.gif",
    "Moderate rain": "gifs/rain.gif",
    "Heavy rain": "gifs/rain.gif",
    "Light snow": "gifs/snow.gif",
    "Moderate snow": "gifs/snow.gif",
    "Heavy snow": "gifs/snow.gif",
    "Thunderstorm": "gifs/thunderstorm.gif",
    "Severe thunderstorm": "gifs/thunderstorm.gif",
}

# -------------------------
# Animation HTML snippets
# -------------------------
SPLASH_HTML = """
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:180px;">
  <div style="font-size:72px; animation:pop 1s ease-out;">🌤️</div>
  <div style="margin-top:8px;font-weight:600;">Welcome to Live Weather</div>
</div>
<style>
@keyframes pop {
  0% { transform: scale(0.2); opacity: 0; }
  70% { transform: scale(1.08); opacity: 1; }
  100% { transform: scale(1); }
}
</style>
"""

# loading animation (rotating sun + floating cloud)
LOADING_HTML_SUN = """
<div style="display:flex;align-items:center;justify-content:center;height:160px;">
  <div style="font-size:72px; animation:spin 1.3s linear infinite;">☀️</div>
</div>
<style>
@keyframes spin { from { transform: rotate(0deg);} to { transform: rotate(360deg); } }
</style>
"""

LOADING_HTML_CLOUD = """
<div style="display:flex;align-items:center;justify-content:center;height:160px;">
  <div style="font-size:72px; animation:float 1.4s ease-in-out infinite;">☁️</div>
</div>
<style>
@keyframes float { 0%{transform:translateY(0);}50%{transform:translateY(-10px);}100%{transform:translateY(0);} }
</style>
"""

SELECTION_BADGE_HTML = """
<div style="display:inline-block;padding:10px 16px;border-radius:20px;background:linear-gradient(90deg,#FFB347,#FF7043);color:white;font-weight:700; font-size:16px; animation:pop 0.7s ease-out;">
  Selected!
</div>
<style>
@keyframes pop {
  0% { transform: scale(0.1); opacity: 0; }
  60% { transform: scale(1.05); opacity: 1; }
  100% { transform: scale(1); }
}
</style>
"""

# -------------------------
# Session state defaults
# -------------------------
if "app_splash_shown" not in st.session_state:
    st.session_state.app_splash_shown = False

if "prev_country" not in st.session_state:
    st.session_state.prev_country = ""

if "prev_city" not in st.session_state:
    st.session_state.prev_city = ""

# -------------------------
# Helper functions
# -------------------------
def send_notification(city, temp, desc):
    try:
        notification.notify(title=f"Weather Update: {city}", message=f"{desc}, {temp}°C", timeout=5)
    except Exception:
        # if plyer fails (some Linux/remote envs), ignore silently
        pass

def fetch_weather(city_name, country_name):
    """Return dict with weather or None on failure."""
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {"name": city_name, "count": 1, "country": country_name}
        geo_res = requests.get(geo_url, params=geo_params, timeout=8)
        geo_res.raise_for_status()
        geo_data = geo_res.json()
        if "results" not in geo_data or len(geo_data["results"]) == 0:
            return None

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        pretty_name = geo_data["results"][0].get("name", city_name)

        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {"latitude": lat, "longitude": lon, "current_weather": True, "timezone": "auto"}
        weather_res = requests.get(weather_url, params=weather_params, timeout=8)
        weather_res.raise_for_status()
        weather_data = weather_res.json()
        if "current_weather" not in weather_data:
            return None

        cw = weather_data["current_weather"]
        temp = cw.get("temperature", "N/A")
        wind = cw.get("windspeed", "N/A")
        wind_dir = cw.get("winddirection", "N/A")
        code = cw.get("weathercode")
        desc = WC_MAP.get(code, "Unknown")

        icon = WEATHER_ICONS.get(desc, "🌈")
        gif = WEATHER_GIFS.get(desc, "gifs/sunny.gif")

        return {
            "name": pretty_name,
            "temp": temp,
            "wind": wind,
            "wind_dir": wind_dir,
            "desc": desc,
            "icon": icon,
            "gif": gif,
            "observed_time": cw.get("time", "")
        }

    except requests.exceptions.Timeout:
        st.error("⏳ Request timed out. Please check your internet connection.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Network error: {e}")
        return None
    except Exception as e:
        st.error(f"🚨 Unexpected error: {e}")
        return None

def show_splash_once():
    """Show a short splash screen only once per session."""
    if not st.session_state.app_splash_shown:
        splash = st.empty()
        splash.markdown(SPLASH_HTML, unsafe_allow_html=True)
        # show for a short moment
        time.sleep(1.0)
        splash.empty()
        st.session_state.app_splash_shown = True

def show_selection_animation():
    """Show a small 'Selected!' badge briefly when user changes selection."""
    badge = st.empty()
    badge.markdown(SELECTION_BADGE_HTML, unsafe_allow_html=True)
    time.sleep(0.6)
    badge.empty()

# -------------------------
# Main UI
# -------------------------
st.title("🌤 Live Weather — Fun UI")

# Run splash at start
show_splash_once()

# Country & city controls
country_name = st.selectbox("Select Country", options=list(CITIES_BY_COUNTRY.keys()), key="country_select")
city_list = CITIES_BY_COUNTRY.get(country_name, [])
city_name = st.selectbox("Select City", options=city_list, key="city_select")

# detect selection change and show small animation
# only show animation if this is not the first load (prev values exist and changed)
if st.session_state.prev_country != "" and st.session_state.prev_country != country_name:
    show_selection_animation()
if st.session_state.prev_city != "" and st.session_state.prev_city != city_name:
    show_selection_animation()

# update prev values
st.session_state.prev_country = country_name
st.session_state.prev_city = city_name

# placeholder for loading animation
loading_placeholder = st.empty()

# Button to get weather
if st.button("Get Weather", key="get_weather_btn"):
    # show loading animation (choose sun for daytime look or cloud if you prefer)
    # here we pick sun animation by default
    loading_placeholder.markdown(LOADING_HTML_SUN, unsafe_allow_html=True)

    # fetch data (this may take a second)
    weather = fetch_weather(city_name, country_name)

    # remove loading animation
    loading_placeholder.empty()

    if weather:
        # notification
        send_notification(weather["name"], weather["temp"], weather["desc"])

        # display results
        st.subheader(f"{weather['icon']} {weather['name']}")
        # use new parameter name to avoid deprecation warning
        st.image(weather["gif"], use_container_width=True)
        col1, col2 = st.columns(2)
        col1.metric("Temperature (°C)", f"{weather['temp']}°C")
        col1.metric("Wind (km/h)", f"{weather['wind']} km/h")
        col2.metric("Wind Dir (°)", f"{weather['wind_dir']}°")
        st.write(f"Condition: **{weather['desc']}**")
        st.caption(f"Observed at: {weather['observed_time']}")

    else:
        st.warning("City not found or weather unavailable. Try another city.")

# small footer or helper
st.markdown("---")
st.caption("Tip: change country/city to see a fun selection animation. Click Get Weather to fetch live data.")
