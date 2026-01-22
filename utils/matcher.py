import pandas as pd
import numpy as np
import os
import pickle
from sentence_transformers import SentenceTransformer, util
from utils.logger import logger
import streamlit as st

# Global Constants
EMBEDDINGS_FILE = "data/processed/embeddings.pkl"

@st.cache_resource
def load_model():
    """
    Loads the SentenceTransformer model. 
    Cached globally to prevent reloading on every session.
    """
    try:
        logger.info("Loading Semantic Model (all-MiniLM-L6-v2)...")
        return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        logger.exception(f"Failed to load Semantic Model: {e}")
        return None

class ProjectMatcher:
    def __init__(self):
        self.model = load_model()
        self.embeddings = None
        self.project_ids = None

    def encode_projects(self, df):
        """
        Generates or loads embeddings for the projects dataframe.
        """
        if self.model is None or df.empty:
            return

        # 1. Try to load from disk first
        if self._load_embeddings_from_disk(df):
             return

        # 2. If not found or stale, re-compute
        logger.info(f"Computing embeddings for {len(df)} projects...")
        
        text_corpus = df.apply(lambda x: f"{x['title']} {x['objective']} {x['topics']}", axis=1).tolist()
        
        # Compute embeddings
        self.embeddings = self.model.encode(text_corpus, convert_to_tensor=True)
        self.project_ids = df['id'].tolist()
        
        # 3. Save to disk
        self._save_embeddings_to_disk()
        
        logger.success("Project encoding complete (Computed & Saved).")

    def _save_embeddings_to_disk(self):
        """Saves embeddings and project IDs to a pickle file."""
        try:
            data = {
                'ids': self.project_ids,
                'embeddings': self.embeddings
            }
            # Ensure directory exists
            os.makedirs(os.path.dirname(EMBEDDINGS_FILE), exist_ok=True)
            with open(EMBEDDINGS_FILE, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"Embeddings saved to {EMBEDDINGS_FILE}")
        except Exception as e:
            logger.error(f"Failed to save embeddings: {e}")

    def _load_embeddings_from_disk(self, current_df):
        """
        Loads embeddings from disk if they match the current dataset.
        Returns True if successful, False otherwise.
        """
        if not os.path.exists(EMBEDDINGS_FILE):
            return False
        
        try:
            with open(EMBEDDINGS_FILE, 'rb') as f:
                data = pickle.load(f)
            
            cached_ids = data.get('ids', [])
            current_ids = current_df['id'].tolist()
            
            # Simple validation: Check if ID lists are identical
            # (In production, a hash of the content would be safer, but this covers add/remove)
            if cached_ids == current_ids:
                self.project_ids = cached_ids
                self.embeddings = data['embeddings']
                logger.info("Loaded embeddings from disk (Cache Hit).")
                return True
            else:
                logger.warning("Cached embeddings do not match current project list (Cache Miss).")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load cached embeddings: {e}")
            return False

    def search(self, query, df, top_k=None):
        """
        Searches the projects for the query.
        Returns the DataFrame with a new 'Relevance' column, sorted.
        """
        if self.model is None or self.embeddings is None:
            logger.warning("Matcher not initialized or embeddings missing.")
            return df

        # Encode query
        query_embedding = self.model.encode(query, convert_to_tensor=True)

        # Compute Cosine Similarity
        # util.cos_sim returns a tensor of shape (1, num_projects)
        scores = util.cos_sim(query_embedding, self.embeddings)[0]

        # Convert to numpy and then to list
        scores_list = scores.cpu().numpy().tolist()

        score_map = dict(zip(self.project_ids, scores_list))
        
        # Create a copy to avoid SettingWithCopy warnings
        result_df = df.copy()
        
        # Map scores
        result_df['relevance_score'] = result_df['id'].map(score_map).fillna(0)
        
        # Sort
        result_df = result_df.sort_values('relevance_score', ascending=False)
        
        return result_df

    def get_similar_projects(self, project_id, df, top_k=5):
        """
        Finds projects similar to the given project_id based on embeddings.
        """
        if self.model is None or self.embeddings is None:
            return pd.DataFrame()

        # Find index of the project
        try:
            # We need the integer index in the embeddings tensor
            idx = self.project_ids.index(project_id)
        except ValueError:
            logger.warning(f"Project ID {project_id} not found in embeddings.")
            return pd.DataFrame()

        # Get embedding for this project
        target_embedding = self.embeddings[idx]

        # Compute cosine similarity against ALL projects
        scores = util.cos_sim(target_embedding, self.embeddings)[0]
        
        # Convert to list
        scores_list = scores.cpu().numpy().tolist()
        
        # Map to IDs
        score_map = dict(zip(self.project_ids, scores_list))
        
        # Create result DF
        result_df = df.copy()
        result_df['similarity_score'] = result_df['id'].map(score_map).fillna(0)
        
        # Sort desc
        result_df = result_df.sort_values('similarity_score', ascending=False)
        
        # Filter out the project itself (similarity is 1.0)
        result_df = result_df[result_df['id'] != project_id]
        
        return result_df.head(top_k)