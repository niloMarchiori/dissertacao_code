import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime
import ast

class EnergyLogAnalyzer:
    def __init__(self, log_path):
        self.log_path = log_path
        self.df = None
        
    def parse_log(self):
        """
        Realiza o parse do arquivo de log e retorna um DataFrame do Pandas.
        Formato esperado:
        [2026-07-02 13:52:58] Node: sta0 | alpha: 5.128e-09 | cpu_voltage: 1.03 | freq: [4600000.0, 4223375.0]
        """
        data = []
        
        # Expressão regular para extrair os componentes da linha
        # [data hora] Node: nome | alpha: valor | cpu_voltage: valor | freq: [lista]
        pattern = re.compile(r'\[(.*?)\] Node: (.*?) \| alpha: (.*?) \| cpu_voltage: (.*?) \| freq: (\[.*?\])')
        
        with open(self.log_path, 'r') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    timestamp_str = match.group(1)
                    node = match.group(2)
                    alpha = float(match.group(3))
                    cpu_voltage = float(match.group(4))
                    freq_list = ast.literal_eval(match.group(5))
                    
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    
                    row = {
                        'timestamp': timestamp,
                        'node': node,
                        'alpha': alpha,
                        'cpu_voltage': cpu_voltage,
                        'avg_freq': sum(freq_list)/len(freq_list) if freq_list else 0
                    }
                    
                    # Adiciona frequencia de cada core separadamente
                    for i, freq in enumerate(freq_list):
                        row[f'freq_core_{i}'] = freq
                        
                    data.append(row)
                    
        self.df = pd.DataFrame(data)
        return self.df

    def summary_statistics(self):
        """Imprime estatísticas descritivas básicas."""
        if self.df is None:
            self.parse_log()
            
        print("=== Estatísticas Descritivas ===")
        print(self.df.describe())
        print("\n=== Média por Nó ===")
        print(self.df.groupby('node')[['cpu_voltage', 'avg_freq']].mean())

    def plot_voltage_over_time(self):
        """Plota a voltagem do CPU ao longo do tempo para cada nó."""
        if self.df is None:
            self.parse_log()
            
        plt.figure(figsize=(12, 6))
        for node in self.df['node'].unique():
            node_data = self.df[self.df['node'] == node]
            plt.plot(node_data['timestamp'], node_data['cpu_voltage'], label=node, marker='o', markersize=3)
            
        plt.title('CPU Voltage ao longo do tempo por Nó')
        plt.xlabel('Tempo')
        plt.ylabel('CPU Voltage (V)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.grid(True)
        plt.show()

    def plot_freq_over_time(self):
        """Plota a frequência média do CPU ao longo do tempo para cada nó."""
        if self.df is None:
            self.parse_log()
            
        plt.figure(figsize=(12, 6))
        for node in self.df['node'].unique():
            node_data = self.df[self.df['node'] == node]
            plt.plot(node_data['timestamp'], node_data['avg_freq'], label=node, marker='o', markersize=3)
            
        plt.title('Frequência Média do CPU ao longo do tempo por Nó')
        plt.xlabel('Tempo')
        plt.ylabel('Frequência Média (Hz)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.grid(True)
        plt.show()

    def plot_core_frequencies(self, node_name):
        """Plota as frequências de cada core ao longo do tempo para um nó específico."""
        if self.df is None:
            self.parse_log()
            
        node_data = self.df[self.df['node'] == node_name]
        if node_data.empty:
            print(f"Nó {node_name} não encontrado.")
            return
            
        plt.figure(figsize=(12, 6))
        
        # Encontra as colunas de cores dinamicamente
        core_cols = [c for c in self.df.columns if c.startswith('freq_core_')]
        
        for core in core_cols:
            plt.plot(node_data['timestamp'], node_data[core], label=core, marker='o', markersize=3)
            
        plt.title(f'Frequência dos Cores ao longo do tempo - Nó: {node_name}')
        plt.xlabel('Tempo')
        plt.ylabel('Frequência (Hz)')
        plt.legend()
        plt.tight_layout()
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    
    analyzer = EnergyLogAnalyzer('energy_debug_0702_135258.log')
    df = analyzer.parse_log()
    # Exibe os dados estatísticos
    analyzer.summary_statistics()
    # Exibe os gráficos
    analyzer.plot_voltage_over_time()
    analyzer.plot_freq_over_time()
