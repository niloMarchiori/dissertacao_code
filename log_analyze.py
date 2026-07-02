from shared.analyze_energy_log import EnergyLogAnalyzer

# Faz o parse dos dados
analyzer = EnergyLogAnalyzer('./Results/iid_leastEnergy/energy_debug_141315.log')
df = analyzer.parse_log()

# Exibe os dados estatísticos
analyzer.summary_statistics()

# Exibe os gráficos
analyzer.plot_voltage_over_time()
analyzer.plot_freq_over_time()
