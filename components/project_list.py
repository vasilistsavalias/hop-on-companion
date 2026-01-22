import streamlit as st
import pandas as pd
from utils.db import get_watchlist, add_to_watchlist, remove_from_watchlist
from utils.export import convert_df_to_csv, convert_df_to_excel

def render_project_list(filtered_df, user_id):
    col_header, col_export = st.columns([0.7, 0.3])
    
    with col_header:
        st.write("### Filtered Data")
    
    with col_export:
        if not filtered_df.empty:
            csv = convert_df_to_csv(filtered_df)
            st.download_button(
                label="📥 CSV",
                data=csv,
                file_name='projects_export.csv',
                mime='text/csv',
                key='download-csv'
            )
            # Excel button (optional, can be heavy for large files but fine here)
            # excel_data = convert_df_to_excel(filtered_df)
            # st.download_button(label="📥 Excel", data=excel_data, file_name='projects.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    if filtered_df.empty:
        st.write("No projects match the criteria.")
        return None
    
    # Get current watchlist for the user
    if user_id:
        watchlist = get_watchlist(user_id)
    else:
        watchlist = []
    
    # Add 'Favorite' column
    df_display = filtered_df.copy()
    df_display.insert(0, 'Favorite', df_display['id'].isin(watchlist))

    # Construct clickable DOI links
    if 'grantDoi' in df_display.columns:
        # Prepend base URL to DOI, handling NaNs
        df_display['grantDoi'] = df_display['grantDoi'].apply(lambda x: f"https://doi.org/{x}" if pd.notnull(x) and str(x).strip() != '' else None)

    # Reorder columns: Move Match Score to front if present
    if 'relevance_score' in df_display.columns:
        cols = ['Favorite', 'relevance_score'] + [c for c in df_display.columns if c not in ['Favorite', 'relevance_score']]
        df_display = df_display[cols]

    # Display editor
    # We disable editing if no user is selected
    disabled_cols = [col for col in df_display.columns if col != 'Favorite']
    if not user_id:
        disabled_cols.append('Favorite')

    edited_df = st.data_editor(
        df_display, 
        hide_index=True,
        column_config={
            "Favorite": st.column_config.CheckboxColumn(
                "Favorite",
                help="Select your favorite projects (Login required)",
                default=False,
                disabled=(user_id is None)
            ),
            "relevance_score": st.column_config.ProgressColumn(
                "Match Score",
                help="AI Relevance Score (Semantic Similarity)",
                format="%.2f",
                min_value=0,
                max_value=1
            ),
            "grantDoi": st.column_config.LinkColumn(
                "DOI Link",
                help="Click to open project on CORDIS/DOI",
                display_text="Open Link"
            ),
            "totalCost": st.column_config.NumberColumn(
                "Total Cost (€)",
                format="€%.2f"
            )
        },
        disabled=disabled_cols,
        key="project_editor"
    )

    # Detect Changes only if user is logged in
    if user_id and not edited_df.equals(df_display):
        # New Favorites
        new_favs_mask = edited_df['Favorite'] & ~df_display['Favorite']
        new_fav_ids = edited_df.loc[new_favs_mask, 'id'].tolist()
        
        for pid in new_fav_ids:
            add_to_watchlist(pid, user_id)
            
        # Removed Favorites
        removed_favs_mask = ~edited_df['Favorite'] & df_display['Favorite']
        removed_fav_ids = edited_df.loc[removed_favs_mask, 'id'].tolist()
        
        for pid in removed_fav_ids:
            remove_from_watchlist(pid, user_id)
            
        # Force rerun to update UI immediately
        st.rerun()
    
    # Select project
    selected_project = st.selectbox("Select a Project ID to View Organizations", filtered_df['id'].unique())
    st.write('Results: ' + str(filtered_df.shape[0]))

    # --- Similar Projects Recommender ---
    if selected_project and 'project_matcher' in st.session_state:
        matcher = st.session_state['project_matcher']
        # Only try if embeddings are ready
        if matcher.embeddings is not None:
            st.markdown("---")
            st.subheader("💡 Similar Projects")
            
            similar_df = matcher.get_similar_projects(selected_project, filtered_df, top_k=3)
            
            if not similar_df.empty:
                cols = st.columns(3)
                for idx, (col, row) in enumerate(zip(cols, similar_df.iterrows())):
                    _, project = row
                    with col:
                        score = int(project['similarity_score'] * 100)
                        st.metric(label=f"Match: {score}%", value=project['id'])
                        st.caption(f"**{project['title']}**")
                        with st.expander("Brief"):
                            st.write(project['objective'][:200] + "...")
            else:
                st.caption("No similar projects found (try generating embeddings first).")
    
    return selected_project
