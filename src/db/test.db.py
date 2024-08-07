import unittest
import os
from db_init import create_tables
from db import create_crud_functions

class TestCRUDOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set environment variable to use test database
        os.environ['USE_TEST_DB'] = 'true'
        
        # Create tables in the test database
        create_tables()

    def setUp(self):
        self.sitemap_crud = create_crud_functions('sitemap_data')
        self.auction_crud = create_crud_functions('auction_data')
        self.items_crud = create_crud_functions('items_data')
        self.ebay_demand_crud = create_crud_functions('ebay_demand_data')

    def test_sitemap_crud(self):
        # Insert
        new_record = {'url': 'http://example.com', 'parent_id': 1, 'depth': 2}
        record_id = self.sitemap_crud['insert'](new_record)
        self.assertIsNotNone(record_id)

        # Get by ID
        record = self.sitemap_crud['get_by_id'](record_id)
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
        # Insert
        new_record = {'auction_id': '12345', 'title': 'Test Auction'}
        record_id = self.auction_crud['insert'](new_record)
        self.assertIsNotNone(record_id)

        # Get by ID
        record = self.auction_crud['get_by_id'](record_id)
        self.assertEqual(record[1], new_record['auction_id'])

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
        # Insert
        new_record = {'item_id': 1, 'product_code': 'ABC123'}
        record_id = self.items_crud['insert'](new_record)
        self.assertIsNotNone(record_id)

        # Get by ID
        record = self.items_crud['get_by_id'](record_id)
        self.assertEqual(record[1], new_record['item_id'])

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

    def test_ebay_demand_crud(self):
        # Insert
        new_record = {'auction_id': '12345', 'search_string': 'Test Search'}
        record_id = self.ebay_demand_crud['insert'](new_record)
        self.assertIsNotNone(record_id)

        # Get by ID
        record = self.ebay_demand_crud['get_by_id'](record_id)
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