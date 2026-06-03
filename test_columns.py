# test_columns.py

from src.data_ingestion import load_data

df = load_data()

print(df.columns.tolist())