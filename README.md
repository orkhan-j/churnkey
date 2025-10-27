# 📊 Churnkey Analytics Dashboard

Interactive dashboards visualizing accepted offers, churn prevention metrics, and revenue impact from Churnkey.

## 🌐 Live Dashboards

- **Main Dashboard**: https://orkhan-j.github.io/churnkey/
- **Revenue Dashboard**: https://orkhan-j.github.io/churnkey/revenue.html

## 📈 Available Dashboards

### 1. Main Dashboard (index.html)

**Two main sections**:

#### 🎯 Accepted Offers Section
- **Acceptance Rates** - Weekly and monthly offer acceptance percentages
- **Offer Counts** - Number of accepted offers vs total sessions
- **Revenue Saved** - Total revenue saved from accepted offers
- **Offer Type Breakdown** - Distribution of DISCOUNT, PAUSE, PLAN_CHANGE, etc.
- **Toggle Views** - Switch between weekly and monthly data views
- **Color-Coded Rates** - Visual indicators for good/medium/low acceptance rates

#### ❌ Canceled Sessions Section
- **Cancellation Rates** - Weekly and monthly cancellation percentages
- **Cancellation Counts** - Number of canceled sessions
- **Top Reasons** - Most common cancellation reasons for each period
- **Trend Analysis** - See how cancellations change over time
- **Toggle Views** - Switch between weekly and monthly data views

### 2. Revenue Impact Dashboard (revenue.html) 💰

**Financial analysis focused on revenue metrics**:

#### Revenue Trends
- **Revenue Saved** - Total revenue retained from accepted offers
- **Revenue Lost** - Revenue from cancellations
- **Net Revenue Impact** - Saved minus lost
- **Average Revenue per Save** - Financial efficiency metric
- **Save Rate Tracking** - Percentage of successful saves
- **Weekly/Monthly Views** - Track revenue trends over time

#### Breakdown by Offer Type
- **Revenue by Save Type** - DISCOUNT, PAUSE, PLAN_CHANGE performance
- **Number of Saves** - Volume per offer type
- **Average Revenue per Save** - Which offers generate most value
- **Percentage Distribution** - Share of total revenue per offer type

## 🎨 Features

- ✅ **Two dashboards**: Main (offers/cancellations) + Revenue Impact
- ✅ **Monthly view by default** (with weekly toggle)
- ✅ Simple, clean table-based design
- ✅ Financial metrics and revenue tracking
- ✅ Acceptance rate and cancellation rate tracking
- ✅ Top cancellation reasons breakdown
- ✅ Revenue breakdown by offer type
- ✅ Color-coded performance metrics (green = good, red = loss)
- ✅ Fully responsive (mobile & desktop)
- ✅ Self-contained HTML (no external dependencies)
- ✅ Last 6 months of data
- ✅ Section tabs for easy navigation
- ✅ Updated every Monday for fresh data

## 📊 Metrics Overview

The dashboard analyzes:
- Accepted offer rates
- Revenue impact
- Offer type effectiveness
- Time-based trends
- Regional patterns

## 🔄 How to Update

### Update All Dashboards (Recommended for Monday updates):

```bash
# Update main dashboard
python3 generate_dashboard_v2.py

# Update revenue dashboard
python3 generate_revenue_dashboard.py

# Push to GitHub
git add index.html revenue.html
git commit -m "Update dashboards with latest data"
git push origin main
```

### What Gets Updated:
1. ✅ Latest 6 months of session data from Churnkey API
2. ✅ Weekly and monthly acceptance rates
3. ✅ Weekly and monthly cancellation rates and reasons
4. ✅ Revenue saved vs lost calculations
5. ✅ Revenue breakdown by offer type
6. ✅ Both `index.html` and `revenue.html` files

The live dashboards update automatically on GitHub Pages within 1-2 minutes!

## 📦 Requirements

```bash
pip install -r requirements.txt
```

---

**Generated with**: Python, Pandas
**Data Source**: Churnkey Data API
