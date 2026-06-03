from pymongo import MongoClient

client = MongoClient(
    "mongodb://localhost:27017/"
)

db = client["saas_business_analytics"]

users_collection = db["users"]
sales_collection = db["sales_data"]