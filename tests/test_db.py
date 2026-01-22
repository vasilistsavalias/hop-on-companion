import unittest
from unittest.mock import patch
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.models import Base
# Import the functions we want to test
# Note: We will patch the internal get_db logic via context manager
import utils.db 

class TestDB(unittest.TestCase):

    def setUp(self):
        # Create an in-memory engine
        self.engine = create_engine("sqlite:///:memory:")
        # Create all tables
        Base.metadata.create_all(self.engine)
        # Create a session factory
        self.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Patch the SessionLocal in utils.db to use our in-memory engine
        self.patcher = patch('utils.db.SessionLocal', self.TestingSessionLocal)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        Base.metadata.drop_all(self.engine)

    def test_user_creation_and_auth(self):
        # Test Create
        uid = utils.db.create_user("testuser", "password123", "Test Name", "test@example.com")
        self.assertIsNotNone(uid)

        # Test Verify Success
        self.assertTrue(utils.db.verify_user("testuser", "password123"))
        
        # Test Verify Fail
        self.assertFalse(utils.db.verify_user("testuser", "wrongpassword"))

        # Test Get Config
        config = utils.db.get_all_users_config()
        self.assertIn("testuser", config)
        self.assertEqual(config["testuser"]["email"], "test@example.com")

    def test_watchlist_flow(self):
        # Create User first
        uid = utils.db.create_user("watcher", "pass")
        
        # Test Add
        utils.db.add_to_watchlist('proj_1', uid)
        watchlist = utils.db.get_watchlist(uid)
        self.assertIn('proj_1', watchlist)
        
        # Test Duplicate Add (should not crash/duplicate)
        utils.db.add_to_watchlist('proj_1', uid)
        watchlist = utils.db.get_watchlist(uid)
        self.assertEqual(len(watchlist), 1)

        # Test Remove
        utils.db.remove_from_watchlist('proj_1', uid)
        watchlist = utils.db.get_watchlist(uid)
        self.assertNotIn('proj_1', watchlist)

    def test_saved_search_flow(self):
        uid = utils.db.create_user("searcher", "pass")
        
        # Test Save
        filters = '{"cluster": "Health"}'
        utils.db.save_search('My Search', filters, uid)
        
        searches = utils.db.get_saved_searches(uid)
        self.assertEqual(len(searches), 1)
        self.assertEqual(searches[0]['name'], 'My Search')
        self.assertEqual(searches[0]['filters'], filters)
        
        # Test Delete
        search_id = searches[0]['id']
        utils.db.delete_search(search_id)
        
        searches = utils.db.get_saved_searches(uid)
        self.assertEqual(len(searches), 0)

if __name__ == '__main__':
    unittest.main()
