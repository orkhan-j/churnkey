#!/usr/bin/env python3
"""
Generate Comprehensive Dashboard for Churnkey Offers and Cancellations
Shows acceptance rates and cancellation reasons with week/month toggle
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os

# Configuration
API_KEY = "live_data_rAjRNH71aZ3rdk7rG1yOqsl6Ir1YFy4a"
APP_ID = "9lv36y492"
BASE_URL = "https://api.churnkey.co/v1/data"

class ComprehensiveDashboard:
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
        """Process sessions for analysis"""
        all_records = []

        for session in sessions:
            created_at = pd.to_datetime(session.get('createdAt'))
            save_type = session.get('saveType')
            canceled = session.get('canceled', False)

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
            df['week_label'] = df['date'].dt.strftime('%Y-W%U')
            df['month_label'] = df['date'].dt.strftime('%Y-%m')
            df['revenue_saved'] = df['plan_price'] / 100

        return df

    def calculate_period_stats(self, df, period='week'):
        """Calculate acceptance stats for a period"""
        period_col = f'{period}_label'
        df_accepted = df[df['accepted'] == True].copy()

        # All sessions
        all_sessions = df.groupby(period_col).size().reset_index(name='total_count')
        accepted = df_accepted.groupby(period_col).size().reset_index(name='accepted_count')
        revenue = df_accepted.groupby(period_col)['revenue_saved'].sum().reset_index(name='revenue_saved')

        # Offer types
        offer_types_data = []
        for period_val in df[period_col].unique():
            period_data = df[(df[period_col] == period_val) & (df['accepted'] == True)]
            offer_types = period_data['offer_type'].value_counts().to_dict() if not period_data.empty else {}
            offer_types_data.append({period_col: period_val, 'offer_types': offer_types})

        offers_df = pd.DataFrame(offer_types_data)

        # Merge
        result = all_sessions.merge(accepted, on=period_col, how='left')
        result = result.merge(revenue, on=period_col, how='left')
        result = result.merge(offers_df, on=period_col, how='left')

        result['accepted_count'] = result['accepted_count'].fillna(0).astype(int)
        result['revenue_saved'] = result['revenue_saved'].fillna(0)
        result['acceptance_rate'] = (result['accepted_count'] / result['total_count'] * 100).round(1)

        result = result.rename(columns={period_col: 'period'})
        return result.sort_values('period', ascending=False)

    def calculate_cancellation_stats(self, df, period='week'):
        """Calculate cancellation stats for a period"""
        period_col = f'{period}_label'
        df_canceled = df[df['canceled'] == True].copy()

        # All sessions
        all_sessions = df.groupby(period_col).size().reset_index(name='total_count')
        canceled = df_canceled.groupby(period_col).size().reset_index(name='canceled_count')

        # Cancellation reasons
        reason_data = []
        for period_val in df[period_col].unique():
            period_data = df[(df[period_col] == period_val) & (df['canceled'] == True)]
            reasons = period_data['cancellation_reason'].value_counts().to_dict() if not period_data.empty else {}
            reason_data.append({period_col: period_val, 'reasons': reasons})

        reasons_df = pd.DataFrame(reason_data)

        # Merge
        result = all_sessions.merge(canceled, on=period_col, how='left')
        result = result.merge(reasons_df, on=period_col, how='left')

        result['canceled_count'] = result['canceled_count'].fillna(0).astype(int)
        result['cancellation_rate'] = (result['canceled_count'] / result['total_count'] * 100).round(1)

        result = result.rename(columns={period_col: 'period'})
        return result.sort_values('period', ascending=False)

    def generate_html(self, df):
        """Generate comprehensive HTML dashboard"""

        # Calculate all stats
        weekly_accepted = self.calculate_period_stats(df, 'week')
        monthly_accepted = self.calculate_period_stats(df, 'month')
        weekly_canceled = self.calculate_cancellation_stats(df, 'week')
        monthly_canceled = self.calculate_cancellation_stats(df, 'month')

        # Overall metrics
        total_sessions = len(df)
        total_accepted = df['accepted'].sum()
        total_canceled = df['canceled'].sum()
        overall_acceptance_rate = (total_accepted / total_sessions * 100) if total_sessions > 0 else 0
        overall_cancellation_rate = (total_canceled / total_sessions * 100) if total_sessions > 0 else 0
        total_revenue = df[df['accepted'] == True]['revenue_saved'].sum()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Churnkey Dashboard</title>
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
            background: #4a5568;
            color: white;
            padding: 30px;
            border-radius: 8px 8px 0 0;
        }}

        .header h1 {{ font-size: 24px; margin-bottom: 5px; }}
        .header p {{ font-size: 14px; opacity: 0.9; }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            border-bottom: 1px solid #e2e8f0;
        }}

        .metric {{ text-align: center; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #2d3748; margin-bottom: 5px; }}
        .metric-label {{ font-size: 13px; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; }}

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
            color: #4a5568;
            border-bottom-color: #4a5568;
        }}

        .section-tab:hover {{ color: #2d3748; }}

        .section-content {{ display: none; }}
        .section-content.active {{ display: block; }}

        .controls {{
            padding: 20px 30px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            gap: 10px;
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

        .toggle-btn.active {{ background: #4a5568; color: white; }}
        .toggle-btn:hover {{ background: #2d3748; color: white; border-color: #2d3748; }}

        .content {{ padding: 30px; }}
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

        .rate-good {{ color: #38a169; font-weight: 600; }}
        .rate-medium {{ color: #d69e2e; font-weight: 600; }}
        .rate-low {{ color: #e53e3e; font-weight: 600; }}

        .details {{ font-size: 12px; color: #718096; }}

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
            .controls {{ flex-direction: column; }}
            table {{ font-size: 12px; }}
            th, td {{ padding: 8px; }}
            .section-tabs {{ flex-wrap: wrap; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Churnkey Dashboard</h1>
            <p>Last 6 Months | Updated {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
        </div>

        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{total_sessions:,}</div>
                <div class="metric-label">Total Sessions</div>
            </div>
            <div class="metric">
                <div class="metric-value">{total_accepted:,}</div>
                <div class="metric-label">Accepted Offers</div>
            </div>
            <div class="metric">
                <div class="metric-value">{overall_acceptance_rate:.1f}%</div>
                <div class="metric-label">Acceptance Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value">{total_canceled:,}</div>
                <div class="metric-label">Canceled</div>
            </div>
            <div class="metric">
                <div class="metric-value">${total_revenue:,.0f}</div>
                <div class="metric-label">Revenue Saved</div>
            </div>
        </div>

        <div class="section-tabs">
            <button class="section-tab active" onclick="showSection('accepted')">Accepted Offers</button>
            <button class="section-tab" onclick="showSection('canceled')">Canceled Sessions</button>
        </div>

        <!-- ACCEPTED OFFERS SECTION -->
        <div id="accepted-section" class="section-content active">
            <div class="controls">
                <button class="toggle-btn" onclick="showView('accepted', 'weekly')">Weekly View</button>
                <button class="toggle-btn active" onclick="showView('accepted', 'monthly')">Monthly View</button>
            </div>

            <div class="content">
                <div id="accepted-weekly-view" class="view">
                    <h2 style="margin-bottom: 10px; color: #2d3748;">Weekly Acceptance Rates</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Week</th>
                                <th style="text-align: right;">Accepted</th>
                                <th style="text-align: right;">Total</th>
                                <th style="text-align: right;">Rate</th>
                                <th style="text-align: right;">Revenue</th>
                                <th>Offer Types</th>
                            </tr>
                        </thead>
                        <tbody>
"""

        # Add weekly accepted rows
        for _, row in weekly_accepted.iterrows():
            rate_class = 'rate-good' if row['acceptance_rate'] >= 40 else 'rate-medium' if row['acceptance_rate'] >= 25 else 'rate-low'
            offer_types_str = ', '.join([f"{k}: {v}" for k, v in row['offer_types'].items()]) if row['offer_types'] else '-'

            html += f"""
                            <tr>
                                <td><strong>{row['period']}</strong></td>
                                <td style="text-align: right;">{int(row['accepted_count'])}</td>
                                <td style="text-align: right;">{int(row['total_count'])}</td>
                                <td style="text-align: right;" class="{rate_class}">{row['acceptance_rate']}%</td>
                                <td style="text-align: right;">${row['revenue_saved']:,.0f}</td>
                                <td class="details">{offer_types_str}</td>
                            </tr>
"""

        html += """
                        </tbody>
                    </table>
                </div>

                <div id="accepted-monthly-view" class="view active">
                    <h2 style="margin-bottom: 10px; color: #2d3748;">Monthly Acceptance Rates</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Month</th>
                                <th style="text-align: right;">Accepted</th>
                                <th style="text-align: right;">Total</th>
                                <th style="text-align: right;">Rate</th>
                                <th style="text-align: right;">Revenue</th>
                                <th>Offer Types</th>
                            </tr>
                        </thead>
                        <tbody>
"""

        # Add monthly accepted rows
        for _, row in monthly_accepted.iterrows():
            rate_class = 'rate-good' if row['acceptance_rate'] >= 40 else 'rate-medium' if row['acceptance_rate'] >= 25 else 'rate-low'
            offer_types_str = ', '.join([f"{k}: {v}" for k, v in row['offer_types'].items()]) if row['offer_types'] else '-'

            html += f"""
                            <tr>
                                <td><strong>{row['period']}</strong></td>
                                <td style="text-align: right;">{int(row['accepted_count'])}</td>
                                <td style="text-align: right;">{int(row['total_count'])}</td>
                                <td style="text-align: right;" class="{rate_class}">{row['acceptance_rate']}%</td>
                                <td style="text-align: right;">${row['revenue_saved']:,.0f}</td>
                                <td class="details">{offer_types_str}</td>
                            </tr>
"""

        html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- CANCELED SESSIONS SECTION -->
        <div id="canceled-section" class="section-content">
            <div class="controls">
                <button class="toggle-btn" onclick="showView('canceled', 'weekly')">Weekly View</button>
                <button class="toggle-btn active" onclick="showView('canceled', 'monthly')">Monthly View</button>
            </div>

            <div class="content">
                <div id="canceled-weekly-view" class="view">
                    <h2 style="margin-bottom: 10px; color: #2d3748;">Weekly Cancellation Rates</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Week</th>
                                <th style="text-align: right;">Canceled</th>
                                <th style="text-align: right;">Total</th>
                                <th style="text-align: right;">Rate</th>
                                <th>Top Cancellation Reasons</th>
                            </tr>
                        </thead>
                        <tbody>
"""

        # Add weekly canceled rows
        for _, row in weekly_canceled.iterrows():
            rate_class = 'rate-low' if row['cancellation_rate'] >= 60 else 'rate-medium' if row['cancellation_rate'] >= 40 else 'rate-good'
            reasons_str = ', '.join([f"{k}: {v}" for k, v in sorted(row['reasons'].items(), key=lambda x: x[1], reverse=True)[:3]]) if row['reasons'] else '-'

            html += f"""
                            <tr>
                                <td><strong>{row['period']}</strong></td>
                                <td style="text-align: right;">{int(row['canceled_count'])}</td>
                                <td style="text-align: right;">{int(row['total_count'])}</td>
                                <td style="text-align: right;" class="{rate_class}">{row['cancellation_rate']}%</td>
                                <td class="details">{reasons_str}</td>
                            </tr>
"""

        html += """
                        </tbody>
                    </table>
                </div>

                <div id="canceled-monthly-view" class="view active">
                    <h2 style="margin-bottom: 10px; color: #2d3748;">Monthly Cancellation Rates</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Month</th>
                                <th style="text-align: right;">Canceled</th>
                                <th style="text-align: right;">Total</th>
                                <th style="text-align: right;">Rate</th>
                                <th>Top Cancellation Reasons</th>
                            </tr>
                        </thead>
                        <tbody>
"""

        # Add monthly canceled rows
        for _, row in monthly_canceled.iterrows():
            rate_class = 'rate-low' if row['cancellation_rate'] >= 60 else 'rate-medium' if row['cancellation_rate'] >= 40 else 'rate-good'
            reasons_str = ', '.join([f"{k}: {v}" for k, v in sorted(row['reasons'].items(), key=lambda x: x[1], reverse=True)[:3]]) if row['reasons'] else '-'

            html += f"""
                            <tr>
                                <td><strong>{row['period']}</strong></td>
                                <td style="text-align: right;">{int(row['canceled_count'])}</td>
                                <td style="text-align: right;">{int(row['total_count'])}</td>
                                <td style="text-align: right;" class="{rate_class}">{row['cancellation_rate']}%</td>
                                <td class="details">{reasons_str}</td>
                            </tr>
"""

        html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="footer">
            Churnkey Analytics | Data from Churnkey API
        </div>
    </div>

    <script>
        function showSection(section) {
            // Hide all sections
            document.querySelectorAll('.section-content').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.section-tab').forEach(t => t.classList.remove('active'));

            // Show selected section
            document.getElementById(section + '-section').classList.add('active');
            event.target.classList.add('active');
        }

        function showView(section, period) {
            // Hide all views in this section
            const sectionEl = document.getElementById(section + '-section');
            sectionEl.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            sectionEl.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));

            // Show selected view
            document.getElementById(section + '-' + period + '-view').classList.add('active');
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
        print("║       Churnkey Comprehensive Dashboard Generator            ║")
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
    dashboard = ComprehensiveDashboard()
    dashboard.run()
