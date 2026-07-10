import json
import os

base_dir = '/home/nilo/Documents/dissertacao_code/Analise'
input_file = os.path.join(base_dir, 'Analise_Resultados.ipynb')
output_file = os.path.join(base_dir, 'non_iid_Analise_Resultados.ipynb')

with open(input_file, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code' or cell['cell_type'] == 'markdown':
        new_source = []
        for line in cell['source']:
            # Substituições para os diretórios non-iid
            line = line.replace("'iid_all'", "'non-iid_all'")
            line = line.replace("'iid_leastEnergy'", "'non-iid_leastEnergy'")
            line = line.replace("'iid_afea'", "'non_iid_afea'")
            new_source.append(line)
        cell['source'] = new_source

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Notebook modificado e salvo em: {output_file}")
