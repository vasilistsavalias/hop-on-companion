import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from utils.data_loader import load_projects, load_orgs

class TestDataLoader(unittest.TestCase):
    
    @patch('utils.data_loader.pd.read_csv')
    def test_load_projects(self, mock_read_csv):
        # Mock data
        mock_df = pd.DataFrame({
            'id': [1, 2],
            'acronym': ['A', 'B'],
            'title': ['Title A', 'Title B'],
            'objective': ['Obj A', 'Obj B'],
            'cluster': ['C1', 'C2'],
            'topics': ['T1', 'T2'],
            'fundingScheme': ['F1', 'F2'],
            'startDate': ['2024-01-01', '2025-01-01'],
            'endDate': ['2026-01-01', '2027-01-01'],
            'legalBasis': ['L1', 'L2'],
            'grantDoi': ['D1', 'D2'],
            'extra_col': ['x', 'y'] # Should be filtered out
        })
        mock_read_csv.return_value = mock_df

        # Call function
        result = load_projects()

        # Assertions
        # Check if result is None (since we haven't implemented it) or check columns
        self.assertIsNotNone(result) 
        self.assertTrue('extra_col' not in result.columns)
        self.assertEqual(len(result), 2)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['startDate']))
        self.assertTrue(pd.api.types.is_string_dtype(result['id']))

    @patch('utils.data_loader.pd.read_csv')
    def test_load_orgs(self, mock_read_csv):
         # Mock data
        mock_df = pd.DataFrame({
            'name': ['Org A'],
            'activityType': ['T1'],
            'city': ['City A'],
            'country': ['Country A'],
            'role': ['Role A'],
            'organizationURL': ['http://a.com'],
            'projectID': [1],
            'order': [1],
            'ecContribution': [100],
            'contactForm': ['form'],
            'extra_col': ['z'] # Should be filtered out
        })
        mock_read_csv.return_value = mock_df
        
        result = load_orgs()
        
        self.assertIsNotNone(result)
        self.assertTrue('extra_col' not in result.columns)
        self.assertEqual(len(result), 1)
        self.assertTrue(pd.api.types.is_string_dtype(result['projectID']))

if __name__ == '__main__':
    unittest.main()
