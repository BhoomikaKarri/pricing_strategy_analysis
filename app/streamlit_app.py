import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# PATH SETUP
BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_DIR   = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

# PAGE CONFIG
st.set_page_config(
    page_title="Retail Pricing Strategy Optimizer",
    page_icon="🏷️",
    layout="wide"
)

# LOAD DATA
@st.cache_data
def load_data():
    df       = pd.read_csv(DATA_DIR / "superstore_cleaned.csv")
    sim_df   = pd.read_csv(OUTPUT_DIR / "pricing_summary.csv")
    best_df  = pd.read_csv(OUTPUT_DIR / "best_scenario_per_subcategory.csv")
    elast_df = pd.read_csv(OUTPUT_DIR / "elasticity_by_subcategory.csv")
    return df, sim_df, best_df, elast_df

df, sim_df, best_df, elast_df = load_data()

# SIDEBAR
st.sidebar.header("Pricing Controls")
st.sidebar.markdown(
    "**1. Select product → 2. Test price → 3. See impact → 4. Decide**"
)
st.sidebar.divider()

category = st.sidebar.selectbox(
    "Select Category",
    options=sorted(df['Category'].unique())
)

sub_categories = sorted(
    df[df['Category'] == category]['Sub-Category'].unique()
)
sub_category = st.sidebar.selectbox(
    "Select Sub-Category",
    options=sub_categories
)

# BEST SCENARIO (needed before slider)
best_row = best_df[best_df['Sub-Category'] == sub_category]
best_scen          = best_row['Scenario'].values[0] \
    if len(best_row) > 0 else 'N/A'
best_profit        = best_row['New_Profit'].values[0] \
    if len(best_row) > 0 else 0
best_profit_change = best_row['Profit_Change'].values[0] \
    if len(best_row) > 0 else 0

# Smart default slider value based on best scenario
default_change = (
    10  if "+" in best_scen else
    -10 if "-" in best_scen else
    0
)

price_change = st.sidebar.slider(
    "Price Change (%)",
    min_value=-30,
    max_value=30,
    value=default_change,
    step=5
)

st.sidebar.divider()
st.sidebar.caption(
    "Results are directional estimates based on proxy elasticity."
)

# BASE METRICS
base_data = df[df['Sub-Category'] == sub_category]
elast_row = elast_df[elast_df['Sub-Category'] == sub_category]

base_price      = base_data['Unit_Price'].mean()
base_revenue    = base_data['Revenue'].sum()
base_profit     = base_data['Profit'].sum()
base_margin     = base_data['Profit_Margin'].mean()
base_qty        = base_data['Quantity'].sum()
base_margin_pct = base_profit / base_revenue if base_revenue != 0 else 0
txn_count       = len(base_data)

elasticity = elast_row['Proxy_Elasticity'].values[0] \
    if len(elast_row) > 0 else 0.0
demand_response = elast_row['Demand_Response'].values[0] \
    if len(elast_row) > 0 else 'Unknown'

if pd.isna(elasticity):
    elasticity = 0.0

# CONFIDENCE SIGNAL
if txn_count < 50:
    confidence = "Low"
elif abs(elasticity) < 0.2:
    confidence = "Low"
elif abs(elasticity) < 1.0:
    confidence = "Medium"
else:
    confidence = "High"

# SIMULATION
price_change_pct   = price_change / 100
new_price          = base_price * (1 + price_change_pct)
demand_change_pct  = elasticity * price_change_pct
new_quantity       = max(base_qty * (1 + demand_change_pct), 0)
new_revenue        = new_price * new_quantity
new_profit         = new_revenue * base_margin_pct
revenue_change     = new_revenue - base_revenue
profit_change      = new_profit - base_profit

# Revenue as base for consistency
profit_change_pct  = (profit_change / base_revenue * 100) \
    if base_revenue != 0 else 0
revenue_change_pct = (revenue_change / base_revenue * 100) \
    if base_revenue != 0 else 0

# Opportunity gap
gap = best_profit - base_profit

# STRATEGY LOGIC (nuanced)
def get_strategy(profit_change, price_change, base_profit):
    if base_profit < 0 and profit_change <= 0:
        return (
            "Avoid discounts — product is loss-making. "
            "Consider bundling or price increase.",
            "red"
        )
    elif base_profit < 0 and profit_change > 0:
        return (
            "Price increase helps recover losses — "
            "consider gradual increase.",
            "orange"
        )
    elif profit_change > 0 and price_change > 0:
        return (
            "Increase price — "
            "profit improves with limited demand risk.",
            "green"
        )
    elif profit_change > 0 and price_change < 0:
        return (
            "Discounting increases profit — demand is highly responsive. "
            "Apply selectively, monitor margins.",
            "orange"
        )
    elif profit_change < 0 and price_change < 0:
        return (
            "Avoid discounts — "
            "margin loss outweighs volume gain.",
            "red"
        )
    elif price_change == 0:
        return (
            "Hold price — "
            "adjust slider to simulate pricing scenarios.",
            "blue"
        )
    else:
        return (
            "Review pricing — "
            "profit impact is negative at this price point.",
            "orange"
        )

strategy_text, strategy_color = get_strategy(
    profit_change, price_change, base_profit
)

# EXECUTIVE SUMMARY — human language direction
direction = (
    "Increase Price" if "+" in best_scen else
    "Reduce Price"   if "-" in best_scen else
    "Hold Price"
)

# HEADER
st.title("🏷️ Retail Pricing Strategy Optimizer")
st.caption(
    "Simulate pricing decisions and evaluate profit impact instantly."
)
st.divider()

# EXECUTIVE SUMMARY
st.subheader("Executive Summary")

exc1, exc2, exc3, exc4 = st.columns(4)
exc1.info(f"**Most Profitable Direction**\n\n{direction}")
exc2.error("**Risk Area**\n\nHigh discounting (>20%)")
exc3.warning(
    f"**Key Issue**\n\n"
    f"{'Loss-making product' if base_profit < 0 else 'Margin optimization'}"
)
exc4.success(f"**Confidence Level**\n\n{confidence}")

st.divider()

# SECTION 1 — CURRENT STATE
st.subheader(f"Current State — {sub_category}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Unit Price",    f"${base_price:,.2f}")
col2.metric("Total Revenue",     f"${base_revenue:,.0f}")
col4.metric("Avg Profit Margin", f"{base_margin:.1f}%")

# Color-aware profit display
if base_profit < 0:
    col3.error(f"**Total Profit**\n\n${base_profit:,.0f} Loss-making")
else:
    col3.metric("Total Profit", f"${base_profit:,.0f}")

st.divider()

# SECTION 2 — SIMULATION RESULTS
st.subheader(f"Simulation — {price_change:+}% Price Change")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("New Price",
            f"${new_price:,.2f}",
            f"{price_change:+}%")
col2.metric("New Revenue",
            f"${new_revenue:,.0f}",
            f"{revenue_change_pct:+.1f}%")
col3.metric("New Profit",
            f"${new_profit:,.0f}",
            f"{profit_change_pct:+.1f}% vs revenue")
col4.metric("Profit Change $",
            f"${profit_change:+,.0f}")
col5.metric("Demand Change",
            f"{demand_change_pct*100:+.1f}%")

st.divider()

# SECTION 3 — FINAL DECISION CARD
st.subheader("💡 Final Recommendation")

dec_col1, dec_col2 = st.columns([2, 1])

with dec_col1:
    if strategy_color == "green":
        st.success(f"### {strategy_text}")
    elif strategy_color == "red":
        st.error(f"### {strategy_text}")
    elif strategy_color == "orange":
        st.warning(f"### {strategy_text}")
    else:
        st.info(f"### {strategy_text}")

with dec_col2:
    st.markdown("**Recommended Action**")
    st.markdown(f"### `{direction}`")
    st.markdown(f"**Best Scenario:** `{best_scen}`")
    st.markdown(f"**Expected Profit Change:** `${best_profit_change:+,.0f}`")
    st.markdown(f"**Opportunity Gap:** `${gap:+,.0f}` vs current")
    st.markdown(f"**Demand Response:** `{demand_response}`")
    st.markdown(f"**Proxy Elasticity:** `{elasticity:.3f}`")
    st.markdown(f"**Confidence Level:** `{confidence}`")

st.divider()

# SECTION 4 — SCENARIO COMPARISON
st.markdown("## 📈 Scenario Comparison")

sub_sim = sim_df[sim_df['Sub-Category'] == sub_category].copy()

scenario_order = [
    'Price -20%', 'Price -10%', 'Price -5%',
    'Current', 'Price +5%', 'Price +10%'
]
sub_sim['Scenario'] = pd.Categorical(
    sub_sim['Scenario'], categories=scenario_order, ordered=True
)
sub_sim = sub_sim.sort_values('Scenario')

st.markdown(
    f"**For {sub_category}, {direction.lower()} is the most profitable "
    f"direction (best: {best_scen}, "
    f"profit change: ${best_profit_change:+,.0f})**"
)

def bar_colors(series, best_scen, col_type):
    colors = []
    for scen, val in zip(sub_sim['Scenario'], series):
        if scen == best_scen:
            colors.append('#2ecc71')
        elif scen == 'Current':
            colors.append('#3498db')
        elif col_type == 'profit' and val < 0:
            colors.append('#e74c3c')
        else:
            colors.append('#bdc3c7')
    return colors

colors_rev  = bar_colors(sub_sim['New_Revenue'], best_scen, 'revenue')
colors_prof = bar_colors(sub_sim['New_Profit'],  best_scen, 'profit')

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
fig.patch.set_facecolor('#0e1117')

for ax in axes:
    ax.set_facecolor('#0e1117')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#444')

axes[0].bar(sub_sim['Scenario'], sub_sim['New_Revenue'], color=colors_rev)
axes[0].set_title("Revenue by Scenario", fontsize=11)
axes[0].set_xlabel("Scenario")
axes[0].set_ylabel("Revenue ($)")
axes[0].tick_params(axis='x', rotation=30)

axes[1].bar(sub_sim['Scenario'], sub_sim['New_Profit'], color=colors_prof)
axes[1].set_title("Profit by Scenario", fontsize=11)
axes[1].set_xlabel("Scenario")
axes[1].set_ylabel("Profit ($)")
axes[1].axhline(0, color='white', linestyle='--', linewidth=0.8)
axes[1].tick_params(axis='x', rotation=30)

legend_elements = [
    mpatches.Patch(color='#2ecc71', label='Best scenario'),
    mpatches.Patch(color='#3498db', label='Current'),
    mpatches.Patch(color='#e74c3c', label='Loss-making'),
    mpatches.Patch(color='#bdc3c7', label='Other scenarios'),
]
axes[1].legend(
    handles=legend_elements,
    loc='lower right',
    fontsize=8,
    facecolor='#0e1117',
    labelcolor='white'
)

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.divider()

# SECTION 5 — DISCOUNT STRATEGY
st.subheader("Discount Strategy")

disc_col1, disc_col2 = st.columns(2)

with disc_col1:
    discount_summary = df.groupby(
        'Discount_Band')['Profit_Margin'].mean().round(2)

    disc_table = {
        'Discount Band'  : [],
        'Avg Margin (%)' : [],
        'Verdict'        : []
    }
    for band, margin in discount_summary.items():
        disc_table['Discount Band'].append(str(band))
        disc_table['Avg Margin (%)'].append(margin)
        disc_table['Verdict'].append(
            'Acceptable' if margin > 0 else 'Avoid'
        )

    st.table(pd.DataFrame(disc_table))

with disc_col2:
    st.markdown("### Recommendation")
    st.markdown("""
- **No Discount** → best margin
- **Low (1–20%)** → acceptable
- **Medium (21–40%)** → unprofitable 
- **High (41%+)** → strongly avoid 

**Hard cap: MAX 20% discount across all categories.**
""")

st.divider()

# FOOTER

st.caption(
    "⚠️ Results are directional estimates based on proxy elasticity "
    "analysis. Validate with controlled pricing experiments before "
    "full implementation."
)