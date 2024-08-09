import sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

import unittest
from db_init import create_tables
from db_utils import create_crud_functions, delete_database

class TestCRUDOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set environment variable to use test database
        os.environ['USE_TEST_DB'] = 'true'
    
    @classmethod
    def tearDownClass(cls):
        delete_database(test=True)

    def setUp(self):
        # Reset the database before each test
        delete_database(test=True)
        create_tables()

        self.sitemap_crud = create_crud_functions('sitemap_data')
        self.auction_crud = create_crud_functions('auction_data')
        self.items_crud = create_crud_functions('items_data')
        self.ebay_demand_crud = create_crud_functions('ebay_demand_data')

    def test_sitemap_crud(self):
        # Insert
        new_record = {'url': 'http://example.com', 'parent_id': None, 'depth': 2}
        
        record_id = self.sitemap_crud['insert'](new_record)
        self.assertIsNotNone(record_id, "Failed to insert sitemap record")

        # Get by ID
        record = self.sitemap_crud['get_by_id'](record_id)
        self.assertIsNotNone(record, "Record not found by ID")
        self.assertEqual(record[1], new_record['url'])

        # Get by column
        record = self.sitemap_crud['get_by_column']('url', new_record['url'])
        self.assertIsNotNone(record, "Record not found by column")
        self.assertEqual(record[1], new_record['url'])

        # Update
        updated_record = {'url': 'http://newexample.com'}
        rows_affected = self.sitemap_crud['update'](record_id, updated_record)
        self.assertEqual(rows_affected, 1)

        # Get all
        records = self.sitemap_crud['get_all']()
        self.assertGreaterEqual(len(records), 1)

        # Delete
        rows_deleted = self.sitemap_crud['delete'](record_id)
        self.assertEqual(rows_deleted, 1)

    def test_auction_crud(self):
        # Insert a sitemap record to reference
        sitemap_record = {'url': 'http://example.com', 'parent_id': None, 'depth': 2}
        sitemap_id = self.sitemap_crud['insert'](sitemap_record)
        self.assertIsNotNone(sitemap_id, "Failed to insert sitemap record")

        # Insert
        new_record = {'url': sitemap_id, 'auction_id': '12345', 'title': 'Test Auction'}
        record_id = self.auction_crud['insert'](new_record)
        self.assertIsNotNone(record_id, "Failed to insert auction record")

        # Get by ID
        record = self.auction_crud['get_by_id'](record_id)
        self.assertIsNotNone(record, "Record not found by ID")
        self.assertEqual(record[2], new_record['auction_id'])

        # Get by column
        record = self.auction_crud['get_by_column']('auction_id', new_record['auction_id'])
        self.assertIsNotNone(record, "Record not found by column")
        self.assertEqual(record[2], new_record['auction_id'])

        # Update
        updated_record = {'title': 'Updated Auction'}
        rows_affected = self.auction_crud['update'](record_id, updated_record)
        self.assertEqual(rows_affected, 1)

        # Get all
        records = self.auction_crud['get_all']()
        self.assertGreaterEqual(len(records), 1)

        # Delete
        rows_deleted = self.auction_crud['delete'](record_id)
        self.assertEqual(rows_deleted, 1)

    def test_items_crud(self):
        # Ensure auction_id exists in auction_data
        sitemap_record = {'url': 'http://example.com', 'parent_id': None, 'depth': 2}
        sitemap_id = self.sitemap_crud['insert'](sitemap_record)
        self.assertIsNotNone(sitemap_id, "Failed to insert sitemap record")

        auction_record = {'url': sitemap_id, 'auction_id': '12345', 'title': 'Test Auction'}
        auction_id = self.auction_crud['insert'](auction_record)
        self.assertIsNotNone(auction_id, "Failed to insert auction record")

        # Insert
        new_record = {'auction_id': '12345', 'item_id': 1, 'product_code': 'ABC123'}
        record_id = self.items_crud['insert'](new_record)
        self.assertIsNotNone(record_id, "Failed to insert item record")

        # Get by ID
        record = self.items_crud['get_by_id'](record_id)
        self.assertIsNotNone(record, "Record not found by ID")
        self.assertEqual(record[3], new_record['item_id'])

        # Get by column
        record = self.items_crud['get_by_column']('item_id', new_record['item_id'])
        self.assertIsNotNone(record, "Record not found by column")
        self.assertEqual(record[3], new_record['item_id'])

        # Update
        updated_record = {'product_code': 'XYZ789'}
        rows_affected = self.items_crud['update'](record_id, updated_record)
        self.assertEqual(rows_affected, 1)

        # Get all
        records = self.items_crud['get_all']()
        self.assertGreaterEqual(len(records), 1)

        # Delete
        rows_deleted = self.items_crud['delete'](record_id)
        self.assertEqual(rows_deleted, 1)

        # Delete the auction record
        rows_deleted = self.auction_crud['delete'](record_id)
        self.assertEqual(rows_deleted, 1)

    def test_ebay_demand_crud(self):
        # Ensure auction_id exists in auction_data
        sitemap_record = {'url': 'http://example.com', 'parent_id': None, 'depth': 2}
        sitemap_id = self.sitemap_crud['insert'](sitemap_record)
        self.assertIsNotNone(sitemap_id, "Failed to insert sitemap record")

        auction_record = {'url': sitemap_id, 'auction_id': '12345', 'title': 'Test Auction'}
        auction_id = self.auction_crud['insert'](auction_record)
        self.assertIsNotNone(auction_id, "Failed to insert auction record")

        # Ensure item_id exists in items_data
        item_record = {'auction_id': '12345', 'item_id': 1, 'product_code': 'ABC123'}
        item_id = self.items_crud['insert'](item_record)
        self.assertIsNotNone(item_id, "Failed to insert item record")

        # Insert
        new_record = {'auction_id': '12345', 'item_id': item_id, 'search_string': 'Test Search'}
        record_id = self.ebay_demand_crud['insert'](new_record)
        self.assertIsNotNone(record_id, "Failed to insert ebay demand record")

        # Get by ID
        record = self.ebay_demand_crud['get_by_id'](record_id)
        self.assertIsNotNone(record, "Record not found by ID")
        self.assertEqual(record[1], new_record['auction_id'])

        # Get by column
        record = self.ebay_demand_crud['get_by_column']('auction_id', new_record['auction_id'])
        self.assertIsNotNone(record, "Record not found by column")
        self.assertEqual(record[1], new_record['auction_id'])

        # Update
        updated_record = {'search_string': 'Updated Search'}
        rows_affected = self.ebay_demand_crud['update'](record_id, updated_record)
        self.assertEqual(rows_affected, 1)

        # Get all
        records = self.ebay_demand_crud['get_all']()
        self.assertGreaterEqual(len(records), 1)

        # Delete
        rows_deleted = self.ebay_demand_crud['delete'](record_id)
        self.assertEqual(rows_deleted, 1)

if __name__ == '__main__':
    unittest.main()