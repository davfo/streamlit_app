import streamlit as st
import requests

# -----------------------------
# CONFIG NODE-RED
# -----------------------------
NODE_RED_URL = "https://nodered.david.work.gd/api/control"



st.set_page_config(page_title="Commande Aération", layout="centered")

st.title("🌀 Commande du système d’aération")

# =============================
# SYSTEME ON / OFF
# =============================
st.header("Système")

col1, col2 = st.columns(2)

system_state = None

with col1:
    if st.button("🟢 Mise en service"):
        system_state = 1

with col2:
    if st.button("🔴 Arrêt du système"):
        system_state = 0

# =============================
# VENTILATEURS
# =============================
st.header("Ventilateurs")

adm_speed = st.slider(
    "Vitesse admission (%)",
    0, 100, 50
)

ext_speed = st.slider(
    "Vitesse extraction (%)",
    0, 100, 50
)

# =============================
# ENVOI AUTOMATIQUE HTTP
# =============================
data = {
    "system": system_state,
    "adm_speed": adm_speed,
    "ext_speed": ext_speed
}

try:
    response = requests.post(NODE_RED_URL, json=data, timeout=2)
    if response.status_code == 200:
        st.success("Commande envoyée à Node-RED")
    else:
        st.error(f"Erreur HTTP : {response.status_code}")
except Exception as e:
    st.error("Impossible de joindre Node-RED")
