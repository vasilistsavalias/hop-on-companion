import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
from dotenv import load_dotenv
from utils.logger import setup_logger, logger
from utils.db import get_all_users_config, get_user_id

# --- Load Environment Variables ---
load_dotenv()

# --- Logger Initialization ---
if 'logger_configured' not in st.session_state:
    setup_logger()
    st.session_state['logger_configured'] = True

st.set_page_config(page_title="HopOn Projects", layout="wide")

# --- Authentication ---
users_config = get_all_users_config()
credentials = {'usernames': users_config}

authenticator = stauth.Authenticate(
    credentials,
    'hopon_cookie',
    'hopon_auth_key', # In production, verify this is random/secret
    cookie_expiry_days=30
)

# Render Login Widget
authenticator.login()

if st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
    st.stop()
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
    st.stop()

# --- Application Logic (Only runs if Authenticated) ---
logger.info(f"User authenticated: {st.session_state['name']}")

# Get internal User ID
current_username = st.session_state['username']
current_user_id = get_user_id(current_username)

# Logout Button in Sidebar
with st.sidebar:
    st.write(f"Welcome, **{st.session_state['name']}**!")
    authenticator.logout('Logout', 'main')
    st.divider()

from utils.data_loader import load_projects, load_orgs
from utils.db import get_watchlist
from utils.matcher import ProjectMatcher
from components.sidebar import render_sidebar
from components.project_list import render_project_list
from components.metrics import render_metrics
from components.charts import render_charts, render_coordinator_stats, render_project_timeline, render_choropleth_map
from components.admin import render_admin_panel

logger.info("Application started/reloaded.")

# --- Semantic Search Initialization ---
if 'project_matcher' not in st.session_state:
    st.session_state['project_matcher'] = ProjectMatcher()

# Dictionary mapping country codes to country names
country_mapping = {
    'IT': 'Italy', 'AT': 'Austria', 'CZ': 'Czech Republic', 'ES': 'Spain', 'FR': 'France', 'DE': 'Germany',
    'NL': 'Netherlands',
    'UK': 'United Kingdom', 'BE': 'Belgium', 'EE': 'Estonia', 'PL': 'Poland', 'HR': 'Croatia', 'IE': 'Ireland',
    'FI': 'Finland',
    'NO': 'Norway', 'LU': 'Luxembourg', 'DK': 'Denmark', 'CH': 'Switzerland', 'SE': 'Sweden', 'PT': 'Portugal',
    'RO': 'Romania',
    'BG': 'Bulgaria', 'LV': 'Latvia', 'SI': 'Slovenia', 'LT': 'Lithuania', 'SK': 'Slovakia', 'UA': 'Ukraine',
    'RS': 'Serbia',
    'CY': 'Cyprus', 'HU': 'Hungary', 'MT': 'Malta', 'MK': 'North Macedonia', 'IS': 'Iceland',
    'BA': 'Bosnia and Herzegovina',
    'AL': 'Albania', 'MD': 'Moldova', 'XK': 'Kosovo', 'ME': 'Montenegro'
}

# Title
st.title("Available Hopon Projects")
projects = load_projects()

# --- Semantic Encoding ---
if 'project_matcher' in st.session_state and st.session_state['project_matcher'].embeddings is None and not projects.empty:
    with st.spinner("Initializing AI Search Engine... (First run only)"):
        st.session_state['project_matcher'].encode_projects(projects)

df_organizations = load_orgs()

# Filter organizations to keep only those in Europe
if not df_organizations.empty:
    df_organizations = df_organizations[df_organizations['country'].isin(country_mapping.keys())]
    # Replace country codes with country names
    df_organizations['country'] = df_organizations['country'].map(country_mapping)

# Render Sidebar and get filters
# We pass the authenticated user_id to the sidebar
filters = render_sidebar(projects, current_user_id) 

# --- ROUTING LOGIC ---
if filters.get('page') == "User Management":
    render_admin_panel(current_user_id)
    st.stop() # Stop rendering the dashboard

# --- DASHBOARD LOGIC ---

# Apply filters
if not projects.empty and filters:
    filtered_df = projects.copy() # Start with a copy
    
    # Date filters (only if dates are selected)
    if filters['start_date']:
        filtered_df = filtered_df[filtered_df['startDate'] >= pd.to_datetime(filters['start_date'])]
    if filters['end_date']:
        filtered_df = filtered_df[filtered_df['endDate'] <= pd.to_datetime(filters['end_date'])]

    # Cluster and Funding Scheme filters
    if filters['selected_clusters']:
        filtered_df = filtered_df[filtered_df['cluster'].isin(filters['selected_clusters'])]
    if filters['selected_funding_schemes']:
        filtered_df = filtered_df[filtered_df['fundingScheme'].isin(filters['selected_funding_schemes'])]

    # Text search filters
    if filters['search_objective']:
        # Semantic Search & Ranking
        if 'project_matcher' in st.session_state:
            filtered_df = st.session_state['project_matcher'].search(filters['search_objective'], filtered_df)
            st.info(f"Showing results for '{filters['search_objective']}' sorted by AI Relevance.")
    
    if filters['search_id']:
        filtered_df = filtered_df[filtered_df['id'].str.contains(filters['search_id'], case=False, na=False)]
    
    # Watchlist Filter
    if filters.get('show_watchlist'):
        if current_user_id:
            watchlist_ids = get_watchlist(current_user_id)
            filtered_df = filtered_df[filtered_df['id'].isin(watchlist_ids)]
        else:
            filtered_df = filtered_df[filtered_df['id'].isin([])]
else:
    filtered_df = projects

# --- Dashboard Metrics ---
render_metrics(filtered_df, df_organizations)

# --- Visualizations ---
with st.expander("📊 Dashboard Analytics", expanded=False):
    render_project_timeline(filtered_df)
    render_charts(filtered_df)
    render_coordinator_stats(filtered_df, df_organizations)
    render_choropleth_map(filtered_df, df_organizations)

# Create tabs
tab1, tab2 = st.tabs(["Projects", "Organisations"])

with tab1:
    st.header("Projects")
    
    if not projects.empty:
        min_date = projects['startDate'].min()
        max_date = projects['endDate'].max()
        st.write(f"**Min Start Date:** {min_date}")
        st.write(f"**Max End Date:** {max_date}")

    selected_project = render_project_list(filtered_df, current_user_id)

    # --- AI Project Brief ---
    if selected_project:
        st.markdown("---")
        st.subheader(f"Project Details: {selected_project}")
        
        # Check session state for cached brief
        brief_key = f"brief_{selected_project}"
        
        col_gen, _ = st.columns([0.3, 0.7])
        with col_gen:
             if st.button("✨ Generate AI One-Pager", key="btn_gen_brief"):
                # Get project data
                project_row = projects[projects['id'] == selected_project]
                if not project_row.empty:
                    project_data = project_row.iloc[0].to_dict()
                    with st.spinner("Generating One-Pager with Gemini 3.0 Flash..."):
                        from utils.ai import generate_project_brief
                        brief = generate_project_brief(project_data)
                        if brief:
                            st.session_state[brief_key] = brief
                            st.rerun() # Rerun to display the result cleanly
                        else:
                            st.error("Generation failed. Please check your API key.")
        
        if brief_key in st.session_state:
            st.markdown(st.session_state[brief_key])
            if st.button("Clear Brief", key="btn_clear_brief"):
                del st.session_state[brief_key]
                st.rerun()

    # Detail View
    if filters and filters.get('search_id'):
        def format_row(row,df):
            return "\n\n".join(f"**{col}:** {row[col]}" for col in df.columns)

        # Convert entire DataFrame to formatted Markdown with line breaks
        formatted_text = "\n\n---\n\n".join(format_row(row,filtered_df) for _, row in filtered_df.iterrows())

        # Display formatted text using Markdown
        st.subheader("Info for specific project")
        st.markdown(formatted_text)

    # Org view for selected project
    if not df_organizations.empty and selected_project:
        st.write("### Participating Organizations")
        project_orgs = df_organizations[df_organizations['projectID'] == selected_project]
        project_orgs = project_orgs.sort_values(by=['order'],ascending=True)
        st.dataframe(project_orgs,hide_index=True)

with tab2:
    st.header("Organisations")
    
    if not df_organizations.empty:
        # Organisation-specific filters
        org_countries = df_organizations['country'].unique().tolist()
        selected_countries = st.multiselect("Select Countries", options=org_countries, default=org_countries)

        org_types = df_organizations['activityType'].unique().tolist()
        selected_types = st.multiselect("Select Organisation Types", options=org_types, default=org_types)
        org_roles = df_organizations['role'].unique().tolist()
        selected_roles = st.multiselect("Select Organisation Role",options=org_roles,default='coordinator')
        # Organization name search
        search_org_name = st.text_input("Search Organisation Name")

        # Apply filters
        filtered_orgs = df_organizations[df_organizations['country'].isin(selected_countries)]
        filtered_orgs = filtered_orgs[filtered_orgs['activityType'].isin(selected_types)]
        filtered_orgs  = filtered_orgs[filtered_orgs['role'].isin(selected_roles)]

        if search_org_name:
            filtered_orgs = filtered_orgs[filtered_orgs['name'].str.contains(search_org_name, case=False, na=False)]

        # Display filtered organisations
        st.write("### Filtered Organisations")
        st.dataframe(filtered_orgs)
