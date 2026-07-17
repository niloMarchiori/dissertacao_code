import json

with open("Analise/Tabelas_Eficiencia.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb.get("cells", []):
    if cell.get("cell_type") == "code":
        source = cell["source"]
        
        # Replacement 1: Tabela Global
        new_source_1 = []
        modified_1 = False
        for line in source:
            if "print(tabela_global.to_latex" in line:
                new_source_1.append("with open('tabela_global.tex', 'w') as f:\n")
                new_source_1.append("    f.write(tabela_global.to_latex(index=False, na_rep='-', float_format='%.2f'))\n")
                new_source_1.append("print('Tabela global salva em tabela_global.tex')")
                modified_1 = True
            elif "Imprime o código LaTeX da tabela global" in line:
                new_source_1.append("# Salva o código LaTeX da tabela global\n")
            else:
                new_source_1.append(line)
        if modified_1:
            cell["source"] = new_source_1
            source = new_source_1
            
        # Replacement 2 & 3: exibir_tabela_comparativa
        new_source_2 = []
        modified_2 = False
        for i, line in enumerate(source):
            if "def exibir_tabela_comparativa(df, metrica, titulo, casas_decimais=2):\n" == line:
                new_source_2.append("def exibir_tabela_comparativa(df, metrica, titulo, filename_tex=None, casas_decimais=2):\n")
                modified_2 = True
            elif "    display(HTML(html))\n" == line:
                new_source_2.append(line)
                new_source_2.append("    \n")
                new_source_2.append("    if filename_tex:\n")
                new_source_2.append("        with open(filename_tex, 'w') as f:\n")
                new_source_2.append("            f.write(pivot.to_latex(na_rep='-', float_format=f'%.{casas_decimais}f'))\n")
                new_source_2.append("        print(f'Tabela {titulo.split(':')[0]} salva em {filename_tex}\\n')\n")
            elif "exibir_tabela_comparativa(tabela_device_mean, 'Taxa de Seleção (%)', 'Tabela Comparativa: Taxa Percentual de Seleção (%)')\n" == line:
                new_source_2.append("exibir_tabela_comparativa(tabela_device_mean, 'Taxa de Seleção (%)', 'Tabela Comparativa: Taxa Percentual de Seleção (%)', filename_tex='tabela_taxa_selecao.tex')\n")
            elif "exibir_tabela_comparativa(tabela_device_mean, 'Frequência de Seleção', 'Tabela Comparativa: Qtd. Absoluta de Seleções por Experimento')\n" == line:
                new_source_2.append("exibir_tabela_comparativa(tabela_device_mean, 'Frequência de Seleção', 'Tabela Comparativa: Qtd. Absoluta de Seleções por Experimento', filename_tex='tabela_frequencia.tex')\n")
            elif "exibir_tabela_comparativa(tabela_device_mean, 'Tempo Médio (s)', 'Tabela Comparativa: Tempo Médio Gasto Treinando (s)', casas_decimais=4)\n" == line:
                new_source_2.append("exibir_tabela_comparativa(tabela_device_mean, 'Tempo Médio (s)', 'Tabela Comparativa: Tempo Médio Gasto Treinando (s)', filename_tex='tabela_tempo_treinamento.tex', casas_decimais=4)\n")
            elif "exibir_tabela_comparativa(tabela_device_mean, 'Consumo Acumulado (Wh)', 'Tabela Comparativa: Consumo Energético Total Requerido (Wh)')" == line:
                new_source_2.append("exibir_tabela_comparativa(tabela_device_mean, 'Consumo Acumulado (Wh)', 'Tabela Comparativa: Consumo Energético Total Requerido (Wh)', filename_tex='tabela_consumo_energia.tex')")
            else:
                new_source_2.append(line)
                
        if modified_2:
            cell["source"] = new_source_2

with open("Analise/Tabelas_Eficiencia.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
