import streamlit as st
import paho.mqtt.client as mqtt

# -----------------------------
# CONFIG MQTT
# -----------------------------
BROKER = "test.mosquitto.org"
PORT = 1883

TOPIC_SYSTEM = "dashboard/system/cmd"       # Commande globale ON/OFF du système
TOPIC_ADM_SPEED = "dashboard/adm/speed"     # Vitesse ventilateur admission
TOPIC_EXT_SPEED = "dashboard/ext/speed"     # Vitesse ventilateur extraction

# -----------------------------
# MQTT : Initialisation
# -----------------------------
client = mqtt.Client()
client.connect(BROKER, PORT, 60)
client.loop_start()

# -----------------------------
# INTERFACE STREAMLIT
# -----------------------------
st.title("Commande du système d’aération")

st.header("Mise en service ")

col1, col2 = st.columns(2)

with col1:
    if st.button("🟢 Mise en service"):
        client.publish(TOPIC_SYSTEM, "1")
        st.success("Système mis en service")

with col2:
    if st.button("🔴 Arrêt du système"):
        client.publish(TOPIC_SYSTEM, "0")
        st.error("Système arrêté")


# =============================
# VENTILATEUR D’ADMISSION
# =============================
st.header(" Ventilateur d’admission")

speed_adm = st.slider(
    "Vitesse admission (%)",
    min_value=0,
    max_value=100,
    value=50,
    key="adm_speed"
)

client.publish(TOPIC_ADM_SPEED, speed_adm)
st.info(f"Vitesse admission envoyée : {speed_adm}%")


# =============================
# VENTILATEUR D’EXTRACTION
# =============================
st.header("🌬️ Ventilateur d’extraction")

speed_ext = st.slider(
    "Vitesse extraction (%)",
    min_value=0,
    max_value=100,
    value=50,
    key="ext_speed"
)

client.publish(TOPIC_EXT_SPEED, speed_ext)
st.info(f"Vitesse extraction envoyée : {speed_ext}%")


