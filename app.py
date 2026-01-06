import streamlit as st
import requests
import json

# -----------------------------
# CONFIG NODE-RED
# -----------------------------
NODE_RED_CMD_URL = "https://nodered.david.work.gd/api/control"  # POST
NODE_RED_DATA_URL = "https://nodered.david.work.gd/api/data"   # GET

st.set_page_config(page_title="Commande Aération", layout="centered")
st.title("🌀 Commande du système d’aération")

# ============================================================
# ÉTATS PERSISTANTS (UNE SEULE FOIS)
# ============================================================
if "system_state" not in st.session_state:
    st.session_state.system_state = 0

if "adm_speed" not in st.session_state:
    st.session_state.adm_speed = 50

if "ext_speed" not in st.session_state:
    st.session_state.ext_speed = 50

if "last_sent" not in st.session_state:
    st.session_state.last_sent = None

# ============================================================
# LECTURE DES DONNÉES (SANS IMPACT SUR COMMANDE)
# ============================================================
st.header("📊 Données environnementales")

try:
    r = requests.get(NODE_RED_DATA_URL, timeout=2)
    if r.status_code == 200:
        data = r.json()

        colT, colH, colC = st.columns(3)
        colT.metric("🌡 Températures", f"{data.get('temperature', '—')} °C")
        colH.metric("💧 Humidité", f"{data.get('humidity', '—')} %")

        co2 = data.get("co2", -1)
        colC.metric(
            "🧪 CO₂",
            "Non disponible" if co2 is None or co2 < 0 else f"{co2} ppm"
        )
    else:
        st.warning("Aucune donnée disponible")

except Exception:
    st.error("❌ Impossible de récupérer les données")

st.divider()

# ============================================================
# COMMANDE SYSTÈME
# ============================================================
st.header("⚙️ Système")

col1, col2 = st.columns(2)

with col1:
    if st.button("🟢 Mise en service"):
        st.session_state.system_state = 1

with col2:
    if st.button("🔴 Arrêt du système"):
        st.session_state.system_state = 0

st.info(
    f"État système : {'ON' if st.session_state.system_state == 1 else 'OFF'}"
)

st.divider()

# ============================================================
# COMMANDE VENTILATEURS
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
# ENVOI EXPLICITE (SEUL POINT DE POST)
# ============================================================
st.header("📡 Envoi de la commande")

if st.button("📤 Envoyer la commande"):
    payload = {
        "system": st.session_state.system_state,
        "adm_speed": st.session_state.adm_speed,
        "ext_speed": st.session_state.ext_speed
    }

    # Anti double envoi
    if payload != st.session_state.last_sent:
        try:
            response = requests.post(
                NODE_RED_CMD_URL,
                json=payload,
                timeout=2
            )

            if response.status_code == 200:
                st.success("✅ Commande envoyée")
                st.code(json.dumps(payload, indent=2), language="json")
                st.session_state.last_sent = payload
            else:
                st.error(f"❌ Erreur HTTP : {response.status_code}")

        except Exception:
            st.error("❌ Node-RED injoignable")
    else:
        st.info("ℹ️ Commande identique déjà envoyée")

# ============================================================
# DEBUG (OPTIONNEL)
# ============================================================
with st.expander("🛠 Debug interne"):
    st.json({
        "system": st.session_state.system_state,
        "adm_speed": st.session_state.adm_speed,
        "ext_speed": st.session_state.ext_speed,
        "last_sent": st.session_state.last_sent
    })
