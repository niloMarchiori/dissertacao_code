from topology import topology

def main(kappa=100,time_limit_sec=1.4, callback_stop=True):
    NUM_ROUNDS=70
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
                   "output_dir_name":'Results/midiid_var_k/',
                   "output_csv_name":f"metrics_opt_k_{kappa:.2f}.csv"}
    

    trainer_callbacks={"TrainStopper": {'target_accuracy':0.99,
                                'time_limit_sec':time_limit_sec,
                                'monitor':'accuracy'}}
    
    client_args = {"mode": 'random same_samples',
                   'num_samples':15000,
                   "trainer_class": 
                   "TrainerMNIST"}
    
    if callback_stop:
        client_args["trainer_callbacks"]=trainer_callbacks
    
    experiment_name = 'var_k'

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
    

if __name__=='__main__':
    main(kappa=10,time_limit_sec=1.3, callback_stop=True)
    main(kappa=10,time_limit_sec=1.3, callback_stop=False)

    main(kappa=10**0.75,time_limit_sec=1.6,callback_stop=True)
    main(kappa=10**0.75,time_limit_sec=1.6,callback_stop=False)

    main(kappa=10**0.25, time_limit_sec=1.78794,callback_stop=True)
    main(kappa=10**0.25, time_limit_sec=1.78794,callback_stop=False)