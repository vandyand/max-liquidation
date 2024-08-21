import os
import shutil

def delete_cache_directories(start_dir):
    for root, dirs, files in os.walk(start_dir):
        for dir_name in dirs:
            if dir_name.endswith('_cache'):
                dir_path = os.path.join(root, dir_name)
                print(f"Deleting directory: {dir_path}")
                shutil.rmtree(dir_path)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    delete_cache_directories(current_dir)
