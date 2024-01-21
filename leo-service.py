import sys
import subprocess

module = "service"
try:
    subprocess.check_call([sys.executable, "-m", module])
except subprocess.CalledProcessError as e:
    print(e.returncode)
    print(e.output)