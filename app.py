import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import matplotlib.pyplot as plt

# Set Streamlit page config first thing
st.set_page_config(page_title="EV Forecast", layout="wide")

# === Load model ===
model = joblib.load('forecasting_ev_model.pkl')

# === Styling ===
st.markdown("""
    <style>
        /* Gradient background for the whole app */
        .stApp {
            background: linear-gradient(to right, #e0f0ff, #a0c4ff);
            color: #1a1a1a;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        /* Override headers and special elements for better visibility */
        .st-header, .st-subheader, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #003366 !important;
        }
        /* Style the titles with white on a deeper blue background */
        .title-container {
            background: #003366;
            padding: 20px;
            border-radius: 8px;
            color: white;
            font-weight: 700;
            font-size: 36px;
            text-align: center;
            margin-top: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        /* Subtitle style */
        .subtitle-container {
            font-weight: 600;
            font-size: 22px;
            color: #00509E;
            text-align: center;
            margin-bottom: 30px;
        }
        /* Instruction text */
        .instructions {
            font-size: 20px;
            font-weight: 500;
            color: #003366;
            margin-bottom: 15px;
        }
        /* Customize selectbox labels */
        .css-1aumxhk {
            font-weight: 600;
            font-size: 20px;
            color: #003366;
        }
        /* Image styling */
        .stImage > img {
            border-radius: 10px;
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }
        /* Success message styling */
        div.stSuccess > div {
            background-color: #d0e8ff !important;
            color: #003366 !important;
            border-radius: 8px;
            padding: 10px 15px;
            font-weight: 600;
            font-size: 18px;
        }
    </style>
""", unsafe_allow_html=True)

# Stylized title using markdown + HTML with class
st.markdown("""
    <div class='title-container'>
        🔮 EV Adoption Forecaster for a County in Washington State
    </div>
""", unsafe_allow_html=True)

# Welcome subtitle
st.markdown("""
    <div class='subtitle-container'>
        Welcome to the Electric Vehicle (EV) Adoption Forecast tool.
    </div>
""", unsafe_allow_html=True)

# Image
st.image("ev-car-factory.jpg", use_container_width=True)

# Instruction line
st.markdown("""
    <div class='instructions'>
        Select a county and see the forecasted EV adoption trend for the next 3 years.
    </div>
""", unsafe_allow_html=True)

# --- Rest of your app code follows unchanged ---

# When creating matplotlib plots, use this style for the dark background with good contrast
# Example for cumulative graph plotting style modifications:

st.subheader(f"📊 Cumulative EV Forecast for {county} County")
fig, ax = plt.subplots(figsize=(12, 6))
for label, data in combined.groupby('Source'):
    ax.plot(data['Date'], data['Cumulative EV'], label=label, marker='o', linewidth=2)

ax.set_title(f"Cumulative EV Trend - {county} (3 Years Forecast)", fontsize=16, color='#003366', fontweight='bold')
ax.set_xlabel("Date", color='#003366', fontsize=14)
ax.set_ylabel("Cumulative EV Count", color='#003366', fontsize=14)
ax.grid(True, alpha=0.15)
ax.set_facecolor("#f0f8ff")
fig.patch.set_facecolor('#e6f0ff')
ax.tick_params(colors='#003366', labelsize=12)
ax.legend(frameon=False, fontsize=12)
st.pyplot(fig)

# Similarly update other plotting code blocks with above style for consistency
# ...

# Modern success message styling
st.success("Forecast complete")

st.markdown("Prepared for the **AICTE Internship Cycle 2**")
