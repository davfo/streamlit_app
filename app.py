import streamlit as st
import paho.mqtt.client as mqtt

# -----------------------------
# CONFIG MQTT
# -----------------------------
BROKER = "test.mosquitto.org" 
PORT = 1883

TOPIC_ADM_CMD = "dashboard/adm/cmd"         # ON/OFF ventilateur admission
TOPIC_ADM_SPEED = "dashboard/adm/speed"     # vitesse ventilateur admission

TOPIC_EXT_CMD = "dashboard/ext/cmd"         # ON/OFF ventilateur extraction
TOPIC_EXT_SPEED = "dashboard/ext/speed"     # vitesse ventilateur extraction

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
st.write("Contrôle séparé des ventilateurs **d’admission** et **d’extraction** via MQTT.")

# =============================
# VENTILATEUR D’ADMISSION
# =============================
st.header("Ventilateur d’admission")

col1, col2 = st.columns(2)

with col1:
    if st.button("Admission ON"):
        client.publish(TOPIC_ADM_CMD, "1")

with col2:
    if st.button("Admission OFF"):
        client.publish(TOPIC_ADM_CMD, "0")

speed_adm = st.slider(
    "Vitesse admission (%)",
    min_value=0,
    max_value=100,
    value=50,
    key="adm_speed"
)

client.publish(TOPIC_ADM_SPEED, speed_adm)
st.success(f"Vitesse admission envoyée : {speed_adm}%")

# =============================
# VENTILATEUR D’EXTRACTION
# =============================
st.header("Ventilateur d’extraction")

col3, col4 = st.columns(2)

with col3:
    if st.button("Extraction ON"):
        client.publish(TOPIC_EXT_CMD, "1")

with col4:
    if st.button("Extraction OFF"):
        client.publish(TOPIC_EXT_CMD, "0")

speed_ext = st.slider(
    "Vitesse extraction (%)",
    min_value=0,
    max_value=100,
    value=50,
    key="ext_speed"
)

client.publish(TOPIC_EXT_SPEED, speed_ext)
st.success(f"Vitesse extraction envoyée : {speed_ext}%")

st.info("Les commandes sont envoyées en temps réel vers Node-RED via MQTT.")
