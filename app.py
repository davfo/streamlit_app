import streamlit as st
import requests
import time

# ============================
# CONFIG NODE-RED
# ============================
NODE_RED_CMD_URL = "https://nodered.david.work.gd/api/control"  # POST
NODE_RED_DATA_URL = "https://nodered.david.work.gd/api/data"   # GET

st.set_page_config(page_title="Commande Aération", layout="centered")
st.title("🌀 Commande du système d’aération")

# ============================
# MÉMOIRE STREAMLIT
# ============================
if "system_state" not in st.session_state:
    st.session_state.system_state = 0  # 0 = arrêt
if "last_cmd" not in st.session_state:
    st.session_state.last_cmd = None
if "last_send_time" not in st.session_state:
    st.session_state.last_send_time = 0

# ============================
# LECTURE DES DONNÉES
# ============================

# ============================
# CACHER LA FONCTION POUR RÉCUPÉRER LES DONNÉES
# ============================
@st.cache
def get_data():
    try:
        r = requests.get(NODE_RED_DATA_URL, timeout=2)
        return r.json()
    except Exception as e:
        st.error("❌ Impossible de récupérer les données depuis Node-RED")
        return {}

# Récupérer les données de Node-RED
data = get_data()

mode = data.get("mode", "—")  # Récupérer le mode du système
temp = data.get("temperature")
hum  = data.get("humidite")
co2  = data.get("co2")

# Si le mode est ARRET, réinitialiser les données à "None"
if mode == "ARRET":
    temp, hum, co2 = None, None, None

# Affichage des données
st.header("📊 Données environnementales")
col1, col2, col3 = st.columns(3)

col1.metric(
    "🌡 Température (°C)",
    f"{temp:.1f}" if isinstance(temp, (int, float)) else "--"
)

col2.metric(
    "💧 Humidité (%)",
    f"{hum:.0f}" if isinstance(hum, (int, float)) else "--"
)

col3.metric(
    "🫁 CO₂ (ppm)",
    f"{co2}" if isinstance(co2, (int, float)) else "--"
)

# Affichage du mode actuel
st.info(f"Mode actuel : **{mode}**")

st.divider()

# ============================
# COMMANDE SYSTEME
# ============================
st.header("🎛 Commande")

# Utilisation de 2 boutons pour activer ou désactiver le système
if st.button("Allumer le système"):
    system_on = True
elif st.button("Éteindre le système"):
    system_on = False
else:
    system_on = bool(st.session_state.system_state)  # Maintenir l'état actuel

# Slider pour les vitesses des ventilateurs
adm_speed = st.slider("Ventilateur admission (%)", 0, 100, 0)
ext_speed = st.slider("Ventilateur extraction (%)", 0, 100, 0)

# Créer la payload pour envoyer à Node-RED
payload = {
    "system": int(system_on),
    "adm_speed": adm_speed,
    "ext_speed": ext_speed
}

now = time.time()

# 🔒 PROTECTION CONTRE LES ENVOIS EN BOUCLE
if payload != st.session_state.last_cmd and now - st.session_state.last_send_time > 2:
    try:
        res = requests.post(NODE_RED_CMD_URL, json=payload, timeout=2)

        if res.status_code == 200:
            st.success("✅ Commande envoyée")
            st.session_state.last_cmd = payload
            st.session_state.last_send_time = now
            st.session_state.system_state = int(system_on)
        else:
            st.error("❌ Erreur côté Node-RED")

    except Exception:
        st.error("❌ Node-RED injoignable")
else:
    st.info("ℹ️ Commande identique ignorée")
