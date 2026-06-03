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

    df = pd.DataFrame(data)

    df["Order Date"] = pd.to_datetime(
        df["Order Date"]
    )

    return df


def monthly_sales():

    df = load_data()

    result = (
        df.groupby(
            pd.Grouper(
                key="Order Date",
                freq="ME"
            )
        )["Sales"]
        .sum()
        .reset_index()
    )

    return result

def sales_by_category():

    df = load_data()

    result = (
        df.groupby("Segment")["Sales"]
        .sum()
        .reset_index()
    )

    return result


def sales_by_region():

    df = load_data()

    result = (
        df.groupby("Region")["Sales"]
        .sum()
        .reset_index()
    )

    return result


def top_products():

    df = load_data()

    result = (
        df.groupby("Product")["Sales"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    return result


def top_customers():

    df = load_data()

    result = (
        df.groupby("Customer")["Sales"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    return result


def monthly_profit():

    df = load_data()

    result = (
        df.groupby(
            pd.Grouper(
                key="Order Date",
                freq="ME"
            )
        )["Profit"]
        .sum()
        .reset_index()
    )

    return result