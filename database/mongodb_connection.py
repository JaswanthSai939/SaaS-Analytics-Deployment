from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi
import streamlit as st

load_dotenv()

# Reads from Streamlit secrets on Cloud, .env locally
MONGODB_URI = (
    st.secrets.get("MONGODB_URI")
    or os.getenv("MONGODB_URI")
)

if not MONGODB_URI:
    raise Exception("MONGODB_URI not found in secrets or .env")

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