import pandas as pd
import streamlit as st
import os
from utils.logger import logger

def get_optimized_dataframe(csv_path: str, loader_func, cleaning_func=None):
    """
    Generic function to handle CSV -> Parquet caching strategy.
    
    Args:
        csv_path: Path to the source CSV file.
        loader_func: Function to read the CSV (pd.read_csv with specific args).
        cleaning_func: Optional function to clean/process the DF after loading CSV.
    """
    parquet_path = csv_path.replace('.csv', '.parquet')
    
    if not os.path.exists(csv_path):
        logger.warning(f"Source file not found: {csv_path}")
        return pd.DataFrame()

    # Check timestamps
    # If parquet exists and is newer than CSV, use it.
    if os.path.exists(parquet_path):
        csv_mtime = os.path.getmtime(csv_path)
        parquet_mtime = os.path.getmtime(parquet_path)
        
        if parquet_mtime > csv_mtime:
            try:
                logger.info(f"Loading cached data from {parquet_path}")
                return pd.read_parquet(parquet_path)
            except Exception as e:
                logger.warning(f"Failed to read parquet cache ({e}), falling back to CSV.")
    
    # Fallback to CSV (Slow Path)
    try:
        logger.info(f"Reading source CSV: {csv_path}")
        df = loader_func(csv_path)
        
        if cleaning_func:
            df = cleaning_func(df)
            
        # Save to Parquet for next time
        try:
            df.to_parquet(parquet_path, index=False)
            logger.info(f"Cached data to {parquet_path}")
        except Exception as e:
            logger.warning(f"Failed to create parquet cache: {e}")
            
        return df
    except Exception as e:
        logger.exception(f"Error loading data from {csv_path}: {e}")
        return pd.DataFrame()

@st.cache_data
def load_projects():
    csv_path = 'data/processed/projects.csv'
    
    def load_csv(path):
        return pd.read_csv(path, delimiter='|')
        
    def clean_projects(projects):
        projects['startDate'] = pd.to_datetime(projects['startDate'], errors='coerce')
        projects['endDate'] = pd.to_datetime(projects['endDate'], errors='coerce')
        
        # Clean totalCost: replace comma with dot and convert to numeric
        if 'totalCost' in projects.columns:
            projects['totalCost'] = projects['totalCost'].astype(str).str.replace(',', '.', regex=False)
            projects['totalCost'] = pd.to_numeric(projects['totalCost'], errors='coerce').fillna(0)

        projects['id'] = projects['id'].astype('str')
        # Select specific columns
        cols = ['id','acronym','title','objective','cluster','topics','fundingScheme','startDate','endDate','legalBasis','grantDoi','totalCost']
        # Ensure only existing columns are selected to avoid KeyErrors
        existing_cols = [c for c in cols if c in projects.columns]
        return projects[existing_cols]

    df = get_optimized_dataframe(csv_path, load_csv, clean_projects)
    logger.success(f"Loaded {len(df)} projects.")
    return df

@st.cache_data
def load_orgs():
    csv_path = 'data/processed/orgs.csv'

    def load_csv(path):
        return pd.read_csv(path, delimiter='|')

    def clean_orgs(orgs):
        orgs['projectID'] = orgs['projectID'].astype('str')
        
        # Clean ecContribution
        if 'ecContribution' in orgs.columns:
            orgs['ecContribution'] = orgs['ecContribution'].astype(str).str.replace(',', '.', regex=False)
            orgs['ecContribution'] = pd.to_numeric(orgs['ecContribution'], errors='coerce').fillna(0)

        # Select specific columns
        cols = ['name','activityType','city','country','role','organizationURL','projectID','order','ecContribution','contactForm']
        existing_cols = [c for c in cols if c in orgs.columns]
        return orgs[existing_cols]

    df = get_optimized_dataframe(csv_path, load_csv, clean_orgs)
    logger.success(f"Loaded {len(df)} organizations.")
    return df