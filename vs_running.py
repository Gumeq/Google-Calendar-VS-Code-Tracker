import psutil
import time

def is_vscode_running():
    for process in psutil.process_iter(['pid', 'name']):
        if 'code' in process.info['name'].lower():
            return True
    return False

while True:
    if is_vscode_running():
        print("VS Code is running")
    else:
        print("VS Code is not running")
    time.sleep(5)
