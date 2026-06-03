# SaaS Business Analytics & Prediction Platform

A full-stack business intelligence web application built with **Streamlit**, **MongoDB** for persistent data storage, and **Claude AI** for natural language business insights. Designed for SaaS teams to monitor KPIs, analyse customer behaviour, predict churn, and generate executive-level recommendations — all from a single dashboard.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Authentication](#authentication)
- [Dashboard](#dashboard)
- [AI Insights](#ai-insights)
- [Dataset](#dataset)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Environment Variables](#environment-variables)
- [Requirements](#requirements)

---

## Overview

This platform was built to give SaaS businesses a single place to answer the questions that matter most to management:

- How is revenue trending month over month?
- Which customers are at risk of churning?
- Which products and regions drive the most profit?
- What should we do next — and why?

The app combines traditional data visualisation with AI-generated strategic recommendations, making it useful for both analysts and executives.

---

## Project Structure

```
saas-business-analytics/
│
├── auth/                           # Authentication module
│   ├── __init__.py
│   ├── __pycache__/
│   ├── google_auth.py              # Google OAuth2 sign-in integration
│   ├── login.py                    # Email/password credential verification
│   ├── password_utils.py           # Password hashing and validation utilities
│   ├── register.py                 # New user registration logic
│   └── session_manager.py          # Streamlit session state initialisation and logout
│
├── dashboard/                      # Streamlit multi-page application
│   ├── __init__.py
│   ├── app.py                      # Entry point — page router and navigation
│   ├── dashboard_page.py           # Main analytics dashboard
│   ├── insights_page.py            # AI-powered SaaS insights and CSV upload
│   ├── login_page.py               # Login page (email/password + Google OAuth)
│   └── register_page.py            # User registration page
│
├── data/                           # Data directory
│   ├── generate_dataset.py         # Script to generate synthetic SaaS dataset
│   ├── saas_data.csv               # Generated sample SaaS dataset (500 customers)
│   └── SaaS-Sales.csv              # Real SaaS sales data used by the main dashboard
│
├── database/                       # Database module
│   ├── __pycache__/
│   ├── __init__.py
│   └── mongodb_connection.py       # MongoDB connection and user collection management
│
├── src/                            # Core analytics and data processing modules
│   ├── __pycache__/
│   ├── __init__.py
│   ├── customer_analysis.py        # Customer metrics, repeat customers, retention rate
│   ├── dashboard_charts.py         # Reusable Streamlit chart helper functions
│   ├── dashboard_metrics.py        # KPI calculations (MRR, ARR, sales, profit)
│   ├── data_ingestion.py           # Data loading and preprocessing pipeline
│   ├── discount_analysis.py        # Discount impact analysis on revenue and profit
│   ├── filter_data.py              # Region and segment filtering logic
│   ├── forecasting.py              # Prophet-based time-series sales forecasting
│   ├── geographic_analysis.py      # Country and city level sales aggregation
│   └── product_analysis.py         # Product performance and discount analytics
│
├── .streamlit/                     # Streamlit configuration
│   └── secrets.toml                # API keys and OAuth credentials (not committed to git)
│
├── venv/                           # Python virtual environment
├── .env                            # Environment variables file
├── requirements.txt                # Python package dependencies
└── README.md                       # Project documentation
```

---

## Tech Stack

| Layer | Technology | Used In | Purpose |
|---|---|---|---|
| **Frontend / UI** | [Streamlit](https://streamlit.io) | All `dashboard/` pages | Web application framework — pages, charts, forms, navigation |
| **Data manipulation** | [Pandas](https://pandas.pydata.org) | All `src/` modules | Loading, filtering, grouping, and transforming datasets |
| **Visualisation** | [Plotly Express](https://plotly.com/python/plotly-express/) | `dashboard_page.py`, `insights_page.py` | Interactive charts — line, bar, scatter, histogram, choropleth, pie |
| **Forecasting** | [Prophet](https://facebook.github.io/prophet/) | `src/forecasting.py` | Time-series sales forecasting with confidence intervals |
| **AI Insights** | [Anthropic Claude API](https://www.anthropic.com) | `insights_page.py` | Natural language business insights and strategic recommendations |
| **Database** | [MongoDB](https://www.mongodb.com) | `database/mongodb_connection.py` | Persistent user account storage for authentication |
| **Authentication** | Custom + [Streamlit OAuth](https://github.com/dnl-blkv/streamlit-oauth) | `auth/` module | Email/password login, registration, Google OAuth2 sign-in |
| **Password Security** | bcrypt / hashlib | `auth/password_utils.py` | Secure password hashing and verification |
| **Dataset Generation** | NumPy + Pandas | `data/generate_dataset.py` | Synthetic SaaS customer data with realistic churn, MRR, NPS, upgrades |
| **Configuration** | python-dotenv | `.env`, `secrets.toml` | Managing API keys and environment-specific configuration |

---

## Features

### Authentication

Located in the `auth/` module, the authentication system provides:

- **Email and password** login and registration via `auth/login.py` and `auth/register.py`
- **Password security** via `auth/password_utils.py` — passwords are hashed before being stored in MongoDB; plain-text passwords are never saved
- **Google OAuth2** single sign-on via `auth/google_auth.py` — users can sign in with their Google account in one click using the Streamlit OAuth library
- **Session management** via `auth/session_manager.py` — initialises and maintains `st.session_state` fields (`logged_in`, `user_name`, `user_email`, `user_picture`) across all pages
- **MongoDB persistence** via `database/mongodb_connection.py` — all registered user accounts are stored in a MongoDB collection, enabling persistent login across sessions
- Separate, sidebar-free pages for Login (`login_page.py`) and Register (`register_page.py`) with navigation between them using `st.switch_page`

---

### Dashboard

The main dashboard (`dashboard/dashboard_page.py`) loads data from `data/SaaS-Sales.csv` via `src/filter_data.py` and is divided into the following sections:

#### Filters
Inline region and segment selectors (no sidebar) that instantly re-filter all charts and metrics on the page. A **Download Report** button exports the filtered dataset as a CSV file.

#### KPI Metrics
Four top-level metrics computed via `src/dashboard_metrics.py`:

| Metric | Description |
|---|---|
| Total Sales | Sum of all sales values in the filtered dataset |
| Total Profit | Sum of all profit values |
| Total Orders | Total number of order rows |
| Total Customers | Count of unique customer IDs |

#### Customer Analytics
Computed via `src/customer_analysis.py`:
- Total customers, repeat customers, and percentage retention rate
- Top 10 customers by sales — bar chart

#### Sales Forecast
Powered by **Prophet** via `src/forecasting.py`:
- Trains a time-series model on historical order data
- Displays the predicted future sales figure
- Line chart showing `yhat` (forecast), `yhat_lower` and `yhat_upper` (confidence bands)

#### Monthly Sales and Profit Trends
- Monthly aggregation using Pandas `.resample("ME")`
- Separate line charts for sales and profit trends over time

#### Sales by Segment and Region
- Bar charts breaking down sales by business segment (Enterprise, SMB, Strategic)
- Bar charts breaking down sales by region (AMER, APJ, EMEA)

#### Geographic Analytics
Powered by `src/geographic_analysis.py`:
- **World choropleth map** — colour intensity represents total sales per country
- **Top cities table** — dataframe of cities ranked by sales volume

#### Product Analytics
Powered by `src/product_analysis.py`:
- Top selling and lowest selling products
- Most profitable products
- Most discounted products
- Top 10 products by sales from the filtered dataset

#### Discount Analytics
Powered by `src/discount_analysis.py`:
- Average discount rate and its Pearson correlation with profit
- Discount distribution histogram
- Discount vs profit scatter plot
- High discount risk products — products with average discount above 20% and total profit below $1,000
- Bar chart of the most discounted products

#### Executive Insights and Recommendations
Rule-based intelligence computed directly from the filtered data:
- Best performing region and most profitable product
- Highest revenue growth month
- At-risk products table
- Contextual text recommendations based on computed thresholds (e.g. loyalty programme suggestion when retention drops below 70%, discount policy review when average discount exceeds 20%)

---

### AI Insights

The Insights page (`dashboard/insights_page.py`) provides two modes of analysis.

#### CSV Upload
Users can upload any SaaS CSV file with columns such as `customer_id`, `plan`, `mrr`, `churned`, `signup_date`, `logins_per_week`, `nps_score`, `region`, and `seats`. The page normalises column names automatically and handles missing columns gracefully.

Alternatively, users can load the built-in sample dataset (`data/saas_data.csv`) with a single click.

#### Four Analysis Sections

**User Growth**
- Monthly new vs cumulative customers — dual-axis bar and line chart
- Customer distribution by region — donut chart
- Plan distribution — bar chart
- Customers by industry — horizontal bar chart

**Subscriptions and Revenue**
- MRR trend — area chart over time
- MRR breakdown by plan — donut chart
- ARR by region — bar chart
- Monthly upgrade activity — bar chart

**Retention and Churn**
- Monthly churn rate trend — line chart
- Churn rate by plan — bar chart
- Top 20 at-risk customers table — ranked by a composite risk score derived from login frequency, NPS score, and support ticket volume
- Logins vs MRR scatter plot — coloured by churn status (Active / Churned)

**AI Insights (Claude API)**

A compact statistical summary of the uploaded data (no raw customer PII) is sent to the Claude API. Users select one of five management-focused prompt types:

| Prompt Type | What Claude Generates |
|---|---|
| Executive summary & top priorities | Business health overview, top 3 risks, top 3 opportunities, immediate action items |
| Churn reduction strategy | Root causes of churn, at-risk segments, specific retention tactics, 30/60/90-day action plan |
| Revenue growth opportunities | Upsell and cross-sell tactics, pricing optimisation, expansion revenue strategy |
| Customer retention playbook | Engagement benchmarks, early warning signals, per-tier intervention playbooks |
| Product & pricing recommendations | Plan adjustments, feature priorities, freemium conversion tactics, enterprise expansion |

The generated report can be downloaded as a plain text file. A set of **Quick Insight Cards** also provides instant, rule-based observations without requiring an API call — covering churn signals, worst-performing plan, NPS health, upgrade rate, and month-over-month MRR growth.

---

## Dataset

### SaaS-Sales.csv
The primary dataset powering the main dashboard. Contains historical order-level records with fields for Sales, Profit, Discount, Customer, Segment, Region, Product, and Order Date. Loaded and filtered via `src/filter_data.py`.

### saas_data.csv (Generated)
Generated by running `data/generate_dataset.py`. Produces approximately 10,000+ rows representing 500 synthetic customers across 3 years (2022–2024).

**Columns:**

| Column | Description |
|---|---|
| `customer_id` | Unique customer identifier |
| `customer_name` | Randomly generated full name |
| `company` | Randomly generated company name |
| `region` | AMER / EMEA / APJ |
| `industry` | SaaS / E-Commerce / FinTech / HealthTech / EdTech / Retail |
| `plan` | Free / Starter / Pro / Enterprise |
| `seats` | Number of licensed seats |
| `mrr` | Monthly Recurring Revenue with realistic noise |
| `arr` | Annual Recurring Revenue |
| `signup_date` | Customer acquisition date |
| `month` | Year-month string for the row |
| `month_date` | Full date for the monthly row |
| `logins_per_week` | Simulated weekly engagement metric |
| `nps_score` | Net Promoter Score (0–100) |
| `support_tickets` | Support tickets raised that month |
| `churned` | 1 = churned, 0 = active |
| `churn_date` | Date of churn (if applicable) |
| `upgraded` | 1 = upgraded plan, 0 = no upgrade |
| `upgrade_date` | Date of upgrade (if applicable) |
| `upgrade_plan` | Plan upgraded to |
| `tenure_days` | Total days since signup |

Churn rates, upgrade rates, NPS distributions, and login frequencies are calibrated per plan tier to produce realistic business patterns.

---

## Installation

**Prerequisites:** Python 3.9 or higher, MongoDB running locally or a MongoDB Atlas connection string.

```bash
# 1. Clone the repository
git clone https://github.com/your-username/saas-business-analytics.git
cd saas-business-analytics

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate the sample dataset (optional)
python data/generate_dataset.py
```

---

## Running the App

```bash
streamlit run dashboard/app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Environment Variables

Create a `.streamlit/secrets.toml` file in the project root for all credentials:

```toml
[google_oauth]
client_id     = "your-google-client-id"
client_secret = "your-google-client-secret"
redirect_uri  = "http://localhost:8501"

[mongodb]
uri = "mongodb://localhost:27017"
db  = "saas_analytics"

[anthropic]
api_key = "your-anthropic-api-key"
```

You can also use a `.env` file for local development:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=saas_analytics
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

> **Note:** Never commit `.env` or `secrets.toml` to version control. Add both to your `.gitignore`.

---

## Requirements

Key packages (add to `requirements.txt`):

```
streamlit
pandas
numpy
plotly
prophet
cmdstanpy
requests
pymongo
bcrypt
python-dotenv
streamlit-oauth
```

---
