import numpy as np
import pandas as pd
from aggregator import *
import importlib
from datetime import datetime

from AFEA_Optmizer import AFEA

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
    def __init__(self, min_trainers=2, num_rounds=5, aggregator="FedAvg", clients_args=None):
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
        self.output_data=OutPutData()

        self.clients = {}
        for c in clients_args:
            self.clients[c['name']] = c

        self.theta_prev=np.ones(len(self.clients))*0.1
        self.instance=None
    
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
        self.theta_prev=np.array(self.acc_list)
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
            agg_response = self.aggregator.aggregate(self.client_training_response)
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
        self.clients[trainer_id]['S']=dataset_sz
        #####INACABADO
        print("Model input alterado")

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
        
    def instanceate_afea_parameters(self):
        trainer_list = self.get_trainer_list()

        alpha = np.array([self.clients[t]["alpha"] for t in trainer_list], dtype=float)
        S = np.array([self.clients[t]["S"] for t in trainer_list], dtype=float)
        c = np.array([self.clients[t]["c"] for t in trainer_list], dtype=float)
        fmin = np.array([self.clients[t]["fmin"]*1e9 for t in trainer_list], dtype=float)
        fmax = np.array([self.clients[t]["fmax"]*1e9 for t in trainer_list], dtype=float)

        self.instance = AFEA(
            len(trainer_list),
            alpha,
            c,
            S,
            fmin,
            fmax,
            epsilon_0=0.999,
            theta_prev=self.theta_prev,
        )

    def run_opt_model(self):
        print(f"N={self.instance.problem.N},\n \
                    alpha={self.instance.problem.alpha}, \n \
                    c={self.instance.problem.c}, \n \
                    S={self.instance.problem.S}, \n \
                    f_min={self.instance.problem.f_min}, \n \
                    f_max={self.instance.problem.f_max}, \
                    \n epsilon_0={self.instance.problem.epsilon_0}, \n \
                    theta_prev={self.instance.problem.theta_prev}, \n \
                    beta_h={self.instance.problem.beta_h}",file=sys.stderr)
        self.instance.theta_prev = self.theta_prev

        print("Iniciando a otimização com 3 objetivos...")
        res = self.instance.solve(n_gen=200, pop_size=100)

        if res is None or res.F is None or len(res.F) == 0:
            print("Nenhuma solução viável foi encontrada.", file=sys.stderr)

            trainer_list = self.get_trainer_list()
            cpu_frequency = {t: self.clients[t]["fmin"] for t in trainer_list}
            select_trainers_bool = np.ones(len(trainer_list), dtype=bool)
            tgt_acc = {t: float(self.theta_prev[i]) for i, t in enumerate(trainer_list)}
            time_limit = 1.0
            n_epochs = {t: 1 for t in trainer_list}
            return cpu_frequency, select_trainers_bool, tgt_acc, time_limit, n_epochs

        pesos = [0.4, 0.2, 0.4]
        idx = self.instance.mcdm_pseudo_weights(pesos, verbose=True)

        if idx is None:
            trainer_list = self.get_trainer_list()
            cpu_frequency = {t: self.clients[t]["fmin"] for t in trainer_list}
            select_trainers_bool = np.ones(len(trainer_list), dtype=bool)
            tgt_acc = {t: float(self.theta_prev[i]) for i, t in enumerate(trainer_list)}
            time_limit = 1.0
            n_epochs = {t: 1 for t in trainer_list}
            return cpu_frequency, select_trainers_bool, tgt_acc, time_limit, n_epochs

        solucao_vars = res.X[idx]

        f_n = {}
        beta_n = {}
        theta_n = {}
        psi_n = {}
        for i, t in enumerate(self.get_trainer_list()):
            f_n[t] = round(solucao_vars[f"f_{i}"] * 10**(-9), 3)
            beta_n[t] = solucao_vars[f"beta_{i}"]
            theta_n[t] = solucao_vars[f"theta_{i}"]
            psi_n[t] = solucao_vars[f"psi_{i}"]

        self.instance.beta_h += 1 - np.array([beta_n[t] for t in self.trainer_list])

        T = solucao_vars["T"]
        return f_n, beta_n, theta_n, T, psi_n
        
        
        
        
        