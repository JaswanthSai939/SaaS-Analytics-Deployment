import pandas as pd
from src.data_ingestion import load_data


def average_discount():

    df = load_data()

    return round(
        df["Discount"].mean() * 100,
        2
    )


def discount_profit_correlation():

    df = load_data()

    return round(
        df["Discount"].corr(df["Profit"]),
        4
    )


def discount_distribution():

    df = load_data()

    return df["Discount"]


def high_discount_risk_products():

    df = load_data()

    return (
        df.groupby("Product")
        .agg({
            "Discount": "mean",
            "Profit": "sum"
        })
        .reset_index()
        .sort_values(
            by="Discount",
            ascending=False
        )
        .head(10)
    )