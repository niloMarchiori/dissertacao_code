from topology import topology


def main(kappa=100):
    NUM_ROUNDS=60
    NUM_CLIENTS=6
    stop_acc=0.99
    model_inputs= {"N": NUM_CLIENTS,
                "alpha": 2e-28,
                "num_samples":[6000,12000,15000,15000,8000,4000],
                "S": [259700928, 519401856, 649277568, 649277568, 346301568, 173150784],
                "c": [9, 5, 4, 4, 8, 11],
                "f_min": [1300000000.0, 1300000000.0, 1300000000.0, 1300000000.0, 1300000000.0, 1300000000.0],
                "f_max": [2300000000, 2900000000, 2700000000, 2500000000, 2100000000, 2100000000],
                'epsilon_0': stop_acc,
                'theta_prev': [0.1]*NUM_CLIENTS
                }

    server_args = {"min_trainers": NUM_CLIENTS, 
                   "num_rounds": NUM_ROUNDS,
                   "stop_acc": stop_acc, 
                   'client_selector': 'All', 
                   'aggregator': "FedAvg", 
                   "model_inputs": model_inputs,
                   "output_dir_name":'Results/midiid_sbpo/',
                   "output_csv_name":"metrics_sbpo.csv"}
    
    
    client_args = {"mode": 'random same_samples',
                   'num_samples':15000,
                   "trainer_class": "TrainerMNIST"}

    experiment_name = 'SBPO'

    client_script="flw/topology_sbpo/client/client_sbpo.py"
    
    #Corresponde as saidas com valores otimizados
    server_script="flw/topology_sbpo/server/server_sbpo.py"
    topology(server_script,
             client_script, 
             server_args,
             client_args,
             model_inputs,
             cpu_governor='userspace',
             experiment_name=experiment_name,
             n_rounds=NUM_ROUNDS)
if __name__=='__main__':
    main()