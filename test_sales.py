# test_sales.py

from database.mongodb_connection import db

print(db.list_collection_names())

print(
    db["sales_data"].count_documents({})
)