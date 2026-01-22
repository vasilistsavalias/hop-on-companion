import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from utils.matcher import ProjectMatcher

# Mock data
@pytest.fixture
def sample_projects():
    return pd.DataFrame({
        'id': ['1', '2', '3'],
        'title': ['Green Energy', 'Sustainable Power', 'AI for Health'],
        'objective': ['Solar panels research', 'Wind turbine efficiency', 'Machine learning in hospitals'],
        'topics': ['Energy', 'Environment', 'Health']
    })

@patch('utils.matcher.SentenceTransformer')
def test_matcher_initialization(mock_sentence_transformer):
    """Test that the matcher initializes the model correctly."""
    matcher = ProjectMatcher()
    mock_sentence_transformer.assert_called_with('all-MiniLM-L6-v2')
    assert matcher.model is not None

@patch('utils.matcher.SentenceTransformer')
def test_encode_projects(mock_sentence_transformer, sample_projects):
    """Test that projects are encoded and IDs are stored."""
    # Setup mock
    mock_model_instance = MagicMock()
    # Mock encode to return a fake embedding tensor/array
    # Shape: (3 projects, 4 dimensions)
    mock_model_instance.encode.return_value = np.array([
        [0.9, 0.1, 0.0, 0.0], # Green Energy
        [0.8, 0.2, 0.0, 0.0], # Sustainable Power (Similar to above)
        [0.0, 0.0, 0.9, 0.1]  # AI Health (Different)
    ])
    mock_sentence_transformer.return_value = mock_model_instance

    matcher = ProjectMatcher()
    matcher.encode_projects(sample_projects)

    assert matcher.embeddings is not None
    assert matcher.project_ids == ['1', '2', '3']
    mock_model_instance.encode.assert_called_once()

@patch('utils.matcher.SentenceTransformer')
def test_search(mock_sentence_transformer, sample_projects):
    """Test semantic search functionality."""
    # Setup mock with simple dot product logic in mind
    mock_model_instance = MagicMock()
    
    # Embeddings for projects
    # 1: Green, 2: Sustainable, 3: Health
    project_embeddings = np.array([
        [1.0, 0.0], 
        [0.9, 0.1], 
        [0.0, 1.0]
    ])
    
    # Query embedding for "Solar" (matches Green)
    query_embedding = np.array([1.0, 0.0])

    mock_model_instance.encode.side_effect = [
        project_embeddings, # First call: encode_projects
        query_embedding     # Second call: search query
    ]
    mock_sentence_transformer.return_value = mock_model_instance

    # Init and Encode
    matcher = ProjectMatcher()
    matcher.encode_projects(sample_projects)

    # Search
    # We need to mock util.cos_sim or rely on the real one?
    # Real util.cos_sim might fail if we pass numpy arrays instead of tensors if sentence-transformers is not installed/mocked perfectly.
    # But utils.matcher imports util. 
    # Let's rely on the fact that we can mock `util.cos_sim` too for pure unit isolation.
    
    with patch('utils.matcher.util') as mock_util:
        # Mock cos_sim to return high score for proj 1 & 2, low for 3
        # Return shape (1, 3)
        mock_util.cos_sim.return_value.cpu.return_value.numpy.return_value = np.array([[0.99, 0.85, 0.01]])
        
        results = matcher.search("Solar", sample_projects)
        
        assert not results.empty
        assert 'relevance_score' in results.columns
        # Project 1 should be top
        assert results.iloc[0]['id'] == '1'
        assert results.iloc[0]['relevance_score'] == 0.99

@patch('utils.matcher.SentenceTransformer')
def test_get_similar_projects(mock_sentence_transformer, sample_projects):
    """Test similar project recommendation."""
    mock_model_instance = MagicMock()
    # Embeddings
    project_embeddings = np.array([
        [1.0, 0.0], # 1
        [0.9, 0.1], # 2
        [0.0, 1.0]  # 3
    ])
    mock_model_instance.encode.return_value = project_embeddings
    mock_sentence_transformer.return_value = mock_model_instance

    matcher = ProjectMatcher()
    matcher.encode_projects(sample_projects)

    with patch('utils.matcher.util') as mock_util:
        # Mock similarity for Project 1 (Target) against [1, 2, 3]
        # It should be [1.0, 0.85, 0.01]
        mock_util.cos_sim.return_value.cpu.return_value.numpy.return_value = np.array([1.0, 0.85, 0.01])

        # Get similar to Project 1
        recommendations = matcher.get_similar_projects('1', sample_projects, top_k=2)
        
        # Should exclude itself, so top match should be Project 2
        assert len(recommendations) == 2 # We asked for top 2, but only 2 others exist. Wait, filter out self -> 2 left.
        assert recommendations.iloc[0]['id'] == '2'
        assert recommendations.iloc[0]['similarity_score'] == 0.85
        # Ensure ID 1 is not in results
        assert '1' not in recommendations['id'].values
