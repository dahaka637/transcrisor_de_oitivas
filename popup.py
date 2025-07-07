from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QClipboard, QFont


class Popup(QWidget):
    def __init__(self, message, popup_type="success", parent=None):
        """
        :param message: Mensagem a ser exibida no popup.
        :param popup_type: Tipo do popup ("success", "error", "warning", "info").
        :param parent: Referência para a janela que chamou o popup (usada para centralizar).
        """
        super().__init__(parent)
        self.message = self.wrap_text(message, max_chars=50)
        self.popup_type = popup_type.lower()
        self.duration = 2000 if self.popup_type != "error" else 0
        self.parent = parent
        self.initUI()

    def initUI(self):
        text_lines = self.message.count("\n") + 1
        popup_width = 420
        popup_height = 110 + (text_lines * 20)

        self.setFixedSize(popup_width, popup_height)

        # Configuração da janela do popup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint  # Remove bordas da janela
            | Qt.WindowType.ToolTip  # 🔥 Mantém o popup dentro da interface do programa
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Centraliza dentro da interface do programa
        if self.parent:
            parent_geometry = self.parent.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
        else:
            self.move(500, 300)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título do popup (ex: "SUCESSO" ou "ERRO")
        title_label = QLabel(self.getTitleText())
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {self.getBorderColor()};")
        layout.addWidget(title_label)

        # Mensagem
        message_label = QLabel(self.message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Arial", 11))
        message_label.setStyleSheet(f"color: {self.getBorderColor()};")
        layout.addWidget(message_label)

        if self.popup_type == "error":
            btn_layout = QHBoxLayout()

            close_button = QPushButton("Fechar")
            close_button.setStyleSheet("background-color: #dc3545; color: white; padding: 8px; border-radius: 5px;")
            close_button.clicked.connect(self.closePopup)

            copy_button = QPushButton("Copiar e Fechar")
            copy_button.setStyleSheet("background-color: #007bff; color: white; padding: 8px; border-radius: 5px;")
            copy_button.clicked.connect(self.copyMessageAndClose)

            btn_layout.addWidget(copy_button)
            btn_layout.addWidget(close_button)

            layout.addLayout(btn_layout)

        else:
            self.progress_bar = QProgressBar()
            self.progress_bar.setTextVisible(False)
            self.progress_bar.setRange(0, self.duration)
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 2px solid {self.getBorderColor()};
                    border-radius: 5px;
                    height: 8px;
                }}
                QProgressBar::chunk {{
                    background-color: {self.getBorderColor()};
                    border-radius: 5px;
                }}
            """)
            layout.addWidget(self.progress_bar)

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.closePopup)
            self.timer.start(self.duration)

            self.progress_timer = QTimer(self)
            self.progress_timer.timeout.connect(self.updateProgressBar)
            self.progress_timer.start(10)

        if self.popup_type != "error":
            self.mousePressEvent = self.closePopup

    def wrap_text(self, text, max_chars=50):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 > max_chars:
                lines.append(current_line.strip())
                current_line = word
            else:
                current_line += " " + word

        if current_line:
            lines.append(current_line.strip())

        return "\n".join(lines)

    def paintEvent(self, event):
        """Fundo translúcido e bordas arredondadas."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()

        bg_color = QColor(40, 40, 40, 180)  # 🔥 Fundo escuro translúcido
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(self.getBorderColor()), 3))
        painter.drawRoundedRect(rect.adjusted(3, 3, -3, -3), 15, 15)

    def updateProgressBar(self):
        value = self.progress_bar.value() + 10
        if value > self.duration:
            value = self.duration
        self.progress_bar.setValue(value)

    def closePopup(self, event=None):
        """Fecha o popup."""
        self.close()

    def copyMessageAndClose(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.message)
        self.close()

    def getBorderColor(self):
        colors = {
            "success": "#28a745",
            "error": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8"
        }
        return colors.get(self.popup_type, "#6c757d")

    def getTitleText(self):
        titles = {
            "success": "✔ SUCESSO",
            "error": "✖ ERRO",
            "warning": "⚠ AVISO",
            "info": "ℹ INFORMAÇÃO"
        }
        return titles.get(self.popup_type, "NOTIFICAÇÃO")