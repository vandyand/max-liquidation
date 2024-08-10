import os
import sys
import json
import pandas as pd

# Add the src directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from db.db_utils import create_crud_functions, create_db_connection

def delete_items_data_csv():
    csvs_directory = os.path.join(os.path.dirname(__file__), 'csvs')
    for filename in os.listdir(csvs_directory):
        if filename.endswith("items_data.csv"):
            file_path = os.path.join(csvs_directory, filename)
            os.remove(file_path)
            print(f"Deleted {file_path}")

def main():
    # Load the CSV file into a DataFrame
    csv_file_path = os.path.join(os.path.dirname(__file__), 'csvs', 'items_data.csv')
    df = pd.read_csv(csv_file_path)

    # Replace NaN values with None
    df = df.where(pd.notnull(df), None)

    # Ensure all NaN values are converted to None
    df = df.map(lambda x: None if pd.isna(x) else x)

    # Create a connection to the database
    conn = create_db_connection()

    # Create CRUD functions for the items_data table
    items_crud = create_crud_functions('items_data')

    # Iterate over each row in the DataFrame and insert it into the database
    for _, row in df.iterrows():
        record = {
            'auction_id': row['auction_id'],
            'data': json.dumps(row.to_dict())
        }
        items_crud['insert_or_ignore'](record, conn)

    # Close the database connection
    if conn:
        conn.close()

    delete_items_data_csv()

if __name__ == '__main__':
    main()