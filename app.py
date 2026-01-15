import streamlit as st
import requests
import time
from streamlit_autorefresh import st_autorefresh  # Utilisation de st_autorefresh

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
    st.session_state.system_state = 0  # 0 = arrêt
if "adm_speed" not in st.session_state:
    st.session_state.adm_speed = 0
if "ext_speed" not in st.session_state:
    st.session_state.ext_speed = 0
if "last_cmd" not in st.session_state:
    st.session_state.last_cmd = None

# ============================
# Rafraîchissement automatique des données toutes les 2 secondes
# ============================
st_autorefresh(interval=2000, key="refresh")  # Actualisation toutes les 2 secondes

# ============================
# LECTURE DES DONNÉES (SANS CACHE)
# ============================
def get_data():
    try:
        r = requests.get(NODE_RED_DATA_URL, timeout=2)
        return r.json()
    except Exception as e:
        st.error(f"❌ Impossible de récupérer les données depuis Node-RED: {e}")
        return {}

# Fonction pour vérifier si les données ont changé
def check_for_update():
    new_data = get_data()
    if new_data != st.session_state.get("last_data", {}):
        st.session_state["last_data"] = new_data
        return new_data
    return None

# Récupérer les données de Node-RED
data = check_for_update()

# ============================
# AFFICHAGE DONNÉES
# ============================
if data:
    mode = data.get("mode", "—")
    temp = data.get("temperature")
    hum  = data.get("humidite")
    co2  = data.get("co2")

    # Si le mode est ARRET, réinitialiser les données à "None"
    if mode == "ARRET":
        temp, hum, co2 = None, None, None

    # Création d'un conteneur vide pour éviter les redessins multiples
    with st.empty():
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

        # Affichage du mode actuel
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

# Sliders avec persistance
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
    key="ext_speed"
)

# Payload de commande
payload = {
    "system": st.session_state.system_state,
    "adm_speed": adm_speed,
    "ext_speed": ext_speed
}

# ============================
# ENVOI UNIQUEMENT SUR CLIC
# ============================
if st.button("📤 Envoyer la commande"):
    # Vérifier si les commandes sont modifiées avant d'envoyer
    if payload != st.session_state.last_cmd:
        try:
            res = requests.post(NODE_RED_CMD_URL, json=payload, timeout=2)
            if res.status_code == 200:
                st.success("✅ Commande envoyée avec succès")
                st.session_state.last_cmd = payload
            else:
                st.error("❌ Erreur côté Node-RED")
        except:
            st.error("❌ Node-RED injoignable")
    else:
        st.info("ℹ️ Les commandes n'ont pas changé. Aucune commande envoyée.")

# ============================
# INFO ÉTAT LOCAL
# ============================
st.caption(
    f"État demandé : {'ON' if st.session_state.system_state else 'OFF'} | "
    f"Adm: {adm_speed}% | Ext: {ext_speed}%"
)
