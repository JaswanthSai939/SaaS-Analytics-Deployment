import pandas as pd
from prophet import Prophet

from src.data_ingestion import load_data


def sales_forecast():

    df = load_data()

    df["Order Date"] = pd.to_datetime(
        df["Order Date"]
    )

    monthly_df = (
        df.groupby(
            pd.Grouper(
                key="Order Date",
                freq="ME"
            )
        )["Sales"]
        .sum()
        .reset_index()
    )

    monthly_df.columns = [
        "ds",
        "y"
    ]

    model = Prophet(
        yearly_seasonality=True
    )

    model.fit(
        monthly_df
    )

    future = model.make_future_dataframe(
        periods=12,
        freq="ME"
    )

    forecast = model.predict(
        future
    )

    return forecast