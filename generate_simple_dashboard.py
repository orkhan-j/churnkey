#!/usr/bin/env python3
"""
Generate Simple Adaptive Dashboard for Churnkey Offers
Shows acceptance rates with week/month toggle
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os

# Configuration
API_KEY = "live_data_rAjRNH71aZ3rdk7rG1yOqsl6Ir1YFy4a"
APP_ID = "9lv36y492"
BASE_URL = "https://api.churnkey.co/v1/data"

class SimpleDashboard:
    def __init__(self):
        self.headers = {
            "x-ck-api-key": API_KEY,
            "x-ck-app": APP_ID,
            "content-type": "application/json"
        }
        self.output_dir = "."

        # Calculate date range (last 6 months)
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=180)

    def fetch_sessions(self, limit=10000):
        """Fetch all sessions from last 6 months"""
        params = {
            "limit": limit,
            "startDate": self.start_date.strftime("%Y-%m-%d"),
        }

        print(f"📥 Fetching sessions from {self.start_date.date()} to {self.end_date.date()}...")
        response = requests.get(
            f"{BASE_URL}/sessions",
            headers=self.headers,
            params=params
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Fetched {len(data)} sessions")
            return data
        else:
            print(f"✗ Error: {response.status_code}")
            return []

    def process_data(self, sessions):
        """Process sessions for weekly and monthly acceptance rates"""
        all_records = []

        for session in sessions:
            created_at = pd.to_datetime(session.get('createdAt'))
            save_type = session.get('saveType')
            canceled = session.get('canceled', False)

            # Track all sessions
            is_accepted = save_type and save_type != 'ABANDON'

            all_records.append({
                'date': created_at,
                'accepted': is_accepted,
                'canceled': canceled,
                'offer_type': save_type if is_accepted else None,
                'plan_price': session.get('customer', {}).get('planPrice', 0),
                'cancellation_reason': session.get('surveyChoiceValue') if canceled else None,
            })

        df = pd.DataFrame(all_records)

        if not df.empty:
            df['week'] = df['date'].dt.to_period('W').dt.start_time
            df['week_label'] = df['date'].dt.strftime('%Y-W%U')
            df['month'] = df['date'].dt.to_period('M').dt.start_time
            df['month_label'] = df['date'].dt.strftime('%Y-%m')
            df['revenue_saved'] = df['plan_price'] / 100  # Convert cents to dollars

        return df

    def calculate_weekly_stats(self, df):
        """Calculate weekly statistics"""
        # Filter accepted offers for revenue calculation
        df_accepted = df[df['accepted'] == True].copy()

        # Calculate stats for all sessions
        weekly_all = df.groupby('week_label').size().reset_index(name='total_count')
        weekly_accepted = df[df['accepted'] == True].groupby('week_label').size().reset_index(name='accepted_count')
        weekly_revenue = df_accepted.groupby('week_label')['revenue_saved'].sum().reset_index(name='revenue_saved')

        # Get offer types breakdown
        offer_types_data = []
        for week in df['week_label'].unique():
            week_data = df[(df['week_label'] == week) & (df['accepted'] == True)]
            offer_types = week_data['offer_type'].value_counts().to_dict() if not week_data.empty else {}
            offer_types_data.append({'week_label': week, 'offer_types': offer_types})

        weekly_offers = pd.DataFrame(offer_types_data)

        # Merge all together
        weekly = weekly_all.merge(weekly_accepted, on='week_label', how='left')
        weekly = weekly.merge(weekly_revenue, on='week_label', how='left')
        weekly = weekly.merge(weekly_offers, on='week_label', how='left')

        weekly['accepted_count'] = weekly['accepted_count'].fillna(0).astype(int)
        weekly['revenue_saved'] = weekly['revenue_saved'].fillna(0)
        weekly['acceptance_rate'] = (weekly['accepted_count'] / weekly['total_count'] * 100).round(1)

        weekly = weekly.rename(columns={'week_label': 'week'})
        return weekly.sort_values('week', ascending=False)

    def calculate_monthly_stats(self, df):
        """Calculate monthly statistics"""
        # Filter accepted offers for revenue calculation
        df_accepted = df[df['accepted'] == True].copy()

        # Calculate stats for all sessions
        monthly_all = df.groupby('month_label').size().reset_index(name='total_count')
        monthly_accepted = df[df['accepted'] == True].groupby('month_label').size().reset_index(name='accepted_count')
        monthly_revenue = df_accepted.groupby('month_label')['revenue_saved'].sum().reset_index(name='revenue_saved')

        # Get offer types breakdown
        offer_types_data = []
        for month in df['month_label'].unique():
            month_data = df[(df['month_label'] == month) & (df['accepted'] == True)]
            offer_types = month_data['offer_type'].value_counts().to_dict() if not month_data.empty else {}
            offer_types_data.append({'month_label': month, 'offer_types': offer_types})

        monthly_offers = pd.DataFrame(offer_types_data)

        # Merge all together
        monthly = monthly_all.merge(monthly_accepted, on='month_label', how='left')
        monthly = monthly.merge(monthly_revenue, on='month_label', how='left')
        monthly = monthly.merge(monthly_offers, on='month_label', how='left')

        monthly['accepted_count'] = monthly['accepted_count'].fillna(0).astype(int)
        monthly['revenue_saved'] = monthly['revenue_saved'].fillna(0)
        monthly['acceptance_rate'] = (monthly['accepted_count'] / monthly['total_count'] * 100).round(1)

        monthly = monthly.rename(columns={'month_label': 'month'})
        return monthly.sort_values('month', ascending=False)

    def calculate_cancellation_stats_weekly(self, df):
        """Calculate weekly cancellation statistics"""
        df_canceled = df[df['canceled'] == True].copy()

        # Calculate stats
        weekly_all = df.groupby('week_label').size().reset_index(name='total_count')
        weekly_canceled = df_canceled.groupby('week_label').size().reset_index(name='canceled_count')

        # Get cancellation reasons breakdown
        reason_data = []
        for week in df['week_label'].unique():
            week_data = df[(df['week_label'] == week) & (df['canceled'] == True)]
            reasons = week_data['cancellation_reason'].value_counts().to_dict() if not week_data.empty else {}
            reason_data.append({'week_label': week, 'reasons': reasons})

        weekly_reasons = pd.DataFrame(reason_data)

        # Merge
        weekly = weekly_all.merge(weekly_canceled, on='week_label', how='left')
        weekly = weekly.merge(weekly_reasons, on='week_label', how='left')

        weekly['canceled_count'] = weekly['canceled_count'].fillna(0).astype(int)
        weekly['cancellation_rate'] = (weekly['canceled_count'] / weekly['total_count'] * 100).round(1)

        weekly = weekly.rename(columns={'week_label': 'week'})
        return weekly.sort_values('week', ascending=False)

    def calculate_cancellation_stats_monthly(self, df):
        """Calculate monthly cancellation statistics"""
        df_canceled = df[df['canceled'] == True].copy()

        # Calculate stats
        monthly_all = df.groupby('month_label').size().reset_index(name='total_count')
        monthly_canceled = df_canceled.groupby('month_label').size().reset_index(name='canceled_count')

        # Get cancellation reasons breakdown
        reason_data = []
        for month in df['month_label'].unique():
            month_data = df[(df['month_label'] == month) & (df['canceled'] == True)]
            reasons = month_data['cancellation_reason'].value_counts().to_dict() if not month_data.empty else {}
            reason_data.append({'month_label': month, 'reasons': reasons})

        monthly_reasons = pd.DataFrame(reason_data)

        # Merge
        monthly = monthly_all.merge(monthly_canceled, on='month_label', how='left')
        monthly = monthly.merge(monthly_reasons, on='month_label', how='left')

        monthly['canceled_count'] = monthly['canceled_count'].fillna(0).astype(int)
        monthly['cancellation_rate'] = (monthly['canceled_count'] / monthly['total_count'] * 100).round(1)

        monthly = monthly.rename(columns={'month_label': 'month'})
        return monthly.sort_values('month', ascending=False)

    def generate_html(self, df):
        """Generate simple, clean HTML dashboard"""

        weekly_stats = self.calculate_weekly_stats(df)
        monthly_stats = self.calculate_monthly_stats(df)

        # Overall metrics
        total_sessions = len(df)
        total_accepted = df['accepted'].sum()
        overall_acceptance_rate = (total_accepted / total_sessions * 100) if total_sessions > 0 else 0
        total_revenue = df[df['accepted'] == True]['revenue_saved'].sum()

        # Get offer type breakdown
        offer_breakdown = df[df['accepted'] == True]['offer_type'].value_counts().to_dict()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Churnkey Offers Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .header {{
            background: #4a5568;
            color: white;
            padding: 30px;
            border-radius: 8px 8px 0 0;
        }}

        .header h1 {{
            font-size: 24px;
            margin-bottom: 5px;
        }}

        .header p {{
            font-size: 14px;
            opacity: 0.9;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            border-bottom: 1px solid #e2e8f0;
        }}

        .metric {{
            text-align: center;
        }}

        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 5px;
        }}

        .metric-label {{
            font-size: 13px;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .controls {{
            padding: 20px 30px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            gap: 10px;
            align-items: center;
        }}

        .toggle-btn {{
            padding: 10px 20px;
            border: 2px solid #4a5568;
            background: white;
            color: #4a5568;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
        }}

        .toggle-btn.active {{
            background: #4a5568;
            color: white;
        }}

        .toggle-btn:hover {{
            background: #2d3748;
            color: white;
            border-color: #2d3748;
        }}

        .content {{
            padding: 30px;
        }}

        .view {{
            display: none;
        }}

        .view.active {{
            display: block;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th {{
            background: #f7fafc;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            color: #4a5568;
            border-bottom: 2px solid #e2e8f0;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
        }}

        tr:hover {{
            background: #f7fafc;
        }}

        .rate-good {{
            color: #38a169;
            font-weight: 600;
        }}

        .rate-medium {{
            color: #d69e2e;
            font-weight: 600;
        }}

        .rate-low {{
            color: #e53e3e;
            font-weight: 600;
        }}

        .offer-types {{
            font-size: 12px;
            color: #718096;
        }}

        .footer {{
            padding: 20px 30px;
            background: #f7fafc;
            text-align: center;
            font-size: 13px;
            color: #718096;
            border-radius: 0 0 8px 8px;
        }}

        @media (max-width: 768px) {{
            .metrics {{
                grid-template-columns: 1fr 1fr;
            }}

            .controls {{
                flex-direction: column;
                align-items: stretch;
            }}

            table {{
                font-size: 12px;
            }}

            th, td {{
                padding: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Churnkey Offers Dashboard</h1>
            <p>Last 6 Months | Updated {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
        </div>

        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{total_accepted:,}</div>
                <div class="metric-label">Accepted Offers</div>
            </div>
            <div class="metric">
                <div class="metric-value">{total_sessions:,}</div>
                <div class="metric-label">Total Sessions</div>
            </div>
            <div class="metric">
                <div class="metric-value">{overall_acceptance_rate:.1f}%</div>
                <div class="metric-label">Acceptance Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value">${total_revenue:,.0f}</div>
                <div class="metric-label">Revenue Saved</div>
            </div>
        </div>

        <div class="controls">
            <button class="toggle-btn active" onclick="showView('weekly')">Weekly View</button>
            <button class="toggle-btn" onclick="showView('monthly')">Monthly View</button>
        </div>

        <div class="content">
            <div id="weekly-view" class="view active">
                <h2 style="margin-bottom: 10px; color: #2d3748;">Weekly Acceptance Rates</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Week</th>
                            <th style="text-align: right;">Accepted</th>
                            <th style="text-align: right;">Total Sessions</th>
                            <th style="text-align: right;">Acceptance Rate</th>
                            <th style="text-align: right;">Revenue Saved</th>
                            <th>Offer Types</th>
                        </tr>
                    </thead>
                    <tbody>
"""

        # Add weekly rows
        for _, row in weekly_stats.iterrows():
            rate_class = 'rate-good' if row['acceptance_rate'] >= 40 else 'rate-medium' if row['acceptance_rate'] >= 25 else 'rate-low'
            offer_types_str = ', '.join([f"{k}: {v}" for k, v in row['offer_types'].items()]) if row['offer_types'] else '-'

            html += f"""
                        <tr>
                            <td><strong>{row['week']}</strong></td>
                            <td style="text-align: right;">{int(row['accepted_count'])}</td>
                            <td style="text-align: right;">{int(row['total_count'])}</td>
                            <td style="text-align: right;" class="{rate_class}">{row['acceptance_rate']}%</td>
                            <td style="text-align: right;">${row['revenue_saved']:,.0f}</td>
                            <td class="offer-types">{offer_types_str}</td>
                        </tr>
"""

        html += """
                    </tbody>
                </table>
            </div>

            <div id="monthly-view" class="view">
                <h2 style="margin-bottom: 10px; color: #2d3748;">Monthly Acceptance Rates</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Month</th>
                            <th style="text-align: right;">Accepted</th>
                            <th style="text-align: right;">Total Sessions</th>
                            <th style="text-align: right;">Acceptance Rate</th>
                            <th style="text-align: right;">Revenue Saved</th>
                            <th>Offer Types</th>
                        </tr>
                    </thead>
                    <tbody>
"""

        # Add monthly rows
        for _, row in monthly_stats.iterrows():
            rate_class = 'rate-good' if row['acceptance_rate'] >= 40 else 'rate-medium' if row['acceptance_rate'] >= 25 else 'rate-low'
            offer_types_str = ', '.join([f"{k}: {v}" for k, v in row['offer_types'].items()]) if row['offer_types'] else '-'

            html += f"""
                        <tr>
                            <td><strong>{row['month']}</strong></td>
                            <td style="text-align: right;">{int(row['accepted_count'])}</td>
                            <td style="text-align: right;">{int(row['total_count'])}</td>
                            <td style="text-align: right;" class="{rate_class}">{row['acceptance_rate']}%</td>
                            <td style="text-align: right;">${row['revenue_saved']:,.0f}</td>
                            <td class="offer-types">{offer_types_str}</td>
                        </tr>
"""

        html += """
                    </tbody>
                </table>
            </div>
        </div>

        <div class="footer">
            Churnkey Analytics | Data from Churnkey API
        </div>
    </div>

    <script>
        function showView(viewName) {
            // Hide all views
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));

            // Show selected view
            document.getElementById(viewName + '-view').classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""

        return html

    def run(self):
        """Run the dashboard generation"""
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║       Churnkey Simple Dashboard Generator                   ║")
        print("╚══════════════════════════════════════════════════════════════╝\n")

        # Fetch data
        all_sessions = self.fetch_sessions()

        if not all_sessions:
            print("❌ No data fetched. Exiting.")
            return

        # Process data
        print("\n📊 Processing data...")
        df = self.process_data(all_sessions)

        if df.empty:
            print("⚠️  No data found")
            return

        print(f"✓ Processed {len(df)} sessions\n")

        # Generate HTML
        print("📝 Generating HTML dashboard...")
        html = self.generate_html(df)

        # Save
        output_path = 'index.html'
        with open(output_path, 'w') as f:
            f.write(html)

        print(f"✅ Dashboard saved: {output_path}")
        print(f"🌐 Open it in your browser or push to GitHub Pages!")
        print("\n" + "="*60)
        print("✨ Complete!")
        print("="*60)

if __name__ == "__main__":
    dashboard = SimpleDashboard()
    dashboard.run()
