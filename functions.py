import os
from PyQt6.QtWidgets import QFileDialog, QApplication
import pyperclip  # Para copiar texto para a área de transferência


def select_file():
    """Abre um diálogo para selecionar um arquivo de áudio/vídeo."""
    app = QApplication.instance() or QApplication([])
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(
        None,
        "Selecionar Arquivo de Áudio/Vídeo",
        "",
        "Arquivos de áudio (*.mp3 *.wav *.ogg);;Todos os Arquivos (*)"
    )
    return file_path


def transcribe_audio(file_path):
    """Simula uma transcrição de áudio (placeholder para futura implementação)."""
    return f"Transcrição simulada do arquivo: {os.path.basename(file_path)}"


def copy_to_clipboard(text):
    """Copia o texto fornecido para a área de transferência."""
    pyperclip.copy(text)
