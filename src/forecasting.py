import pandas as pd
from prophet import Prophet

from database.mongodb_connection import db


def sales_forecast():

    data = list(
        db["sales_data"].find(
            {},
            {"_id": 0}
        )
    )

    df = pd.DataFrame(data)

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