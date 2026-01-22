import unittest
import os

class TestDirectoryStructure(unittest.TestCase):
    def test_utils_directory_exists(self):
        self.assertTrue(os.path.isdir('utils'), "utils/ directory should exist")

    def test_components_directory_exists(self):
        self.assertTrue(os.path.isdir('components'), "components/ directory should exist")

if __name__ == '__main__':
    unittest.main()
