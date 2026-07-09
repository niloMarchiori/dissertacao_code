Com base na fundamentação teórica fornecida pela literatura revisada, apresento abaixo a estruturação em formato Markdown contendo a previsão matemática para o número de iterações locais, a definição rigorosa de suas variáveis e a interpretação algébrica das constantes quando aplicada a função de perda do Erro Quadrático Médio.

### Previsão do Número Mínimo de Iterações Locais ($\hat{\beta}$)

Segundo a formulação analítica estabelecida por \cite{wei:topo_selection}, o limite inferior teórico para o número de iterações (ou atualizações) locais que um dispositivo cliente deve computar para atingir uma determinada acurácia de convergência local é definido pela seguinte inequação:

$$ \hat{\beta} \geq \frac{2}{(2-\zeta\eta)\eta\varepsilon} \log \frac{1}{\theta} $$

**Definição das Variáveis e Constantes:**
*   **$\hat{\beta}$**: Representa o número mínimo de atualizações do gradiente descendente estocástico (iterações locais) executadas pelo trabalhador (*worker*) no conjunto de dados local.
*   **$\theta$**: Denota a acurácia de convergência local estipulada como alvo para a rodada, consistindo em um valor contido no intervalo $(0, 1)$.
*   **$\eta$**: Refere-se à taxa de aprendizado (*learning rate*) empregada no algoritmo de otimização local.
*   **$\zeta$**: Constante que parametriza a premissa de suavidade (*$\zeta$-smoothness*) da função de perda. Analiticamente, impõe um limite superior à variação do gradiente.
*   **$\varepsilon$**: Constante que parametriza a premissa de que a função de perda é fortemente convexa (*$\varepsilon$-strongly convex*), existindo a restrição de que $0 < \varepsilon \leq \zeta$.

---

### Comportamento das Constantes $\varepsilon$ e $\zeta$ para o Erro Quadrático Médio

Quando o algoritmo de aprendizado local utiliza a função de perda do Erro Quadrático (frequentemente implementada em modelos de regressão linear e citada na literatura como de natureza suave e convexa), as constantes de suavidade ($\zeta$) e de forte convexidade ($\varepsilon$) perdem a sua abstração e assumem valores estritamente algébricos derivados da matriz Hessiana do modelo.

Conforme as definições matemáticas de Li et al. (2020) e \cite{yang:energy_efficient}, para que a função de perda atenda aos critérios dessas constantes, a sua matriz Hessiana de segunda ordem $\nabla^2 F_k(w)$ deve ter todos os seus autovalores contidos dentro do intervalo delimitado por elas. Isso é formulado por meio da condição matricial $\varepsilon I \preceq \nabla^2 F_k(w) \preceq \zeta I$ (sendo que diferentes autores podem adotar letras distintas para representar essas constantes, como $\gamma$ e $L$, ou $\mu$ e $L$). 

No caso de problemas baseados no Erro Quadrático, os documentos demonstram que a matriz Hessiana é composta predominantemente pela matriz construída a partir do próprio conjunto de dados de entrada do cliente (geralmente representada como a matriz $X^T X$, atrelada à covariância amostral) somada a um fator de regularização imposto pela função. Nesse cenário, as constantes assumem os seguintes papéis:

*   **$\varepsilon$ (Forte Convexidade)**: Corresponde ao **menor autovalor** da matriz Hessiana associada à função do cliente. Li et al. (2020) demonstram que, em modelos de erro quadrático regularizados (como o uso da norma $\mathcal{L}_2$), mesmo que a matriz de dados seja deficiente em posto (autovalor zero), a constante $\varepsilon$ assumirá o valor da penalidade de regularização imposta (frequentemente denotada por $\mu$ ou $\lambda$), garantindo que a função permaneça estritamente convexa.
*   **$\zeta$ (Suavidade)**: Corresponde ao **maior autovalor** da mesma matriz Hessiana. Este valor descreve o limite máximo de curvatura (ou inclinação) da função de perda quadrática com base nas características do conjunto de dados. Conforme dita a Equação de $\hat{\beta}$ formulada por \cite{wei:topo_selection}, o valor numérico que $\zeta$ assumir limitará diretamente as escolhas viáveis para a taxa de aprendizado $\eta$, pois o termo $(2-\zeta\eta)$ deve manter-se positivo para assegurar o declínio da função em direção à convergência.