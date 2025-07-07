import os
import subprocess
import whisper
import torch
import warnings
import random
import time
from PyQt6.QtCore import QThread, pyqtSignal
from estimador import atualizar_tempo_real

# Suprimir warnings desnecessários
warnings.filterwarnings("ignore", category=UserWarning, module="whisper.transcribe")
warnings.filterwarnings("ignore", category=FutureWarning, module="whisper")

def criar_diretorio_temp():
    """Garante que o diretório temp_converter exista."""
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_converter")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def gerar_nome_temporario():
    """Gera um nome de arquivo temporário único."""
    return f"temp_audio{random.randint(100000, 999999)}.wav"

def converter_para_wav(input_file, output_dir):
    """Converte qualquer arquivo de áudio/vídeo para WAV usando FFmpeg."""
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Erro: O arquivo '{input_file}' não foi encontrado.")

    output_file = os.path.join(output_dir, gerar_nome_temporario())
    
    try:
        comando = [
            "ffmpeg", "-i", input_file, "-ar", "16000", "-ac", "1",
            "-c:a", "pcm_s16le", output_file, "-y", "-loglevel", "error"
        ]
        resultado = subprocess.run(comando, capture_output=True, text=True)

        if resultado.returncode != 0:
            raise RuntimeError(f"Erro ao converter para WAV: {resultado.stderr}")

        return output_file
    except Exception as e:
        raise RuntimeError(f"Erro ao converter para WAV: {e}")

def calcular_duracao_audio(input_file):
    """Obtém a duração do arquivo de áudio usando FFprobe."""
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Erro: O arquivo '{input_file}' não foi encontrado.")

    comando = [
        "ffprobe", "-i", input_file, "-v", "error",
        "-select_streams", "a:0", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1"
    ]
    
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True)

        if resultado.returncode != 0:
            raise RuntimeError(f"Erro ao calcular duração do áudio: {resultado.stderr}")

        return float(resultado.stdout.strip())
    except Exception as e:
        raise RuntimeError(f"Erro ao calcular duração do áudio: {e}")

class TranscricaoThread(QThread):
    """Thread para rodar a transcrição sem travar a interface."""
    transcricao_finalizada = pyqtSignal(str)
    erro_ocorrido = pyqtSignal(str)
    progresso_atualizado = pyqtSignal(int)

    def __init__(self, input_file, modelo="base", dispositivo="cuda"):
        super().__init__()
        self.input_file = input_file
        self.modelo = modelo
        self.dispositivo = "GPU" if dispositivo == "cuda" else "CPU"

    def run(self):
        """Executa a transcrição do áudio na thread separada."""
        temp_dir = criar_diretorio_temp()
        arquivo_wav = None  
        inicio_transcricao = time.time()

        try:
            duracao = calcular_duracao_audio(self.input_file)
            print(f"🎵 Duração do áudio: {duracao:.2f} segundos")
            self.progresso_atualizado.emit(0)

            arquivo_wav = converter_para_wav(self.input_file, temp_dir)

            if self.dispositivo == "GPU" and not torch.cuda.is_available():
                print("⚠️ CUDA não está disponível. Usando CPU.")
                self.dispositivo = "CPU"

            print("📥 Carregando modelo Whisper...")
            modelo_whisper = whisper.load_model(self.modelo, device="cuda" if self.dispositivo == "GPU" else "cpu")  

            print("🔍 Iniciando transcrição...")
            transcricao = modelo_whisper.transcribe(arquivo_wav, language="pt")
            
            # 🔥 Modificação para adicionar '|' entre frases detectadas
            texto_formatado = " | ".join(transcricao["text"].split('. '))
            
            self.transcricao_finalizada.emit(texto_formatado)

            tempo_real = time.time() - inicio_transcricao
            atualizar_tempo_real(self.modelo, self.dispositivo, duracao, int(tempo_real))
            print(f"⏳ Tempo real da transcrição: {tempo_real:.2f} segundos")

        except Exception as e:
            self.erro_ocorrido.emit(f"Erro na transcrição: {e}")

        finally:
            if arquivo_wav and os.path.exists(arquivo_wav):
                os.remove(arquivo_wav)
                print(f"🗑️ Arquivo temporário removido: {arquivo_wav}")
