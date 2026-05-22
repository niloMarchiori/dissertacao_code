import os
import sys

from topology_ref.server import api_communication
from topology_ref.api import app, call_sensor, call_network
from .server import clientSelection