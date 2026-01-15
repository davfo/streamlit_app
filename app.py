import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

# ============================
# CONFIG NODE-RED
# ============================
NODE_RED_CMD_URL = "https://nodered.david.work.gd/api/control"  # POST
NODE_RED_DATA_URL = "https://nodered.david.work.gd/api/data"   # GET

st.set_page_config(page_title="Commande Aération", layout="centered")
st.title("🌀 Commande du système d’aération")

# ============================
# SESSION STATE (PERSISTANCE)
# ============================
if "system_state" not in st.session_state:
    st.session_state.system_state = 0
if "adm_speed" not in st.session_state:
    st.session_state.adm_speed = 0
if "ext_speed" not in st.session_state:
    st.session_state.ext_speed = 0
if "last_cmd" not in st.session_state:
    st.session_state.last_cmd = None
if "last_data" not in st.session_state:
    st.session_state.last_data = {}

# ============================
# AUTO-REFRESH (30 secondes)
# ============================
st_autorefresh(interval=30000, key="refresh")

# ============================
# LECTURE DES DONNÉES (SANS CACHE)
# ============================
def get_data():
    try:
        r = requests.get(NODE_RED_DATA_URL, timeout=2)
        return r.json()
    except:
        return None

def update_data():
    new_data = get_data()
    if new_data:
        st.session_state.last_data = new_data
    return st.session_state.last_data

# ============================
# DONNÉES ACTUELLES
# ============================
data = update_data()

mode = data.get("mode", "—")
temp = data.get("temperature")
hum  = data.get("humidite")
co2  = data.get("co2")

if mode == "ARRET":
    temp, hum, co2 = None, None, None

# ============================
# AFFICHAGE DONNÉES (STABLE)
# ============================
st.header("📊 Données environnementales")

col1, col2, col3 = st.columns(3)

col1.metric(
    "🌡 Température (°C)",
    f"{temp:.1f}" if isinstance(temp, (int, float)) else "--"
)

col2.metric(
    "💧 Humidité (%)",
    f"{hum:.1f}" if isinstance(hum, (int, float)) else "--"
)

col3.metric(
    "🫁 CO₂ (ppm)",
    f"{co2}" if isinstance(co2, (int, float)) else "--"
)

st.info(f"Mode actuel : **{mode}**")
st.divider()

# ============================
# COMMANDE UTILISATEUR
# ============================
st.header("🎛 Commande du système")

col_on, col_off = st.columns(2)

with col_on:
    if st.button("🟢 Allumer"):
        st.session_state.system_state = 1

with col_off:
    if st.button("🔴 Éteindre"):
        st.session_state.system_state = 0

adm_speed = st.slider(
    "Ventilateur admission (%)",
    0, 100,
    st.session_state.adm_speed,
    key="adm_speed"
)

ext_speed = st.slider(
    "Ventilateur extraction (%)",
    0, 100,
    st.session_state.ext_speed,
    key="
