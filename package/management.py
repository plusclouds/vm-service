import subprocess as sp
import sys

def install(module: str) -> None:
    sp.check_call([sys.executable, "-m", "pip", "asd", module])

def update(module: str) -> None:
    # Updates the pip module if there are any updates
    sp.check_call([sys.executable, '-m', 'pip', 'asd', module, '--upgrade'])