import os
import shutil
from app.utils.xml_handler import update_xml_recipient_status, create_hdr_file, rename_and_zip_return_files
from app.utils.sftp_client import sftp_upload
from datetime import datetime
from tkinter import filedialog, Tk

def select_directory(title="Select Folder"):
    root = Tk()
    root.withdraw()
    selected_directory = filedialog.askdirectory(title=title)
    return selected_directory

def process_order_folder(root_dir, order_folder, status, subfolder_reason, entries, dated_folder_path):
    order_path = os.path.join(root_dir, order_folder)
    if os.path.isdir(order_path):
        order_id = order_folder[:8]
        reason = subfolder_reason if status in ['Pending', 'Stopped'] else None

        # Process XML files
        xml_files = [f for f in os.listdir(order_path) if f.endswith(".xml")]
        if xml_files:
            original_xml_file = os.path.join(order_path, xml_files[0])
            xml_copy_file = os.path.join(order_path, f"Copied_{os.path.basename(original_xml_file)}")
            shutil.copyfile(original_xml_file, xml_copy_file)
            tree = update_xml_recipient_status(xml_copy_file, status, reason)
            tree.write(xml_copy_file)
            completed_xml_path = os.path.join(dated_folder_path, os.path.basename(xml_copy_file))
            shutil.move(xml_copy_file, completed_xml_path)
            print(f"Processed and moved XML: {completed_xml_path}")

        # Add entry to HDR file
        entries.append({'date': datetime.now().strftime('%Y-%m-%d'), 'order_id': order_id, 'status': status})
        if status == 'Ready':
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
            zip_filepath, done_filepath = rename_and_zip_return_files(order_path, order_id, timestamp, original_xml_file)
            shutil.copy(zip_filepath, dated_folder_path)
            shutil.copy(done_filepath, dated_folder_path)
            print(f"Created and copied ZIP and DONE files: {zip_filepath}, {done_filepath}")

def process_orders(base_path):
    status_folders = ['Pending', 'Ready', 'Received', 'Shipped', 'Stopped']
    entries = []
    completed_path = os.path.join(base_path, 'Status Updates', 'completed')

    current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
    dated_folder_path = os.path.join(completed_path, current_datetime)
    os.makedirs(dated_folder_path, exist_ok=True)

    ready_folders_to_move = []

    for status in status_folders:
        status_path = os.path.join(base_path, 'Status Updates', status)
        for root_dir, dirs, files in os.walk(status_path):
            if status in ['Pending', 'Stopped']:
                for subfolder in dirs:
                    subfolder_path = os.path.join(root_dir, subfolder)
                    if os.path.isdir(subfolder_path):
                        for order_folder in os.listdir(subfolder_path):
                            if order_folder[:8].isdigit():
                                process_order_folder(subfolder_path, order_folder, status, subfolder, entries, dated_folder_path)
            else:
                if os.path.basename(root_dir) in status_folders:
                    for order_folder in dirs:
                        if order_folder[:8].isdigit():
                            process_order_folder(root_dir, order_folder, status, None, entries, dated_folder_path)
                            if status == 'Ready':
                                ready_folders_to_move.append(os.path.join(root_dir, order_folder))

    hdr_filename = create_hdr_file(entries, 'ACCESS')
    hdr_output_path = os.path.join(dated_folder_path, hdr_filename)
    shutil.move(hdr_filename, hdr_output_path)
    print(f"Created and moved HDR file: {hdr_output_path}")

    for root, _, files in os.walk(dated_folder_path):
        for file in files:
            if file.startswith("Copied_") and file.endswith(".xml"):
                original_file_path = os.path.join(root, file)
                new_file_path = os.path.join(root, file.replace("Copied_", ""))
                os.rename(original_file_path, new_file_path)
                print(f"Renamed {original_file_path} to {new_file_path}")

    return dated_folder_path, ready_folders_to_move

def move_ready_folders(ready_folders_to_move):
    for order_path in ready_folders_to_move:
        order_folder = os.path.basename(order_path)
        ready_done_path = os.path.join(os.path.dirname(order_path), 'done')
        os.makedirs(ready_done_path, exist_ok=True)
        dest_path = os.path.join(ready_done_path, order_folder)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(ready_done_path, f"{order_folder}_{counter}")
            counter += 1
        shutil.move(order_path, dest_path)
        print(f"Moved order folder {order_folder} to {dest_path}")

def generate_response():
    base_path = select_directory("Select the local base directory")
    completed_path, ready_folders_to_move = process_orders(base_path)
    sftp_upload(completed_path, '/KP-TAF/Production/From Vendor Outbox')
    move_ready_folders(ready_folders_to_move)
