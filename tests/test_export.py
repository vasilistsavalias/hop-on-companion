import unittest
import pandas as pd
from utils.export import convert_df_to_csv

class TestExport(unittest.TestCase):
    def test_convert_to_csv(self):
        # Create dummy dataframe
        df = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
        
        # Convert
        csv_bytes = convert_df_to_csv(df)
        
        # Verify
        self.assertIsInstance(csv_bytes, bytes)
        decoded = csv_bytes.decode('utf-8')
        self.assertIn("id,name", decoded)
        self.assertIn("1,A", decoded)
        self.assertIn("2,B", decoded)

if __name__ == '__main__':
    unittest.main()
