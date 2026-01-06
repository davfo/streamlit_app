import streamlit as st
import requests
import json

# =============================
# CONFIG NODE-RED
# =============================
NODE_RED_CMD_URL = "https://nodered.david.work.gd/api/control"
NODE_RED_DATA_URL = "https://nodered.david.work.gd/api/data"

st.set_page_config(page_title="Commande Aération", layout="centered")
st.title("🌀 Commande du système d’aération")

# =============================
# INIT SESSION (UNE SEULE FOIS)
# =============================
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.system_state = 0
    st.session_state.adm_speed = 50
    st.session_state.ext_speed = 50
    st.session_state.last_sent = None

# =============================
# LECTURE DONNÉES (SANS POST)
# =============================
st.header("📊 Données environnementales")

try:
    r = requests.get(NODE_RED_DATA_URL, timeout=2)
    if r.status_code == 200:
        data = r.json()
        colT, colH, colC = st.columns(3)

        colT.metric("🌡 Température", f"{data.get('temperature','—')} °C")
        colH.metric("💧 Humidité", f"{data.get('humidity','—')} %")

        co2 = data.get("co2", -1)
        colC.metric(
            "🧪 CO₂",
            "Non disponible" if co2 is None or co2 < 0 else f"{co2} ppm"
        )
    else:
        st.warning("Aucune donnée")
except Exception:
    st.error("❌ Données indisponibles")

st.divider()

# =============================
# FORMULAIRE DE COMMANDE (BLOQUANT)
# =============================
st.header("⚙️ Commande système")

with st.form("commande_form", clear_on_submit=False):

    col1, col2 = st.columns(2)
    with col1:
        system_on = st.form_submit_button("🟢 Mise en service")
    with col2:
        system_off = st.form_submit_button("🔴 Mise hors service")

    if system_on:
        st.session_state.system_state = 1
    if system_off:
        st.session_state.system_state = 0

    st.markdown(
        f"**État système : {'ON' if st.session_state.system_state == 1 else 'OFF'}**"
    )

    adm_speed = st.slider(
        "Vitesse admission (%)",
        0, 255,
        st.session_state.adm_speed
    )

    ext_speed = st.slider(
        "Vitesse extraction (%)",
        0, 255,
        st.session_state.ext_speed
    )

    envoyer = st.form_submit_button("📤 Envoyer la commande")

    if envoyer:
        payload = {
            "system": st.session_state.system_state,
            "adm_speed": adm_speed,
            "ext_speed": ext_speed
        }

        if payload != st.session_state.last_sent:
            try:
                r = requests.post(
                    NODE_RED_CMD_URL,
                    json=payload,
                    timeout=2
                )
                if r.status_code == 200:
                    st.success("✅ Commande envoyée")
                    st.session_state.last_sent = payload
                    st.session_state.adm_speed = adm_speed
                    st.session_state.ext_speed = ext_speed
                else:
                    st.error(f"❌ Erreur HTTP {r.status_code}")
            except Exception:
                st.error("❌ Node-RED injoignable")
        else:
            st.info("ℹ️ Commande déjà envoyée")

# =============================
# DEBUG
# =============================
with st.expander("🛠 Debug"):
    st.json({
        "system": st.session_state.system_state,
        "adm_speed": st.session_state.adm_speed,
        "ext_speed": st.session_state.ext_speed,
        "last_sent": st.session_state.last_sent
    })
