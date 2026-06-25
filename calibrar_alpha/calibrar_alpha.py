from topo_wired import topology_wired as topology
import random
import numpy as np



NUM_ROUNDS=3
NUM_CLIENTS=11
clients_args=[]
for i in range(NUM_CLIENTS):
    num_samples=10000
    client_args = {'name': f'sta{i}',
                    "mode": 'random same_samples',
                    'num_samples':num_samples,
                    "alpha": 2e-28,
                    "trainer_class": "TrainerMNIST", 
                    "c": random.randint(5, 30),
                    "S": num_samples*43285.45, 
                    "fmin": 0.9,
                    "fmax": 3.9,
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
                "output_dir_name":'Results/calibrar_alpha/',
                "output_csv_name":"calibrar_alpha.csv"}


experiment_name = 'calibrar_alpha'

client_script="flw/calibrar_alpha/client/client.py"
server_script="flw/calibrar_alpha/server/server.py"

topology(server_script,
            client_script, 
            server_args,
            clients_args,
            cpu_governor='performance',
            experiment_name=experiment_name,
            n_rounds=NUM_ROUNDS)