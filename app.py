import sys
import platform
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QTextEdit, QFileDialog, QHBoxLayout,
    QGroupBox, QGridLayout, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QMetaObject
from PyQt6.QtGui import QIcon
from functions import *  # Importa o editor de prompts
from prompt import PromptEditor  # Agora importamos do prompt.py
from transcritor import TranscricaoThread, calcular_duracao_audio
from popup import Popup
import pyperclip  
import wmi
from estimador import registrar_transcricao, atualizar_tempo_real, estimar_tempo
import platform
import json
from py3nvml.py3nvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetName, nvmlDeviceGetCount, nvmlShutdown


def get_devices():
    devices = []

    # Detectar CPU (usando WMI)
    try:
        w = wmi.WMI()
        for cpu in w.Win32_Processor():
            devices.append(f"CPU: {cpu.Name.strip()}")
    except Exception as e:
        print(f"Erro ao detectar CPU: {e}")
        devices.append("CPU: Erro ao detectar")

    # Detectar GPU (usando NVML)
    try:
        # Inicializar NVML para detectar GPUs
        nvmlInit()
        gpu_count = nvmlDeviceGetCount()
        for i in range(gpu_count):
            handle = nvmlDeviceGetHandleByIndex(i)
            gpu_name = nvmlDeviceGetName(handle)  # Remove .decode("utf-8")
            devices.append(f"GPU: {gpu_name}")
    except Exception as e:
        print(f"Erro ao detectar GPUs: {e}")
    finally:
        try:
            nvmlShutdown()
        except:
            pass

    return devices






class TranscriptionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transcrição de Oitiva")
        self.setGeometry(100, 100, 750, 700)
        self.initUI()
        # ✅ Obtém o caminho absoluto do ícone e define sem quebrar a interface
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icone.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print("⚠️ Ícone não encontrado, continuando sem ícone...")

    def initUI(self):
        mainLayout = QVBoxLayout()

        # Título
        title = QLabel("Transcrição de Oitiva")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        subtitle = QLabel("Ferramenta para transcrever arquivos de áudio/vídeo de oitivas e procedimentos")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 14px;
        """)

        mainLayout.addWidget(title)
        mainLayout.addWidget(subtitle)

        # Seletor de Arquivo
        fileGroup = QGroupBox("Selecionar Arquivo de Áudio/Vídeo")
        fileLayout = QHBoxLayout()
        self.fileInput = QLineEdit()
        self.fileInput.setPlaceholderText("Nenhum arquivo selecionado...")
        self.fileInput.setReadOnly(True)
        btnSelectFile = QPushButton("Selecionar")
        btnSelectFile.clicked.connect(self.selectFile)
        fileLayout.addWidget(self.fileInput)
        fileLayout.addWidget(btnSelectFile)
        fileGroup.setLayout(fileLayout)
        mainLayout.addWidget(fileGroup)

        # Configurações de Transcrição
        settingsGroup = QGroupBox("Configurações de Transcrição")
        settingsLayout = QGridLayout()

        whisperLabel = QLabel("Selecionar Modelo Whisper")
        self.whisperModel = QComboBox()
        self.whisperModel.addItems(["Rápido", "Moderado", "Preciso"])
        self.whisperModel.setCurrentIndex(2)
        self.whisperModel.setFixedWidth(500)

        deviceLabel = QLabel("Selecionar Dispositivo")
        self.deviceSelector = QComboBox()
        self.deviceSelector.addItems(get_devices())
        self.deviceSelector.setFixedWidth(500)

        settingsLayout.addWidget(whisperLabel, 0, 0)
        settingsLayout.addWidget(self.whisperModel, 0, 1)
        settingsLayout.addWidget(deviceLabel, 1, 0)
        settingsLayout.addWidget(self.deviceSelector, 1, 1)
        settingsGroup.setLayout(settingsLayout)
        mainLayout.addWidget(settingsGroup)

        # Informações Adicionais
        infoGroup = QGroupBox("Informações Adicionais")
        infoLayout = QGridLayout()

        partNameLabel = QLabel("Nome da Parte Ouvinte")
        self.partNameInput = QLineEdit()
        self.partNameInput.setPlaceholderText("Informe o nome da parte ouvida...")
        self.partNameInput.setFixedWidth(500)

        partTypeLabel = QLabel("Tipo")
        self.partType = QComboBox()
        self.partType.addItems(["Declaração", "Depoimento", "Interrogatório"])
        self.partType.setFixedWidth(500)

        infoLayout.addWidget(partNameLabel, 0, 0)
        infoLayout.addWidget(self.partNameInput, 0, 1)
        infoLayout.addWidget(partTypeLabel, 1, 0)
        infoLayout.addWidget(self.partType, 1, 1)
        infoGroup.setLayout(infoLayout)
        mainLayout.addWidget(infoGroup)

        # Texto da Transcrição
        transcriptionLabel = QLabel("Texto da Transcrição")
        self.transcriptionText = QTextEdit()
        self.transcriptionText.setPlaceholderText("O texto transcrito aparecerá aqui...")
        mainLayout.addWidget(transcriptionLabel)
        mainLayout.addWidget(self.transcriptionText)

        self.timer_progresso = QTimer()
        self.timer_progresso.timeout.connect(self.incrementarProgresso)
        self.tempo_estimado = 0
        self.progresso_atual = 0


        # Barra de Carregamento
        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #007bff;
                border-radius: 5px;
                text-align: center;
                font-size: 12px;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                width: 20px;
            }
        """)
        mainLayout.addWidget(self.progressBar)

        # Linha separadora
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        mainLayout.addWidget(separator)

        # Botões de Ação
        btnLayout = QHBoxLayout()
        btnTranscribe = QPushButton("Transcrever")
        btnTranscribe.setStyleSheet("background-color: #007bff; color: white; padding: 10px 20px;")
        btnTranscribe.clicked.connect(self.transcribeAudio)

        btnCopy = QPushButton("Copiar Transcrição com Prompt")
        btnCopy.setStyleSheet("background-color: #28a745; color: white; padding: 10px 20px;")
        btnCopy.clicked.connect(self.copyTranscription)

        btnEditPrompt = QPushButton("Editar Prompt")
        btnEditPrompt.setStyleSheet("background-color: #6f42c1; color: white; padding: 10px 20px;")
        btnEditPrompt.clicked.connect(self.openPromptEditor)

        btnClear = QPushButton("Limpar Conteúdo")
        btnClear.setStyleSheet("background-color: #dc3545; color: white; padding: 10px 20px;")
        btnClear.clicked.connect(self.clearContent)

        btnLayout.addWidget(btnTranscribe)
        btnLayout.addWidget(btnCopy)
        btnLayout.addWidget(btnEditPrompt)
        btnLayout.addWidget(btnClear)
        mainLayout.addLayout(btnLayout)

        self.setLayout(mainLayout)

    def selectFile(self):
        """Função para selecionar um arquivo de áudio ou vídeo."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, 
            "Selecionar Arquivo de Áudio/Vídeo", 
            "", 
            "Arquivos de mídia (*.mp3 *.wav *.ogg *.mp4 *.mkv *.avi *.flv *.mov *.webm);;Todos os Arquivos (*)"
        )
        if file_path:
            self.fileInput.setText(file_path)


    def copyTranscription(self):
        """Copia a transcrição para a área de transferência com as informações adicionais e o prompt correto."""

        # Obter os valores atuais dos campos preenchidos pelo usuário
        nome_parte = self.partNameInput.text().strip() or "Não informado"
        tipo_procedimento = self.partType.currentText()
        conteudo_transcrito = self.transcriptionText.toPlainText().strip()
        
        # Verificar se há transcrição antes de copiar
        if not conteudo_transcrito:
            popup = Popup("Nenhuma transcrição disponível para copiar.", "warning", parent=self)
            popup.show()
            return

        # 📌 **Obter o prompt respectivo (com base no tipo de procedimento)**
        prompt_mapping = {
            "Declaração": "prompt_declaracao.json",
            "Depoimento": "prompt_depoimento.json",
            "Interrogatório": "prompt_interrogatorio.json"
        }

        prompt_filename = prompt_mapping.get(tipo_procedimento, "prompt_declaracao.json")  # Padrão para declaração
        prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts", prompt_filename)

        # Inicializa o prompt como "PROMPT NÃO ENCONTRADO" caso não haja um arquivo válido
        prompt_text = "PROMPT NÃO ENCONTRADO"

        if os.path.exists(prompt_path):
            try:
                with open(prompt_path, "r", encoding="utf-8") as prompt_file:
                    data = json.load(prompt_file)
                    prompt_text = data.get("prompt", "").strip() or "PROMPT NÃO DEFINIDO"
            except Exception as e:
                prompt_text = f"Erro ao carregar prompt: {e}"

        # 🔥 **Criar o texto formatado para copiar**
        texto_copiado = f"""Nome da parte: {nome_parte}
    Tipo de procedimento: {tipo_procedimento}

    {prompt_text}

    "{conteudo_transcrito}"
    """

        # Copiar para a área de transferência
        pyperclip.copy(texto_copiado)

        # Popup de sucesso
        popup = Popup("Transcrição copiada para a área de transferência!", "success", parent=self)
        popup.show()

    def clearContent(self):
        """Limpa os campos de entrada, transcrição e reseta a barra de carregamento."""
        self.transcriptionText.clear()
        self.fileInput.clear()
        self.partNameInput.clear()
        self.partType.setCurrentIndex(0)

        # 🔥 Resetar a barra de progresso
        self.progressBar.setValue(0)
        self.timer_progresso.stop()  # Garante que a contagem pare se estiver ativa
        self.progresso_atual = 0  # Reinicia a variável de controle

        # 🔔 Exibir popup informando que o conteúdo foi limpo
        popup = Popup("Conteúdo limpo com sucesso!", "info", parent=self)
        popup.show()


    def openPromptEditor(self):
        """Abre o editor de prompts na mesma posição central da janela principal."""
        self.promptEditor = PromptEditor()
        parent_geometry = self.geometry()
        x = parent_geometry.x() + (parent_geometry.width() - self.promptEditor.width()) // 2
        y = parent_geometry.y() + (parent_geometry.height() - self.promptEditor.height()) // 2
        self.promptEditor.move(x, y)
        self.promptEditor.show()


    def transcribeAudio(self):
        """Função para transcrever o áudio/vídeo sem travar a UI."""
        input_file = self.fileInput.text()
        modelo = self.whisperModel.currentText().lower()
        dispositivo = "GPU" if "GPU" in self.deviceSelector.currentText() else "CPU"

        multiplicadores = {"rápido": 1.0, "moderado": 1.5, "preciso": 3.5}
        fator_tempo = multiplicadores.get(modelo, 2.0)

        modelos_whisper = {"preciso": "large", "moderado": "medium", "rápido": "small"}
        modelo_whisper = modelos_whisper.get(modelo, "base")

        if not input_file:
            popup = Popup("Por favor, selecione um arquivo de áudio ou vídeo.", "warning", parent=self)
            popup.show()
            return

        # 📌 **ETAPA 1: Criar o texto dinâmico antes de iniciar a transcrição**
        tipo_transcricao = self.partType.currentText()
        nome_parte = self.partNameInput.text().strip()

        mensagem_transcricao = f"🎥 Transcrevendo {tipo_transcricao} de {nome_parte}\n Aguarde..." if nome_parte else f"🎥 Transcrevendo {tipo_transcricao}\n Aguarde..."
        
        # 🔥 **Definir o texto indicando que a transcrição está em andamento**
        self.transcriptionText.setStyleSheet("font-size: 24px; font-weight: bold")
        self.transcriptionText.setPlainText(mensagem_transcricao)
        
        # 🔥 **Forçar a atualização da interface antes de continuar**
        QApplication.processEvents()

        # 📌 **ETAPA 2: Obter a duração do áudio antes de iniciar a transcrição**
        try:
            duracao = calcular_duracao_audio(input_file)
            if duracao <= 0:
                raise ValueError("Duração do áudio inválida.")
            
            estimativa_real = estimar_tempo(modelo, dispositivo, duracao)
            
            self.tempo_estimado = estimativa_real if estimativa_real is not None else int(duracao * fator_tempo)
            print(f"📊 Estimativa de tempo: {self.tempo_estimado} segundos")

            registrar_transcricao(modelo.lower(), dispositivo, duracao)

            self.progressBar.setRange(0, 100)
            self.progressBar.setValue(0)

            self.progresso_atual = 0
            self.timer_progresso.start(1000)

        except Exception as e:
            popup = Popup(f"(main)Erro ao calcular duração: {e}", "error", parent=self)
            popup.show()
            return

        # 📌 **ETAPA 3: Iniciar a transcrição**
        popup = Popup("Iniciando transcrição, aguarde...", "info", parent=self)
        popup.show()

        self.thread_transcricao = TranscricaoThread(input_file, modelo=modelo_whisper, dispositivo=dispositivo)
        self.thread_transcricao.transcricao_finalizada.connect(self.mostrarTranscricao)
        self.thread_transcricao.erro_ocorrido.connect(self.mostrarErro)
        self.thread_transcricao.start()





    def incrementarProgresso(self):
        """Atualiza a barra de progresso gradualmente até atingir 100%."""
        if self.progresso_atual < 100:
            incremento = (100 / self.tempo_estimado)  # Valor incremental baseado no tempo total
            self.progresso_atual += incremento
            self.progressBar.setValue(int(self.progresso_atual))
        else:
            self.timer_progresso.stop()  # 🔥 Para o timer automaticamente



    def mostrarTranscricao(self, texto):
        """Atualiza a interface com a transcrição finalizada."""
        self.timer_progresso.stop()  # 🔥 Para a barra imediatamente
        self.progressBar.setValue(100)  # 🔥 Define como completa

        # 🔥 **Salvar tempo real de transcrição no estimador**
        atualizar_tempo_real(self.whisperModel.currentText().lower(), 
                            "GPU" if "GPU" in self.deviceSelector.currentText() else "CPU", 
                            round(self.tempo_estimado, 2), 
                            self.tempo_estimado)


        # 🔥 **Resetar o estilo do texto e exibir a transcrição final**
        self.transcriptionText.setStyleSheet("font-size: 14px")
        self.transcriptionText.setPlainText(texto)

        popup = Popup("Transcrição concluída com sucesso!", "success", parent=self)
        popup.show()




    def mostrarErro(self, erro):
        """Exibe erro se houver falha na transcrição."""
        popup = Popup(erro, "error", parent=self)
        popup.show()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranscriptionApp()
    window.show()
    sys.exit(app.exec())
