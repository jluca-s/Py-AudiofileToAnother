import os
from pydub import AudioSegment
from multiprocessing import Pool, cpu_count

def processa_arquivo(args):
    """
    Função que recebe as informações de conversão
    e processa um arquivo individualmente.
    """
    (caminho_entrada, caminho_saida, formato_saida, bitrate, sample_rate, channels) = args

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

    return caminho_entrada  # apenas para possível logging ou checagem futura

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

                # Montamos a tupla de argumentos que será passada
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

    # Opcionalmente, você pode imprimir ou usar o resultado, que 
    # neste exemplo é apenas o caminho de entrada convertido
    print("Arquivos convertidos:", resultado)

if __name__ == "__main__":
    diretorio = r"E:"
    converter_arquivos_audio_paralelo(
        diretorio_raiz=diretorio,
        formatos_entrada=[".wav"],   # Quais formatos converter
        formato_saida="mp3",
        bitrate="320k",
        sample_rate=44100,
        channels=2,
        num_processos=None         # Defina quantos processos paralelos deseja
    )
