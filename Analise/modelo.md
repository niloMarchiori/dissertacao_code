# Modelo teórico:

## Modelo de potência

$$P_i = \left(1 + \gamma \cdot V \right) \cdot \alpha \cdot f_i \cdot V^2$$

Sendo:
- $f_i \rightarrow$ frequência de CPU do dispositivo i
- $V \rightarrow$ tensão de operação
- $\alpha, \gamma \rightarrow$ constantes empíricas dependentes da arquitetura do chipset

## Modelo de tempo de processamento

$$T_i = c_i\frac{S_i}{f_i-k_i}$$

Sendo:
- $S_i \rightarrow$ tamanho em bits do dataset do dispositivo i
- $f_i \rightarrow$ frequência de CPU do dispositivo i
- $c_i\rightarrow$ ciclos de cpu por bit
- $k_i \rightarrow$ constante empírica referente ao uso de cpu por processor de background

## Dados

Os dados coletados em formato CSV são resultados de execuções experimentais focadas em calibrar as constantes do sistema (como consumo de energia e tempo de treinamento) para 11 estações (clientes).

### 1. Calibração de Alpha (`calibrar_alpha_x.csv`)
Este arquivo contém métricas detalhadas obtidas durante a execução de rodadas de treinamento. As colunas principais incluem:
- **Tamanho dos Dados (`staX_datasz`)**: Quantidade de dados alocada para cada estação.
- **Tempo e Consumo (`training_time_staX`, `host_consumption_staX`)**: Tempo gasto no treinamento local e energia consumida.
- **Métricas de CPU (`cpu_voltage_staX`, `cpus_freqs_staX`)**: Tensão e frequências de operação da CPU registradas durante o treinamento, fundamentais para a modelagem do consumo de energia.

O objetivo destes dados é calibrar as constantes $\alpha, \gamma$, que relaciona a frequência da CPU ao consumo energético real.

### 2. Calibração de C_n (`calibrar_cn_x.csv`)
Este arquivo contém métricas semelhantes (tamanho dos dados, tempo de treinamento, consumo e acurácia), mas não inclui os dados granulares de tensão e frequência da CPU. Esses resultados são utilizados para calibrar os parâmetros gerais de custo/tempo (como a constante $c_i$ e $k_i$), isolando variáveis que dependem do tamanho dos dados e das características computacionais intrínsecas de cada dispositivo.

## Dependência com `sta_const.json`

Os arquivos CSV de calibração possuem uma dependência direta com as constantes base definidas em `sta_const.json`. Este arquivo JSON atua como a "verdade fundamental" ou configuração inicial das 11 estações (`N = 11`) antes (ou como resultado) da calibração. Ele define:
- **`alpha`**: Um array com os valores iniciais da constante de consumo de energia para cada estação.
- **`c`**: Os coeficientes de custo ou capacidade de processamento para cada estação.
- **`num_samples`**: O número de amostras (tamanho do dataset local) disponível em cada nó.
- **Limites de Frequência (`f_min`, `f_max`)**: As frequências mínima e máxima (em GHz) suportadas pela CPU de cada estação. Estes limites justificam o porquê da coleta de `cpus_freqs` no CSV do alpha.
- **Outros hiperparâmetros**: Como `epsilon_0` e `theta_prev`.
