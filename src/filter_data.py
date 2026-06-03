from src.data_ingestion import load_data


def load_filtered_data(region, segment):

    df = load_data()

    if region != "All":
        df = df[df["Region"] == region]

    if segment != "All":
        df = df[df["Segment"] == segment]

    return df