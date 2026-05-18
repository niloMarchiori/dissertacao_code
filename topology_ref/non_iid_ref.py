from topology import topology


def main(kappa=100):
    NUM_ROUNDS=60
    NUM_CLIENTS=6
    model_inputs= {"kappa": kappa,
                "N": NUM_CLIENTS,
                "alpha": 2e-28,
                "num_samples":[6000, 10000, 15000, 12000, 8000, 4000],
                "D": [259700928, 519401856, 649277568, 649277568, 346301568, 173150784],
                "c": [9, 5, 4, 4, 8, 11],
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
                   "output_dir_name":'Results/noniid_ref/',
                   "output_csv_name":"metrics_ref_all.csv"}

    client_args = {"mode": 'n_classes random same_samples',
                   'num_samples':15000, 'n_classes_per_trainer':4,
                   "trainer_class": "TrainerMNIST"}
    experiment_name = 'non_iid_ref'

    client_script="flw/topology_ref/client/client_ref.py"
    
   
    server_args["output_csv_name"]="metrics_ref_all_n7.csv"
    server_script="flw/topology_ref/server/server_ref.py"
    topology(server_script,
             client_script, 
             server_args,
             client_args,
             model_inputs,
             cpu_governor='ondemand',
             experiment_name=experiment_name,
             n_rounds=NUM_ROUNDS)
    
    #Corresponde a saída do algoritmo apresentado no sbrc
    server_args["output_csv_name"]="metrics_ref_sbrc_n7.csv"
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