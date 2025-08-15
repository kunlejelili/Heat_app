#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import smtplib
from email.message import EmailMessage
import tempfile
import os
from dotenv import load_dotenv
import datetime

# --- Load local .env ---
load_dotenv()  # for local development

def get_secret(key, default=None):
    """Safely get secret from Streamlit or .env"""
    if "secrets" in dir(st) and hasattr(st, "secrets") and key in st.secrets:
        return st.secrets[key]
    return os.getenv(key, default)

# --- Email credentials ---
EMAIL_ADDRESS = get_secret("EMAIL_ADDRESS")
EMAIL_PASSWORD = get_secret("EMAIL_PASSWORD")
SMTP_SERVER = get_secret("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(get_secret("SMTP_PORT", 587))

# --- Check credentials ---
if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    st.warning("⚠ Email credentials not found. Add them to `.env` or Streamlit secrets.")
else:
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        st.success(f"✅ Email connection test passed for {EMAIL_ADDRESS}")
    except Exception as e:
        st.error(f"❌ Email connection failed: {e}")

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("Thermal Simulation and Tissue Damage Prediction")

if "log" not in st.session_state:
    st.session_state["log"] = []

# Sidebar inputs
st.sidebar.header("Simulation Parameters")
tissue_type = st.sidebar.selectbox("Tissue Type", ["Muscle", "Fat", "Skin"])
total_time = st.sidebar.slider("Total Simulation Time (s)", 10, 300, 60)
time_step = st.sidebar.slider("Time Step (s)", 1, 20, 5)
heat_size = st.sidebar.slider("Heat Source Size (pixels)", 1, 20, 10)
heat_power = st.sidebar.number_input("Heat Source Power (W/m³)", value=10000)
email_recipient = st.sidebar.text_input("Recipient Email (for export)")
auto_email = st.sidebar.checkbox("Auto-send email after simulation", value=True)
include_animation = st.sidebar.checkbox("Attach animation GIF to email", value=False)

# Test email button
if st.sidebar.button("Send Test Email") and email_recipient and EMAIL_ADDRESS and EMAIL_PASSWORD:
    try:
        test_msg = EmailMessage()
        test_msg['Subject'] = 'Test: Thermal Simulation Email Setup'
        test_msg['From'] = EMAIL_ADDRESS
        test_msg['To'] = email_recipient
        test_msg.set_content('✅ Test email sent successfully. Your SMTP config works!')
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(test_msg)
        st.success("Test email sent!")
    except Exception as e:
        st.error(f"Failed to send test email: {e}")

# --- Tissue properties ---
properties = {
    "Muscle": {"rho": 1050, "c": 3600, "k": 0.5, "w": 0.001},
    "Fat":    {"rho": 920,  "c": 2300, "k": 0.2, "w": 0.0005},
    "Skin":   {"rho": 1100, "c": 3400, "k": 0.37, "w": 0.002},
}
p = properties[tissue_type]

cb = 3770
Tb = 37.0
A = 3.1e98
Ea = 6.28e5
R = 8.314

L = 0.05
N = 100
dx = L / N
dt = time_step
steps = int(total_time / dt)

T = np.ones((N, N)) * Tb
damage = np.zeros_like(T)
source = np.zeros_like(T)
center = N // 2
s = heat_size // 2
source[center-s:center+s, center-s:center+s] = heat_power

T_frames = []
damage_frames = []

# --- Simulation loop ---
st.session_state["log"].append(f"Simulation started: {datetime.datetime.now()}")
for step in range(steps):
    laplacian = (
        np.roll(T, 1, axis=0) + np.roll(T, -1, axis=0) +
        np.roll(T, 1, axis=1) + np.roll(T, -1, axis=1) - 4*T
    ) / dx**2
    dT = (p['k'] * laplacian + p['w'] * p['rho'] * cb * (Tb - T) + source) * dt / (p['rho'] * p['c'])
    T += dT
    T_k = T + 273.15
    omega = A * np.exp(-Ea / (R * T_k)) * dt
    damage += omega
    if step % 5 == 0:
        T_frames.append(T.copy())
        damage_frames.append(1 - np.exp(-damage.copy()))
st.session_state["log"].append(f"Simulation ended: {datetime.datetime.now()}")

# --- Final outputs ---
final_T = T_frames[-1]
final_D = damage_frames[-1]

# Static plotting
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.imshow(final_T, cmap='hot', origin='lower')
ax1.set_title('Final Temperature (°C)')
ax2.imshow(final_D, cmap='inferno', origin='lower', vmin=0, vmax=1)
ax2.set_title('Final Damage (0–1)')
st.pyplot(fig)

# CSV export
csv_T = pd.DataFrame(final_T).to_csv(index=False).encode('utf-8')
csv_D = pd.DataFrame(final_D).to_csv(index=False).encode('utf-8')
st.download_button("Download Temperature CSV", csv_T, "temperature_map.csv")
st.download_button("Download Damage CSV", csv_D, "damage_map.csv")

# Animation
fig_anim, (ax1a, ax2a) = plt.subplots(1, 2, figsize=(12, 5))
im1 = ax1a.imshow(T_frames[0], cmap='hot', origin='lower')
im2 = ax2a.imshow(damage_frames[0], cmap='inferno', origin='lower', vmin=0, vmax=1)
ax1a.set_title("Temperature Evolution")
ax2a.set_title("Damage Evolution")
def update(i):
    im1.set_data(T_frames[i])
    im2.set_data(damage_frames[i])
    return im1, im2
ani = animation.FuncAnimation(fig_anim, update, frames=len(T_frames), interval=200, blit=False)
st.pyplot(fig_anim)

# Optional GIF
gif_path = None
if include_animation:
    gif_path = os.path.join(tempfile.gettempdir(), "thermal_sim.gif")
    ani.save(gif_path, writer='pillow')

# --- Email sending function ---
def send_email(recipient):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        st.warning("⚠ Cannot send email — credentials missing.")
        return
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Thermal Simulation Results'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        msg.set_content('Attached are the thermal simulation results.')
        msg.add_attachment(csv_T, maintype='text', subtype='csv', filename='temperature_map.csv')
        msg.add_attachment(csv_D, maintype='text', subtype='csv', filename='damage_map.csv')
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
            fig.savefig(tmp_img.name)
            tmp_img.seek(0)
            msg.add_attachment(tmp_img.read(), maintype='image', subtype='png', filename='final_plots.png')
        if include_animation and gif_path:
            with open(gif_path, 'rb') as gif_file:
                msg.add_attachment(gif_file.read(), maintype='image', subtype='gif', filename='thermal_sim.gif')
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        st.success(f"Email sent to {recipient}!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Manual send
if st.sidebar.button("Send Email") and email_recipient:
    send_email(email_recipient)

# Auto send
if email_recipient and auto_email:
    send_email(email_recipient)


# In[ ]:




