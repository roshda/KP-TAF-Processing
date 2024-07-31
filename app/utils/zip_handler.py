import zipfile
import os

def extract_zip_contents(zip_path, extract_folder):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)
    print(f"extracted {zip_path} to {extract_folder}")
