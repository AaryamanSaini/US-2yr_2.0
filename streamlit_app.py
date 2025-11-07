import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Bond Futures Dashboard", layout="wide")
st.title("Bond Futures Dashboard")

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
    # Safe read with encoding and BOM fix (important for Streamlit Cloud)
    df = pd.read_csv(path, encoding='utf-8-sig', on_bad_lines='skip')
    df.columns = df.columns.str.strip()
    if df.columns[0].startswith("ï»¿"):
        df.rename(columns={df.columns[0]: df.columns[0].replace("ï»¿", "")}, inplace=True)

    price_col = [c for c in df.columns if "Lst" in c][0]
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Price'] = df[price_col].apply(parse_price)
    df['Day'] = df['Date'].dt.date

    # Handle time safely
    if 'Time' in df.columns and df['Time'].dtype == object:
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce').dt.time
    else:
        df['Time'] = df['Date'].dt.time

    df = df.dropna(subset=['Time'])
    df['Rel_Yield'] = df.groupby('Day')['Price'].transform(lambda x: x - x.iloc[0])
    df = df.drop_duplicates(subset=['Day', 'Time'], keep='last')
    return df

# --- Load datasets ---
data_files = {
    "2 Year (TUZ5)": "Copy of TUZ5 - 5M5D.csv",
    "5 Year (FVZ5)": "5year.csv",
    "10 Year (TYZ5)": "10year.csv"
}

# --- Sidebar selector ---
st.sidebar.header("Select Bond Contract")
selected_label = st.sidebar.radio("Choose maturity:", list(data_files.keys()))
selected_path = data_files[selected_label]

df = load_data(selected_path)

# --- Calendar-style day selection ---
all_days = sorted(df['Day'].unique())
selected_days = st.sidebar.multiselect(
    "Select trading days:",
    options=all_days,
    default=all_days[-5:]
)

if len(selected_days) == 0:
    st.warning("Please select at least one trading day to display.")
    st.stop()

# --- Compute pivot and time index ---
df_sel = df[df['Day'].isin(selected_days)]
pivot = df_sel.pivot(index='Time', columns='Day', values='Rel_Yield')
pivot_total = df.pivot(index='Time', columns='Day', values='Rel_Yield')
times = [pd.Timestamp.combine(datetime.today(), t) for t in pivot.index]

# --- Create figure ---
fig = go.Figure()

# Plot selected individual days
for col in pivot.columns:
    fig.add_trace(go.Scatter(
        x=times, y=pivot[col],
        mode='lines',
        name=str(col),
        line=dict(width=1)
    ))

# --- Mean ± SD for selected days ---
mean_sel = pivot.mean(axis=1)
sd_sel = pivot.std(axis=1)
fig.add_trace(go.Scatter(
    x=times, y=mean_sel + sd_sel,
    mode='lines', name='Selected +1 SD',
    line=dict(width=0),
    fill=None
))
fig.add_trace(go.Scatter(
    x=times, y=mean_sel - sd_sel,
    mode='lines', name='Selected -1 SD',
    fill='tonexty',
    fillcolor='rgba(200,200,200,0.3)',
    line=dict(width=0)
))
fig.add_trace(go.Scatter(
    x=times, y=mean_sel,
    mode='lines', name='Selected Mean',
    line=dict(color='white', width=2, dash='solid')
))

# --- Total Mean ± SD ---
mean_total = pivot_total.mean(axis=1)
sd_total = pivot_total.std(axis=1)
fig.add_trace(go.Scatter(
    x=times, y=mean_total,
    mode='lines', name='Total Mean',
    line=dict(color='orange', width=2, dash='dot')
))

# --- Layout ---
fig.update_layout(
    template="plotly_dark",
    title=f"{selected_label} — Relative Yield Analysis",
    xaxis_title="Time (18:00–17:59)",
    yaxis_title="Relative Yield (Δ Price)",
    height=650,
    legend=dict(orientation="h", y=-0.25),
    margin=dict(l=40, r=40, t=70, b=60)
)

st.plotly_chart(fig, use_container_width=True)

# --- Stats Table ---
st.subheader("Daily Summary")
summary = df_sel.groupby('Day')['Rel_Yield'].agg(['min', 'max', 'mean', 'std']).round(5)
st.dataframe(summary, use_container_width=True)
