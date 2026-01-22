import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

@st.cache_data
def get_cluster_chart(projects_df):
    if 'cluster' in projects_df.columns:
        cluster_counts = projects_df['cluster'].value_counts().reset_index()
        cluster_counts.columns = ['Cluster', 'Count']
        
        return alt.Chart(cluster_counts).mark_bar().encode(
            x=alt.X('Count', title='Number of Projects', axis=alt.Axis(tickMinStep=1)),
            y=alt.Y('Cluster', sort='-x', title=None),
            tooltip=['Cluster', 'Count']
        ).properties(height=300)
    return None

@st.cache_data
def get_funding_chart_data(projects_df):
    # Returns data for st.bar_chart (which doesn't return an object we can easily cache-and-render the same way)
    if 'cluster' in projects_df.columns and 'totalCost' in projects_df.columns:
        funding_data = projects_df.groupby('cluster')['totalCost'].sum().reset_index()
        funding_data.columns = ['Cluster', 'TotalFunding']
        funding_data['TotalFunding'] = funding_data['TotalFunding'].astype(float)
        return funding_data.set_index('Cluster')['TotalFunding']
    return None

def render_charts(projects_df):
    """
    Renders interactive charts for the dashboard.
    """
    if projects_df.empty:
        return

    st.subheader("Visual Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### Projects by Cluster")
        chart = get_cluster_chart(projects_df)
        if chart:
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Cluster data not available.")

    with col2:
        st.write("#### Funding Distribution")
        chart_data = get_funding_chart_data(projects_df)
        if chart_data is not None:
            st.bar_chart(chart_data, color="#FFA500", horizontal=True)
        else:
            st.info("Funding data not available.")
            
    st.markdown("---")

@st.cache_data
def get_coordinator_chart(projects_df, orgs_df):
    # Filter orgs to only those involved in the visible projects
    relevant_orgs = orgs_df[orgs_df['projectID'].isin(projects_df['id'])]
    
    # Filter for Coordinators only
    coordinators = relevant_orgs[relevant_orgs['role'].str.contains('coordinator', case=False, na=False)]
    
    if coordinators.empty:
        return None

    # Count projects per coordinator
    coord_counts = coordinators['name'].value_counts().reset_index()
    coord_counts.columns = ['Coordinator', 'Projects Managed']
    
    # Take Top 10
    top_coords = coord_counts.head(10)
    
    return alt.Chart(top_coords).mark_bar().encode(
        x=alt.X('Projects Managed', title='Projects', axis=alt.Axis(tickMinStep=1)),
        y=alt.Y('Coordinator', sort='-x', title=None),
        tooltip=['Coordinator', 'Projects Managed']
    ).properties(height=300)

def render_coordinator_stats(projects_df, orgs_df):
    """
    Renders a leaderboard of project coordinators.
    """
    if projects_df.empty or orgs_df.empty:
        return

    st.subheader("🏆 Coordinator Leaderboard")
    
    chart = get_coordinator_chart(projects_df, orgs_df)
    
    if chart:
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No coordinator data found.")
        
    st.markdown("---")

@st.cache_data
def get_timeline_chart(projects_df):
    # Sort by Start Date
    timeline_df = projects_df.sort_values('startDate', ascending=False).head(30).copy()
    
    # Calculate duration
    timeline_df['duration_months'] = ((timeline_df['endDate'] - timeline_df['startDate']) / pd.Timedelta(days=30)).astype(int)

    return alt.Chart(timeline_df).mark_bar().encode(
        x=alt.X('startDate', title='Timeline'),
        x2='endDate',
        y=alt.Y('acronym', sort='-x', title='Project'),
        color=alt.Color('cluster', legend=None),
        tooltip=[
            alt.Tooltip('title', title='Title'),
            alt.Tooltip('startDate', title='Start', format='%Y-%m-%d'),
            alt.Tooltip('endDate', title='End', format='%Y-%m-%d'),
            alt.Tooltip('duration_months', title='Months')
        ]
    ).properties(
        height=400
    ).interactive()

def render_project_timeline(projects_df):
    """
    Renders a Gantt chart of project timelines.
    """
    if projects_df.empty:
        return

    st.subheader("⏳ Project Timeline")
    chart = get_timeline_chart(projects_df)
    st.altair_chart(chart, use_container_width=True)
    st.caption("Displaying 30 most recent projects sorted by Start Date.")
    st.markdown("---")

@st.cache_data
def get_choropleth_map(projects_df, orgs_df):
    # Filter orgs
    relevant_orgs = orgs_df[orgs_df['projectID'].isin(projects_df['id'])].copy()
    
    # Aggregate by Country
    country_stats = relevant_orgs.groupby('country').agg(
        TotalFunding=('ecContribution', 'sum'),
        ProjectCount=('projectID', 'count')
    ).reset_index()
    
    if country_stats.empty:
        return None

    # Create Plotly Choropleth
    fig = px.choropleth(
        country_stats,
        locations='country',
        locationmode='country names', # Matches "Germany", "France" etc.
        color='TotalFunding',
        hover_name='country',
        hover_data={'TotalFunding': ':,.0f', 'ProjectCount': True, 'country': False},
        color_continuous_scale='Viridis',
        scope='europe',
        title='Total Funding by Country (€)'
    )
    
    # Adjust layout
    fig.update_layout(
        margin={"r":0,"t":30,"l":0,"b":0},
        geo=dict(
            center=dict(lat=50, lon=15),
            projection_scale=1.2 # Zoom in slightly on Europe
        )
    )
    return fig

def render_choropleth_map(projects_df, orgs_df):
    """
    Renders a Choropleth map of funding using Plotly.
    """
    if projects_df.empty or orgs_df.empty:
        return
        
    st.subheader("🌍 European Funding Landscape")
    
    fig = get_choropleth_map(projects_df, orgs_df)
    
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No geographic data available.")
