# 📊 Churnkey Analytics Dashboard

An interactive dashboard visualizing accepted offers and churn prevention metrics from Churnkey.

## 🌐 Live Dashboard

View the live dashboard: **https://orkhan-j.github.io/churnkey/**

## 📈 What's Inside

This dashboard has **two main sections**:

### 🎯 Accepted Offers Section
- **Acceptance Rates** - Weekly and monthly offer acceptance percentages
- **Offer Counts** - Number of accepted offers vs total sessions
- **Revenue Saved** - Total revenue saved from accepted offers
- **Offer Type Breakdown** - Distribution of DISCOUNT, PAUSE, PLAN_CHANGE, etc.
- **Toggle Views** - Switch between weekly and monthly data views
- **Color-Coded Rates** - Visual indicators for good/medium/low acceptance rates

### ❌ Canceled Sessions Section
- **Cancellation Rates** - Weekly and monthly cancellation percentages
- **Cancellation Counts** - Number of canceled sessions
- **Top Reasons** - Most common cancellation reasons for each period
- **Trend Analysis** - See how cancellations change over time
- **Toggle Views** - Switch between weekly and monthly data views

## 🎨 Features

- ✅ **Two separate views**: Accepted Offers and Canceled Sessions
- ✅ **Monthly view by default** (with weekly toggle)
- ✅ Simple, clean table-based design
- ✅ Acceptance rate and cancellation rate tracking
- ✅ Top cancellation reasons breakdown
- ✅ Color-coded performance metrics
- ✅ Fully responsive (mobile & desktop)
- ✅ Self-contained HTML (no external dependencies)
- ✅ Last 6 months of data
- ✅ Section tabs for easy navigation

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
python3 generate_dashboard_v2.py
```

This will:
1. Fetch latest 6 months of session data from Churnkey API
2. Calculate weekly and monthly acceptance rates
3. Calculate weekly and monthly cancellation rates and reasons
4. Generate a new `index.html` file with both sections
5. Push to GitHub to update the live dashboard:

```bash
git add index.html
git commit -m "Update dashboard data"
git push origin main
```

## 📦 Requirements

```bash
pip install -r requirements.txt
```

---

**Generated with**: Python, Pandas
**Data Source**: Churnkey Data API
