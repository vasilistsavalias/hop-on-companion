import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from components.project_list import render_project_list

class TestProjectList(unittest.TestCase):

    @patch('components.project_list.st')
    def test_render_project_list(self, mock_st):
        # Mock data
        mock_projects = pd.DataFrame({
            'id': ['1', '2'],
            'title': ['A', 'B']
        })
        
        # Mock widget returns
        mock_st.selectbox.return_value = '1'

        # Call function
        selected_id = render_project_list(mock_projects)

        # Assertions
        self.assertEqual(selected_id, '1')
        
        # Verify calls
        mock_st.write.assert_any_call("### Filtered Data")
        # st.dataframe might be replaced by data_editor, check accordingly if I change impl
        # For now, it fails if I change implementation. I will update this test in the Green phase or now if I know the plan.
    
    @patch('components.project_list.st')
    @patch('components.project_list.add_to_watchlist')
    @patch('components.project_list.remove_from_watchlist')
    @patch('components.project_list.get_watchlist')
    def test_watchlist_interaction(self, mock_get, mock_remove, mock_add, mock_st):
        # Mock initial watchlist (Project 1 is fav)
        mock_get.return_value = ['1']
        
        # Mock dataframe
        mock_projects = pd.DataFrame({
            'id': ['1', '2'],
            'title': ['A', 'B']
        })
        
        # Mock data_editor return
        # Scenario: User UN-favorites Project 1, Favorites Project 2
        edited_df = mock_projects.copy()
        edited_df['Favorite'] = [False, True] 
        mock_st.data_editor.return_value = edited_df

        # Call
        render_project_list(mock_projects)

        # Assertions
        mock_add.assert_called_with('2')
        mock_remove.assert_called_with('1')

if __name__ == '__main__':
    unittest.main()