# Introdução 

A ascensão da Internet das Coisas (IoT) e a proliferação de dispositivos móveis inteligentes resultaram em uma geração de dados em escala sem precedentes, trazendo consigo desafios significativos em termos de privacidade, latência de comunicação e consumo energético. Neste contexto, o Aprendizado Federado (Federated Learning - FL) tem se destacado como um paradigma promissor de aprendizado de máquina distribuído [2]. O FL permite que múltiplos dispositivos, ou clientes, treinem um modelo de forma colaborativa sem a necessidade de centralizar seus dados brutos, preservando a privacidade local ao compartilhar apenas os parâmetros do modelo, como pesos ou gradientes [1]. Essa abordagem reduz a sobrecarga de comunicação e mitiga riscos de privacidade inerentes aos modelos de treinamento centralizados.

Apesar de seus benefícios, a aplicação do FL em redes sem fio, especialmente em cenários de IoT com dispositivos de recursos computacionais e energéticos limitados, enfrenta obstáculos consideráveis [3][5]. A heterogeneidade dos dados entre os clientes — caracterizada por distribuições não independentes e identicamente distribuídas (non-IID) e por volumes de dados distintos — pode prejudicar a convergência e a precisão do modelo global [2][3]. Além disso, o consumo de energia associado ao treinamento local e à transmissão de modelos é um fator crítico, podendo esgotar rapidamente a bateria de dispositivos restritos e comprometer a sustentabilidade da rede, especialmente em topologias multi-salto como as que utilizam o protocolo RPL (Routing Protocol for Low-Power and Lossy Networks)[6].

Diante desses desafios, a literatura tem explorado extensivamente modelos teóricos de otimização. Trabalhos como [1] e [2] buscam minimizar a função de perda e o consumo de energia por meio da otimização conjunta do agendamento de clientes, da alocação de recursos sem fio e do número de épocas de treinamento local. Outras pesquisas, como [3] e [4], propõem esquemas de gerenciamento que consideram o volume de dados e o poder computacional, além de mecanismos de incentivo para equilibrar a relação entre eficiência energética e precisão. Tais estudos apresentam formulações matemáticas robustas e soluções ótimas do ponto de vista teórico, porém, frequentemente, carecem de uma validação prática que demonstre sua real eficiência em cenários de rede dinâmicos e sujeitos a falhas.


Em contrapartida, ferramentas de emulação como o MininetFed [5] surgem como uma solução para avaliar algoritmos de FL em ambientes de rede realistas e configuráveis. Essas plataformas permitem a emulação de dispositivos heterogêneos com restrições de CPU, memória e conectividade, além de possibilitar o monitoramento do consumo energético, tal qual como [1] necessita. Embora o desenvolvimento de algoritmos para otimização do consumo de energia seja apontado como uma necessidade [6], essas ferramentas, em sua essência, fornecem o ambiente para experimentação, não incorporando nativamente os modelos de otimização propostos na teoria. Essa dissociação entre os avanços teóricos em otimização e as plataformas de validação prática configura uma lacuna significativa na área.


# Objetivo

A ferramenta MininetFed [5] possibilita emular redes de aprendizado federado, de forma a disponibilizar um ambiente sensível ao consumo de energia. Os próprios autores da ferramenta mencionam no trabalho [6] a necessidade de desenvolver algoritmos que otimizem o consumo de energia em redes de treinamento, mas reconhecem não apresentar em si um modelo de otimização. 

Outros trabalhos ocmo [1] e [5] apresentam modelos muito bem estruturados e também métodos que atingem suas soluções ótimas. Tais trabalhos se concentram em analisar o modelo teórico, por outro lado deixam lacunas na apresentação de resultados práticos que se aproximem da eficiêna real de tais modelos de otimização.

O intúito dessa pesquisa é utilizar-se da ferramenta MininetFed para emular a rede de aprendizado federado lançando mão dos modelos de otimização no objetivo de, com essa emulação, sermos capazes de produzir dados pseudo-realísticos que possibilitem análises da eficiência dos modelos teóricos em ambientes reais.


# Fluxo da emulação de treinamento

1. Server:
    * Obtem os inputs do Modelo de Otimização
    * Obtem os valores ótimos por meio do FEDL [1] e inicia o treinamento
    * server publica em 'minifed/selectionQueue' selecionados
    * usa a variável global MODEL_TRAINED para esperar o cliente concluir o treinamento

2. Client: 

        callback on_message_selection() escutando 'minifed/selectionQueue'
    * Recebe a mensagem que foi selecionado
    * Roda a calibragem do modelo
    * Publica os pesos em minifed/preAggQueue

3. Server: 

        callback on_message_agg() escutando minifed/preAggQueue
    * Recebe os pesos e armazena eles
    * Libera a variável MODEL_TRAINED para que o próximo client comece o trainamento

4. Server:

        Todos os clients calibraram seus modelos
    * Agrega-se os pesos e os publica em 'minifed/posAggQueue'
    * Espera as métricas escutando com on_message_metrics()
    
5. Client:

        Callback on_message_agg() escutando 'minifed/posAggQueue' 
    * Recebe os pesos agregados
    * Teste o modelo e obtem as métrica**
    * Atualiza os pesos
    * Publica as métricas (id | acc | energy | selected) em 'minifed/metricsQueue'

6. Server:
        Recebeu todas as métricas 
    * Para caso a acurácia médica global desejada foi alcançada

# Implementação do modelo de otimização

(Repositório da reprodução do experimento teórico)

[https://github.com/niloMarchiori/Model_analysis]

# Problemas e próximos passos

## Problemas não resolvidos

1. As interfaces de redes dos dispositivos de redes 6LowPan não possuem Tx_Power (previsto no modelo de otimização)

2. Dispositivos com interface de rede que permitem o controlo manual de Tx_Power não possuem consumo de energia implementado
    * Segundo Ramon a implementação é simples, entretando seria necessário encontrar um modelo matemático

## To do:
Em andamento:
- [x] Debugar o motivo de select by leastEnergy selecionar todos os dispositivos
- [x] Número de épocas e rodadas limitadas pela acc_local e T_cmp
- [ ] Server deve passar T_cmp para client
- [ ] Plotar acc baseada em T_cmp
- [ ] Executar para consumo de energia padrao
    
Standy: 
- [ ] Validação assíncrona
- [ ] Passar range_freq no client_args/on_message_register

### Problemas

# Referências

<a name="ref1"></a>
[1] Tran, N. H., Bao, W., Zomaya, A. Y., Nguyen Minh, N. H., & Hong, C. S. (2019). Federated Learning over Wireless Networks: Optimization Model Design and Analysis. International Conference on Computer Communications, 1387–1395. https://doi.org/10.1109/INFOCOM.2019.8737464

<a name="ref2"></a>
[2] Han, X., Li, J., Chen, W., Mei, Z., Wei, K., Ding, M., & Poor, H. V. (2023). Analysis and Optimization of Wireless Federated Learning with Data Heterogeneity. arXiv.Org, abs/2308.03521. https://doi.org/10.48550/arxiv.2308.03521

<a name="ref3"></a>
[3] A Novel Joint Dataset and Incentive Management Mechanism for Federated Learning Over MEC. (2022). IEEE Access, 10, 30026–30038. https://doi.org/10.1109/access.2022.3156045

<a name="ref4"></a>
[4] Kim, J., Kim, D., Lee, J., & Hwang, J.-Y. (2022). A Novel Joint Dataset and Computation Management Scheme for Energy-Efficient Federated Learning in Mobile Edge Computing. IEEE Wireless Communications Letters, 11(5), 898–902. https://doi.org/10.1109/lwc.2022.3147236

[5] Johann Bastos, João Batista, Ramon Fontes, Eduardo Cerqueira, Rodolfo Villaça, and Vinícius F. S. Mota. 2025. A Lightweight Emulation Framework for Energy-Aware Federated Learning. In Proceedings of the ACM SIGCOMM 2025 Posters and Demos (ACM SIGCOMM Posters and Demos '25). Association for Computing Machinery, New York, NY, USA, 130–131. https://doi.org/10.1145/3744969.3748395

[6] J. Schmitz Bastos, J. C. Batista, R. dos Reis Fontes, E. Cerqueira, R. S. Villaça, and V. F. S. Mota. " Otimizando Energia no Aprendizado Federado em Redes de Baixa potência e com Alta Taxa de Perda de Pacotes", in Anais do XLIII Simpósio Brasileiro de Redes de Computadores e Sistemas Distribuídos, Natal/RN, 2025, pp. 43-56, doi: https://doi.org/10.5753/sbrc.2025.5786.