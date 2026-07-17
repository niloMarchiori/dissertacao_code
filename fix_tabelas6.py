import json

file_path = '/home/nilo/Documents/dissertacao_code/Analise/Tabelas_Eficiencia.ipynb'
with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if 'source' in cell:
        new_source = []
        for line in cell['source']:
            new_source.append(line)
            
            # Injeta a lógica de exportação na Seção 2
            if "display(HTML(tabela_global.to_html(index=False, na_rep='NaN')))" in line:
                new_source.append("with open('tabela_visao_global.tex', 'w', encoding='utf-8') as f:\n")
                new_source.append("    f.write(tabela_global.to_latex(index=False, na_rep='-', float_format='%.2f'))\n")
                new_source.append("print('Tabela global exportada para: tabela_visao_global.tex')\n")
                
            # Injeta a lógica de exportação na Seção 3
            if "display(HTML(html))" in line:
                new_source.append("    nome_arquivo = 'tabela_' + titulo.replace(' ', '_').replace(':', '').replace('%', 'pct').replace('(', '').replace(')', '').replace('.', '') + '.tex'\n")
                new_source.append("    with open(nome_arquivo, 'w', encoding='utf-8') as f:\n")
                new_source.append("        f.write(pivot.to_latex(na_rep='-', float_format='%.2f'))\n")
                new_source.append("    print(f'Tabela exportada para: {nome_arquivo}')\n")

        cell['source'] = new_source

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Lógica de exportação LaTeX injetada com sucesso!")
