import os

SFTP_HOSTNAME = os.getenv('SFTP_HOSTNAME')
SFTP_PORT = int(os.getenv('SFTP_PORT', 22))
SFTP_USERNAME = os.getenv('SFTP_USERNAME')
SFTP_PASSWORD = os.getenv('SFTP_PASSWORD')
LOCAL_BASE_DIR = '/app/data'
