"""
Run this once to generate a sample SaaS dataset:
    python generate_dataset.py
Output: data/saas_data.csv
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# ── Config ──────────────────────────────────────────────────────────────────
N_CUSTOMERS   = 500
START_DATE    = datetime(2022, 1, 1)
END_DATE      = datetime(2024, 12, 31)
DATE_RANGE    = (END_DATE - START_DATE).days

PLANS         = ["Free", "Starter", "Pro", "Enterprise"]
PLAN_PRICES   = {"Free": 0, "Starter": 29, "Pro": 99, "Enterprise": 499}
PLAN_WEIGHTS  = [0.30, 0.35, 0.25, 0.10]

REGIONS       = ["AMER", "EMEA", "APJ"]
REGION_WEIGHTS = [0.50, 0.30, 0.20]

INDUSTRIES    = ["SaaS", "E-Commerce", "FinTech", "HealthTech", "EdTech", "Retail"]
IND_WEIGHTS   = [0.25, 0.20, 0.20, 0.15, 0.10, 0.10]

CHURN_RATES   = {"Free": 0.35, "Starter": 0.18, "Pro": 0.10, "Enterprise": 0.04}
UPGRADE_RATES = {"Free": 0.20, "Starter": 0.15, "Pro": 0.08, "Enterprise": 0.00}

# ── Helpers ──────────────────────────────────────────────────────────────────
def rand_date(start, days):
    return start + timedelta(days=random.randint(0, days))

def rand_name():
    firsts = ["Alex","Jordan","Morgan","Taylor","Riley","Casey","Drew","Jamie",
              "Avery","Blake","Quinn","Reese","Cameron","Skylar","Parker"]
    lasts  = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller",
              "Davis","Wilson","Moore","Anderson","Thomas","Jackson","White"]
    return f"{random.choice(firsts)} {random.choice(lasts)}"

def company_name():
    prefixes = ["Nova","Apex","Bright","Cloud","Data","Edge","Fast","Go","Hub",
                "Insight","Jet","Key","Lead","Max","Net","Open","Peak","Quick",
                "Rise","Scale","Tech","Uni","Value","Web","Xcel","Yield","Zen"]
    suffixes = ["io","ly","ify","Hub","Labs","Works","AI","Tech","Base","Suite"]
    return f"{random.choice(prefixes)}{random.choice(suffixes)}"

# ── Generate customers ───────────────────────────────────────────────────────
rows = []

for cid in range(1, N_CUSTOMERS + 1):
    plan       = random.choices(PLANS, PLAN_WEIGHTS)[0]
    region     = random.choices(REGIONS, REGION_WEIGHTS)[0]
    industry   = random.choices(INDUSTRIES, IND_WEIGHTS)[0]
    signup     = rand_date(START_DATE, DATE_RANGE - 60)
    seats      = random.choices([1,2,3,5,10,20,50], [.30,.20,.20,.15,.08,.05,.02])[0]
    mrr        = PLAN_PRICES[plan] * seats
    base_nps   = {"Free":30, "Starter":45, "Pro":60, "Enterprise":72}[plan]
    nps        = int(np.clip(np.random.normal(base_nps, 15), 0, 100))
    logins_pw  = max(0, int(np.random.normal({"Free":2,"Starter":5,"Pro":9,"Enterprise":15}[plan], 3)))

    # Determine if churned
    churned    = random.random() < CHURN_RATES[plan]
    churn_date = None
    tenure_days = (END_DATE - signup).days
    if churned:
        churn_day  = random.randint(30, min(tenure_days, 730))
        churn_date = signup + timedelta(days=churn_day)
        tenure_days = churn_day

    # Determine if upgraded
    upgraded   = (not churned) and (random.random() < UPGRADE_RATES[plan])
    upgrade_date = None
    upgrade_plan = None
    if upgraded:
        plan_idx    = PLANS.index(plan)
        upgrade_plan = PLANS[min(plan_idx + 1, len(PLANS)-1)]
        upgrade_day  = random.randint(30, tenure_days)
        upgrade_date = signup + timedelta(days=upgrade_day)

    # Monthly event rows (one row per month active)
    months_active = max(1, tenure_days // 30)
    for m in range(months_active):
        month_date = signup + timedelta(days=m * 30)
        if month_date > END_DATE:
            break
        current_plan = upgrade_plan if (upgraded and upgrade_date and month_date >= upgrade_date) else plan
        current_mrr  = PLAN_PRICES[current_plan] * seats
        # add noise
        current_mrr  = round(current_mrr * random.uniform(0.95, 1.05), 2)

        rows.append({
            "customer_id":     f"CUST-{cid:04d}",
            "customer_name":   rand_name(),
            "company":         company_name(),
            "region":          region,
            "industry":        industry,
            "plan":            current_plan,
            "seats":           seats,
            "mrr":             current_mrr,
            "signup_date":     signup.strftime("%Y-%m-%d"),
            "month":           month_date.strftime("%Y-%m"),
            "month_date":      month_date.strftime("%Y-%m-%d"),
            "logins_per_week": logins_pw + random.randint(-1, 1),
            "nps_score":       nps,
            "support_tickets": max(0, int(np.random.poisson({"Free":0.5,"Starter":0.8,"Pro":0.6,"Enterprise":1.2}[current_plan]))),
            "churned":         1 if (churned and churn_date and month_date >= churn_date) else 0,
            "churn_date":      churn_date.strftime("%Y-%m-%d") if churned and churn_date else "",
            "upgraded":        1 if upgraded else 0,
            "upgrade_date":    upgrade_date.strftime("%Y-%m-%d") if upgrade_date else "",
            "upgrade_plan":    upgrade_plan if upgraded else "",
            "tenure_days":     tenure_days,
            "arr":             round(current_mrr * 12, 2),
        })

df = pd.DataFrame(rows)

os.makedirs("data", exist_ok=True)
out = "data/saas_data.csv"
df.to_csv(out, index=False)
print(f"✅  Saved {len(df):,} rows → {out}")
print(df.head(3).to_string())