#!/usr/bin/env python3
"""
Generate Revenue Impact Dashboard for Churnkey
Shows revenue saved vs lost, trends, and financial impact
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os

# Configuration
API_KEY = "live_data_rAjRNH71aZ3rdk7rG1yOqsl6Ir1YFy4a"
APP_ID = "9lv36y492"
BASE_URL = "https://api.churnkey.co/v1/data"

class RevenueDashboard:
    def __init__(self):
        self.headers = {
            "x-ck-api-key": API_KEY,
            "x-ck-app": APP_ID,
            "content-type": "application/json"
        }

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
        """Process sessions for revenue analysis"""
        all_records = []

        for session in sessions:
            created_at = pd.to_datetime(session.get('createdAt'))
            save_type = session.get('saveType')
            canceled = session.get('canceled', False)
            plan_price = session.get('customer', {}).get('planPrice', 0)
            billing_interval = session.get('customer', {}).get('billingInterval', 'MONTH')

            is_accepted = save_type and save_type != 'ABANDON'

            all_records.append({
                'date': created_at,
                'accepted': is_accepted,
                'canceled': canceled,
                'save_type': save_type,
                'plan_price': plan_price,
                'billing_interval': billing_interval,
                'revenue': plan_price / 100,  # Convert to dollars
            })

        df = pd.DataFrame(all_records)

        if not df.empty:
            df['week_label'] = df['date'].dt.strftime('%Y-W%U')
            df['month_label'] = df['date'].dt.strftime('%Y-%m')
            df['month_name'] = df['date'].dt.strftime('%b %Y')

        return df

    def calculate_revenue_stats(self, df, period='month'):
        """Calculate revenue metrics by period"""
        period_col = f'{period}_label'

        # Revenue saved (accepted offers)
        saved = df[df['accepted'] == True].groupby(period_col).agg({
            'revenue': 'sum',
            'accepted': 'size'
        }).rename(columns={'revenue': 'revenue_saved', 'accepted': 'saves_count'})

        # Revenue lost (canceled)
        lost = df[df['canceled'] == True].groupby(period_col).agg({
            'revenue': 'sum',
            'canceled': 'size'
        }).rename(columns={'revenue': 'revenue_lost', 'canceled': 'cancels_count'})

        # All sessions
        all_sessions = df.groupby(period_col).size().reset_index(name='total_sessions')

        # Merge
        result = all_sessions.set_index(period_col)
        result = result.join(saved, how='left')
        result = result.join(lost, how='left')

        result = result.fillna(0)
        result['net_revenue'] = result['revenue_saved'] - result['revenue_lost']
        result['save_rate'] = (result['saves_count'] / result['total_sessions'] * 100).round(1)

        result = result.reset_index()
        result = result.rename(columns={period_col: 'period'})

        return result.sort_values('period', ascending=False)

    def calculate_save_type_revenue(self, df):
        """Calculate revenue by save type"""
        saved = df[df['accepted'] == True].groupby('save_type').agg({
            'revenue': 'sum',
            'accepted': 'size'
        }).rename(columns={'accepted': 'count'})

        saved['avg_revenue'] = (saved['revenue'] / saved['count']).round(2)
        saved = saved.sort_values('revenue', ascending=False)

        return saved.reset_index()

    def generate_html(self, df):
        """Generate revenue impact dashboard HTML"""

        # Calculate all stats
        weekly_revenue = self.calculate_revenue_stats(df, 'week')
        monthly_revenue = self.calculate_revenue_stats(df, 'month')
        save_type_revenue = self.calculate_save_type_revenue(df)

        # Overall metrics
        total_saved = df[df['accepted'] == True]['revenue'].sum()
        total_lost = df[df['canceled'] == True]['revenue'].sum()
        net_revenue = total_saved - total_lost
        total_saves = df['accepted'].sum()
        total_cancels = df['canceled'].sum()
        avg_revenue_per_save = total_saved / total_saves if total_saves > 0 else 0
        save_rate = (total_saves / len(df) * 100) if len(df) > 0 else 0

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Revenue Impact Dashboard - Churnkey</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px 8px 0 0;
        }}

        .header h1 {{ font-size: 28px; margin-bottom: 5px; }}
        .header p {{ font-size: 14px; opacity: 0.9; }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            border-bottom: 2px solid #e2e8f0;
        }}

        .metric {{
            text-align: center;
            padding: 20px;
            background: #f7fafc;
            border-radius: 8px;
        }}

        .metric-value {{
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 8px;
        }}

        .metric-value.positive {{ color: #38a169; }}
        .metric-value.negative {{ color: #e53e3e; }}
        .metric-value.neutral {{ color: #4a5568; }}

        .metric-label {{
            font-size: 13px;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }}

        .metric-change {{
            font-size: 12px;
            margin-top: 5px;
            color: #718096;
        }}

        .section-tabs {{
            padding: 20px 30px 0;
            border-bottom: 2px solid #e2e8f0;
            display: flex;
            gap: 5px;
        }}

        .section-tab {{
            padding: 12px 24px;
            background: transparent;
            border: none;
            border-bottom: 3px solid transparent;
            color: #718096;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            transition: all 0.2s;
        }}

        .section-tab.active {{
            color: #667eea;
            border-bottom-color: #667eea;
        }}

        .section-content {{ display: none; padding: 30px; }}
        .section-content.active {{ display: block; }}

        .controls {{
            padding: 20px 30px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            gap: 10px;
        }}

        .toggle-btn {{
            padding: 10px 20px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
        }}

        .toggle-btn.active {{ background: #667eea; color: white; }}

        .view {{ display: none; }}
        .view.active {{ display: block; }}

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

        tr:hover {{ background: #f7fafc; }}

        .positive-value {{ color: #38a169; font-weight: 600; }}
        .negative-value {{ color: #e53e3e; font-weight: 600; }}

        .summary-box {{
            background: linear-gradient(135deg, #f7fafc 0%, #e6f7ff 100%);
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 4px solid #667eea;
        }}

        .summary-box h3 {{
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .summary-item {{
            background: white;
            padding: 15px;
            border-radius: 6px;
        }}

        .summary-item-label {{
            font-size: 12px;
            color: #718096;
            margin-bottom: 5px;
        }}

        .summary-item-value {{
            font-size: 20px;
            font-weight: bold;
            color: #2d3748;
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
            .metrics {{ grid-template-columns: 1fr 1fr; }}
            .summary-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Revenue Impact Dashboard</h1>
            <p>Last 6 Months Financial Analysis | Updated {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
        </div>

        <div class="metrics">
            <div class="metric">
                <div class="metric-value positive">${total_saved:,.0f}</div>
                <div class="metric-label">Revenue Saved</div>
                <div class="metric-change">From {total_saves} accepted offers</div>
            </div>
            <div class="metric">
                <div class="metric-value negative">${total_lost:,.0f}</div>
                <div class="metric-label">Revenue Lost</div>
                <div class="metric-change">From {total_cancels} cancellations</div>
            </div>
            <div class="metric">
                <div class="metric-value {'positive' if net_revenue > 0 else 'negative'}">${net_revenue:,.0f}</div>
                <div class="metric-label">Net Revenue Impact</div>
                <div class="metric-change">Saved - Lost</div>
            </div>
            <div class="metric">
                <div class="metric-value neutral">${avg_revenue_per_save:,.0f}</div>
                <div class="metric-label">Avg Revenue/Save</div>
                <div class="metric-change">{save_rate:.1f}% save rate</div>
            </div>
        </div>

        <div class="section-tabs">
            <button class="section-tab active" onclick="showSection('trends')">Revenue Trends</button>
            <button class="section-tab" onclick="showSection('breakdown')">Breakdown by Offer</button>
        </div>

        <!-- REVENUE TRENDS SECTION -->
        <div id="trends-section" class="section-content active">
            <div class="controls">
                <button class="toggle-btn" onclick="showView('trends', 'weekly')">Weekly View</button>
                <button class="toggle-btn active" onclick="showView('trends', 'monthly')">Monthly View</button>
            </div>

            <div id="trends-weekly-view" class="view">
                <h2 style="margin-bottom: 10px; color: #2d3748;">Weekly Revenue Impact</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Week</th>
                            <th style="text-align: right;">Revenue Saved</th>
                            <th style="text-align: right;">Revenue Lost</th>
                            <th style="text-align: right;">Net Impact</th>
                            <th style="text-align: right;">Saves</th>
                            <th style="text-align: right;">Save Rate</th>
                        </tr>
                    </thead>
                    <tbody>
"""

        # Weekly revenue rows
        for _, row in weekly_revenue.iterrows():
            net_class = 'positive-value' if row['net_revenue'] > 0 else 'negative-value'

            html += f"""
                        <tr>
                            <td><strong>{row['period']}</strong></td>
                            <td style="text-align: right;" class="positive-value">${row['revenue_saved']:,.0f}</td>
                            <td style="text-align: right;" class="negative-value">${row['revenue_lost']:,.0f}</td>
                            <td style="text-align: right;" class="{net_class}">${row['net_revenue']:,.0f}</td>
                            <td style="text-align: right;">{int(row['saves_count'])}</td>
                            <td style="text-align: right;">{row['save_rate']:.1f}%</td>
                        </tr>
"""

        html += """
                    </tbody>
                </table>
            </div>

            <div id="trends-monthly-view" class="view active">
                <h2 style="margin-bottom: 10px; color: #2d3748;">Monthly Revenue Impact</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Month</th>
                            <th style="text-align: right;">Revenue Saved</th>
                            <th style="text-align: right;">Revenue Lost</th>
                            <th style="text-align: right;">Net Impact</th>
                            <th style="text-align: right;">Saves</th>
                            <th style="text-align: right;">Save Rate</th>
                        </tr>
                    </thead>
                    <tbody>
"""

        # Monthly revenue rows
        for _, row in monthly_revenue.iterrows():
            net_class = 'positive-value' if row['net_revenue'] > 0 else 'negative-value'

            html += f"""
                        <tr>
                            <td><strong>{row['period']}</strong></td>
                            <td style="text-align: right;" class="positive-value">${row['revenue_saved']:,.0f}</td>
                            <td style="text-align: right;" class="negative-value">${row['revenue_lost']:,.0f}</td>
                            <td style="text-align: right;" class="{net_class}">${row['net_revenue']:,.0f}</td>
                            <td style="text-align: right;">{int(row['saves_count'])}</td>
                            <td style="text-align: right;">{row['save_rate']:.1f}%</td>
                        </tr>
"""

        html += """
                    </tbody>
                </table>
            </div>
        </div>

        <!-- BREAKDOWN BY OFFER SECTION -->
        <div id="breakdown-section" class="section-content">
            <div class="summary-box">
                <h3>Revenue by Offer Type</h3>
                <div class="summary-grid">
"""

        # Summary cards for each save type
        for _, row in save_type_revenue.iterrows():
            percentage = (row['revenue'] / total_saved * 100) if total_saved > 0 else 0
            html += f"""
                    <div class="summary-item">
                        <div class="summary-item-label">{row['save_type']}</div>
                        <div class="summary-item-value">${row['revenue']:,.0f}</div>
                        <div class="summary-item-label">{int(row['count'])} saves • {percentage:.1f}%</div>
                    </div>
"""

        html += """
                </div>
            </div>

            <h2 style="margin-bottom: 10px; color: #2d3748;">Detailed Breakdown by Offer Type</h2>
            <table>
                <thead>
                    <tr>
                        <th>Offer Type</th>
                        <th style="text-align: right;">Total Revenue Saved</th>
                        <th style="text-align: right;">Number of Saves</th>
                        <th style="text-align: right;">Average Revenue/Save</th>
                        <th style="text-align: right;">% of Total Revenue</th>
                    </tr>
                </thead>
                <tbody>
"""

        # Detailed breakdown rows
        for _, row in save_type_revenue.iterrows():
            percentage = (row['revenue'] / total_saved * 100) if total_saved > 0 else 0

            html += f"""
                    <tr>
                        <td><strong>{row['save_type']}</strong></td>
                        <td style="text-align: right;" class="positive-value">${row['revenue']:,.0f}</td>
                        <td style="text-align: right;">{int(row['count'])}</td>
                        <td style="text-align: right;">${row['avg_revenue']:,.0f}</td>
                        <td style="text-align: right;">{percentage:.1f}%</td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
        </div>

        <div class="footer">
            Churnkey Revenue Analytics | Updated from latest session data
        </div>
    </div>

    <script>
        function showSection(section) {
            document.querySelectorAll('.section-content').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.section-tab').forEach(t => t.classList.remove('active'));

            document.getElementById(section + '-section').classList.add('active');
            event.target.classList.add('active');
        }

        function showView(section, period) {
            const sectionEl = document.getElementById(section + '-section');
            sectionEl.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            sectionEl.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));

            document.getElementById(section + '-' + period + '-view').classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""

        return html

    def run(self):
        """Run the revenue dashboard generation"""
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║       Churnkey Revenue Impact Dashboard Generator           ║")
        print("╚══════════════════════════════════════════════════════════════╝\n")

        # Fetch data
        all_sessions = self.fetch_sessions()

        if not all_sessions:
            print("❌ No data fetched. Exiting.")
            return

        # Process data
        print("\n📊 Processing revenue data...")
        df = self.process_data(all_sessions)

        if df.empty:
            print("⚠️  No data found")
            return

        print(f"✓ Processed {len(df)} sessions\n")

        # Generate HTML
        print("💰 Generating revenue dashboard...")
        html = self.generate_html(df)

        # Save
        output_path = 'revenue.html'
        with open(output_path, 'w') as f:
            f.write(html)

        print(f"✅ Revenue dashboard saved: {output_path}")
        print(f"🌐 Open it in your browser!")
        print("\n" + "="*60)
        print("✨ Complete!")
        print("="*60)

if __name__ == "__main__":
    dashboard = RevenueDashboard()
    dashboard.run()
