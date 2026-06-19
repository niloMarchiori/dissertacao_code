import os
import sys
import threading
import random
import numpy as np

from pathlib import Path
from time import sleep


from mininet.log import info, setLogLevel

from containernet.cli import CLI

from containernet.energy import Energy
from energy import EnergyFreqBased

from federated.net import MininetFed
from federated.node import Client, Server

from api import app, call_sensor, call_network
from server import api_communication

import uvicorn
import threading


def topology(server_script, client_script, server_args, clients_args, cpu_governor, experiment_name='Experiment', n_rounds=20):
    setLogLevel('info')

    volume = "/flw"
    volumes = [f"{Path.cwd()}:" + volume, "/tmp/.X11-unix:/tmp/.X11-unix:rw"]

    experiment_config = {
        "ipBase": "10.0.0.0/24",
        "experiments_folder": "Experiment",
        "date_prefix": False
    }

    NUM_CLIENTS = len(clients_args)

    net = MininetFed(**experiment_config, controller=[], experiment_name=experiment_name,
                     default_volumes=volumes, broker_mode="internal", topology_file=sys.argv[0])

    path = os.path.dirname(os.path.abspath(__file__))

    info('*** Adding Switch...\n')
    s1 = net.addSwitch("s1", failMode='standalone')

    info('*** Adding Nodes...\n')
    srv1 = net.addHost('srv1', cls=Server, script=server_script,
                         args=server_args,
                         volumes=volumes,
                         dimage='mininetfed:serversensor',
                         privileged=True,
                         clients_args=clients_args
                         )

    clients = []
    for i in range(NUM_CLIENTS):
        client_args = clients_args[i].copy()
        clients.append(net.addHost(f'sta{i}', cls=Client, script=client_script,
                                   privileged=True,
                                   numeric_id=i,
                                   args=client_args.copy(), 
                                   volumes=volumes,
                                   dimage='mininetfed:clientsensor',
                                   cpuset_cpus=client_args.get('cpuset_cpus', '0')
                                   ))

    info('*** Connecting to the MininetFed Devices...\n')
    net.connectMininetFedDevices()

    info('*** Creating wired links...\n')
    net.addLink(srv1, s1)
    for client in clients:
        net.addLink(client, s1)

    info('*** Starting network...\n')
    net.build()
    s1.start([])

    # ----------------------- Inicia API de comunicação host - server ------------------------
    def pass_network():
        if net is None:
            return RuntimeError("'network' Not implemented")
        return net

    def pass_clients():
        if clients is None:
            return RuntimeError("'clients' Not implemented")
        return clients

    app.dependency_overrides[call_network] = pass_network
    app.dependency_overrides[call_sensor] = pass_clients

    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run)
    thread.start()
    sleep(3)
    print("API is running...")
    api_communication.set_cpu_governor(governor=cpu_governor)
    # -----------------------------------------------------------------------------------------

    info("*** Measuring energy consumption\n")
    EnergyFreqBased(net.sensors)

    info('*** Running devices...\n')
    net.runFlDevices()

    info('*** Running broker...\n')

    sleep(1)

    info('*** Server...\n')
    srv1.run(broker_addr=net.broker_addr, experiment_controller=net.experiment_controller)

    sleep(3)

    info('*** Clients...\n')
    for client in clients:
        client.run(broker_addr=net.broker_addr, experiment_controller=net.experiment_controller)

    info('*** Running Autostop...\n')
    net.wait_experiment(start_cli=False)

    os.system('pkill -9 -f xterm')
    info('*** Stopping network...\n')
    net.stop()

    api_communication.set_lower_frequency(freq=0.8)
    api_communication.set_upper_frequency(freq=4.7)
    server.should_exit = True
    thread.join()


if __name__ == '__main__':
    setLogLevel('info')
    NUM_ROUNDS=3
    NUM_CLIENTS=2
    clients_args=[]
    for i in range(NUM_CLIENTS):
        num_samples=random.randint(5000, 30000)
        f_min=np.random.randint(8, 20)/10
        client_args = {'name': f'sta{i}',
                        "mode": 'random same_samples',
                        'num_samples':num_samples,
                        "alpha": 2e-28,
                        "trainer_class": "TrainerMNIST", 
                        "c": random.randint(5, 30),
                        "S": num_samples*43285.45, 
                        "fmin": f_min,
                        "fmax": np.random.randint(f_min*10, 40)/10,
                        "cpuset_cpus": str(i)
                        }
        clients_args.append(client_args)

    #Roda o experimento para D_n diferentes mas todas as classes

    server_args = {"min_trainers": NUM_CLIENTS, 
                    "num_rounds": NUM_ROUNDS,
                    "stop_acc": 0.999, 
                    'client_selector': 'All', 
                    'aggregator': "FedAvg",
                    'clients_args': clients_args,
                    "output_dir_name":'Results/midiid_ref/',
                    "output_csv_name":"metrics_ref_all.csv"}


    experiment_name = 'energy_padrao'

    client_script="/flw/topology_AFEA/client/client.py"
    server_script="/flw/topology_AFEA/server/server.py"
    
    topology(server_script=server_script,
             client_script=client_script,
             server_args=server_args,
             clients_args=clients_args,
             cpu_governor="powersave",
             experiment_name="wired_experiment")