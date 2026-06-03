import pandas as pd

from src.data_ingestion import (
    load_data
)


def sales_by_country():

    df = load_data()

    return (
        df.groupby("Country")["Sales"]
        .sum()
        .reset_index()
    )


def sales_by_city():

    df = load_data()

    return (
        df.groupby("City")["Sales"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
    )