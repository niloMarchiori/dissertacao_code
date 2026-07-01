import json
import os

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Dependência de Tempo de Treinamento e Frequência\n",
    "\n",
    "De acordo com o modelo teórico de tempo de processamento descrito em `modelo.md`:\n",
    "\n",
    "$$T_i = c_i\\frac{S_i}{f_i-k_i}$$\n",
    "\n",
    "Onde:\n",
    "- $S_i$ é o tamanho em bits do dataset do dispositivo $i$\n",
    "- $f_i$ é a frequência de CPU do dispositivo $i$\n",
    "- $c_i$ e $k_i$ são constantes a serem calibradas\n",
    "\n",
    "Neste notebook, utilizaremos os dados de calibração (`calibrar_cn_x.csv`) que contêm os tempos de treinamento, mas não a frequência. Para estabelecer a dependência, usaremos os limites de frequência definidos em `sta_const.json` (`f_min` e `f_max`) e avaliaremos o comportamento esperado da curva de tempo."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import glob\n",
    "import json\n",
    "import os\n",
    "\n",
    "# Carregar as constantes (f_min, f_max, etc)\n",
    "with open('../sta_const.json', 'r') as f:\n",
    "    sta_const = json.load(f)\n",
    "\n",
    "N = sta_const['N']\n",
    "f_min = sta_const['f_min']\n",
    "f_max = sta_const['f_max']\n",
    "\n",
    "# Carregar todos os CSVs da pasta data\n",
    "csv_files = glob.glob(os.path.join('data', '*.csv'))\n",
    "\n",
    "df_list = []\n",
    "for file in csv_files:\n",
    "    df = pd.read_csv(file)\n",
    "    \n",
    "    # A coluna staX_datasz possui o valor de S_i apenas na primeira linha.\n",
    "    # Preenchemos as demais linhas com este valor\n",
    "    for i in range(N):\n",
    "        col_name = f'sta{i}_datasz'\n",
    "        if col_name in df.columns:\n",
    "            val = df.loc[0, col_name]\n",
    "            if pd.notna(val):\n",
    "                df[col_name] = df[col_name].fillna(val)\n",
    "                \n",
    "    df_list.append(df)\n",
    "\n",
    "df_all = pd.concat(df_list, ignore_index=True)\n",
    "print(f\"Total de linhas carregadas: {len(df_all)}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Mapeamento e Dependência T_i vs f_i\n",
    "\n",
    "Vamos calcular o Tempo Médio de Treinamento ($T_i$) para cada estação nos dados.\n",
    "Como a frequência exata de cada execução não está disponível, podemos modelar a relação para todo o espectro suportado por cada CPU, de $f_{min}$ a $f_{max}$. \n",
    "Se considerarmos uma aproximação em que os experimentos ocorreram perto de uma certa referência (ex: $f_{max}$), podemos estimar a curva de calibração baseada em $c_i$."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "def theoretical_time(f, c, k, S):\n",
    "    return c * S / (f - k)\n",
    "\n",
    "stats = []\n",
    "for i in range(N):\n",
    "    time_col = f'training_time_sta{i}'\n",
    "    size_col = f'sta{i}_datasz'\n",
    "    \n",
    "    if time_col in df_all.columns and size_col in df_all.columns:\n",
    "        mean_time = df_all[time_col].dropna().mean()\n",
    "        data_size = df_all[size_col].iloc[0]\n",
    "        \n",
    "        stats.append({\n",
    "            'STA': i,\n",
    "            'T_mean': mean_time,\n",
    "            'S': data_size,\n",
    "            'f_min': f_min[i],\n",
    "            'f_max': f_max[i]\n",
    "        })\n",
    "\n",
    "df_stats = pd.DataFrame(stats)\n",
    "display(df_stats)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Visualização do Modelo\n",
    "\n",
    "Abaixo geramos as curvas teóricas de dependência $T(f)$ no intervalo de $f_{min}$ a $f_{max}$ para cada nó.\n",
    "Assumimos, por exemplo, que $k_i \\approx 0$ e usamos o tempo médio nos ensaios como se estivesse rodando na frequência $f_{max}$ para calibrar a curva $c_i$. Dessa forma:\n",
    "\n",
    "$$ c_i = \\frac{T_{mean} \\cdot f_{max}}{S_i} $$"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.figure(figsize=(12, 8))\n",
    "\n",
    "for idx, row in df_stats.iterrows():\n",
    "    i = int(row['STA'])\n",
    "    S_i = row['S']\n",
    "    T_mean = row['T_mean']\n",
    "    f_min_i = row['f_min']\n",
    "    f_max_i = row['f_max']\n",
    "    \n",
    "    # Calibrando c_i a partir de T_mean e assumindo f=f_max e k=0 para fins de exibição\n",
    "    f_ref = f_max_i\n",
    "    k_assumed = 0.0\n",
    "    c_calibrated = T_mean * (f_ref - k_assumed) / S_i\n",
    "    \n",
    "    # Dominio de frequencia da estacao i\n",
    "    f_range = np.linspace(f_min_i, f_max_i, 50)\n",
    "    T_pred = theoretical_time(f_range, c_calibrated, k_assumed, S_i)\n",
    "    \n",
    "    # Plot da curva\n",
    "    p = plt.plot(f_range, T_pred, label=f'STA {i}')\n",
    "    color = p[0].get_color()\n",
    "    \n",
    "    # Plot do ponto de calibração/medição\n",
    "    plt.plot(f_ref, T_mean, 'o', color=color)\n",
    "\n",
    "plt.title('Dependência Estimada: Tempo de Treinamento vs Frequência de Operação')\n",
    "plt.xlabel('Frequência de Operação $f_i$ (GHz)')\n",
    "plt.ylabel('Tempo de Treinamento $T_i$ (s)')\n",
    "plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')\n",
    "plt.grid(True, linestyle='--', alpha=0.7)\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

with open('/home/nilo/Documents/dissertacao_code_calibrar_constantes/Analise/calibrar_cn_11/analise_tempo_frequencia.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)
