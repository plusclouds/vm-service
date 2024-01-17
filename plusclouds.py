import sys
import subprocess as sp
import platform

def update(module: str) -> None:
    sp.check_call([sys.executable,'-m','pip','install',module,'--upgrade'])

def install(module: str) -> None:
    sp.check_call([sys.executable, "-m","pip","install",module])

def check_module(module: str, os: str) -> bool:
    if os == 'Linux':
        if len(sp.getoutput(sys.executable + " -m pip freeze | grep " + module)):
            return True
    elif os == 'Windows':
        if len(sp.getoutput(sys.executable + " -m pip freeze | Findstr " + module)):
            return True
    return False

def execute_module(module: str, os: str) -> None:
    if check_module(module, os):
        if os == 'Linux':
            sp.check_call([sys.executable, "-m",module])
        else:
            sp.check_call([sys.executable, "-m",module])
    else:
        install(module)

OS = platform.system()        
MODULE_NAME = "plusclouds-service"      
execute_module(MODULE_NAME,OS)