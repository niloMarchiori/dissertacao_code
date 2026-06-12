from topology import topology
import random
import numpy as np


def main(kappa=100):
    NUM_ROUNDS=30
    NUM_CLIENTS=20
    clients_args=[]
    for i in range(NUM_CLIENTS):
        num_samples=10000
        f_min=0.9
        client_args = {'name': f'sta{i}',
                       "mode": 'random same_samples',
                       'num_samples':num_samples,
                       "alpha": 2e-28,
                       "trainer_class": "TrainerMNIST", 
                       "c": random.randint(5, 30),
                       "S": num_samples*43285.45, 
                       "fmin": f_min,
                       "fmax": 3.9,
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

    client_script="flw/calibrar_const/client/client.py"
    server_script="flw/calibrar_const/server/server.py"

    topology(server_script,
             client_script, 
             server_args,
             clients_args,
             cpu_governor='performance',
             experiment_name=experiment_name,
             n_rounds=NUM_ROUNDS)
    
if __name__=='__main__':
    main()