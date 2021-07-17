import subprocess
import sys

if __name__ == '__main__':
    ec = subprocess.call(['LittleWrapper-c.exe', '-asfasf'], shell=False)
    print(ec)
