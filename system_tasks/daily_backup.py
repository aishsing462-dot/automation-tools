import os
import shutil
import time
from datetime import datetime, timedelta

# Configuration
# Add directories you want to back up here
SOURCE_DIRS = [
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/automation-tools")
]
BACKUP_DEST = os.path.expanduser("~/Backups")
RETENTION_DAYS = 7

import os
import shutil
import time
import stat
from datetime import datetime, timedelta

def on_rm_error(func, path, exc_info):
    # path contains the name of the file
    # set the file to read-write
    os.chmod(path, stat.S_IWRITE)
    func(path)

def create_backup():
    if not os.path.exists(BACKUP_DEST):
        os.makedirs(BACKUP_DEST)
        print(f"Created backup directory: {BACKUP_DEST}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{timestamp}"
    backup_path = os.path.join(BACKUP_DEST, backup_filename)

    # Create a temporary directory to gather files
    temp_dir = os.path.join(BACKUP_DEST, f"temp_{timestamp}")
    os.makedirs(temp_dir)

    try:
        for source in SOURCE_DIRS:
            if os.path.exists(source):
                folder_name = os.path.basename(source)
                dest_folder = os.path.join(temp_dir, folder_name)
                # Ignore junctions and system folders that cause Access Denied
                def ignore_junk(path, names):
                    ignored = []
                    for name in names:
                        full_path = os.path.join(path, name)
                        if os.path.islink(full_path):
                            ignored.append(name)
                        if name.lower() in ["my music", "my pictures", "my videos", "appdata"]:
                            ignored.append(name)
                    return ignored

                shutil.copytree(source, dest_folder, dirs_exist_ok=True, ignore=ignore_junk)
                print(f"Added {source} to backup.")
            else:
                print(f"Warning: Source path {source} does not exist. Skipping.")

        # Compress the temp directory
        shutil.make_archive(backup_path, 'zip', temp_dir)
        print(f"Backup created: {backup_path}.zip")

    finally:
        # Clean up temp directory with error handling for read-only files (like .git objects)
        shutil.rmtree(temp_dir, onerror=on_rm_error)


def cleanup_old_backups():
    now = time.time()
    retention_period = RETENTION_DAYS * 86400 # convert days to seconds

    print(f"Cleaning up backups older than {RETENTION_DAYS} days...")
    for filename in os.listdir(BACKUP_DEST):
        file_path = os.path.join(BACKUP_DEST, filename)
        if os.path.isfile(file_path) and filename.endswith(".zip"):
            file_age = os.path.getmtime(file_path)
            if now - file_age > retention_period:
                os.remove(file_path)
                print(f"Deleted old backup: {filename}")

if __name__ == "__main__":
    print(f"Starting backup process...")
    create_backup()
    cleanup_old_backups()
    print("Backup process complete.")
