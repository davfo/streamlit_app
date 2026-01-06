import streamlit as st
import requests
import json

NODE_RED_CMD_URL = "https://nodered.david.work.gd/api/control"
NODE_RED_DATA_URL = "https://nodered.david.work.gd/api/data"

st.set_page_config(page_title="Commande Aération", layout="centered")
st.title("🌀 Commande du système d’aération")

# =============================
# INIT SESSION
# =============================
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.system_state = 0
    st.session_state.adm_speed = 50
    st.session_state.ext_speed = 50
    st.session_state.last_sent = None

# =============================
# AFFICHAGE DONNÉES
# =============================
st.header("📊 Données environnementales")

try:
    r = requests.get(NODE_RED_DATA_URL, timeout=2)
    if r.status_code == 200:
        data = r.json()
        c1, c2, c3 = st.columns(3)
        c1.metric("🌡 Température", f"{data.get('temperature','—')} °C")
        c2.metric("💧 Humidité", f"{data.get('humidity','—')} %")
        co2 = data.get("co2", -1)
        c3.metric("🧪 CO₂", "N/A" if co2 < 0 else f"{co2} ppm")
except Exception:
    st.warning("Données indisponibles")

st.divider()

# =============================
# FORMULAIRE UNIQUE
# =============================
st.header("⚙️ Commande")

with st.form("commande_form"):

    # ✅ Sélecteur ON / OFF (PAS de bouton)
    system_choice = st.radio(
        "État du système",
        options=[0, 1],
        format_func=lambda x: "OFF" if x == 0 else "ON",
        index=st.session_state.system_state
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
            "system": system_choice,
            "adm_speed": adm_speed,
            "ext_speed": ext_speed
        }

        if payload != st.session_state.last_sent:
            try:
                r = requests.post(NODE_RED_CMD_URL, json=payload, timeout=2)
                if r.status_code == 200:
                    st.success("✅ Commande envoyée")
                    st.session_state.system_state = system_choice
                    st.session_state.adm_speed = adm_speed
                    st.session_state.ext_speed = ext_speed
                    st.session_state.last_sent = payload
                else:
                    st.error(f"Erreur HTTP {r.status_code}")
            except Exception:
                st.error("Node-RED injoignable")
        else:
            st.info("Commande identique déjà envoyée")

# =============================
# DEBUG
# =============================
with st.expander("🛠 Debug"):
    st.json(st.session_state)
