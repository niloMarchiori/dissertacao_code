from asyncio import subprocess
from collections import deque

import subprocess
from threading import Thread as thread
from datetime import datetime
from time import sleep

from mininet.log import error


class EnergyFreqBased(object):
    ''' Energy consumption model based on CPU frequency em voltage. 
        Adapted from:
            De Vogeleer, K., et al (2014): The Energy/Frequency Convexity Rule: Modeling
            and Experimental Validation on Mobile Devices.
            https://doi.org/10.1007/978-3-642-55224-3_74
            ---
            T. D. Burd and R. W. Brodersen(1996): "Processor Design for Portable
            Systems"
    '''

    thread_ = None

    def __init__(self, nodes, log_dir='./'):
        import os
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.run_id = datetime.now().strftime("%H%M%S")
        # Histórico das últimas 3 medidas para suavização
        self._freq_history = {node.name: deque(maxlen=3) for node in nodes}
        self._voltage_history = deque(maxlen=3)
        EnergyFreqBased.thread_ = thread(target=self.start, args=(nodes,))
        EnergyFreqBased.thread_.daemon = True
        EnergyFreqBased.thread_._keep_alive = True
        EnergyFreqBased.thread_.start()

    def start(self, nodes):
        try:
            while self.thread_._keep_alive:
                sleep(0.1)
                for node in nodes:
                    if(self.thread_._keep_alive):
                        energy = self.get_energy(node)
                        node.consumption += energy
        except BaseException as e:
            error(f"Energy consumption error: {e}\n")

    def get_cpu_freq(self, node):
        cores=node.resources.get('cpuset_cpus')
        if cores:
            if '-' in cores:
                core_i=int(cores.split('-')[0])
                core_f=int(cores.split('-')[1])
                cores=','.join([str(i) for i in range(core_i, core_f+1)])
            cores = cores.split(',')
            
            all_freq=[]
            for core in cores:
                stdout, stderr, rc = node.pexec(f"cat /sys/devices/system/cpu/cpu{core}/cpufreq/scaling_cur_freq")
                all_freq.append(int(stdout.strip()))
            return all_freq
        else:
            return None

    def get_cpu_voltage(self):
        resultado = subprocess.run(
            'echo "scale=2; $(sudo rdmsr 0x198 -u --bitfield 47:32)/8192" | bc', 
            shell=True, 
            capture_output=True, 
            text=True)
        return float(resultado.stdout.strip())


    def get_energy(self, node, alpha=1E-18, N=4.18E9):
        """
        Calculates power consumption based on voltage, cpu frequency, and hardware constants.

        voltage (float): Processor operating voltage in volts (V).
        frequency (float): Current consumed by the processor in Hz.
        alpha (float): Efetive chip capacitance constant in F (C/V).
        Returns: float: EnergyFreqBased consumed in watt-hours (Wh).
        """
        current_datetime = datetime.now()
        cpus_freqs_raw = self.get_cpu_freq(node)
        cpu_voltage_raw = self.get_cpu_voltage()

        # Armazena medidas no histórico
        self._freq_history[node.name].append(cpus_freqs_raw)
        self._voltage_history.append(cpu_voltage_raw)

        # Calcula média das últimas 3 medidas de frequência (por core)
        freq_hist = list(self._freq_history[node.name])
        num_cores = len(cpus_freqs_raw)
        cpus_freqs = [
            sum(sample[i] for sample in freq_hist) / len(freq_hist)
            for i in range(num_cores)
        ]

        # Calcula média das últimas 3 medidas de tensão
        volt_hist = list(self._voltage_history)
        cpu_voltage = sum(volt_hist) / len(volt_hist)
        
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        node.pexec('echo {} > /tmp/consumption'.format(node.consumption), shell=True)
        node.pexec('echo {} > /tmp/cpu_voltage'.format(cpu_voltage), shell=True)
        node.pexec('echo {} > /tmp/cpus_freqs'.format(cpus_freqs), shell=True)

        freq=sum(cpus_freqs)/len(cpus_freqs)
        
        gamma = getattr(node, 'gamma', None)
        alpha = getattr(node, 'alpha', None)
        
        with open(f'{self.log_dir}/energy_debug.log', 'a') as f:
            f.write(f"[{formatted_datetime}] Node: {node.name} | alpha: {alpha} | cpu_voltage: {cpu_voltage} | freq: {cpus_freqs}\n")

        power = (1+node.gamma*cpu_voltage)*node.alpha*freq*(10**9)*cpu_voltage**2  # Power in watts
        power_converted = power * 0.1 / 3600  # Converts to watt-hours (Wh) considering a 1-second interval
        node.pexec('echo {},{} >> /tmp/consumption-cpu'.format(formatted_datetime, power_converted), shell=True)
        return power_converted
