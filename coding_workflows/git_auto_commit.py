import os
import subprocess
from datetime import datetime

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e.stderr}")
        return None

def git_auto_commit():
    # Check if we are in a git repository
    if not os.path.exists(".git"):
        print("Error: Not a git repository.")
        return

    # Check for changes
    status = run_command("git status --short")
    if not status:
        print("No changes to commit.")
        return

    print("Staging changes...")
    run_command("git add -A")

    # Generate a message based on modified files
    diff_stat = run_command("git diff --cached --stat")

    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Auto-commit: {today}\n\nSummary of changes:\n{diff_stat}"

    print(f"Committing changes with message:\n{commit_msg}")

    # Use a temporary file for the commit message to handle multi-line messages safely
    with open("temp_commit_msg.txt", "w") as f:
        f.write(commit_msg)

    run_command("git commit -F temp_commit_msg.txt")
    os.remove("temp_commit_msg.txt")

    print("Successfully committed changes.")

if __name__ == "__main__":
    git_auto_commit()
