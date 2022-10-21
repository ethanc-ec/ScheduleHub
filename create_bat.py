import sys
from pathlib import Path

def create_bat():
    create = open('SchHub.bat', 'w+')

    with open('SchHub.bat', 'w+') as bat:
        python_path = sys.exec_prefix + '\python.exe'
        bat.write(f'@echo off\n"{python_path}" "{Path(__file__).parent.absolute()}\schedule_hub.py"\npause')

    return None