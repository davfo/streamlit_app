import streamlit as st
import paho.mqtt.client as mqtt

# -----------------------------
# CONFIG MQTT
# -----------------------------
BROKER = "test.mosquitto.org"    # Adresse de ton broker Node-RED/Mosquitto
PORT = 1883
TOPIC_CMD = "dashboard/cmd"  # Topic de commande

# -----------------------------
# MQTT : Initialisation
# -----------------------------
client = mqtt.Client()
client.connect(BROKER, PORT, 60)
client.loop_start()

# -----------------------------
# INTERFACE STREAMLIT
# -----------------------------
st.title("Dashboard Commande Ventilation")

st.subheader("Contrôle des ventilateurs")

# Commande Extraction
if st.button("Extraction ON"):
    client.publish(TOPIC_CMD, "extraction=1")

if st.button("Extraction OFF"):
    client.publish(TOPIC_CMD, "extraction=0")

# Commande Admission
if st.button("Admission ON"):
    client.publish(TOPIC_CMD, "admission=1")

if st.button("Admission OFF"):
    client.publish(TOPIC_CMD, "admission=0")

st.info("Les commandes sont envoyées vers Node-RED via MQTT.")
