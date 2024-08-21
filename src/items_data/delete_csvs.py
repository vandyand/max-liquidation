import os

def delete_all_csv_files():
    csvs_directory = os.path.join(os.path.dirname(__file__), 'csvs')
    for filename in os.listdir(csvs_directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(csvs_directory, filename)
            os.remove(file_path)
            print(f"Deleted {file_path}")

if __name__ == "__main__":
    delete_all_csv_files()
