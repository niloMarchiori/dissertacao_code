# Reorganização de Código - Consolidação de Módulos Compartilhados

## Resumo das Mudanças

Foi realizada uma refatoração para eliminar duplicação de código entre `calibrar_alpha/` e `calibrar_cn/`.

### Estrutura Anterior
```
calibrar_alpha/
├── energy.py          ❌ duplicado
├── api.py             ❌ duplicado
├── topo_wired.py      ❌ duplicado (função idêntica)
└── ...

calibrar_cn/
├── energy.py          ❌ duplicado
├── api.py             ❌ duplicado
├── topo_wired.py      ❌ duplicado (função idêntica)
└── ...
```

### Estrutura Atual
```
shared/                ✅ CENTRALIZADO
├── __init__.py
├── energy.py          (consolidado)
├── api.py             (consolidado)
└── topo_wired.py      (consolidado - função topology_wired)

calibrar_alpha/
├── calibrar_alpha.py  (importa de shared/)
├── client/
├── server/
└── ... (sem topo_wired.py) ✅

calibrar_cn/
├── calibrar_cn.py     (importa de shared/)
├── client/
├── server/
└── ... (sem topo_wired.py) ✅
```

## Arquivos Movidos

### 1. **energy.py**
- **Antes**: `calibrar_alpha/energy.py` e `calibrar_cn/energy.py`
- **Agora**: `shared/energy.py` (consolidado)
- **Classe exportada**: `EnergyFreqBased`

### 2. **api.py**
- **Antes**: `calibrar_alpha/api.py` e `calibrar_cn/api.py`
- **Agora**: `shared/api.py` (consolidado)
- **Funções exportadas**:
  - `app` (FastAPI)
  - `call_sensor()`, `call_network()`
  - `cmd_set_freq()`, `cmd_set_cpu_governor()`
  - `cmd_set_upper_freq()`, `cmd_set_lower_freq()`

### 3. **topo_wired.py** - função `topology_wired()`
- **Antes**: Função definida identicamente em ambos os arquivos
- **Agora**: `shared/topo_wired.py` (consolidado)
- **Função exportada**: `topology_wired()`

## Imports Atualizados

### Em `calibrar_alpha/calibrar_alpha.py` e `calibrar_cn/calibrar_cn.py`
```python
from shared.topo_wired import topology_wired as topology
from server import api_communication

# ...

topology(
    server_script=server_script,
    client_script=client_script,
    server_args=server_args,
    clients_args=clients_args,
    api_communication=api_communication,  # agora passado explicitamente
    cpu_governor='performance',
    experiment_name=experiment_name,
    n_rounds=NUM_ROUNDS
)
```

## Benefícios

✅ **Eliminação total de duplicação** - Código compartilhado consolidado em um único lugar  
✅ **Facilidade de manutenção** - Correções em um local afetam ambos os projetos  
✅ **Melhor organização** - Separação clara de código compartilhado vs específico  
✅ **Compatibilidade retroativa** - Imports existentes continuam funcionando  
✅ **Escalabilidade** - Fácil adicionar novos módulos compartilhados  

## Estrutura de Compartilhamento

```
shared/
├── __init__.py         (re-exporta tudo para facilitar imports)
├── energy.py           (lógica de consumo de energia)
├── api.py              (endpoints FastAPI + funções CLI)
└── topo_wired.py       (topologia Mininet - ÚNICA IMPLEMENTAÇÃO)

calibrar_alpha/calibrar_alpha.py  ┐
calibrar_cn/calibrar_cn.py        └─ Importam direto de shared/
                                     Passam api_communication como parâmetro
```

## Como Usar

### Importação de módulos compartilhados
```python
from shared import EnergyFreqBased, topology_wired, app
# ou
from shared.energy import EnergyFreqBased
from shared.topo_wired import topology_wired
```

### Chamada da função de topologia (em calibrar_alpha.py ou calibrar_cn.py)
```python
from shared.topo_wired import topology_wired as topology
from server import api_communication

topology(
    server_script=server_script,
    client_script=client_script,
    server_args=server_args,
    clients_args=clients_args,
    api_communication=api_communication,  # passado explicitamente
    cpu_governor='powersave',
    experiment_name='experiment_name'
)
```

## Mudanças em `shared/topo_wired.py`

A função foi ajustada para aceitar `api_communication` como parâmetro injetável, permitindo que seja testada independentemente:

```python
def topology_wired(..., api_communication=None, ...):
    # ...
    if api_communication:
        api_communication.set_cpu_governor(governor=cpu_governor)
    # ...
    if api_communication:
        api_communication.set_lower_frequency(freq=0.8)
        api_communication.set_upper_frequency(freq=4.7)
```

## Próximos Passos (Opcional)

Se necessário, você pode:
1. **Criar mais módulos** em `shared/` para outras duplicações detectadas
2. **Adicionar testes unitários** para os módulos compartilhados
3. **Documentar contratos de interface** entre módulos
4. **Versionar módulos compartilhados** se usados por outros projetos

