import psutil
import shutil
import logging
import os
from datetime import datetime

# Configuration
CPU_THRESHOLD = 80.0  # Percent
MEMORY_THRESHOLD = 85.0  # Percent
DISK_THRESHOLD = 90.0  # Percent
LOG_FILE = os.path.expanduser("~/Documents/system_health.log")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def check_cpu():
    usage = psutil.cpu_percent(interval=1)
    if usage > CPU_THRESHOLD:
        logging.warning(f"High CPU usage detected: {usage}%")
    return usage

def check_memory():
    memory = psutil.virtual_memory()
    if memory.percent > MEMORY_THRESHOLD:
        logging.warning(f"High Memory usage detected: {memory.percent}%")
    return memory.percent

def check_disk():
    disk = psutil.disk_usage('/')
    if disk.percent > DISK_THRESHOLD:
        logging.warning(f"Low Disk space detected: {disk.percent}% used")
    return disk.percent

def check_battery():
    battery = psutil.sensors_battery()
    if battery:
        percent = battery.percent
        plugged = battery.power_plugged
        status = "Plugged in" if plugged else "On battery"
        if not plugged and percent < 20:
            logging.warning(f"Low Battery detected: {percent}% ({status})")
        return f"{percent}% ({status})"
    return "No battery detected"

def generate_report():
    print(f"\n--- System Health Report ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
    print(f"CPU Usage:    {check_cpu()}%")
    print(f"Memory Usage: {check_memory()}%")
    print(f"Disk Usage:   {check_disk()}%")
    print(f"Battery:      {check_battery()}")
    print(f"Log file:     {LOG_FILE}")
    print("---------------------------------------------------\n")

if __name__ == "__main__":
    generate_report()
