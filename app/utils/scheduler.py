import schedule
import time
import threading
from app.services.intake_service import intake_files
from app.services.processing_service import process_files
from app.services.response_service import generate_response
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger(__name__)

def schedule_task(task, task_time, hostname, port, username, password, base_dir):
    schedule_time_str = task_time.strftime("%Y-%m-%d %H:%M:%S")
    
    def task_runner():
        logger.info(f"running scheduled task: {task} at {datetime.now()}")
        if task == "intake":
            intake_files()
        elif task == "processing":
            process_files()
        elif task == "response":
            generate_response()

    if datetime.now() > task_time:
        logger.error("scheduled time is in the past; please select a future time:")
    else:
        schedule.every().day.at(task_time.strftime("%H:%M:%S")).do(task_runner)
        logger.info(f"task {task} scheduled for {schedule_time_str}")

    def run_continuously(interval=1):
        cease_continuous_run = threading.Event()

        class ScheduleThread(threading.Thread):
            @classmethod
            def run(cls):
                while not cease_continuous_run.is_set():
                    schedule.run_pending()
                    time.sleep(interval)

        continuous_thread = ScheduleThread()
        continuous_thread.start()
        return cease_continuous_run

    run_continuously()
