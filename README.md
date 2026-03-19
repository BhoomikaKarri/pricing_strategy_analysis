# Retail Pricing Strategy & Profit Optimization

A decision-support system that identifies profit-maximizing pricing strategies using retail transaction data.

## Key Insight

- **18.7% of transactions are loss-making**
- Profit margin drops from **+34% to -108%** at high discounts
- **13 out of 17 product categories** are most profitable at a price increase

The business is **over-discounting and underpricing**, leading to systematic profit loss.

---

## Problem Statement

Most businesses optimize for **revenue**, not **profit**.

Discounting is often used to increase sales, but without understanding demand response, it can silently destroy margins.

**This project asks:**
> What price maximizes profit — not just sales — for each product category?

---

## What This Project Does

This is not just a dashboard. It is a **decision-support system** built across five analytical stages:

### 1) Data Cleaning
- Processed **9,977 retail transactions**
- Created derived metrics:
  - Unit Price
  - Profit Margin
  - Discount Bands
  - Price Segments
- Handled division edge cases
- Retained negative profit rows intentionally to capture pricing inefficiencies

### 2) Exploratory Data Analysis
- Found that **18.7% of transactions are loss-making**
- Discovered that profit margin collapses from **+34%** at zero discount to **-108%** at high discount
- Identified three structurally loss-making sub-categories:
  - Tables
  - Bookcases
  - Supplies

### 3) Pricing Response Analysis
- Built an **observed demand response model** as a proxy for price elasticity
- Classified sub-categories into sensitivity bands
- Built an internal market benchmark to flag overpriced and underpriced products
- Added data reliability signals using transaction volume

### 4) Scenario Simulation
- Simulated **six pricing scenarios** from **-20% to +10%** for every sub-category
- Found that **13 out of 17 sub-categories** are most profitable at a price increase
- Confirmed that the business is underpricing across most product lines

### 5) Recommendations and Streamlit App
- Generated category-specific pricing recommendations
- Built an interactive **Streamlit** tool where users can:
  - Select a product
  - Simulate a price change
  - Instantly see revenue impact, profit impact, and a final pricing recommendation

---

## Tech Stack

Python · Pandas · NumPy · Matplotlib · Seaborn · Streamlit

---

## Project Structure

```text
pricing_strategy_analysis/
│
├── data/
│   ├── SampleSuperstore.csv
│   └── superstore_cleaned.csv
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_pricing_response.ipynb
│   ├── 04_scenario_simulation.ipynb
│   └── 05_recommendations.ipynb
│
├── app/
│   └── streamlit_app.py
│
├── outputs/
│   ├── pricing_summary.csv
│   ├── recommendation_table.csv
│   └── analysis charts
│
├── requirements.txt
└── README.md
