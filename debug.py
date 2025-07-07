import subprocess

try:
    resultado = subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("FFmpeg encontrado!")
except FileNotFoundError:
    print("Erro: FFmpeg não foi encontrado no PATH.")
except Exception as e:
    print(f"Erro ao executar FFmpeg: {e}")
