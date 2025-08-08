import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="EV Forecast", layout="wide")

# Load model
model = joblib.load('forecasting_ev_model.pkl')

# Styling with black font for text (excluding headings) on blue-green gradient background
st.markdown("""
    <style>
        /* Full app gradient background */
        .stApp {
            background: linear-gradient(135deg, #0F4C81, #70C1B3);
            color: #000000; /* Black text for body */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 10px 20px;
        }
        /* Page title container style */
        .title-container {
            background-color: #052F5F;
            padding: 25px 15px;
            border-radius: 12px;
            color: white;  /* White title text */
            font-weight: 800;
            font-size: 38px;
            text-align: center;
            margin-top: 15px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.25);
            font-family: 'Georgia', serif;
        }
        /* Subtitle style */
        .subtitle-container {
            color: #000000;
            font-weight: 600;
            font-size: 24px;
            text-align: center;
            margin-bottom: 35px;
            font-style: italic;
        }
        /* Instruction text */
        .instructions {
            font-size: 20px;
            font-weight: 550;
            color: #000000; /* Black font */
            margin-bottom: 20px;
            padding-left: 10px;
        }
        /* Selectbox label style */
        .css-1aumxhk {
            font-weight: 600;
            font-size: 20px;
            color: #168AAD;
        }
        /* Image styling */
        .stImage > img {
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        /* Success message box */
        div.stSuccess > div {
            background-color: #119DA4 !important;
            color: white !important;
            border-radius: 10px;
            padding: 15px 20px;
            font-weight: 600;
            font-size: 20px;
            margin-top: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        /* Header styles override */
        .st-header, .st-subheader, .stMarkdown h1, .stMarkdown h2 {
            color: #052F5F !important;
        }
    </style>
""", unsafe_allow_html=True)

# Page titles and subtitle
st.markdown("<div class='title-container'>🔮 EV Adoption Forecaster for a County in Washington State</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-container'>Welcome to the Electric Vehicle (EV) Adoption Forecast tool.</div>", unsafe_allow_html=True)

# Image
st.image("ev-car-factory.jpg", use_container_width=True)

# Instruction text
st.markdown("<div class='instructions'>Select a county and see the forecasted EV adoption trend for the next 3 years.</div>", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("preprocessed_ev_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# County selection dropdown
county_list = sorted(df['County'].dropna().unique().tolist())
county = st.selectbox("Select a County", county_list)

if not county or county not in df['County'].unique():
    st.warning("Please select a valid county to proceed.")
    st.stop()

county_df = df[df['County'] == county].sort_values("Date")
county_code = county_df['county_encoded'].iloc[0]

# Forecasting
historical_ev = list(county_df['Electric Vehicle (EV) Total'].values[-6:])
cumulative_ev = list(np.cumsum(historical_ev))
months_since_start = county_df['months_since_start'].max()
latest_date = county_df['Date'].max()

future_rows = []
forecast_horizon = 36

for i in range(1, forecast_horizon + 1):
    forecast_date = latest_date + pd.DateOffset(months=i)
    months_since_start += 1
    lag1, lag2, lag3 = historical_ev[-1], historical_ev[-2], historical_ev[-3]
    roll_mean = np.mean([lag1, lag2, lag3])
    pct_change_1 = (lag1 - lag2) / lag2 if lag2 != 0 else 0
    pct_change_3 = (lag1 - lag3) / lag3 if lag3 != 0 else 0
    recent_cumulative = cumulative_ev[-6:]
    ev_growth_slope = np.polyfit(range(len(recent_cumulative)), recent_cumulative, 1)[0] if len(recent_cumulative) == 6 else 0

    new_row = {
        'months_since_start': months_since_start,
        'county_encoded': county_code,
        'ev_total_lag1': lag1,
        'ev_total_lag2': lag2,
        'ev_total_lag3': lag3,
        'ev_total_roll_mean_3': roll_mean,
        'ev_total_pct_change_1': pct_change_1,
        'ev_total_pct_change_3': pct_change_3,
        'ev_growth_slope': ev_growth_slope
    }

    pred = model.predict(pd.DataFrame([new_row]))[0]
    future_rows.append({"Date": forecast_date, "Predicted EV Total": round(pred)})

    historical_ev.append(pred)
    if len(historical_ev) > 6:
        historical_ev.pop(0)

    cumulative_ev.append(cumulative_ev[-1] + pred)
    if len(cumulative_ev) > 6:
        cumulative_ev.pop(0)

# Combine Historical + Forecast for Cumulative Plot
historical_cum = county_df[['Date', 'Electric Vehicle (EV) Total']].copy()
historical_cum['Source'] = 'Historical'
historical_cum['Cumulative EV'] = historical_cum['Electric Vehicle (EV) Total'].cumsum()

forecast_df = pd.DataFrame(future_rows)
forecast_df['Source'] = 'Forecast'
forecast_df['Cumulative EV'] = forecast_df['Predicted EV Total'].cumsum() + historical_cum['Cumulative EV'].iloc[-1]

combined = pd.concat([
    historical_cum[['Date', 'Cumulative EV', 'Source']],
    forecast_df[['Date', 'Cumulative EV', 'Source']]
], ignore_index=True)

# Plot Cumulative Graph
st.subheader(f"📊 Cumulative EV Forecast for {county} County")
fig, ax = plt.subplots(figsize=(12, 6))
for label, data in combined.groupby('Source'):
    ax.plot(data['Date'], data['Cumulative EV'], label=label, marker='o', linewidth=2)

ax.set_facecolor("#D6F0F0")
fig.patch.set_facecolor("#D6F0F0")
ax.set_title(f"Cumulative EV Trend - {county} (3 Years Forecast)", color="#052F5F", fontsize=18, fontweight='bold')
ax.set_xlabel("Date", color="#168AAD", fontsize=15)
ax.set_ylabel("Cumulative EV Count", color="#168AAD", fontsize=15)
ax.tick_params(colors="#052F5F", labelsize=13)
ax.grid(True, alpha=0.25, color="#A7C7C9")
ax.legend(frameon=False, fontsize=13, title="Source", title_fontsize=14, loc='upper left')
st.pyplot(fig)

# Compare historical and forecasted cumulative EVs
historical_total = historical_cum['Cumulative EV'].iloc[-1]
forecasted_total = forecast_df['Cumulative EV'].iloc[-1]

if historical_total > 0:
    forecast_growth_pct = ((forecasted_total - historical_total) / historical_total) * 100
    trend = "increase 📈" if forecast_growth_pct > 0 else "decrease 📉"
    st.success(f"Based on the graph, EV adoption in **{county}** is expected to show a **{trend} of {forecast_growth_pct:.2f}%** over the next 3 years.")
else:
    st.warning("Historical EV total is zero, so percentage forecast change can't be computed.")

# Compare up to 3 counties
st.markdown("---")
st.header("Compare EV Adoption Trends for up to 3 Counties")

multi_counties = st.multiselect("Select up to 3 counties to compare", county_list, max_selections=3)

if multi_counties:
    comparison_data = []

    for cty in multi_counties:
        cty_df = df[df['County'] == cty].sort_values("Date")
        cty_code = cty_df['county_encoded'].iloc[0]

        hist_ev = list(cty_df['Electric Vehicle (EV) Total'].values[-6:])
        cum_ev = list(np.cumsum(hist_ev))
        months_since = cty_df['months_since_start'].max()
        last_date = cty_df['Date'].max()

        future_rows_cty = []
        for i in range(1, forecast_horizon + 1):
            forecast_date = last_date + pd.DateOffset(months=i)
            months_since += 1
            lag1, lag2, lag3 = hist_ev[-1], hist_ev[-2], hist_ev[-3]
            roll_mean = np.mean([lag1, lag2, lag3])
            pct_change_1 = (lag1 - lag2) / lag2 if lag2 != 0 else 0
            pct_change_3 = (lag1 - lag3) / lag3 if lag3 != 0 else 0
            recent_cum = cum_ev[-6:]
            ev_slope = np.polyfit(range(len(recent_cum)), recent_cum, 1)[0] if len(recent_cum) == 6 else 0

            new_row = {
                'months_since_start': months_since,
                'county_encoded': cty_code,
                'ev_total_lag1': lag1,
                'ev_total_lag2': lag2,
                'ev_total_lag3': lag3,
                'ev_total_roll_mean_3': roll_mean,
                'ev_total_pct_change_1': pct_change_1,
                'ev_total_pct_change_3': pct_change_3,
                'ev_growth_slope': ev_slope
            }

            pred = model.predict(pd.DataFrame([new_row]))[0]
            future_rows_cty.append({"Date": forecast_date, "Predicted EV Total": round(pred)})
            hist_ev.append(pred)
            if len(hist_ev) > 6:
                hist_ev.pop(0)
                
