import pandas as pd
from src.data_ingestion import load_data


def top_products():

    df = load_data()

    return (
        df.groupby("Product")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )


def bottom_products():

    df = load_data()

    return (
        df.groupby("Product")["Sales"]
        .sum()
        .sort_values(ascending=True)
        .head(10)
        .reset_index()
    )


def product_profit():

    df = load_data()

    return (
        df.groupby("Product")["Profit"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )


def product_discount():

    df = load_data()

    return (
        df.groupby("Product")["Discount"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )