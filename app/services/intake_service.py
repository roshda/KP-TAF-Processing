from app.utils.sftp_client import connect_sftp, download_file
from app.utils.zip_handler import extract_zip_contents
from app.utils.config import LOCAL_BASE_DIR
from pathlib import Path
import datetime

def intake_files():
    sftp = connect_sftp()
    sftp.chdir('/KP-TAF/Testing/To Vendor Inbox')
    files = sftp.listdir()
    zip_files = [file for file in files if file.endswith('.zip')]

    today_str = datetime.datetime.now().strftime('%m.%d')
    local_day_dir = Path(LOCAL_BASE_DIR) / today_str
    local_day_dir.mkdir(parents=True, exist_ok=True)

    for zip_file in zip_files:
        local_zip_path = local_day_dir / zip_file
        download_file(sftp, zip_file, str(local_zip_path))
        extract_zip_contents(local_zip_path, local_day_dir)
    
    sftp.close()
