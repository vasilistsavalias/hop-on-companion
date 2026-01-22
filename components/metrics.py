import streamlit as st
import pandas as pd

def render_metrics(projects_df, orgs_df):
    """
    Renders key metrics (KPIs) for the filtered dataset.
    
    Args:
        projects_df (pd.DataFrame): The filtered projects DataFrame.
        orgs_df (pd.DataFrame): The full organizations DataFrame.
    """
    if projects_df.empty:
        st.warning("No projects match the current filters.")
        return

    # Calculate Metrics
    total_projects = len(projects_df)
    
    # Calculate Total Funding (in Millions)
    total_cost = projects_df['totalCost'].sum()
    total_cost_formatted = f"€{total_cost / 1_000_000:.1f}M"
    
    # Calculate Unique Organizations participating in these projects
    # Filter orgs to only those involved in the visible projects
    relevant_orgs = orgs_df[orgs_df['projectID'].isin(projects_df['id'])]
    unique_orgs = relevant_orgs['name'].nunique()

    # Display Metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total Projects", value=total_projects)
    
    with col2:
        st.metric(label="Total Funding Available", value=total_cost_formatted)
        
    with col3:
        st.metric(label="Participating Orgs", value=unique_orgs)

    st.markdown("---")
