import os
import sys
import json
import pandas as pd

# Add the src directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from db.db_utils import create_crud_functions, create_connection

def main():
    # Load the CSV file into a DataFrame
    csv_file_path = os.path.join(os.path.dirname(__file__), 'csvs', 'items_data.csv')
    df = pd.read_csv(csv_file_path)

    # Replace NaN values with None
    df = df.where(pd.notnull(df), None)

    # Create a connection to the database
    conn = create_connection()

    # Create CRUD functions for the items_data table
    items_crud = create_crud_functions('items_data')

    # Iterate over each row in the DataFrame and insert it into the database
    for _, row in df.iterrows():
        record = {
            'auction_id': row['auction_id'],
            'data': json.dumps(row.to_dict())
        }
        items_crud['insert'](record, conn)

    # Close the database connection
    if conn:
        conn.close()

if __name__ == '__main__':
    main()