from topology import topology


def main(kappa=100):
    NUM_ROUNDS=15
    NUM_CLIENTS=6
    model_inputs= {"kappa": kappa,
                "N": NUM_CLIENTS,
                "alpha": 2e-28,
                "num_samples":[10000,10000,10000,10000,10000,10000],
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
                   "output_dir_name":'Results_iid/',
                   "output_csv_name":"metrics_opt.csv"}

    client_args = {"mode": 'all same_samples','num_samples':15000,"trainer_class": "TrainerMNIST"}
    experiment_name = 'all_same_samples'

    client_script="flw/topology/client/client.py"
    
    #Corresponde as saidas com valores otimizados
    server_script="flw/topology/server/server_opt.py"
    topology(server_script,
             client_script, 
             server_args,
             client_args,
             model_inputs,
             cpu_governor='userspace',
             experiment_name=experiment_name,
             n_rounds=NUM_ROUNDS)


    #Corresponde as saidas com valores NAO otimizados
    server_args["output_csv_name"]="metrics_ref_all.csv"
    server_script="flw/topology/server/server_ref.py"
    topology(server_script,
             client_script, 
             server_args,
             client_args,
             model_inputs,
             cpu_governor='ondemand',
             experiment_name=experiment_name,
             n_rounds=NUM_ROUNDS)
    
    #Corresponde a saída do algoritmo apresentado no sbrc
    server_args["output_csv_name"]="metrics_ref_sbrc.csv"
    server_args['client_selector']='LeastEnergyConsumption'
    topology(server_script,
             client_script, 
             server_args,
             client_args,
             model_inputs,
             cpu_governor='ondemand',
             experiment_name=experiment_name,
             n_rounds=NUM_ROUNDS)
    
    

if __name__=='__main__':
    main()