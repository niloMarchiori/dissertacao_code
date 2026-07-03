"""
Módulo compartilhado com código comum entre calibrar_alpha e calibrar_cn.
Contém componentes reutilizáveis como energia, API, topologia e utilitários.
"""

from .energy import EnergyFreqBased
from .api import app, call_sensor, call_network, cmd_set_freq, cmd_set_cpu_governor, cmd_set_upper_freq, cmd_set_lower_freq
from .topo_wired import topology_wired

__all__ = [
    'EnergyFreqBased',
    'app',
    'call_sensor',
    'call_network',
    'cmd_set_freq',
    'cmd_set_cpu_governor',
    'cmd_set_upper_freq',
    'cmd_set_lower_freq',
    'topology_wired'
]
