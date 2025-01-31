import os
from pydub import AudioSegment
from multiprocessing import Pool, cpu_count

def processa_arquivo(args):
    """
    Função que recebe as informações de conversão
    e processa um arquivo individualmente.
    """
    (caminho_entrada, caminho_saida, formato_saida, bitrate, sample_rate, channels) = args
    
    try:
        print(f"Convertendo: {caminho_entrada} -> {caminho_saida}")
        
        # Carrega o áudio
        audio = AudioSegment.from_file(caminho_entrada)
        
        # Ajusta taxa de amostragem se solicitado
        if sample_rate is not None:
            audio = audio.set_frame_rate(sample_rate)

        # Ajusta canais se solicitado
        if channels is not None:
            audio = audio.set_channels(channels)
        
        # Exporta
        if formato_saida.lower() in ["mp3", "ogg", "m4a", "aac"]:
            audio.export(caminho_saida, format=formato_saida, bitrate=bitrate)
        else:
            audio.export(caminho_saida, format=formato_saida)
    
    except Exception as e:
        # Caso haja algum problema na conversão, não removemos o arquivo antigo
        print(f"Falha ao converter {caminho_entrada}: {e}")
        return None
    
    else:
        # Se chegou aqui sem exceção, a conversão deu certo.
        # Então podemos remover o arquivo de entrada.
        try:
            os.remove(caminho_entrada)
            print(f"Arquivo antigo removido: {caminho_entrada}")
        except Exception as e:
            print(f"Falha ao remover {caminho_entrada}: {e}")
        
        return caminho_entrada  # Pode retornar para checagem ou logging futuro

def converter_arquivos_audio_paralelo(
    diretorio_raiz,
    formatos_entrada=None,
    formato_saida="mp3",
    bitrate="192k",
    sample_rate=None,
    channels=None,
    num_processos=None
):
    """
    Converte arquivos de áudio em paralelo, usando multiprocessing.
    E remove o arquivo de entrada após a conversão bem-sucedida.
    """
    if formatos_entrada is None:
        formatos_entrada = [".wav", ".flac", ".ogg", ".m4a", ".aac", ".mp4", ".wma"]

    # Se num_processos não for definido, usaremos todos os núcleos (cpu_count())
    if num_processos is None:
        num_processos = cpu_count()

    # Lista para manter o conjunto de tarefas (args de cada arquivo a converter)
    tarefas = []

    for root, dirs, files in os.walk(diretorio_raiz):
        for file in files:
            if any(file.lower().endswith(ext) for ext in formatos_entrada):
                caminho_entrada = os.path.join(root, file)
                nome_base = os.path.splitext(file)[0]
                caminho_saida = os.path.join(root, f"{nome_base}.{formato_saida}")

                # Montamos a tupla de argumentos que será passada à função de conversão
                tarefa = (
                    caminho_entrada,
                    caminho_saida,
                    formato_saida,
                    bitrate,
                    sample_rate,
                    channels
                )
                tarefas.append(tarefa)

    # Cria um pool de processos
    with Pool(processes=num_processos) as pool:
        resultado = pool.map(processa_arquivo, tarefas)

    # Neste ponto, 'resultado' contém o retorno de cada conversão (ou None se falhou).
    # Opcionalmente, você pode filtrar quais deram certo:
    arquivos_convertidos = [res for res in resultado if res is not None]
    
    print("Arquivos convertidos com sucesso:", arquivos_convertidos)

if __name__ == "__main__":
    diretorio = r"C:\Users\joaol\Desktop\musicas" # Diretório com arquivos de áudio
    converter_arquivos_audio_paralelo(
        diretorio_raiz=diretorio,
        formatos_entrada=[".wav"], # Quais formatos converter
        formato_saida="mp3",
        bitrate="320k",
        sample_rate=44100,
        channels=2,
        num_processos=6 # Defina quantos processos paralelos deseja
    )
