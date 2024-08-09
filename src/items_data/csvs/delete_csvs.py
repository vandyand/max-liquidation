import os

def delete_csv_files():
    current_directory = os.path.dirname(__file__)
    for filename in os.listdir(current_directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(current_directory, filename)
            os.remove(file_path)
            print(f"Deleted {file_path}")

if __name__ == '__main__':
    delete_csv_files()
