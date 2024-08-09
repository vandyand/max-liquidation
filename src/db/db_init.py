import sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

import sqlite3
from dotenv import load_dotenv
from db_table_schemas import sitemap_table_schema, auction_data_table_schema, items_data_table_schema, ebay_demand_data_table_schema, sql_drop_tables

load_dotenv()

# Create a database connection
def create_connection():
    db_file = os.getenv('DB_PATH')
    if os.getenv('USE_TEST_DB') == 'true':
        db_file = os.getenv('TEST_DB_PATH')
    print(db_file)
    conn = None
    
    try:
        conn = sqlite3.connect(db_file)
        print(f'Connected to {db_file}')
    except sqlite3.Error as e:
        print(e)
    
    return conn

# Execute multiple SQL statements
def execute_statements(conn, statements):
    try:
        cursor = conn.cursor()
        
        for statement in statements.strip().split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
    except sqlite3.Error as e:
        print(e)

# Create tables
def create_tables():
    conn = create_connection()
    
    if conn is None:
        print("Error: Database connection is not established.")
        return

    try:
        execute_statements(conn, sql_drop_tables)
        execute_statements(conn, sitemap_table_schema)
        execute_statements(conn, auction_data_table_schema)
        execute_statements(conn, items_data_table_schema)
        execute_statements(conn, ebay_demand_data_table_schema)
    finally:
        conn.close()

if __name__ == '__main__':
    create_tables()