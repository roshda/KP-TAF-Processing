import paramiko
from config import SFTP_HOSTNAME, SFTP_PORT, SFTP_USERNAME, SFTP_PASSWORD

def connect_sftp():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SFTP_HOSTNAME, port=SFTP_PORT, username=SFTP_USERNAME, password=SFTP_PASSWORD)
    return client.open_sftp()

def upload_file(sftp, local_path, remote_path):
    sftp.put(local_path, remote_path)
    print(f"Uploaded {local_path} to {remote_path}")

def download_file(sftp, remote_path, local_path):
    sftp.get(remote_path, local_path)
    print(f"Downloaded {remote_path} to {local_path}")
