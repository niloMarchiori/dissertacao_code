import re

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
            T. D. Burd and R. W. Brodersen(1996): “Processor Design for Portable
            Systems”
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
        cmd_out = node.pexec("cat /proc/cpuinfo | grep MHz", shell=True)[0]
        try:
            cmd_out_lines = cmd_out.strip().split('\n')
            cmd_out_values = [float(line.split(':')[1].strip()) for line in cmd_out_lines]
            return cmd_out_values
        except:
            return 0


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
