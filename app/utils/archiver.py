import os
import shutil

def archive_folder(base_path, day_folder):
    archive_path = os.path.join(base_path, 'Archive')
    if not os.path.exists(archive_path):
        os.makedirs(archive_path)
    archived_day_path = os.path.join(archive_path, day_folder)
    
    counter = 1
    while os.path.exists(archived_day_path):
        archived_day_path = os.path.join(archive_path, f"{day_folder}_{counter}")
        counter += 1

    return archived_day_path

def move_folders_to_status_updates(base_path, day_folder):
    status_update_path = os.path.join(base_path, 'Status Updates')
    day_folder_path = os.path.join(base_path, day_folder)

    for folder in os.listdir(day_folder_path):
        folder_path = os.path.join(day_folder_path, folder)
        if os.path.isdir(folder_path):
            shutil.move(folder_path, status_update_path)
