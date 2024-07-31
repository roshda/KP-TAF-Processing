import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLabel, QLineEdit, QFileDialog, QDateTimeEdit, QComboBox
from app.services.intake_service import intake_files
from app.services.processing_service import process_files
from app.services.response_service import generate_response
from app.utils.logger import get_logger
from app.utils.scheduler import schedule_task

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("KP-TAF Processing Tool")

        self.layout = QVBoxLayout()

        # SFTP Configuration
        self.layout.addWidget(QLabel("SFTP Hostname"))
        self.sftp_hostname = QLineEdit()
        self.layout.addWidget(self.sftp_hostname)

        self.layout.addWidget(QLabel("SFTP Port"))
        self.sftp_port = QLineEdit()
        self.layout.addWidget(self.sftp_port)

        self.layout.addWidget(QLabel("SFTP Username"))
        self.sftp_username = QLineEdit()
        self.layout.addWidget(self.sftp_username)

        self.layout.addWidget(QLabel("SFTP Password"))
        self.sftp_password = QLineEdit()
        self.sftp_password.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.sftp_password)

        # Folder Selection
        self.layout.addWidget(QLabel("Local Base Directory"))
        self.local_base_dir = QLineEdit()
        self.layout.addWidget(self.local_base_dir)
        self.select_base_dir_button = QPushButton("Select Base Directory")
        self.select_base_dir_button.clicked.connect(self.select_base_directory)
        self.layout.addWidget(self.select_base_dir_button)

        # Task Scheduling
        self.layout.addWidget(QLabel("Schedule Task"))
        self.schedule_time = QDateTimeEdit()
        self.layout.addWidget(self.schedule_time)
        self.task_type = QComboBox()
        self.task_type.addItems(["Intake", "Processing", "Response"])
        self.layout.addWidget(self.task_type)
        self.schedule_button = QPushButton("Schedule Task")
        self.schedule_button.clicked.connect(self.schedule_task)
        self.layout.addWidget(self.schedule_button)

        # Operations
        self.intake_button = QPushButton("Intake")
        self.intake_button.clicked.connect(self.intake_files)
        self.layout.addWidget(self.intake_button)

        self.processing_button = QPushButton("Processing")
        self.processing_button.clicked.connect(self.process_files)
        self.layout.addWidget(self.processing_button)

        self.response_button = QPushButton("Response")
        self.response_button.clicked.connect(self.generate_response)
        self.layout.addWidget(self.response_button)

        # Log Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.layout.addWidget(self.log_output)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        logger.addHandler(LogHandler(self.log_output))

    def select_base_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Base Directory")
        self.local_base_dir.setText(directory)

    def intake_files(self):
        logger.info("Intake files started...")
        intake_files()
        logger.info("Intake files completed.")

    def process_files(self):
        logger.info("Processing files started...")
        process_files()
        logger.info("Processing files completed.")

    def generate_response(self):
        logger.info("Generating response started...")
        generate_response()
        logger.info("Generating response completed.")

    def schedule_task(self):
        task_time = self.schedule_time.dateTime().toPyDateTime()
        task = self.task_type.currentText()
        logger.info(f"Scheduling {task} task at {task_time}")
        schedule_task(task, task_time, self.sftp_hostname.text(), self.sftp_port.text(), self.sftp_username.text(), self.sftp_password.text(), self.local_base_dir.text())

class LogHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
