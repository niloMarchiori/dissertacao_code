import json
import numpy as np
import pandas as pd
from pathlib import Path

def find_repo_root(start=None):
    start = Path(start or Path.cwd()).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / 'Analise').exists():
            return candidate
    return start

def main():
    repo_root = find_repo_root()
    analysis_dir = repo_root / 'Analise' / 'calibrar_cn_11'
    sta_const_path = repo_root / 'Analise' / 'sta_const.json'
    data_dir = analysis_dir / 'data'

    if not sta_const_path.exists():
        raise FileNotFoundError(f"sta_const.json não encontrado em {sta_const_path}")

    with open(sta_const_path, 'r') as f:
        instancia = json.load(f)

    csv_paths = sorted(data_dir.glob('calibrar_cn_[1-9].csv'))
    if not csv_paths:
        raise FileNotFoundError(f"Nenhum arquivo CSV encontrado em {data_dir}")

    dfs = [pd.read_csv(p, sep=',', index_col=0) for p in csv_paths]
    print(f"Carregados {len(dfs)} arquivos de {data_dir}")

    all_time_cols = [c for c in dfs[0].columns if c.startswith('training_time_sta')]
    station_ids = [int(c.split('training_time_sta')[1]) for c in all_time_cols]
    
    num_rows = len(dfs[0])
    num_stations = len(station_ids)
    
    # Busca frequências mínimas e máximas do sta_const.json
    f_min = instancia.get('f_min', [])[:num_stations]
    f_max = instancia.get('f_max', [])[:num_stations]
    
    if len(f_min) != num_stations or len(f_max) != num_stations:
        print("Aviso: Número de frequências em sta_const.json não bate com número de estações encontradas.")
    
    # As frequências são recriadas de forma linear, como originalmente no notebook
    freqs = {
        sid: np.linspace(f_min[i]*1e9, f_max[i]*1e9, num_rows)
        for i, sid in enumerate(station_ids)
    }

    results = {}
    fit_rows = []

    print("\nIniciando ajuste para cada estação usando a equação linearizada: T*f = c*S + k*T")
    for sid in station_ids:
        time_col = f'training_time_sta{sid}'
        datasz_col = f'sta{sid}_datasz'
        
        # Tirando a média das várias medições para suavizar o tempo de treino
        stacked = pd.concat([df[time_col].reset_index(drop=True) for df in dfs], axis=1)
        T = stacked.mean(axis=1).to_numpy(dtype=float)
        
        raw_model_sz = dfs[0][datasz_col].dropna()
        if raw_model_sz.empty:
            print(f"Estação {sid} não possui dados de tamanho.")
            continue
        S = float(raw_model_sz.iloc[0])
        f = freqs[sid]
        
        mask = np.isfinite(f) & np.isfinite(T) & (f > 0) & (T > 0)
        T_valid = T[mask]
        f_valid = f[mask]
        
        if len(T_valid) < 3:
            print(f"Estação {sid}: Poucos pontos válidos ({len(T_valid)}). Pulando.")
            continue
            
        # Equação linearizada: T_i * f_i = c_i * S_i + k_i * T_i
        # Y = T * f
        # X = [S, T]
        # coefs = [c, k]
        Y = T_valid * f_valid
        X = np.column_stack((np.full_like(T_valid, S), T_valid))
        
        theta, residuals, rank, s = np.linalg.lstsq(X, Y, rcond=None)
        c, k = theta
        
        # Avaliando a qualidade do ajuste (R^2 na equação original T = c*S/(f-k))
        T_pred = c * S / (f_valid - k)
        ss_res = np.sum((T_valid - T_pred)**2)
        ss_tot = np.sum((T_valid - np.mean(T_valid))**2)
        r2 = 1 - ss_res / ss_tot if ss_tot != 0 else np.nan
        
        results[sid] = {'c': c, 'k': k, 'R2': r2, 'S': S}
        print(f"Estação {sid:2d}: c = {c:.4e}, k = {k:.4e}, R2 = {r2:.4f}")
        
        fit_rows.append({
            'station_id': sid,
            'c': c,
            'k': k,
            'R2': r2,
            'n_points': len(T_valid),
            'model_sz': S
        })

    fit_summary = pd.DataFrame(fit_rows).sort_values('station_id').reset_index(drop=True)
    out_csv = analysis_dir / 'fit_summary_calibrado.csv'
    fit_summary.to_csv(out_csv, index=False)
    print(f"\nResumo salvo em: {out_csv}")

    # Atualiza o arquivo sta_const_calibrado.json com os novos c_i e k_i
    max_id = max(station_ids) if station_ids else 0
    c_array = [0.0] * (max_id + 1)
    k_array = [0.0] * (max_id + 1)
    
    # Se houver valores originais em sta_const.json para 'c', podemos tentar mantê-los se a estação não for calibrada
    if 'c' in instancia:
        for i, val in enumerate(instancia['c']):
            if i < len(c_array):
                c_array[i] = val
            else:
                c_array.append(val)
                k_array.append(0.0)

    for sid, vals in results.items():
        c_array[sid] = vals['c']
        k_array[sid] = vals['k']

    instancia_calibrada = instancia.copy()
    instancia_calibrada['c'] = c_array
    instancia_calibrada['k'] = k_array

    out_json_path = analysis_dir / 'sta_const_calibrado.json'
    with open(out_json_path, 'w') as f:
        json.dump(instancia_calibrada, f, indent=2)
        
    print(f"Valores de c_i e k_i calibrados e salvos em: {out_json_path}")

if __name__ == "__main__":
    main()
