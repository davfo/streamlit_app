import streamlit as st
import requests

# -----------------------------
# CONFIG NODE-RED
# -----------------------------
NODE_RED_CMD_URL = "https://nodered.david.work.gd/api/control"  # POST
NODE_RED_DATA_URL = "https://nodered.david.work.gd/api/data"   # GET

st.set_page_config(
    page_title="Commande Aération",
    layout="centered"
)

st.title("🌀 Commande du système d’aération")

# ============================================================
# MÉMOIRE : ÉTATS PERSISTANTS
# ============================================================
if "system_state" not in st.session_state:
    st.session_state.system_state = 0  # 0 = arrêt

if "adm_speed" not in st.session_state:
    st.session_state.adm_speed = 50

if "ext_speed" not in st.session_state:
    st.session_state.ext_speed = 50

# ============================================================
# VISUALISATION DES DONNÉES (LECTURE SEULE)
# ============================================================
st.header("📊 Données environnementales")

try:
    r = requests.get(NODE_RED_DATA_URL, timeout=2)

    if r.status_code == 204:
        st.warning("Aucune donnée disponible pour le moment")
    else:
        data = r.json()

        colT, colH, colC = st.columns(3)

        colT.metric("🌡 Température", f"{data.get('temperature', '—')} °C")
        colH.metric("💧 Humidité", f"{data.get('humidity', '—')} %")

        co2 = data.get("co2", -1)
        if co2 is None or co2 < 0:
            colC.metric("🧪 CO₂", "Non disponible")
        else:
            colC.metric("🧪 CO₂", f"{co2} ppm")

except Exception:
    st.error("❌ Impossible de récupérer les données capteurs")

st.divider()

# ============================================================
# COMMANDE SYSTÈME (ON / OFF)
# ============================================================
st.header("⚙️ Système")

col1, col2 = st.columns(2)

with col1:
    if st.button("🟢 Mise en service"):
        st.session_state.system_state = 1

with col2:
    if st.button("🔴 Arrêt du système"):
        st.session_state.system_state = 0

st.info(f"État système : {'ON' if st.session_state.system_state == 1 else 'OFF'}")

st.divider()

# ============================================================
# COMMANDE VENTILATEURS (MANUEL)
# ============================================================
st.header("🌀 Ventilateurs")

st.session_state.adm_speed = st.slider(
    "Vitesse admission (%)",
    0, 255,
    st.session_state.adm_speed
)

st.session_state.ext_speed = st.slider(
    "Vitesse extraction (%)",
    0, 255,
    st.session_state.ext_speed
)

st.divider()

# ============================================================
# ENVOI EXPLICITE DE LA COMMANDE
# ============================================================
st.header("📡 Envoi de la commande")

if st.button("📤 Envoyer la commande"):
    data_cmd = {
        "system": st.session_state.system_state,
        "adm_speed": st.session_state.adm_speed,
        "ext_speed": st.session_state.ext_speed
    }

    try:
        response = requests.post(
            NODE_RED_CMD_URL,
            json=data_cmd,
            timeout=2
        )

        if response.status_code == 200:
            st.success("✅ Commande envoyée à Node-RED")
            st.code(data_cmd, language="json")
        else:
            st.error(f"❌ Erreur HTTP : {response.status_code}")

    except Exception:
        st.error("❌ Impossible de joindre Node-RED")

# ============================================================
# INFO DEBUG (OPTIONNEL)
# ============================================================
with st.expander("🛠 État interne (debug)"):
    st.json({
        "system": st.session_state.system_state,
        "adm_speed": st.session_state.adm_speed,
        "ext_speed": st.session_state.ext_speed
    })
