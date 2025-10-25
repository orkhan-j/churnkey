# 📊 Churnkey Analytics Dashboard

An interactive dashboard visualizing accepted offers and churn prevention metrics from Churnkey.

## 🌐 Live Dashboard

View the live dashboard: **https://orkhan-j.github.io/churnkey/**

## 📈 What's Inside

This dashboard shows:

- **Acceptance Rates** - Weekly and monthly offer acceptance percentages
- **Offer Counts** - Number of accepted offers vs total sessions
- **Revenue Saved** - Total revenue saved from accepted offers
- **Offer Type Breakdown** - Distribution of DISCOUNT, PAUSE, PLAN_CHANGE, etc.
- **Toggle Views** - Switch between weekly and monthly data views
- **Color-Coded Rates** - Visual indicators for good/medium/low acceptance rates

## 🎨 Features

- ✅ Simple, clean table-based design
- ✅ Adaptive week/month toggle
- ✅ Weekly acceptance rate tracking
- ✅ Color-coded performance metrics
- ✅ Fully responsive (mobile & desktop)
- ✅ Self-contained HTML (no external dependencies)
- ✅ Last 6 months of data

## 📊 Metrics Overview

The dashboard analyzes:
- Accepted offer rates
- Revenue impact
- Offer type effectiveness
- Time-based trends
- Regional patterns

## 🔄 How to Update

To regenerate the dashboard with latest data:

```bash
python3 generate_simple_dashboard.py
```

This will:
1. Fetch latest 6 months of session data from Churnkey API
2. Calculate weekly and monthly acceptance rates
3. Generate a new `index.html` file
4. Push to GitHub to update the live dashboard

## 📦 Requirements

```bash
pip install -r requirements.txt
```

---

**Generated with**: Python, Pandas
**Data Source**: Churnkey Data API
