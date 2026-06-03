import pandas as pd
from database.mongodb_connection import db


def load_filtered_data(region, segment):

    data = list(
        db["sales_data"].find(
            {},
            {"_id": 0}
        )
    )

    df = pd.DataFrame(data)

    if region != "All":
        df = df[df["Region"] == region]

    if segment != "All":
        df = df[df["Segment"] == segment]

    return df