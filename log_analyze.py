from analyze_energy_log import EnergyLogAnalyzer
import matplotlib.pyplot as plt
import pandas as pd

# Carrega os dados do primeiro cenário
analyzer_all = EnergyLogAnalyzer('./Results/iid_all/energy_debug.log')
df_all = analyzer_all.parse_log()
df_all['scenario'] = 'iid_all'

# Carrega os dados do segundo cenário
analyzer_least = EnergyLogAnalyzer('./Results/iid_leastEnergy/energy_debug.log')
df_least = analyzer_least.parse_log()
df_least['scenario'] = 'iid_leastEnergy'

# Concatena ambos para análise conjunta
df_combined = pd.concat([df_all, df_least], ignore_index=True)

# ==========================================
# Gráfico 1: Média Global entre todos os nós
# ==========================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

for scenario in ['iid_all', 'iid_leastEnergy']:
    df_scen = df_combined[df_combined['scenario'] == scenario]
    if not df_scen.empty:
        df_mean = df_scen.groupby('timestamp').mean(numeric_only=True).reset_index()
        
        ax1.plot(df_mean['timestamp'], df_mean['cpu_voltage'], label=scenario, marker='o', markersize=4)
        ax2.plot(df_mean['timestamp'], df_mean['avg_freq'], label=scenario, marker='o', markersize=4)

ax1.set_title('Média Global de CPU Voltage (Todos os nós)')
ax1.set_xlabel('Tempo')
ax1.set_ylabel('Voltage (V)')
ax1.legend()
ax1.grid(True)

ax2.set_title('Média Global de Frequência Média (Todos os nós)')
ax2.set_xlabel('Tempo')
ax2.set_ylabel('Frequência (Hz)')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

# ==========================================
# Gráfico 2: Detalhamento por Nó (Frequência)
# ==========================================
plt.figure(figsize=(14, 8))
nodes = df_combined['node'].unique()

for node in nodes:
    df_node_all = df_combined[(df_combined['node'] == node) & (df_combined['scenario'] == 'iid_all')]
    df_node_least = df_combined[(df_combined['node'] == node) & (df_combined['scenario'] == 'iid_leastEnergy')]
    
    # Obtém uma nova cor para o nó
    color = next(plt.gca()._get_lines.prop_cycler)['color']
    
    if not df_node_all.empty:
        plt.plot(df_node_all['timestamp'], df_node_all['avg_freq'], label=f'{node} (all)', linestyle='-', color=color, marker='o', markersize=3)
    if not df_node_least.empty:
        plt.plot(df_node_least['timestamp'], df_node_least['avg_freq'], label=f'{node} (leastEnergy)', linestyle='--', color=color, marker='x', markersize=3)

plt.title('Comparação de Frequência Média por Nó (Linha cheia = iid_all, Tracejada = iid_leastEnergy)')
plt.xlabel('Tempo')
plt.ylabel('Frequência Média (Hz)')
# Coloca a legenda fora do gráfico para não sobrepor
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=2)
plt.grid(True)
plt.tight_layout()
plt.show()
