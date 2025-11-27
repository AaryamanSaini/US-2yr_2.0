# US-2yr_2.0

Live--
https://bond-futures.vercel.app/
This project provides an interactive dashboard for analyzing intra-day movements in US Treasury futures (TUZ5 – 2Y, FVZ5 – 5Y, TYZ5 – 10Y).
The dashboard visualizes relative yield changes, daily patterns, and mean ± standard-deviation envelopes across selected trading days.

📊 Overview

The dashboard transforms raw CME futures price data (e.g. 109-05+, 109-05_) into decimal prices, computes relative yield moves, and plots:

Individual day yield curves

Mean ± 1 standard deviation for selected days

Long-term mean curve (all days)

A daily statistics table (min, max, mean, std)

The UI is built in Streamlit and charts use Plotly for a clean, real-time analytics look (dark-themed).

🖼️ Screenshot

(Example dashboard view)

📁 Data Format

Each CSV should contain daily trade-level data:

Date       Time     Lst Trd/Lst Prxx
30/09/2025 18:00    109-05
30/09/2025 18:05    109-05+
30/09/2025 18:10    109-05+
30/09/2025 18:15    109-05_
...


The dashboard automatically detects the price column containing “Lst”.

🔢 Price Parsing Logic

CME futures prices use a fractional format:

109-05 → whole = 109, 5/32

109-05¼ → + 1/128

109-05½ → + 1/64

109-05¾ → + 3/128

+ and _ are normalized to fractional ticks

All of this is handled by the helper:

parse_price(p)

📈 How Relative Yield Is Computed

For each day:

Relative Yield = Price_t − Price_18:00


So all curves start at 0 → intuitive comparison across days.

🧠 Features
✔ Multi-day selection

Choose any combination of trading days to analyze.

✔ Plotly time-series visualization

Smooth, interactive zoom/pan tool with a full dark theme.

✔ Mean & Standard Deviation Bands

Compute and display ±1 SD envelopes for selected days.

✔ Long-term Average Benchmark

Overlay the mean curve across all trading days.

✔ Daily Summary Table

Auto-computed statistics:

Min

Max

Mean

Std

🏗 Tech Stack
Component	Technology
UI	Streamlit
Charts	Plotly
Data processing	Pandas / NumPy
Deployment	Vercel
🚀 Running Locally
1. Clone the repo
git clone https://github.com/<your-username>/US-2yr_2.0.git
cd US-2yr_2.0

2. Install dependencies
pip install -r requirements.txt

3. Run the Streamlit app
streamlit run app.py

📦 Project Structure
.
├── app.py
├── tuz5.csv
├── fvz5.csv
├── tyz5.csv
├── requirements.txt
└── README.md

✨ Future Enhancements

Add 30Y (USZ5) futures

Volume analysis + heatmaps

Session segmentation (Asia / Europe / US)

Rolling averages & volatility metrics
