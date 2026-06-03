import pandas as pd


def customer_metrics(df):

    total_customers = (
        df["Customer ID"]
        .nunique()
    )

    repeat_customers = (
        df.groupby(
            "Customer ID"
        )
        .size()
        .gt(1)
        .sum()
    )

    retention_rate = (
        repeat_customers /
        total_customers
    ) * 100

    return (
        total_customers,
        repeat_customers,
        retention_rate
    )


def top_customers(df):

    return (
        df.groupby(
            "Customer"
        )["Sales"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
    )