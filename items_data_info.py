import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv('items_data.csv')

# Display basic information about the DataFrame
print("DataFrame Info:")
print(df.info())

print("\nDataFrame Description:")
print(df.describe())

# Calculate and display additional metrics
print("\nMissing Values:")
print(df.isnull().sum())

print("\nUnique Values per Column:")
print(df.nunique())

# Example of calculating a specific metric (mean) for a specific column
# Replace 'column_name' with the actual column name you are interested in
# print("\nMean of column_name:")
# print(df['column_name'].mean())