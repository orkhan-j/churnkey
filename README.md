# 📊 Churnkey Analytics Dashboard

Interactive dashboard showing cancel flows and reactivation metrics from Churnkey.

## 🌐 Live Dashboard

**Cancel Flows & Reactivation Dashboard**: https://orkhan-j.github.io/churnkey/

## 📈 Dashboard Overview

### 🔄 Cancel Flows & Reactivation Dashboard

**Four main sections**:

#### 1. Flow 1 📊
Your primary cancel flow tracking:
- **Sessions Count** - Total sessions through this flow
- **Acceptance Rate** - Percentage of offers accepted
- **Cancellation Rate** - Percentage of cancellations
- **Weekly/Monthly Views** - Track trends over time

#### 2. Flow 2 📊
Your secondary cancel flow tracking:
- **Sessions Count** - Total sessions through this flow
- **Acceptance Rate** - Percentage of offers accepted
- **Cancellation Rate** - Percentage of cancellations
- **Weekly/Monthly Views** - Track trends over time

#### 3. Combined Flows 📈
Aggregate view of both cancel flows:
- **Total Sessions** - Combined from both flows
- **Overall Acceptance Rate** - Across both flows
- **Overall Cancellation Rate** - Across both flows
- **Trend Analysis** - See combined performance

#### 4. Reactivation 🔄
Track customers who return:
- **Unique Customers** - Total customers per period
- **Reactivated Customers** - Those who came back
- **Reactivation Rate** - Percentage who returned
- **Weekly/Monthly Views** - Track reactivation trends

## 🎨 Features

- ✅ **Two cancel flows** tracked separately and combined
- ✅ **Reactivation tracking** - See who comes back
- ✅ **Monthly view by default** (with weekly toggle)
- ✅ Simple, clean table-based design
- ✅ Acceptance rate and cancellation rate tracking
- ✅ Color-coded performance metrics (green = good, yellow = medium, red = low)
- ✅ Fully responsive (mobile & desktop)
- ✅ Self-contained HTML (no external dependencies)
- ✅ Last 6 months of data
- ✅ Section tabs for easy navigation
- ✅ Updated every Monday for fresh data

## 📊 Metrics Overview

The dashboard tracks:
- **Two separate cancel flows** performance
- **Acceptance rates** per flow and combined
- **Cancellation rates** per flow and combined
- **Reactivation rates** - Customers who return
- **Time-based trends** (weekly & monthly)
- **Session volumes** across flows

## 🔄 How to Update

### Update Dashboard (Recommended for Monday updates):

```bash
# Update flows dashboard
python3 generate_flows_dashboard.py

# Push to GitHub
git add index.html
git commit -m "Update dashboard with latest data"
git push origin main
```

### What Gets Updated:
1. ✅ Latest 6 months of session data from Churnkey API
2. ✅ Both cancel flows identified and tracked
3. ✅ Weekly and monthly acceptance rates per flow
4. ✅ Weekly and monthly cancellation rates per flow
5. ✅ Reactivation rates and customer tracking
6. ✅ Combined flow statistics
7. ✅ `index.html` file

The live dashboard updates automatically on GitHub Pages within 1-2 minutes!

## 📦 Requirements

```bash
pip install -r requirements.txt
```

---

**Generated with**: Python, Pandas
**Data Source**: Churnkey Data API
