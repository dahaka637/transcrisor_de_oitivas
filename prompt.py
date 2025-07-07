import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTextEdit, QPushButton
)
from PyQt6.QtCore import Qt
from popup import Popup


class PromptEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor de Prompts")
        self.setGeometry(150, 150, 450, 350)

        # Obtém o diretório do próprio script e define a pasta correta de prompts
        self.base_dir = os.path.dirname(os.path.abspath(__file__))  # Garante que está no mesmo diretório do script
        self.prompt_folder = os.path.join(self.base_dir, "prompts")  # Define o caminho absoluto da pasta

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Título
        title = QLabel("Editor de Prompts")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
        """)
        layout.addWidget(title)

        # Seletor de Prompt
        self.promptSelector = QComboBox()
        self.promptSelector.addItems(["prompt_declaracao.json", "prompt_interrogatorio.json", "prompt_depoimento.json"])
        self.promptSelector.currentIndexChanged.connect(self.loadPromptContent)
        layout.addWidget(self.promptSelector)

        # Caixa de Texto para o Conteúdo do Prompt
        self.promptEditor = QTextEdit()
        self.promptEditor.setPlaceholderText("Conteúdo do prompt aparecerá aqui...")
        layout.addWidget(self.promptEditor)

        # Botão para salvar alterações
        saveButton = QPushButton("Salvar Conteúdo")
        saveButton.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
        saveButton.clicked.connect(self.savePromptContent)
        layout.addWidget(saveButton)

        self.setLayout(layout)

        # Certifica-se de que a pasta e os arquivos de prompts existem
        self.ensurePromptFiles()

        # Carrega o conteúdo do primeiro prompt ao iniciar
        self.loadPromptContent()

    def ensurePromptFiles(self):
        """Garante que a pasta de prompts e os arquivos JSON existem no diretório do script."""
        if not os.path.exists(self.prompt_folder):
            os.makedirs(self.prompt_folder)  # Cria a pasta no diretório correto

        # Lista de prompts que devem existir
        prompt_files = ["prompt_declaracao.json", "prompt_interrogatorio.json", "prompt_depoimento.json"]

        for prompt_name in prompt_files:
            prompt_path = os.path.join(self.prompt_folder, prompt_name)

            if not os.path.exists(prompt_path):
                self.createEmptyPrompt(prompt_path)  # Cria o arquivo vazio caso não exista

    def loadPromptContent(self):
        """Carrega o conteúdo do prompt selecionado."""
        prompt_name = self.promptSelector.currentText()
        prompt_path = os.path.join(self.prompt_folder, prompt_name)

        if os.path.exists(prompt_path):
            try:
                with open(prompt_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    self.promptEditor.setText(data.get("prompt", ""))
            except Exception as e:
                popup = Popup(f"Erro ao carregar o arquivo: {e}", "error", parent=self)
                popup.show()
        else:
            self.createEmptyPrompt(prompt_path)

    def createEmptyPrompt(self, prompt_path):
        """Cria um arquivo de prompt vazio se ele não existir."""
        try:
            with open(prompt_path, "w", encoding="utf-8") as file:
                json.dump({"prompt": ""}, file, indent=4)
        except Exception as e:
            popup = Popup(f"Erro ao criar o arquivo: {e}", "error")
            popup.show()

    def savePromptContent(self):
        """Salva o conteúdo do prompt no arquivo JSON."""
        prompt_name = self.promptSelector.currentText()
        prompt_path = os.path.join(self.prompt_folder, prompt_name)

        try:
            content = self.promptEditor.toPlainText()
            with open(prompt_path, "w", encoding="utf-8") as file:
                json.dump({"prompt": content}, file, indent=4)
            popup = Popup(f"Prompt '{prompt_name}' salvo com sucesso!", "success", parent=self)
            popup.show()
        except Exception as e:
            popup = Popup(f"Erro ao salvar o arquivo: {e}", "error", parent=self)
            popup.show()
