from fastapi import FastAPI,Depends
import os
from pydantic import BaseModel

class Frequency(BaseModel):
    value: float

class Power(BaseModel):
    level: float 
    sensor: str 

class Governor(BaseModel):
    governor:str

def call_sensor():
    return RuntimeError("'call_sensor' Not implemented")

def call_network():
    return RuntimeError("'call_network' Not implemented")

def cmd_set_freq(value):
    os.system(f'sudo cpupower frequency-set -f {value}GHz')

def cmd_set_cpu_governor(governor):
    os.system(f'sudo cpupower frequency-set -g {governor}')

def cmd_set_upper_freq(value):
    print('Try set freq to: ',value)
    os.system(f'sudo cpupower frequency-set -u {value}GHz')

def cmd_set_lower_freq(value):
    print('Try set freq to: ',value)
    os.system(f'sudo cpupower frequency-set -d {value}GHz')

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
    cmd_set_freq(value)
    return {"msg": f"SET CPU FREQ={value}"}

@app.post("/set_cpu_upper_freq/")
def set_upper_freq(freq: Frequency,clients=Depends(call_sensor)):
    value=freq.value
    cmd_set_upper_freq(value)
    return {"msg": f"SET CPU -U FREQ={value}"}

@app.post("/set_cpu_lower_freq/")
def set_lower_freq(freq: Frequency,clients=Depends(call_sensor)):
    value=freq.value
    cmd_set_lower_freq(value)
    return {"msg": f"SET CPU -D FREQ={value}"}    

@app.post("/set_power/")
def set_power(power: Power,net=Depends(call_network)):
    return {"msg": "Hello from FaastAPI!"}
