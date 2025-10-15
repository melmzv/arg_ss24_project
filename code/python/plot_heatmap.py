# build_em_map_from_pickle.py
# Creates an interactive world map with a top-right dropdown (EM1–EM4 + Aggregate)
# Input: output/em_results.pickle produced by your analysis pipeline
# Output: assets/em_map_interactive.html + assets/em_table.csv

import pickle
import pandas as pd
import plotly.express as px
import os
import re

# ----------------------------
# Config
# ----------------------------
PICKLE_PATH = "output/em_results.pickle"          # from your cfg['results']
HTML_OUT    = "assets/em_map_interactive.html"
CSV_OUT     = "assets/em_table.csv"

# Metric columns in your final table
METRIC_COLS = ["EM1", "EM2", "EM3", "EM4", "Aggregate_EM_Score"]

# Pretty names for the dropdown
PRETTY = {
    "EM1": "EM1 (Volatility ratio)",
    "EM2": "EM2 (Accrual–CFO comovement)",
    "EM3": "EM3 (Abs accruals intensity)",
    "EM4": "EM4 (Small profits / small losses)",
    "Aggregate_EM_Score": "Aggregate"
}

# ----------------------------
# Helpers
# ----------------------------
def normalize_name(s: str) -> str:
    """Light normalization for country names to improve ISO-3 mapping."""
    if not isinstance(s, str):
        return s
    x = s.strip().upper()
    x = re.sub(r"\s+", " ", x)
    # common aliases / Natural Earth quirks
    aliases = {
        "UNITED STATES": "UNITED STATES OF AMERICA",
        "USA": "UNITED STATES OF AMERICA",
        "US": "UNITED STATES OF AMERICA",
        "UK": "UNITED KINGDOM",
        "KOREA (SOUTH)": "KOREA, REPUBLIC OF",
        "SOUTH KOREA": "KOREA, REPUBLIC OF",
        "RUSSIA": "RUSSIAN FEDERATION",
        "IRAN": "IRAN, ISLAMIC REPUBLIC OF",
        "VIETNAM": "VIET NAM",
        "BOLIVIA": "BOLIVIA (PLURINATIONAL STATE OF)",
        "TANZANIA": "TANZANIA, UNITED REPUBLIC OF",
        "VENEZUELA": "VENEZUELA (BOLIVARIAN REPUBLIC OF)",
        "SYRIA": "SYRIAN ARAB REPUBLIC",
        "CZECH REPUBLIC": "CZECHIA",
        "LAOS": "LAO PEOPLE'S DEMOCRATIC REPUBLIC",
        "BRUNEI": "BRUNEI DARUSSALAM",
        "MOLDOVA": "MOLDOVA, REPUBLIC OF",
        "MACEDONIA": "NORTH MACEDONIA",
        "SLOVAK REPUBLIC": "SLOVAKIA",
        "BOSNIA": "BOSNIA AND HERZEGOVINA",
        "BURMA": "MYANMAR",
        "SWAZILAND": "ESWATINI",
        "CAPE VERDE": "CABO VERDE",
        "IVORY COAST": "CÔTE D’IVOIRE",
        "COTE D'IVOIRE": "CÔTE D’IVOIRE",
        "CONGO (KINSHASA)": "CONGO, THE DEMOCRATIC REPUBLIC OF THE",
        "CONGO (BRAZZAVILLE)": "CONGO",
        "PALESTINE": "PALESTINE, STATE OF",
        "BOLIVIA (PLURINATIONAL STATE OF)": "BOLIVIA (PLURINATIONAL STATE OF)",
    }
    return aliases.get(x, x)

def to_iso3(country_series: pd.Series) -> pd.Series:
    """
    Try to map country names to ISO3.
    Strategy:
    1) If values already look like ISO3 (3 letters), keep them.
    2) Use a minimal built-in dict for common countries (extend as needed).
    3) Best-effort fuzzy through pycountry if installed (optional).
    """
    # 1) already ISO3?
    def looks_like_iso3(val):
        return isinstance(val, str) and len(val) == 3 and val.isalpha()

    iso = []
    manual = {
        # extend with the actual countries in your table if needed
        "GREECE": "GRC",
        "AUSTRIA": "AUT",
        "TAIWAN": "TWN",
        "KOREA, REPUBLIC OF": "KOR",
        "BELGIUM": "BEL",
        "PORTUGAL": "PRT",
        "ITALY": "ITA",
        "PHILIPPINES": "PHL",
        "THAILAND": "THA",
        "SINGAPORE": "SGP",
        "INDONESIA": "IDN",
        "GERMANY": "DEU",
        "JAPAN": "JPN",
        "HONG KONG": "HKG",
        "SWITZERLAND": "CHE",
        "DENMARK": "DNK",
        "MALAYSIA": "MYS",
        "PAKISTAN": "PAK",
        "FRANCE": "FRA",
        "INDIA": "IND",
        "NETHERLANDS": "NLD",
        "SWEDEN": "SWE",
        "NORWAY": "NOR",
        "FINLAND": "FIN",
        "UNITED KINGDOM": "GBR",
        "AUSTRALIA": "AUS",
        "IRELAND": "IRL",
        "UNITED STATES OF AMERICA": "USA",
        "SOUTH AFRICA": "ZAF",
        "CANADA": "CAN",
        "NEW ZEALAND": "NZL",
        "SPAIN": "ESP",
        "TURKEY": "TUR",
        "MEXICO": "MEX",
        "BRAZIL": "BRA",
        "CHILE": "CHL",
        "ARGENTINA": "ARG"
    }

    try:
        import pycountry  # optional
    except Exception:
        pycountry = None

    for raw in country_series:
        if looks_like_iso3(raw):
            iso.append(raw.upper())
            continue
        name = normalize_name(raw)
        if name in manual:
            iso.append(manual[name])
            continue
        # pycountry fallback
        code = None
        if pycountry is not None:
            try:
                # direct
                m = pycountry.countries.search_fuzzy(name)
                if m:
                    code = m[0].alpha_3
            except Exception:
                code = None
        iso.append(code)
    return pd.Series(iso, index=country_series.index)

# ----------------------------
# Load
# ----------------------------
os.makedirs(os.path.dirname(HTML_OUT), exist_ok=True)

with open(PICKLE_PATH, "rb") as f:
    payload = pickle.load(f)

df = payload["final_combined_table"].copy()

# ----------------------------
# Clean & coerce types
# ----------------------------
# Drop blank/summaries you append at the end
drop_vals = {"", "Mean", "Median", "Std", "Min", "Max"}
df = df[~df["item6026"].isin(drop_vals)].reset_index(drop=True)

# Coerce metrics to numeric (strings with formatted zeros need this)
for col in METRIC_COLS:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Rename for clarity
df = df.rename(columns={"item6026": "Country"})

# ----------------------------
# ISO3 mapping
# ----------------------------
if "ISO3" not in df.columns:
    df["ISO3"] = to_iso3(df["Country"])

missing_iso = df["ISO3"].isna().sum()
if missing_iso > 0:
    print(f"Warning: {missing_iso} countries could not be mapped to ISO3 and will be omitted on the map.")
df_plot = df.dropna(subset=["ISO3"]).copy()

# ----------------------------
# Build interactive map with dropdown
# ----------------------------
start_metric = "Aggregate_EM_Score"

fig = px.choropleth(
    df_plot,
    locations="ISO3",
    color=start_metric,
    hover_name="Country",
    hover_data={m:":.3f" for m in METRIC_COLS},
    projection="natural earth",
    color_continuous_scale="RdYlGn_r",
    title="Earnings Management by Country"
)

# Dropdown (top-right) to switch metric
buttons = []
for m in METRIC_COLS:
    buttons.append(dict(
        label=PRETTY.get(m, m),
        method="restyle",
        args=[{"z": [df_plot[m]], "color": [df_plot[m]]}]
    ))

fig.update_layout(
    updatemenus=[dict(
        type="dropdown",
        x=0.98, y=0.98, xanchor="right", yanchor="top",
        buttons=buttons, showactive=True
    )],
    margin=dict(l=0, r=0, t=60, b=0)
)
fig.update_coloraxes(colorbar_title="EM level")

# ----------------------------
# Save outputs
# ----------------------------
fig.write_html(HTML_OUT, include_plotlyjs="cdn")
df_export = df_plot[["Country","ISO3"] + METRIC_COLS].sort_values("Aggregate_EM_Score", ascending=False)
df_export.to_csv(CSV_OUT, index=False)

print(f"Saved:\n  - {HTML_OUT}\n  - {CSV_OUT}")