import sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from db.db_utils import create_crud_functions

def delete_all_ebay_demand_data():
    ebay_demand_crud = create_crud_functions('ebay_demand_data')
    rows_deleted = ebay_demand_crud['delete_all']()
    print(f"Deleted {rows_deleted} rows from ebay_demand_data")

if __name__ == '__main__':
    delete_all_ebay_demand_data()
