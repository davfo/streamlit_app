import streamlit as st
import requests

# -----------------------------
# CONFIG NODE-RED
# -----------------------------
NODE_RED_CMD_URL = "https://nodered.david.work.gd/api/control"  # POST
NODE_RED_DATA_URL = "https://nodered.david.work.gd/api/data"     # GET

st.set_page_config(page_title="Commande Aération", layout="centered")
st.title("🌀 Commande du système d’aération")

# ============================================================
# VISUALISATION DES DONNÉES (TEMP / HUM / CO2)
# ============================================================
st.header("📊 Données environnementales")

try:
    r = requests.get(NODE_RED_DATA_URL, timeout=2)

    if r.status_code == 204:
        st.warning("Aucune donnée disponible pour le moment")
    else:
        data_capteurs = r.json()

        colT, colH, colC = st.columns(3)

        colT.metric(
            "🌡 Température",
            f"{data_capteurs['temperature']} °C"
        )

        colH.metric(
            "💧 Humidité",
            f"{data_capteurs['humidity']} %"
        )

        if data_capteurs["co2"] < 0:
            colC.metric("🧪 CO₂", "Non disponible")
        else:
            colC.metric("🧪 CO₂", f"{data_capteurs['co2']} ppm")

except Exception:
    st.error(" Impossible de récupérer les données capteurs")

st.divider()

# ============================================================
# SYSTEME ON / OFF
# ============================================================
st.header("Système")

col1, col2 = st.columns(2)
system_state = None

with col1:
    if st.button("🟢 Mise en service"):
        system_state = 1

with col2:
    if st.button("🔴 Arrêt du système"):
        system_state = 0

# ============================================================
# VENTILATEURS
# ============================================================
st.header("Ventilateurs")

adm_speed = st.slider(
    "Vitesse admission (%)",
    0, 100, 50
)

ext_speed = st.slider(
    "Vitesse extraction (%)",
    0, 100, 50
)

# ============================================================
# ENVOI AUTOMATIQUE HTTP (COMMANDES)
# ============================================================
data_cmd = {
    "system": system_state,
    "adm_speed": adm_speed,
    "ext_speed": ext_speed
}

try:
    response = requests.post(NODE_RED_CMD_URL, json=data_cmd, timeout=2)
    if response.status_code == 200:
        st.success("Commande envoyée à Node-RED")
    else:
        st.error(f"Erreur HTTP : {response.status_code}")
except Exception:
    st.error("Impossible de joindre Node-RED pour la commande")
