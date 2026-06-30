from asyncio import subprocess
import re

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

    def __init__(self, nodes):
        EnergyFreqBased.thread_ = thread(target=self.start, args=(nodes,))
        EnergyFreqBased.thread_.daemon = True
        EnergyFreqBased.thread_._keep_alive = True
        EnergyFreqBased.thread_.start()

    def start(self, nodes):
        try:
            while self.thread_._keep_alive:
                sleep(0.1)  # set sleep time to 1 second
                for node in nodes:
                    if(self.thread_._keep_alive):
                        node.consumption += self.get_energy(node)
        except:
            error("Error with the energy consumption function\n")

    def get_cpu_freq(self, node):
        cores=node.resources.get('cpuset_cpus')
        if cores:
            if '-' in cores:
                core_i=int(cores.split('-')[0])
                core_f=int(cores.split('-')[1])
                cores=','.join([str(i) for i in range(core_i, core_f+1)])
            cores.split(',')
            
            all_freq=[]
            for core in cores:
                all_freq.append(int(node.pexec("cat /sys/devices/system/cpu/cpu{core}/cpufreq/scaling_cur_freq")))
            return all_freq
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
        frequency (float): Current consumed by the processor in MHz.
        alpha (float): Chip capacitance constant in F (C/V).
        N (int): Number of transistors in cpu core
        Returns: float: EnergyFreqBased consumed in watt-hours (Wh).
        """
        current_datetime = datetime.now()
        cpus_freqs = self.get_cpu_freq(node)
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        node.pexec('echo {} > /tmp/consumption'.format(node.consumption), shell=True)
        power = sum([N*alpha * freq * 1E6 * node.voltage**2 for freq in cpus_freqs])  # Power in watts
        power_converted = power * 0.1 / 3600  # Converts to watt-hours (Wh) considering a 1-second interval
        node.pexec('echo {},{} >> /tmp/consumption-cpu'.format(formatted_datetime, power_converted), shell=True)
        return power_converted
