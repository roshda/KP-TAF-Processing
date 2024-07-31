import os
import re
import shutil
from tkinter import filedialog, Tk
from app.utils.archiver import archive_folder, move_folders_to_status_updates

def select_directory(title="Select Folder"):
    root = Tk()
    root.withdraw()
    selected_directory = filedialog.askdirectory(title=title)
    return selected_directory

def process_files():
    base_path = select_directory("Select the local base directory")
    day_folders = [f for f in os.listdir(base_path) if re.match(r'^\d{2}\.\d{2}$', f)]
    
    for day_folder in day_folders:
        day_folder_full_path = os.path.join(base_path, day_folder)
        archive_destination = archive_folder(base_path, day_folder)
        shutil.copytree(day_folder_full_path, archive_destination)
        move_folders_to_status_updates(base_path, day_folder)
