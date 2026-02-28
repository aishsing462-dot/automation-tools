import os
import time
import shutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
DEST_DIRS = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"],
    "Audio": [".mp3", ".wav", ".aac", ".flac"],
    "Video": [".mp4", ".mov", ".avi", ".mkv"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
    "Executables": [".exe", ".msi"],
}

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

class DownloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        self.organize_files()

    def organize_files(self):
        for filename in os.listdir(DOWNLOADS_DIR):
            filepath = os.path.join(DOWNLOADS_DIR, filename)

            # Skip directories
            if os.path.isdir(filepath):
                continue

            # Get file extension
            extension = os.path.splitext(filename)[1].lower()

            # Find destination category
            moved = False
            for category, extensions in DEST_DIRS.items():
                if extension in extensions:
                    dest_path = os.path.join(DOWNLOADS_DIR, category)

                    # Create category folder if it doesn't exist
                    if not os.path.exists(dest_path):
                        os.makedirs(dest_path)
                        logging.info(f"Created directory: {dest_path}")

                    # Move file
                    try:
                        # Add a small delay to ensure file is completely written
                        time.sleep(1)
                        shutil.move(filepath, os.path.join(dest_path, filename))
                        logging.info(f"Moved {filename} to {category}/")
                        moved = True
                        break
                    except Exception as e:
                        logging.error(f"Error moving {filename}: {e}")

            if not moved and extension:
                logging.info(f"Skipped {filename} (no category for {extension})")

if __name__ == "__main__":
    event_handler = DownloadHandler()
    observer = Observer()
    observer.schedule(event_handler, DOWNLOADS_DIR, recursive=False)

    logging.info(f"Starting Downloads Organizer monitoring: {DOWNLOADS_DIR}")
    # Initial organization
    event_handler.organize_files()

    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
