import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Bond Futures Dashboard", layout="wide", page_icon="📈")
st.title("📊 Bond Futures Dashboard")

# --- Helper: Convert prices like 104-08¼ to decimal ---
def parse_price(p):
    if isinstance(p, str):
        match = re.match(r'(\d+)-(\d+)([¼½¾]?)', p.strip())
        if match:
            whole, thirtyseconds, frac = match.groups()
            val = int(whole) + int(thirtyseconds)/32
            if frac == '¼': val += 1/128
            elif frac == '½': val += 1/64
            elif frac == '¾': val += 3/128
            return val
    return np.nan

# --- Function to load and process each CSV ---
def load_data(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    price_col = [c for c in df.columns if "Lst" in c][0]
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Price'] = df[price_col].apply(parse_price)
    df['Day'] = df['Date'].dt.date
    if 'Time' in df.columns and df['Time'].dtype == object:
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce').dt.time
    else:
        df['Time'] = df['Date'].dt.time
    df = df.dropna(subset=['Time'])

    df['Rel_Yield'] = df.groupby('Day')['Price'].transform(lambda x: x - x.iloc[0])
    df = df.drop_duplicates(subset=['Day', 'Time'], keep='last')
    return df

# --- Load your datasets ---
data_files = {
    "2 Year (TUZ5)": "Copy of TUZ5 - 5M5D.csv",
    "5 Year (FVZ5)": "5year.csv",
    "10 Year (TYZ5)": "10year.csv"
}

# --- Sidebar selector ---
st.sidebar.header("Select Bond Contract")
selected_label = st.sidebar.radio("Choose maturity:", list(data_files.keys()))
selected_path = data_files[selected_label]

# --- Load and process data ---
df = load_data(selected_path)
pivot = df.pivot(index='Time', columns='Day', values='Rel_Yield')
times = [pd.Timestamp.combine(datetime.today(), t) for t in pivot.index]

# --- Create the plot ---
fig = go.Figure()

for col in pivot.columns:
    fig.add_trace(go.Scatter(
        x=times, y=pivot[col],
        mode='lines',
        name=str(col),
        line=dict(width=1)
    ))

# Add average line
fig.add_trace(go.Scatter(
    x=times, y=pivot.mean(axis=1),
    mode='lines', name='Average',
    line=dict(color='white', width=2, dash='dash')
))

fig.update_layout(
    template="plotly_dark",
    title=f"{selected_label} Futures — Relative Yield by Day",
    xaxis_title="Time (18:00–17:59)",
    yaxis_title="Relative Yield (Δ Price)",
    height=650,
    legend=dict(orientation="h", y=-0.2),
    margin=dict(l=50, r=50, t=80, b=80)
)

st.plotly_chart(fig, use_container_width=True)

# --- Summary Stats ---
st.subheader("📈 Daily Summary")
st.write(df.groupby('Day')['Rel_Yield'].agg(['min', 'max', 'mean']).round(5))
