
import numpy as np

from topo_wired import topology_wired as topology
import json

NUM_ROUNDS=3

with open('topology_ref/sta_const.json') as f:
    sta_const = json.load(f)

NUM_CLIENTS=sta_const['N']

clients_args=[]
for i in range(NUM_CLIENTS):
    client_args = {'name': f'sta{i}',
                    "mode": 'random same_samples',
                    "trainer_class": "TrainerMNIST", 
                    'num_samples':sta_const['num_samples'][i],
                    "alpha": sta_const['alpha'][i],
                    "c": sta_const['c'][i],
                    "S": sta_const['num_samples'][i]*43285.45, 
                    "fmin": sta_const['f_min'][i],
                    "fmax": sta_const['f_max'][i],
                    "cpuset_cpus": str(i)
                    }
    clients_args.append(client_args)

#Roda o experimento para D_n diferentes mas todas as classes

server_args = {"min_trainers": NUM_CLIENTS, 
                "num_rounds": NUM_ROUNDS,
                "stop_acc": 0.999, 
                'client_selector': 'LeastEnergyConsumption', 
                'aggregator': "FedAvg",
                'clients_args': clients_args,
                "output_dir_name":'Results/iid_leastEnergy/',
                "output_csv_name":"metrics_leastEnergy_all.csv"}


experiment_name = 'energy_padrao'

client_script="flw/topology_ref/client/client.py"
server_script="flw/topology_ref/server/server.py"

topology(server_script,
            client_script, 
            server_args,
            clients_args,
            cpu_governor='performance',
            experiment_name=experiment_name,
            n_rounds=NUM_ROUNDS)
