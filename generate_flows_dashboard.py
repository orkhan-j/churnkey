#!/usr/bin/env python3
"""
Generate Cancel Flows & Reactivation Dashboard
Shows two cancel flows separately and combined, plus reactivation rates
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

# Configuration
API_KEY = "live_data_rAjRNH71aZ3rdk7rG1yOqsl6Ir1YFy4a"
APP_ID = "9lv36y492"
BASE_URL = "https://api.churnkey.co/v1/data"

class FlowsDashboard:
    def __init__(self):
        self.headers = {
            "x-ck-api-key": API_KEY,
            "x-ck-app": APP_ID,
            "content-type": "application/json"
        }

        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=180)

        # Top 2 flow IDs (will be determined from data)
        self.flow1_id = None
        self.flow2_id = None

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

    def identify_flows(self, sessions):
        """Identify top 2 cancel flows"""
        from collections import Counter
        flow_counts = Counter(s.get('blueprintId') for s in sessions if s.get('blueprintId'))
        top_flows = flow_counts.most_common(2)

        if len(top_flows) >= 2:
            self.flow1_id = top_flows[0][0]
            self.flow2_id = top_flows[1][0]
            print(f"\n✓ Identified Flow 1: {self.flow1_id} ({top_flows[0][1]} sessions)")
            print(f"✓ Identified Flow 2: {self.flow2_id} ({top_flows[1][1]} sessions)")

        return self.flow1_id, self.flow2_id

    def process_data(self, sessions):
        """Process sessions for flows and reactivation analysis"""
        all_records = []
        customer_sessions = defaultdict(list)

        for session in sessions:
            created_at = pd.to_datetime(session.get('createdAt'))
            blueprint_id = session.get('blueprintId')
            customer_id = session.get('customer', {}).get('id')
            save_type = session.get('saveType')
            canceled = session.get('canceled', False)

            is_accepted = save_type and save_type != 'ABANDON'

            # Determine which flow
            if blueprint_id == self.flow1_id:
                flow = 'Flow 1'
            elif blueprint_id == self.flow2_id:
                flow = 'Flow 2'
            else:
                flow = 'Other'

            all_records.append({
                'date': created_at,
                'customer_id': customer_id,
                'flow': flow,
                'blueprint_id': blueprint_id,
                'accepted': is_accepted,
                'canceled': canceled,
                'save_type': save_type,
            })

            # Track customer sessions for reactivation
            if customer_id:
                customer_sessions[customer_id].append({
                    'date': created_at,
                    'canceled': canceled,
                    'accepted': is_accepted
                })

        df = pd.DataFrame(all_records)

        if not df.empty:
            df['week_label'] = df['date'].dt.strftime('%Y-W%U')
            df['month_label'] = df['date'].dt.strftime('%Y-%m')

        return df, customer_sessions

    def calculate_flow_stats(self, df, period='month', flow_filter=None):
        """Calculate stats for a specific flow or combined"""
        period_col = f'{period}_label'

        # Filter by flow if specified
        if flow_filter:
            df = df[df['flow'] == flow_filter].copy()

        # All sessions
        all_sessions = df.groupby(period_col).size().reset_index(name='total_sessions')

        # Accepted offers
        accepted = df[df['accepted'] == True].groupby(period_col).size().reset_index(name='accepted_count')

        # Canceled
        canceled = df[df['canceled'] == True].groupby(period_col).size().reset_index(name='canceled_count')

        # Merge
        result = all_sessions.merge(accepted, on=period_col, how='left')
        result = result.merge(canceled, on=period_col, how='left')

        result['accepted_count'] = result['accepted_count'].fillna(0).astype(int)
        result['canceled_count'] = result['canceled_count'].fillna(0).astype(int)
        result['acceptance_rate'] = (result['accepted_count'] / result['total_sessions'] * 100).round(1)
        result['cancellation_rate'] = (result['canceled_count'] / result['total_sessions'] * 100).round(1)

        result = result.rename(columns={period_col: 'period'})
        return result.sort_values('period', ascending=False)

    def calculate_reactivation_stats(self, df, customer_sessions, period='month'):
        """Calculate reactivation rates"""
        period_col = f'{period}_label'

        # Get reactivated customers (those with multiple sessions)
        reactivated_customers = {cust_id: sessions for cust_id, sessions in customer_sessions.items() if len(sessions) > 1}

        reactivation_data = []

        for period_val in df[period_col].unique():
            period_start = pd.to_datetime(period_val + '-01') if period == 'month' else None

            # Count unique customers in this period
            period_df = df[df[period_col] == period_val]
            unique_customers = period_df['customer_id'].nunique()

            # Count reactivated customers (those who appeared in this period and had prior sessions)
            reactivated_in_period = 0
            for cust_id in period_df['customer_id'].unique():
                if cust_id in reactivated_customers:
                    cust_sessions = sorted(customer_sessions[cust_id], key=lambda x: x['date'])
                    # Check if this period contains a non-first session
                    for i, sess in enumerate(cust_sessions):
                        if i > 0:  # Not the first session
                            sess_period = pd.to_datetime(sess['date']).strftime(f'%Y-%m' if period == 'month' else '%Y-W%U')
                            if sess_period == period_val:
                                reactivated_in_period += 1
                                break

            reactivation_rate = (reactivated_in_period / unique_customers * 100) if unique_customers > 0 else 0

            reactivation_data.append({
                'period': period_val,
                'unique_customers': unique_customers,
                'reactivated_customers': reactivated_in_period,
                'reactivation_rate': round(reactivation_rate, 1)
            })

        result = pd.DataFrame(reactivation_data)
        return result.sort_values('period', ascending=False)

    def generate_html(self, df, customer_sessions):
        """Generate dashboard HTML"""

        # Calculate all stats
        flow1_weekly = self.calculate_flow_stats(df, 'week', 'Flow 1')
        flow1_monthly = self.calculate_flow_stats(df, 'month', 'Flow 1')
        flow2_weekly = self.calculate_flow_stats(df, 'week', 'Flow 2')
        flow2_monthly = self.calculate_flow_stats(df, 'month', 'Flow 2')
        combined_weekly = self.calculate_flow_stats(df, 'week')
        combined_monthly = self.calculate_flow_stats(df, 'month')

        reactivation_weekly = self.calculate_reactivation_stats(df, customer_sessions, 'week')
        reactivation_monthly = self.calculate_reactivation_stats(df, customer_sessions, 'month')

        # Overall metrics
        flow1_total = len(df[df['flow'] == 'Flow 1'])
        flow2_total = len(df[df['flow'] == 'Flow 2'])
        total_sessions = len(df)
        total_accepted = df['accepted'].sum()
        total_reactivated = len([c for c in customer_sessions.values() if len(c) > 1])
        total_unique_customers = df['customer_id'].nunique()
        overall_reactivation_rate = (total_reactivated / total_unique_customers * 100) if total_unique_customers > 0 else 0

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cancel Flows & Reactivation Dashboard</title>
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
            background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
            color: white;
            padding: 30px;
            border-radius: 8px 8px 0 0;
        }}

        .header h1 {{ font-size: 28px; margin-bottom: 5px; }}
        .header p {{ font-size: 14px; opacity: 0.9; }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            padding: 30px;
            border-bottom: 2px solid #e2e8f0;
        }}

        .metric {{
            text-align: center;
            padding: 15px;
            background: #f7fafc;
            border-radius: 8px;
        }}

        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 5px;
        }}

        .metric-label {{
            font-size: 12px;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }}

        .section-tabs {{
            padding: 20px 30px 0;
            border-bottom: 2px solid #e2e8f0;
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }}

        .section-tab {{
            padding: 12px 20px;
            background: transparent;
            border: none;
            border-bottom: 3px solid transparent;
            color: #718096;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
        }}

        .section-tab.active {{
            color: #4a5568;
            border-bottom-color: #4a5568;
        }}

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
            .section-tabs {{ flex-direction: column; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 Cancel Flows & Reactivation Dashboard</h1>
            <p>Last 6 Months | Updated {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
        </div>

        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{total_sessions:,}</div>
                <div class="metric-label">Total Sessions</div>
            </div>
            <div class="metric">
                <div class="metric-value">{flow1_total:,}</div>
                <div class="metric-label">Flow 1 Sessions</div>
            </div>
            <div class="metric">
                <div class="metric-value">{flow2_total:,}</div>
                <div class="metric-label">Flow 2 Sessions</div>
            </div>
            <div class="metric">
                <div class="metric-value">{total_accepted:,}</div>
                <div class="metric-label">Accepted Offers</div>
            </div>
            <div class="metric">
                <div class="metric-value">{total_reactivated:,}</div>
                <div class="metric-label">Reactivated Customers</div>
            </div>
            <div class="metric">
                <div class="metric-value">{overall_reactivation_rate:.1f}%</div>
                <div class="metric-label">Reactivation Rate</div>
            </div>
        </div>

        <div class="section-tabs">
            <button class="section-tab active" onclick="showSection('flow1')">Flow 1</button>
            <button class="section-tab" onclick="showSection('flow2')">Flow 2</button>
            <button class="section-tab" onclick="showSection('combined')">Combined Flows</button>
            <button class="section-tab" onclick="showSection('reactivation')">Reactivation</button>
        </div>
"""

        # Helper function to generate flow tables
        def generate_flow_table(weekly_stats, monthly_stats, title):
            tables_html = f"""
        <div class="section-content">
            <div class="controls">
                <button class="toggle-btn" onclick="showViewInSection(event, 'weekly')">Weekly View</button>
                <button class="toggle-btn active" onclick="showViewInSection(event, 'monthly')">Monthly View</button>
            </div>

            <div class="content">
                <div class="view">
                    <h2 style="margin-bottom: 10px; color: #2d3748;">{title} - Weekly</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Week</th>
                                <th style="text-align: right;">Sessions</th>
                                <th style="text-align: right;">Accepted</th>
                                <th style="text-align: right;">Canceled</th>
                                <th style="text-align: right;">Acceptance Rate</th>
                                <th style="text-align: right;">Cancellation Rate</th>
                            </tr>
                        </thead>
                        <tbody>
"""
            for _, row in weekly_stats.iterrows():
                acc_rate_class = 'rate-good' if row['acceptance_rate'] >= 40 else 'rate-medium' if row['acceptance_rate'] >= 25 else 'rate-low'
                canc_rate_class = 'rate-low' if row['cancellation_rate'] >= 60 else 'rate-medium' if row['cancellation_rate'] >= 40 else 'rate-good'

                tables_html += f"""
                            <tr>
                                <td><strong>{row['period']}</strong></td>
                                <td style="text-align: right;">{int(row['total_sessions'])}</td>
                                <td style="text-align: right;">{int(row['accepted_count'])}</td>
                                <td style="text-align: right;">{int(row['canceled_count'])}</td>
                                <td style="text-align: right;" class="{acc_rate_class}">{row['acceptance_rate']}%</td>
                                <td style="text-align: right;" class="{canc_rate_class}">{row['cancellation_rate']}%</td>
                            </tr>
"""

            tables_html += """
                        </tbody>
                    </table>
                </div>

                <div class="view active">
                    <h2 style="margin-bottom: 10px; color: #2d3748;">""" + title + """ - Monthly</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Month</th>
                                <th style="text-align: right;">Sessions</th>
                                <th style="text-align: right;">Accepted</th>
                                <th style="text-align: right;">Canceled</th>
                                <th style="text-align: right;">Acceptance Rate</th>
                                <th style="text-align: right;">Cancellation Rate</th>
                            </tr>
                        </thead>
                        <tbody>
"""

            for _, row in monthly_stats.iterrows():
                acc_rate_class = 'rate-good' if row['acceptance_rate'] >= 40 else 'rate-medium' if row['acceptance_rate'] >= 25 else 'rate-low'
                canc_rate_class = 'rate-low' if row['cancellation_rate'] >= 60 else 'rate-medium' if row['cancellation_rate'] >= 40 else 'rate-good'

                tables_html += f"""
                            <tr>
                                <td><strong>{row['period']}</strong></td>
                                <td style="text-align: right;">{int(row['total_sessions'])}</td>
                                <td style="text-align: right;">{int(row['accepted_count'])}</td>
                                <td style="text-align: right;">{int(row['canceled_count'])}</td>
                                <td style="text-align: right;" class="{acc_rate_class}">{row['acceptance_rate']}%</td>
                                <td style="text-align: right;" class="{canc_rate_class}">{row['cancellation_rate']}%</td>
                            </tr>
"""

            tables_html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
"""
            return tables_html

        # Add flow sections
        html += '<div id="flow1-section" class="section-content active">'
        html += generate_flow_table(flow1_weekly, flow1_monthly, "Flow 1")
        html += '</div>'

        html += '<div id="flow2-section" class="section-content">'
        html += generate_flow_table(flow2_weekly, flow2_monthly, "Flow 2")
        html += '</div>'

        html += '<div id="combined-section" class="section-content">'
        html += generate_flow_table(combined_weekly, combined_monthly, "Combined Flows")
        html += '</div>'

        # Reactivation section
        html += """
        <div id="reactivation-section" class="section-content">
            <div class="controls">
                <button class="toggle-btn" onclick="showViewInSection(event, 'weekly')">Weekly View</button>
                <button class="toggle-btn active" onclick="showViewInSection(event, 'monthly')">Monthly View</button>
            </div>

            <div class="content">
                <div class="view">
                    <h2 style="margin-bottom: 10px; color: #2d3748;">Reactivation Rate - Weekly</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Week</th>
                                <th style="text-align: right;">Unique Customers</th>
                                <th style="text-align: right;">Reactivated</th>
                                <th style="text-align: right;">Reactivation Rate</th>
                            </tr>
                        </thead>
                        <tbody>
"""

        for _, row in reactivation_weekly.iterrows():
            rate_class = 'rate-good' if row['reactivation_rate'] >= 15 else 'rate-medium' if row['reactivation_rate'] >= 8 else 'rate-low'
            html += f"""
                            <tr>
                                <td><strong>{row['period']}</strong></td>
                                <td style="text-align: right;">{int(row['unique_customers'])}</td>
                                <td style="text-align: right;">{int(row['reactivated_customers'])}</td>
                                <td style="text-align: right;" class="{rate_class}">{row['reactivation_rate']}%</td>
                            </tr>
"""

        html += """
                        </tbody>
                    </table>
                </div>

                <div class="view active">
                    <h2 style="margin-bottom: 10px; color: #2d3748;">Reactivation Rate - Monthly</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Month</th>
                                <th style="text-align: right;">Unique Customers</th>
                                <th style="text-align: right;">Reactivated</th>
                                <th style="text-align: right;">Reactivation Rate</th>
                            </tr>
                        </thead>
                        <tbody>
"""

        for _, row in reactivation_monthly.iterrows():
            rate_class = 'rate-good' if row['reactivation_rate'] >= 15 else 'rate-medium' if row['reactivation_rate'] >= 8 else 'rate-low'
            html += f"""
                            <tr>
                                <td><strong>{row['period']}</strong></td>
                                <td style="text-align: right;">{int(row['unique_customers'])}</td>
                                <td style="text-align: right;">{int(row['reactivated_customers'])}</td>
                                <td style="text-align: right;" class="{rate_class}">{row['reactivation_rate']}%</td>
                            </tr>
"""

        html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="footer">
            Churnkey Flows & Reactivation Analytics | Updated from latest session data
        </div>
    </div>

    <script>
        function showSection(section) {
            document.querySelectorAll('.section-content').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.section-tab').forEach(t => t.classList.remove('active'));

            document.getElementById(section + '-section').classList.add('active');
            event.target.classList.add('active');
        }

        function showViewInSection(event, viewType) {
            const section = event.target.closest('.section-content');
            section.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            section.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));

            const views = section.querySelectorAll('.view');
            if (viewType === 'weekly') {
                views[0].classList.add('active');
            } else {
                views[1].classList.add('active');
            }
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
        print("║       Cancel Flows & Reactivation Dashboard Generator       ║")
        print("╚══════════════════════════════════════════════════════════════╝\n")

        # Fetch data
        all_sessions = self.fetch_sessions()

        if not all_sessions:
            print("❌ No data fetched. Exiting.")
            return

        # Identify flows
        self.identify_flows(all_sessions)

        # Process data
        print("\n📊 Processing flows and reactivation data...")
        df, customer_sessions = self.process_data(all_sessions)

        if df.empty:
            print("⚠️  No data found")
            return

        print(f"✓ Processed {len(df)} sessions")
        print(f"✓ Found {len(customer_sessions)} unique customers")
        print(f"✓ Found {len([c for c in customer_sessions.values() if len(c) > 1])} reactivated customers\n")

        # Generate HTML
        print("🔄 Generating flows dashboard...")
        html = self.generate_html(df, customer_sessions)

        # Save
        output_path = 'index.html'
        with open(output_path, 'w') as f:
            f.write(html)

        print(f"✅ Dashboard saved: {output_path}")
        print(f"🌐 Open it in your browser!")
        print("\n" + "="*60)
        print("✨ Complete!")
        print("="*60)

if __name__ == "__main__":
    dashboard = FlowsDashboard()
    dashboard.run()
