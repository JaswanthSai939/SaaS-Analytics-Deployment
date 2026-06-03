from pymongo import MongoClient
import streamlit as st

client = MongoClient(
    st.secrets["MONGODB_URI"]
)

db = client["saas_analytics"]

users_collection = db["users"]