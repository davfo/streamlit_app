import streamlit as st
import paho.mqtt.client as mqtt

# -----------------------------
# CONFIG MQTT
# -----------------------------
BROKER = "test.mosquitto.org"    
PORT = 1883

TOPIC_CMD = "dashboard/cmd"            # Commande ON/OFF
TOPIC_SPEED = "dashboard/vent_speed"   # Commande vitesse ventilateur

# -----------------------------
# MQTT : Initialisation
# -----------------------------
client = mqtt.Client()
client.connect(BROKER, PORT, 60)
client.loop_start()

# -----------------------------
# INTERFACE STREAMLIT
# -----------------------------
st.title("Dashboard de Commande du système d'aération")

st.subheader("Contrôle général")

# Commande de mise en service
col1, col2 = st.columns(2)

with col1:
    if st.button("ON"):
        client.publish(TOPIC_CMD, "service=1")

with col2:
    if st.button("OFF"):
        client.publish(TOPIC_CMD, "service=0")

# -----------------------------
# SLIDER DE VITESSE
# -----------------------------
st.subheader("Réglage de la vitesse du ventilateur")

vent_speed = st.slider(
    "Vitesse du ventilateur (%)",
    min_value=0,
    max_value=100,
    value=50
)

# Envoi MQTT à chaque modification
client.publish(TOPIC_SPEED, vent_speed)

st.success(f"Vitesse envoyée : {vent_speed}%")

st.info("Les commandes sont envoyées vers Node-RED via MQTT.")
