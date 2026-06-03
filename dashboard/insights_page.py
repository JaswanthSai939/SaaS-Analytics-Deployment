import sys
import os

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT  = os.path.dirname(DASHBOARD_DIR)
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import requests
import json

# ── Hide sidebar ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
</style>""", unsafe_allow_html=True)

# ── Guard ─────────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page(os.path.join(DASHBOARD_DIR, "login_page.py"))

# ── Header ────────────────────────────────────────────────────────────────────
top_left, top_right = st.columns([4, 1])
with top_left:
    st.title("SaaS Insights & Churn Intelligence")
    st.write(f"Hello, **{st.session_state.user_name}**")
with top_right:
    if st.button("← Dashboard", width="stretch"):
        st.switch_page(os.path.join(DASHBOARD_DIR, "dashboard_page.py"))

st.markdown("---")

# ── CSV Upload ────────────────────────────────────────────────────────────────
st.subheader("Upload your SaaS data")
st.caption("Upload a CSV with columns like: customer_id, plan, mrr, churned, signup_date, logins_per_week, nps_score, region, etc. Or use the sample dataset.")

col_up, col_sample = st.columns([3, 1])

with col_up:
    uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

with col_sample:
    sample_path = os.path.join(PROJECT_ROOT, "data", "saas_data.csv")
    if os.path.exists(sample_path):
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Use sample dataset", width="stretch"):
            st.session_state["use_sample"] = True
    else:
        st.caption("Run `generate_dataset.py` to create sample data.")

# ── Load data ─────────────────────────────────────────────────────────────────
df = None

if uploaded:
    df = pd.read_csv(uploaded)
    st.session_state["use_sample"] = False
    st.success(f"Loaded {len(df):,} rows from uploaded file.")
elif st.session_state.get("use_sample") and os.path.exists(sample_path):
    df = pd.read_csv(sample_path)
    st.info(f"Using sample dataset — {len(df):,} rows.")

if df is None:
    st.markdown("""
    **Expected columns:**

    | Column | Description |
    |---|---|
    | `customer_id` | Unique customer ID |
    | `plan` | Subscription plan (Free / Starter / Pro / Enterprise) |
    | `mrr` | Monthly Recurring Revenue |
    | `churned` | 1 = churned, 0 = active |
    | `signup_date` | Date customer signed up |
    | `month_date` | Month of this row |
    | `logins_per_week` | Weekly login frequency |
    | `nps_score` | Net Promoter Score (0–100) |
    | `region` | AMER / EMEA / APJ |
    | `seats` | Number of seats |
    | `support_tickets` | Tickets raised that month |
    """)
    st.stop()

# ── Normalise columns ─────────────────────────────────────────────────────────
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

for col in ["month_date", "signup_date", "churn_date"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Key metrics")

latest_month = df["month_date"].max() if "month_date" in df.columns else None
latest = df[df["month_date"] == latest_month] if latest_month else df

total_customers = df["customer_id"].nunique()
active_customers = latest[latest.get("churned", pd.Series(0, index=latest.index)) == 0]["customer_id"].nunique() if "churned" in df.columns else total_customers
total_mrr  = latest["mrr"].sum() if "mrr" in df.columns else 0
churn_rate = df["churned"].mean() * 100 if "churned" in df.columns else 0
avg_nps    = df["nps_score"].mean() if "nps_score" in df.columns else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Customers",  f"{total_customers:,}")
k2.metric("Active Customers", f"{active_customers:,}")
k3.metric("MRR",              f"${total_mrr:,.0f}")
k4.metric("Churn Rate",       f"{churn_rate:.1f}%")
k5.metric("Avg NPS",          f"{avg_nps:.0f}")

# ── Section selector ──────────────────────────────────────────────────────────
st.markdown("---")
section = st.radio(
    "Explore",
    ["User Growth", "Subscriptions & Revenue", "Retention & Churn", "AI Insights"],
    horizontal=True
)

st.markdown("---")

# ════════════════════════════════════════════
# USER GROWTH
# ════════════════════════════════════════════
if section == "User Growth":

    st.subheader("User growth over time")

    if "signup_date" in df.columns:
        growth = (
            df.drop_duplicates("customer_id")
            .set_index("signup_date")
            .resample("ME")["customer_id"]
            .count()
            .reset_index()
            .rename(columns={"customer_id": "new_customers"})
        )
        growth["cumulative"] = growth["new_customers"].cumsum()

        fig = go.Figure()
        fig.add_bar(x=growth["signup_date"], y=growth["new_customers"], name="New customers", marker_color="#378ADD")
        fig.add_scatter(x=growth["signup_date"], y=growth["cumulative"], name="Cumulative", yaxis="y2", line=dict(color="#1D9E75", width=2))
        fig.update_layout(
            yaxis2=dict(overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=1.1),
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig, width="stretch")

    if "region" in df.columns:
        st.subheader("Customers by region")
        reg = df.drop_duplicates("customer_id").groupby("region")["customer_id"].count().reset_index()
        fig = px.pie(reg, names="region", values="customer_id", hole=0.45)
        st.plotly_chart(fig, width="stretch")

    if "plan" in df.columns:
        st.subheader("Plan distribution")
        plan_dist = df.drop_duplicates("customer_id").groupby("plan")["customer_id"].count().reset_index()
        fig = px.bar(plan_dist, x="plan", y="customer_id", labels={"customer_id": "Customers"},
                     color="plan", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, width="stretch")

    if "industry" in df.columns:
        st.subheader("Customers by industry")
        ind = df.drop_duplicates("customer_id").groupby("industry")["customer_id"].count().sort_values().reset_index()
        fig = px.bar(ind, x="customer_id", y="industry", orientation="h",
                     labels={"customer_id": "Customers"}, color_discrete_sequence=["#534AB7"])
        st.plotly_chart(fig, width="stretch")


# ════════════════════════════════════════════
# SUBSCRIPTIONS & REVENUE
# ════════════════════════════════════════════
elif section == "Subscriptions & Revenue":

    st.subheader("MRR trend")

    if "month_date" in df.columns and "mrr" in df.columns:
        mrr_trend = df.groupby("month_date")["mrr"].sum().reset_index()
        fig = px.area(mrr_trend, x="month_date", y="mrr", labels={"mrr": "MRR ($)"},
                      color_discrete_sequence=["#1D9E75"])
        st.plotly_chart(fig, width="stretch")

    if "plan" in df.columns and "mrr" in df.columns:
        st.subheader("MRR by plan")
        plan_mrr = latest.groupby("plan")["mrr"].sum().reset_index()
        fig = px.pie(plan_mrr, names="plan", values="mrr", hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, width="stretch")

    if "arr" in df.columns:
        st.subheader("ARR by region")
        arr_reg = latest.groupby("region")["arr"].sum().reset_index() if "region" in latest.columns else None
        if arr_reg is not None:
            fig = px.bar(arr_reg, x="region", y="arr", labels={"arr": "ARR ($)"},
                         color="region", color_discrete_sequence=px.colors.qualitative.Set1)
            st.plotly_chart(fig, width="stretch")

    if "upgraded" in df.columns:
        st.subheader("Upgrade activity")
        upgrades = df[df["upgraded"] == 1].groupby("month_date")["customer_id"].count().reset_index()
        if not upgrades.empty:
            fig = px.bar(upgrades, x="month_date", y="customer_id",
                         labels={"customer_id": "Upgrades"}, color_discrete_sequence=["#EF9F27"])
            st.plotly_chart(fig, width="stretch")


# ════════════════════════════════════════════
# RETENTION & CHURN
# ════════════════════════════════════════════
elif section == "Retention & Churn":

    st.subheader("Monthly churn rate")

    if "month_date" in df.columns and "churned" in df.columns:
        churn_monthly = (
            df.groupby("month_date")
            .agg(total=("customer_id", "count"), churned=("churned", "sum"))
            .reset_index()
        )
        churn_monthly["churn_rate_pct"] = churn_monthly["churned"] / churn_monthly["total"] * 100
        fig = px.line(churn_monthly, x="month_date", y="churn_rate_pct",
                      labels={"churn_rate_pct": "Churn rate (%)"},
                      color_discrete_sequence=["#E24B4A"])
        st.plotly_chart(fig, width="stretch")

    if "plan" in df.columns and "churned" in df.columns:
        st.subheader("Churn rate by plan")
        plan_churn = df.groupby("plan")["churned"].mean().reset_index()
        plan_churn["churn_pct"] = plan_churn["churned"] * 100
        fig = px.bar(plan_churn, x="plan", y="churn_pct",
                     labels={"churn_pct": "Churn rate (%)"},
                     color="plan", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, width="stretch")

    # Churn risk table
    st.subheader("Churn risk signals")
    st.caption("Customers with low logins, low NPS, and high tickets are at risk.")

    risk_cols = ["customer_id"]
    for c in ["company", "plan", "mrr", "logins_per_week", "nps_score", "support_tickets"]:
        if c in df.columns:
            risk_cols.append(c)

    risk_df = latest[risk_cols].copy() if all(c in latest.columns for c in ["logins_per_week", "nps_score"]) else latest[risk_cols].copy()

    if "logins_per_week" in risk_df.columns and "nps_score" in risk_df.columns:
        risk_df["risk_score"] = (
            (10 - risk_df["logins_per_week"].clip(0, 10)) * 5 +
            (100 - risk_df["nps_score"]) * 0.3 +
            (risk_df.get("support_tickets", 0) * 2)
        ).round(1)
        risk_df = risk_df.sort_values("risk_score", ascending=False).head(20)
        st.dataframe(risk_df, width="stretch")

    if "logins_per_week" in df.columns and "mrr" in df.columns:
        st.subheader("Logins vs MRR (colour = churned)")
        scatter_df = latest.copy()
        scatter_df["status"] = scatter_df["churned"].map({0: "Active", 1: "Churned"}) if "churned" in scatter_df.columns else "Active"
        fig = px.scatter(scatter_df, x="logins_per_week", y="mrr", color="status",
                         color_discrete_map={"Active": "#1D9E75", "Churned": "#E24B4A"},
                         opacity=0.6, labels={"logins_per_week": "Logins/week", "mrr": "MRR ($)"})
        st.plotly_chart(fig, width="stretch")


# ════════════════════════════════════════════
# AI INSIGHTS
# ════════════════════════════════════════════
elif section == "AI Insights":

    st.subheader("AI-generated business insights")
    st.caption("Claude analyses your data summary and generates strategic recommendations for management.")

    # Build a compact data summary to send to the API
    def build_summary(df):
        lines = []
        lines.append(f"Total rows: {len(df):,}")
        lines.append(f"Unique customers: {df['customer_id'].nunique():,}")

        if "mrr" in df.columns:
            lines.append(f"Total MRR: ${df.groupby('customer_id')['mrr'].last().sum():,.0f}")

        if "churned" in df.columns:
            lines.append(f"Overall churn rate: {df['churned'].mean()*100:.1f}%")

        if "plan" in df.columns:
            plan_dist = df.drop_duplicates("customer_id")["plan"].value_counts().to_dict()
            lines.append(f"Plan distribution: {plan_dist}")

        if "plan" in df.columns and "churned" in df.columns:
            churn_by_plan = (df.groupby("plan")["churned"].mean() * 100).round(1).to_dict()
            lines.append(f"Churn rate by plan: {churn_by_plan}")

        if "region" in df.columns and "mrr" in df.columns:
            mrr_region = df.groupby("region")["mrr"].sum().round(0).to_dict()
            lines.append(f"MRR by region: {mrr_region}")

        if "nps_score" in df.columns:
            lines.append(f"Average NPS: {df['nps_score'].mean():.1f}")

        if "logins_per_week" in df.columns:
            lines.append(f"Avg logins/week: {df['logins_per_week'].mean():.1f}")
            lines.append(f"Churned customers avg logins/week: {df[df.get('churned', pd.Series(0, index=df.index)) == 1]['logins_per_week'].mean():.1f}" if "churned" in df.columns else "")

        if "upgraded" in df.columns:
            lines.append(f"Upgrade rate: {df['upgraded'].mean()*100:.1f}%")

        if "month_date" in df.columns and "mrr" in df.columns:
            monthly = df.groupby("month_date")["mrr"].sum()
            if len(monthly) >= 2:
                growth = ((monthly.iloc[-1] - monthly.iloc[-3]) / monthly.iloc[-3] * 100) if len(monthly) >= 3 else 0
                lines.append(f"MRR 3-month trend: {growth:+.1f}%")

        return "\n".join(l for l in lines if l)

    summary = build_summary(df)

    st.markdown("**Data summary being sent to AI:**")
    with st.expander("View summary"):
        st.text(summary)

    # Prompt selector
    prompt_type = st.selectbox("Choose insight type", [
        "Executive summary & top priorities",
        "Churn reduction strategy",
        "Revenue growth opportunities",
        "Customer retention playbook",
        "Product & pricing recommendations",
    ])

    PROMPT_TEMPLATES = {
        "Executive summary & top priorities": f"""You are a SaaS business analyst. Based on the following data summary, write a concise executive report for the management team covering:
1. Business health overview
2. Top 3 risks
3. Top 3 growth opportunities
4. Immediate action items

Data:
{summary}""",

        "Churn reduction strategy": f"""You are a customer success expert. Based on this SaaS data, provide a detailed churn reduction strategy including:
1. Root causes of churn
2. At-risk customer segments
3. Specific retention tactics (with expected impact)
4. 30/60/90-day action plan

Data:
{summary}""",

        "Revenue growth opportunities": f"""You are a SaaS revenue strategist. Based on this data, identify revenue growth opportunities:
1. Upsell/cross-sell opportunities
2. Pricing optimisation suggestions
3. Expansion revenue tactics
4. Which segments to focus on and why

Data:
{summary}""",

        "Customer retention playbook": f"""You are a customer success leader. Create a retention playbook based on this data:
1. Engagement benchmarks
2. Early warning signals
3. Intervention playbooks by plan tier
4. Success metrics to track

Data:
{summary}""",

        "Product & pricing recommendations": f"""You are a product strategist. Based on this SaaS data, recommend:
1. Plan/pricing adjustments
2. Feature priorities by segment
3. Freemium-to-paid conversion tactics
4. Enterprise expansion strategy

Data:
{summary}""",
    }

    if st.button("Generate insights", type="primary"):
        with st.spinner("Claude is analysing your data..."):
            try:
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": "claude-sonnet-4-20250514",
                        "max_tokens": 1000,
                        "messages": [
                            {
                                "role": "user",
                                "content": PROMPT_TEMPLATES[prompt_type]
                            }
                        ]
                    }
                )
                data = response.json()
                insight = data["content"][0]["text"]
                st.markdown("### AI Insights")
                st.markdown(insight)

                # Download button
                st.download_button(
                    "Download insights as text",
                    data=insight,
                    file_name="saas_insights.txt",
                    mime="text/plain",
                    width="stretch"
                )

            except Exception as e:
                st.error(f"Error calling AI: {e}")
                st.info("Make sure you're running inside Claude.ai artifacts or have the Anthropic API configured.")

    st.markdown("---")
    st.subheader("Quick insight cards")
    st.caption("Instant data-driven observations — no AI required.")

    cards = []

    if "churned" in df.columns and "logins_per_week" in df.columns:
        churned_logins = df[df["churned"]==1]["logins_per_week"].mean()
        active_logins  = df[df["churned"]==0]["logins_per_week"].mean()
        if churned_logins < active_logins:
            cards.append(f"⚠️ **Churn signal:** Churned customers logged in {churned_logins:.1f}x/week vs {active_logins:.1f}x for active customers. Low engagement = churn risk.")

    if "plan" in df.columns and "churned" in df.columns:
        churn_by_plan = df.groupby("plan")["churned"].mean()
        worst_plan    = churn_by_plan.idxmax()
        worst_rate    = churn_by_plan.max() * 100
        cards.append(f"📉 **Highest churn plan:** `{worst_plan}` at {worst_rate:.1f}% churn rate. Consider improving onboarding or value proposition for this tier.")

    if "nps_score" in df.columns:
        avg_nps_val = df["nps_score"].mean()
        if avg_nps_val < 50:
            cards.append(f"😟 **NPS alert:** Average NPS of {avg_nps_val:.0f} is below healthy threshold (50+). Customer satisfaction needs attention.")
        else:
            cards.append(f"😊 **Strong NPS:** Average NPS of {avg_nps_val:.0f} indicates healthy customer satisfaction.")

    if "upgraded" in df.columns:
        upgrade_rate = df["upgraded"].mean() * 100
        cards.append(f"📈 **Upgrade rate:** {upgrade_rate:.1f}% of customers upgraded their plan. {'Strong upsell motion.' if upgrade_rate > 10 else 'Opportunity to improve upsell strategy.'}")

    if "mrr" in df.columns and "month_date" in df.columns:
        monthly_mrr = df.groupby("month_date")["mrr"].sum()
        if len(monthly_mrr) >= 2:
            mom_growth = (monthly_mrr.iloc[-1] - monthly_mrr.iloc[-2]) / monthly_mrr.iloc[-2] * 100
            cards.append(f"{'🟢' if mom_growth > 0 else '🔴'} **MoM MRR growth:** {mom_growth:+.1f}% last month.")

    for card in cards:
        st.info(card)