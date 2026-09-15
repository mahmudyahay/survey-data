"""
Supabase connection + data access helpers.

Expects the following in .streamlit/secrets.toml:

[supabase]
url = "https://YOUR-PROJECT.supabase.co"
key = "YOUR-ANON-OR-SERVICE-KEY"
"""

import streamlit as st
import pandas as pd
from supabase import create_client, Client


TABLE_NAME = "responses"


@st.cache_resource(show_spinner=False)
def get_client() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


def insert_response(record: dict) -> bool:
    """Insert a single survey response. Returns True on success."""
    try:
        client = get_client()
        client.table(TABLE_NAME).insert(record).execute()
        return True
    except Exception as e:
        st.error(f"Could not save your response: {e}")
        return False


def fetch_responses() -> pd.DataFrame:
    """Fetch all survey responses as a DataFrame."""
    try:
        client = get_client()
        result = client.table(TABLE_NAME).select("*").execute()
        data = result.data
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame()