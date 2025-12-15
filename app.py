import streamlit as st
import paho.mqtt.client as mqtt

# -----------------------------
# CONFIG MQTT
# -----------------------------
BROKER = "172.161.134.198"  # ex: 192.168.1.50
PORT = 1883

TOPIC_SYSTEM = "dashboard/system/cmd"
TOPIC_ADM = "dashboard/adm/speed"
TOPIC_EXT = "dashboard/ext/speed"

# -----------------------------
# MQTT CLIENT (singleton)
# -----------------------------
@st.cache_resource
def get_mqtt_client():
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    return client

client = get_mqtt_client()

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "adm_speed_prev" not in st.session_state:
    st.session_state.adm_speed_prev = 50

if "ext_speed_prev" not in st.session_state:
    st.session_state.ext_speed_prev = 50

# -----------------------------
# UI STREAMLIT
# -----------------------------
st.title("Commande MQTT – Système d’aération")

# =============================
# SYSTEME
# =============================
st.header("Système")

col1, col2 = st.columns(2)

with col1:
    if st.button("🟢 Mise en service"):
        client.publish(TOPIC_SYSTEM, "1")
        st.success("Système ON")

with col2:
    if st.button("🔴 Arrêt du système"):
        client.publish(TOPIC_SYSTEM, "0")
        st.error("Système OFF")

# =============================
# VENTILATEUR ADMISSION
# =============================
st.header("Ventilateur d’admission")

adm_speed = st.slider(
    "Vitesse admission (%)",
    0, 100, 50,
    key="adm_speed"
)

if adm_speed != st.session_state.adm_speed_prev:
    client.publish(TOPIC_ADM, adm_speed)
    st.session_state.adm_speed_prev = adm_speed
    st.info(f"Admission → {adm_speed}%")

# =============================
# VENTILATEUR EXTRACTION
# =============================
st.header("Ventilateur d’extraction")

ext_speed = st.slider(
    "Vitesse extraction (%)",
    0, 100, 50,
    key="ext_speed"
)

if ext_speed != st.session_state.ext_speed_prev:
    client.publish(TOPIC_EXT, ext_speed)
    st.session_state.ext_speed_prev = ext_speed
    st.info(f"Extraction → {ext_speed}%")
