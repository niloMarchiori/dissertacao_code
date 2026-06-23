from fastapi import FastAPI,Depends
import os
import subprocess
from pydantic import BaseModel

class Frequency(BaseModel):
    value: float
    cores: str

class Governor(BaseModel):
    governor:str

def call_sensor():
    return RuntimeError("'call_sensor' Not implemented")

def call_network():
    return RuntimeError("'call_network' Not implemented")

def _run_cpupower(args):
    try:
        subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    except Exception:
        pass


def cmd_set_freq(value, cores=None):
    if cores == '':
        _run_cpupower(['sudo', 'cpupower', 'frequency-set', '-d', f'{value}GHz', '-u', f'{value}GHz'])
    else:
        _run_cpupower(['sudo', 'cpupower', '-c', cores, 'frequency-set', '-d', f'{value}GHz', '-u', f'{value}GHz'])


def cmd_set_cpu_governor(governor):
    _run_cpupower(['sudo', 'cpupower', 'frequency-set', '-g', governor])


def cmd_set_upper_freq(value, cores=None):
    if cores == '':
        _run_cpupower(['sudo', 'cpupower', 'frequency-set', '-u', f'{value}GHz'])
    else:
        _run_cpupower(['sudo', 'cpupower', '-c', cores, 'frequency-set', '-u', f'{value}GHz'])


def cmd_set_lower_freq(value, cores=None):
    if cores == '':
        _run_cpupower(['sudo', 'cpupower', 'frequency-set', '-d', f'{value}GHz'])
    else:
        _run_cpupower(['sudo', 'cpupower', '-c', cores, 'frequency-set', '-d', f'{value}GHz'])

app = FastAPI()

@app.get("/")
def read_root(net=Depends(call_network)):
    return {"msg": "Hello from FastAPI!"}

@app.post("/set_cpu_governor")
def set_cpu_governor(governor:Governor):
    governor=governor.governor
    cmd_set_cpu_governor(governor)
    return {"msg": "set Host cpu governor to 'userspace'"}

@app.post("/set_cpufreq/")
def set_freq(freq: Frequency,clients=Depends(call_sensor)):
    value=freq.value
    cores=freq.cores
    cmd_set_freq(value, cores)
    return {"msg": f"SET CPU FREQ={value}"}

@app.post("/set_cpu_upper_freq/")
def set_upper_freq(freq: Frequency,clients=Depends(call_sensor)):
    value=freq.value
    cores=freq.cores
    cmd_set_upper_freq(value, cores)
    return {"msg": f"SET CPU -U FREQ={value}"}

@app.post("/set_cpu_lower_freq/")
def set_lower_freq(freq: Frequency,clients=Depends(call_sensor)):
    value=freq.value
    cores=freq.cores
    cmd_set_lower_freq(value, cores)
    return {"msg": f"SET CPU -D FREQ={value}"}    
