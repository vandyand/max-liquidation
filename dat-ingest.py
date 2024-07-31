import pandas as pd
import glob
import os

# Function to normalize a dataframe
def normalize_dataframe(df, all_columns, auction_id):
    # Add the auction_id column
    df['auction_id'] = auction_id
    
    # Add missing columns with default values
    for col in all_columns:
        if col not in df.columns:
            df[col] = None
    
    # Ensure the dataframe has all columns in the same order, with auction_id first
    return df[['auction_id'] + all_columns]

# Read all CSV files and collect all unique columns
all_columns = set()
dataframes = []

for file in glob.glob("csvs/*.csv"):
    try:
        df = pd.read_csv(file)
        
        # Extract auction_id from filename
        auction_id = os.path.basename(file).replace("m", "").replace(".csv", "")
        
        # Print statement for each file
        print(f"Processing file {file} with auction_id {auction_id}")
        
        all_columns.update(df.columns)
        dataframes.append((df, auction_id))
    except Exception as e:
        print(f"Error processing file {file}: {e}")

# Convert the set of all columns to a sorted list
all_columns = sorted(all_columns)

# Normalize all dataframes to have the same columns
normalized_dataframes = [normalize_dataframe(df, all_columns, auction_id) for df, auction_id in dataframes]

# Concatenate all dataframes into one
if normalized_dataframes:
    final_df = pd.concat(normalized_dataframes, ignore_index=True)
    
    # Add an auto-incrementing "id" column
    final_df.insert(0, 'id', range(1, len(final_df) + 1))
    
    # Save the standardized data to a new CSV file
    final_df.to_csv("standardized_data.csv", index=False)
else:
    print("No data to save.")