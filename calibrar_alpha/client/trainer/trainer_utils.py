import shutil
import os

def read_file(path):
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"O arquivo {path} não foi encontrado.")

        with open(path, 'r') as file:
            content = file.read().strip()

        # Tenta converter o valor para float
        value = float(content)
        return value
    except ValueError:
        print(f"Erro: O valor no arquivo {path} não é um float válido.")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Erro inesperado: {e}")
    return None

def read_energy():
    # Caminho do arquivo de energia
    file_path = "../tmp/consumption"
    return read_file(file_path)

def read_cpu_voltage():
    file_path='../tmp/cpu_voltage'
    return read_file(file_path)

def read_cpu_freq():
    file_path='../tmp/cpus_freqs'
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"O arquivo {file_path} não foi encontrado.")

        with open(file_path, 'r') as file:
            content = file.read().strip()

        import ast
        freqs = ast.literal_eval(content)
        freqs = list(map(lambda x: round(x/1e6, 3), freqs))
        return freqs
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Erro ao ler cpus_freqs: {e}")
    return None

def copiar_arquivo(origem, destino):
    """
    Copia um arquivo de um local para outro.

    Parâmetros:
        origem (str): Caminho completo do arquivo de origem.
        destino (str): Caminho completo do arquivo de destino.

    Retorna:
        bool: True se a cópia foi bem-sucedida, False caso contrário.
    """
    try:
        # Verifica se o arquivo de origem existe
        if not os.path.isfile(origem):
            print(f"Arquivo de origem não encontrado: {origem}")
            return False

        # Garante que o diretório de destino exista
        os.makedirs(os.path.dirname(destino), exist_ok=True)

        # Copia o arquivo
        shutil.copy2(origem, destino)
        print(f"Arquivo copiado com sucesso de {origem} para {destino}")
        return True
    except Exception as e:
        print(f"Erro ao copiar o arquivo: {e}")
        return False
