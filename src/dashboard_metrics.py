import pandas as pd

from database.mongodb_connection import db


def load_data():

    collection = db["sales_data"]

    data = list(
        collection.find(
            {},
            {"_id": 0}
        )
    )

    return pd.DataFrame(data)


def get_kpis():

    df = load_data()

    total_sales = df["Sales"].sum()

    total_profit = df["Profit"].sum()

    total_orders = len(df)

    total_customers = (
        df["Customer ID"]
        .nunique()
    )

    return (
        total_sales,
        total_profit,
        total_orders,
        total_customers
    )