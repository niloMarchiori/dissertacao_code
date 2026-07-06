import sys
import os
# Adiciona o diretório raiz ao path para importar módulos compartilhados
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np

from shared.topo_wired import topology_wired as topology
from server import api_communication
import json

NUM_ROUNDS=70

with open('topology_afea/sta_const.json') as f:
    sta_const = json.load(f)

NUM_CLIENTS=sta_const['N']

clients_args=[]
for i in range(NUM_CLIENTS):
    client_args = {'name': f'sta{i}',
                    "mode": 'random same_samples',
                    "trainer_class": "TrainerMNIST", 
                    'num_samples':sta_const['num_samples'][i],
                    "alpha": sta_const['alpha'][i],
                    "gamma": sta_const['gamma'][i],
                    "c": sta_const['c'][i],
                    "S": sta_const['num_samples'][i]*43285.45, 
                    "fmin": sta_const['f_min'][i],
                    "fmax": sta_const['f_max'][i],
                    "cpuset_cpus": f'{i},{23-i}'
                    }
    clients_args.append(client_args)

#Roda o experimento para D_n diferentes mas todas as classes

server_args = {"min_trainers": NUM_CLIENTS, 
                "num_rounds": NUM_ROUNDS,
                "stop_acc": 0.999, 
                'client_selector': 'All', 
                'aggregator': "FedAvg",
                'clients_args': clients_args,
                "output_dir_name":'Results/iid_afea/',
                "output_csv_name":"metrics_afea.csv"}


experiment_name = 'energy_padrao'

client_script="flw/topology_afea/client/client.py"
server_script="flw/topology_afea/server/server.py"

topology(server_script,
        client_script, 
        server_args,
        clients_args,
        api_communication=api_communication,
        cpu_governor='performance',
        experiment_name=experiment_name,
        n_rounds=NUM_ROUNDS)
