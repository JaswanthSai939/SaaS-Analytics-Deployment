from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise Exception("MONGODB_URI not found in .env")

client = MongoClient(
    MONGODB_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000
)

# Test connection immediately
client.admin.command("ping")

db = client["saas_analytics"]

users_collection = db["users"]

print("MongoDB Connected Successfully!")
print("Loaded URI:", MONGODB_URI[:40])