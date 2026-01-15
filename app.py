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
    st.session_state.system_state = False  # OFF
if "adm_speed" not in st.session_state:
    st.session_state.adm_speed = 0
if "ext_speed" not in st.session_state:
    st.session_state.ext_speed = 0
if "last_cmd" not in st.session_state:
    st.session_state.last_cmd = None
if "last_data" not in st.session_state:
    st.session_state.last_data = {}

# ============================
# AUTO-REFRESH (LECTURE SEULE)
# ============================
st_autorefresh(interval=30000, key="refresh")  # 30 s

# ============================
# FONCTION D’ENVOI SÉCURISÉE
# ============================
def send_command():
    payload = {
        "system": int(st.session_state.system_state),
        "adm_speed": st.session_state.adm_speed,
        "ext_speed": st.session_state.ext_speed
    }

    # ⛔ Anti-doublon
    if payload == st.session_state.last_cmd:
        return

    try:
        res = requests.post(NODE_RED_CMD_URL, json=payload, timeout=2)
        if res.status_code == 200:
            st.session_state.last_cmd = payload
            st.toast("✅ Commande envoyée", icon="✅")
        else:
            st.toast("❌ Erreur Node-RED", icon="❌")
    except:
        st.toast("❌ Node-RED injoignable", icon="⚠️")

# ============================
# LECTURE DES DONNÉES
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
# COMMANDE UTILISATEUR (AUTO-ENVOI)
# ============================
st.header("🎛 Commande du système")

# Toggle ON/OFF
st.toggle(
    "🟢 Système actif",
    key="system_state",
    on_change=send_command
)

# Sliders avec callback
st.slider(
    "Ventilateur admission (%)",
    0, 100,
    key="adm_speed",
    on_change=send_command
)

st.slider(
    "Ventilateur extraction (%)",
    0, 100,
    key="ext_speed",
    on_change=send_command
)

# ============================
# INFO ÉTAT LOCAL
# ============================
st.caption(
    f"État demandé : {'ON' if st.session_state.system_state else 'OFF'} | "
    f"Adm: {st.session_state.adm_speed}% | "
    f"Ext: {st.session_state.ext_speed}%"
)
