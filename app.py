import streamlit as st
import paho.mqtt.client as mqtt

BROKER = "172.161.134.198"   # ex: 192.168.1.50
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
# VENTILATEURS
# =============================
st.header("Ventilateurs")

speed_adm = st.slider("Admission (%)", 0, 100, 50)
speed_ext = st.slider("Extraction (%)", 0, 100, 50)

if st.button("📤 Envoyer vitesses"):
    client.publish(TOPIC_ADM, speed_adm)
    client.publish(TOPIC_EXT, speed_ext)
    st.info("Vitesses envoyées via MQTT")


