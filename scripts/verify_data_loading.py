from utils.data_loader import load_projects
import pandas as pd

# Mock streamlit cache to avoid errors outside streamlit
import streamlit as st
st.cache_data = lambda func: func

try:
    df = load_projects()
    print("Columns:", df.columns.tolist())
    if 'totalCost' in df.columns:
        print("totalCost Type:", df['totalCost'].dtype)
        print("Sample values:", df['totalCost'].head(5).tolist())
        
        # Try summing
        try:
            total = df['totalCost'].sum()
            print("Sum success:", total)
        except Exception as e:
            print("Sum failed:", e)
    else:
        print("totalCost MISSING")

except Exception as e:
    print("Loader failed:", e)
