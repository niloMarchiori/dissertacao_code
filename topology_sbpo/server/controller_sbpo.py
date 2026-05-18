import numpy as np
import pandas as pd
from aggregator import *
import importlib
from datetime import datetime

from Model_SBPO.FLPOPT import FLPOPT

import pathlib
import json
import copy
import sys

def mkdir(dir_path):
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)

class OutPutData():
    def __init__(self):
        self.data=[]
        self.curr_line={}

    def save(self,dir_name='Results/Optmization/',file_name='results.csv'):
        df=pd.DataFrame(self.data)
        now=datetime.now()
        name_prefix=now.strftime("%Hh%Mm%Ss_")
        mkdir(f'/flw/{dir_name}')
        df.to_csv(f"/flw/{dir_name}{name_prefix+file_name}")

    def new_line(self):
        self.data.append(self.curr_line)
        self.curr_line={}

def criar_objeto(pacote, nome_classe):
    try:
        modulo = importlib.import_module(f"{pacote}")
        classe = getattr(modulo, nome_classe)  # Obtém a classe do módulo
        return classe()  # problem a classe
    except (ModuleNotFoundError, AttributeError) as e:
        print(f"Erro: {e}")
        return None


class Controller:
    def __init__(self, min_trainers=2, num_rounds=5, client_selector='Random', aggregator="FedAvg", model_inputs=None):
        self.trainer_list = []
        self.min_trainers = min_trainers
        # self.trainers_per_round = trainers_per_round
        self.current_round = 0
        self.num_rounds = num_rounds  # total number of rounds
        self.num_responses = 0  # number of responses received on aggWeights and metrics
        self.client_training_response = {}  # save weights and other info for aggregation
        self.trainer_samples = []  # save num_samples scale for agg
        self.acc_list = []
        self.mean_acc_per_round = []
        self.aggregator = criar_objeto("aggregator", aggregator)
        self.metrics = {}
        
        for chave,valor in model_inputs.items():
            if type(valor)==list:
                model_inputs[chave]=np.array(valor)
        self.model_inputs=model_inputs
        self.beta_h= np.zeros(model_inputs['N'])
        self.output_data=OutPutData()

    # getters
    def get_trainer_list(self):
        return self.trainer_list

    def get_current_round(self):
        return self.current_round

    def get_num_trainers(self):
        return len(self.trainer_list)

    def get_num_responses(self):
        return self.num_responses

    def get_mean_acc(self):
        mean = float(np.mean(np.array(self.acc_list)))
        self.mean_acc_per_round.append(mean)  # save mean acc


        #-------ATUALIZA THETA_PREV----------
        self.model_inputs['theta_prev']=np.array(self.acc_list)

        return mean

    # "setters"
    def update_metrics(self, trainer_id, metrics):
        self.metrics[trainer_id] = metrics

    def update_num_responses(self):
        self.num_responses += 1

    def reset_num_responses(self):
        self.num_responses = 0

    def reset_acc_list(self):
        self.acc_list = []

    def update_current_round(self):
        self.current_round += 1

    def add_trainer(self, trainer_id):
        self.trainer_list.append(trainer_id)
        self.trainer_list.sort()

    def add_client_training_response(self, id, response):
        self.client_training_response[id] = response

    def add_accuracy(self, acc):
        self.acc_list.append(acc)

    # operations

    def agg_weights(self) -> dict:
        # Aggregate the models recived from clients
        agg_response = {}
        try:
            agg_response = self.aggregator.aggregate(
                self.client_training_response, self.trainer_list)
        # old aggregator standard
        except:
            agg_response = self.aggregator.aggregate(
                self.client_training_response)
        agg_response_dict = {}

        # The aggregator can return a list of weights or a dictionary mapping the id of each clients to their weights
        # The numpy arrays need to be converted to lists before return to be able to turn into json
        if isinstance(agg_response, dict):
            for r in self.trainer_list:
                try:
                    # Tem que mandar para todos os trainers, mesmo os que não treinaram
                    agg_response[r]["weights"] = [w.tolist()
                                                  for w in agg_response[r]["weights"]]
                except:
                    raise Exception(f"Error: O agregador não retornou os weights do trainer {r}!")
            agg_response_dict = agg_response
        else:
            # for r in self.client_training_response:
            for r in self.trainer_list:
                client_dict = {}
                client_dict["weights"] = [w.tolist() for w in agg_response]
                agg_response_dict[r] = client_dict

        # reset weights and samples for next round
        self.client_training_response.clear()

        # agg_response_dict -> {client_id: {"weights": [], ...}}
        return agg_response_dict
    
    def update_dataset_size(self,trainer_id:str,dataset_sz:float):
        trainer_idx=self.trainer_list.index(trainer_id)
        self.model_inputs['S'][trainer_idx]=dataset_sz
        print("Model iput alterado")
    
    def update_model_size(self,trainer_id:str,model_sz:float):
        trainer_idx=self.trainer_list.index(trainer_id)
        self.model_inputs['s'][trainer_idx]=model_sz

    
    def run_opt_model(self):
        N=self.model_inputs['N']
        alpha=self.model_inputs['alpha']
        c=self.model_inputs['c']
        S=self.model_inputs['S']

        f_min=self.model_inputs['f_min']
        f_max=self.model_inputs['f_max']
        
        epsilon_0=self.model_inputs['epsilon_0']
        theta_prev=self.model_inputs['theta_prev']

        problem=FLPOPT(**self.model_inputs)

        print("Iniciando a otimização com 3 objetivos...")
        res = problem.solve(n_gen=200, pop_size=100, seed=1)
        pesos = [0.4, 0.2, 0.4]
        idx= problem.mcdm_pseudo_weights(pesos, verbose=True)
        solucao_vars=res.X[idx]

        f_n=np.array([solucao_vars[f'f_{n}'] for n in range(N)])
        beta_n=np.array([solucao_vars[f'beta_{n}'] for n in range(N)])
        theta_n=np.array([solucao_vars[f'theta_{n}'] for n in range(N)])
        self.beta_h+=1-beta_n

        T=solucao_vars[f'T']
        psi_n=np.array([solucao_vars[f'psi_{n}'] for n in range(N)])

        f_n=f_n/10**9

        return f_n, beta_n, theta_n, T, psi_n





        

        

        