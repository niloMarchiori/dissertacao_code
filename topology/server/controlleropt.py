import numpy as np
import pandas as pd
from clientSelection import *
from aggregator import *
import importlib
from datetime import datetime

from Opt_Model.sub1 import solve_SUB1

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
        return classe()  # Instancia a classe
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
        # client_selectors[client_selector]()
        self.clientSelection = criar_objeto("clientSelection", client_selector)
        print("CLIENT_SELECTOR=", client_selector)
        self.aggregator = criar_objeto("aggregator", aggregator)
        self.metrics = {}

        self.experiment_ctt={'fmin':1.3, #GHz'
                             'fmax_range': [2,3.0], #GHz
                             'alpha': 2E-28,
                             'kappa': 10**2,
                             'N': self.min_trainers
                             }
        
        self.model_inputs=model_inputs
        if not model_inputs:
            self.creat_model_inputs()
        

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

    def select_trainers_for_round(self):
        return self.clientSelection.select_trainers_for_round(self.trainer_list, self.metrics)

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
    
    def creat_model_inputs(self):
        np.random.seed(seed=42)

        ctt=self.experiment_ctt
    
        self.model_inputs['kappa']=ctt['kappa']
        self.model_inputs['N']=ctt['N']
        self.model_inputs['alpha']=ctt['alpha']
        self.model_inputs['D']=[None]*ctt['N']
        # self.model_inputs['s']=[None]*ctt['N']
        self.model_inputs['c']=np.ones(ctt['N'])
        self.model_inputs['fmin']=ctt['fmin']*10**9 * np.ones(ctt['N'])
        self.model_inputs['fmax']=np.random.uniform(*ctt['fmax_range'],size=ctt['N'])*10**9 
    
    def update_dataset_size(self,trainer_id:str,dataset_sz:float):
        trainer_idx=self.trainer_list.index(trainer_id)
        self.model_inputs['D'][trainer_idx]=dataset_sz
        print("Model iput alterado")
    
    def update_model_size(self,trainer_id:str,model_sz:float):
        trainer_idx=self.trainer_list.index(trainer_id)
        self.model_inputs['s'][trainer_idx]=model_sz

    def save_input_model(self):
        now=datetime.now()
        name_prefix=now.strftime("%Hh%Mm%Ss_")
        mkdir('/flw/Results/Input_Model/')
        with open(f'/flw/Results/Input_Model/{name_prefix}model_imputs.json','w') as f:
            data=copy.deepcopy(self.model_inputs)
            data['c']=list(data['c'])
            data['fmin']=list(data['fmin'])
            data['fmax']=list(data['fmax'])
            data['ctt']=self.experiment_ctt
            json.dump(data,f)

    def get_select_inputs(self, selected_trainers=None,model_inputs=None):
        if not selected_trainers:
            selected_trainers=self.get_trainer_list()

        if not model_inputs:
            model_inputs=self.model_inputs

        trainer_list=self.get_trainer_list()
        select_inputs={k: val if type(val) !=list else [] for k,val in model_inputs.items()}
        for trainer in selected_trainers:
            trainer_idx=trainer_list.index(trainer)
            for key,val in model_inputs.items():
                if type(val)!=list:
                    continue
                select_inputs[key].append(val[trainer_idx])
        
        select_inputs['N']=len(selected_trainers)

        return select_inputs
    
    def run_opt_model(self, selected_trainers=None):

        select_inputs=self.get_select_inputs(selected_trainers)

        T_cmp, f = solve_SUB1(**select_inputs)
        # self.save_input_model()
        frequency_dict = {}
        for key,val in zip(selected_trainers, f):
            frequency_dict[key] = val

        # Tcom, t,p = solve_SUB2(ctt.N, kappa=k, s=inp.s, B=inp.B, N0=inp.N0, h=inp.h, pmin=inp.pmin, pmax=inp.pmax)
        # thteta, eta = solve_SUB3(f, t, T_cmp, Tcom, k)
        return frequency_dict

        

        