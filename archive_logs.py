import os
import shutil
from datetime import datetime

LOG_FILE = 'debug.log'
ARCHIVE_DIR = 'Archived Debug Logs'
MAX_SIZE = 2 * 1024 * 1024  # 2 MB
SEQUENCE_FILE = 'last_sequence.txt'  # File to store the last sequence number

def get_next_archive_file():
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

    if os.path.exists(SEQUENCE_FILE):
        with open(SEQUENCE_FILE, 'r') as file:
            sequence_number = int(file.read().strip()) + 1
    else:
        sequence_number = 1

    timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M-%S-%p")
    archive_file = os.path.join(ARCHIVE_DIR, f"debug{sequence_number} - {timestamp}.log")
    return archive_file, sequence_number

def update_sequence_file(sequence_number):
    with open(SEQUENCE_FILE, 'w') as file:
        file.write(str(sequence_number))

def archive_log():
    archive_file, sequence_number = get_next_archive_file()
    shutil.move(LOG_FILE, archive_file)
    update_sequence_file(sequence_number)
    print(f"Archived log to {archive_file}")

def check_log_size():
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_SIZE:
        archive_log()

if __name__ == "__main__":
    check_log_size()
