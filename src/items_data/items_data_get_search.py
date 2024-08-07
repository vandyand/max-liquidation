import pandas as pd

# Load the standardized data CSV file into a DataFrame
df = pd.read_csv('items_data.csv')

# Define the columns to be concatenated
columns_to_concat = ["ASIN", "Description", "FNSku", "Product", "UPC"]

# Function to create the search string
def create_search_string(row):
    return ' '.join(str(row[col]) for col in columns_to_concat if pd.notna(row[col]))

# Apply the function to each row to create the new 'search' column
df['search'] = df.apply(create_search_string, axis=1)

# Save the updated DataFrame back to the CSV file
df.to_csv('items_data.csv', index=False)