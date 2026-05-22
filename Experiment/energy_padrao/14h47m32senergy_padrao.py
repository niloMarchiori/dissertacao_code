from topology import topology
import random
import numpy as np


def main(kappa=100):
    NUM_ROUNDS=60
    NUM_CLIENTS=6
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
                       "D": num_samples*43285.45, 
                       "fmin": f_min,
                       "fmax": np.random.randint(f_min*10, 40)/10,
                       "cpuset_cpus": str(i)
                       }
        clients_args.append(client_args)
        
    model_inputs= {"kappa": kappa,
                "N": NUM_CLIENTS,
                "alpha": 2e-28,
                "num_samples":[6000,12000,15000,15000,8000,4000],
                "D": [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
                "c": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                "fmin": [1300000000.0, 1300000000.0, 1300000000.0, 1300000000.0, 1300000000.0, 1300000000.0],
                "fmax": [2300000000, 2900000000, 2700000000, 2500000000, 2100000000, 2100000000]
                }
    
    #Roda o experimento para D_n diferentes mas todas as classes

    server_args = {"min_trainers": NUM_CLIENTS, 
                   "num_rounds": NUM_ROUNDS,
                   "stop_acc": 0.999, 
                   'client_selector': 'All', 
                   'aggregator': "FedAvg", 
                   "model_inputs": model_inputs,
                   "output_dir_name":'Results/midiid_ref/',
                   "output_csv_name":"metrics_ref_all.csv"}

    experiment_name = 'energy_padrao'

    client_script="flw/topology_ref/client/client_ref.py"
    
   
    server_args["output_csv_name"]="metrics_ref_all_n7.csv"
    server_script="flw/topology_ref/server/server_ref.py"
    topology(server_script,
             client_script, 
             server_args,
             clients_args,
             model_inputs,
             cpu_governor='performance',
             experiment_name=experiment_name,
             n_rounds=NUM_ROUNDS)
    
if __name__=='__main__':
    main()