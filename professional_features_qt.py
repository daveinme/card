"""
Professional Features - PySide6 Version
Componenti UI professionali per interfaccia Qt
"""

from PySide6.QtWidgets import (QWidget, QPushButton, QLabel, QProgressBar, 
                               QVBoxLayout, QHBoxLayout, QFrame, QStatusBar,
                               QDialog, QTextEdit, QToolBar, QMainWindow)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QSize
from PySide6.QtGui import QFont, QColor, QPalette, QIcon

from config import C, F, S, B


class ModernButton(QPushButton):
    """Pulsante moderno con stile professionale"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        
        # Stile CSS
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['primary']};
                color: white;
                border: none;
                border-radius: {B['radius_md']}px;
                padding: {S['md']}px {S['lg']}px;
                font-size: {F['size_normal']}px;
                font-weight: {F['weight_semibold']};
            }}
            QPushButton:hover {{
                background-color: {C['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {C['primary_active']};
            }}
            QPushButton:disabled {{
                background-color: {C['text_disabled']};
            }}
        """)


class StatusBar(QStatusBar):
    """Barra di stato professionale con indicatore progresso"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QStatusBar {{
                background-color: {C['dark_surface']};
                color: {C['text_primary']};
                border-top: 1px solid {C['light_border']};
                padding: {S['sm']}px;
            }}
        """)
        
        # Label principale
        self.status_label = QLabel("Pronto")
        self.status_label.setStyleSheet(f"color: {C['success']};")
        self.addWidget(self.status_label)
        
        # Progress bar (nascosta di default)
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(200)
        self.progress.setVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {C['light_border']};
                border-radius: {B['radius_sm']}px;
                text-align: center;
                background-color: {C['dark_bg']};
            }}
            QProgressBar::chunk {{
                background-color: {C['primary']};
            }}
        """)
        self.addPermanentWidget(self.progress)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet(f"color: {C['text_secondary']};")
        self.addPermanentWidget(self.info_label)
    
    def set_status(self, text, color=None):
        """Imposta testo status"""
        self.status_label.setText(text)
        if color:
            self.status_label.setStyleSheet(f"color: {color};")
    
    def set_info(self, text):
        """Imposta testo info"""
        self.info_label.setText(text)
    
    def show_progress(self, visible):
        """Mostra/nascondi progress bar"""
        self.progress.setVisible(visible)


class Toolbar(QToolBar):
    """Toolbar professionale"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setIconSize(QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        self.setStyleSheet(f"""
            QToolBar {{
                background-color: {C['dark_surface']};
                border-bottom: 2px solid {C['primary']};
                spacing: {S['sm']}px;
                padding: {S['sm']}px;
            }}
            QToolButton {{
                color: {C['text_primary']};
                background-color: transparent;
                border: none;
                border-radius: {B['radius_sm']}px;
                padding: {S['sm']}px {S['md']}px;
            }}
            QToolButton:hover {{
                background-color: {C['photo_hover']};
            }}
            QToolButton:pressed {{
                background-color: {C['primary_active']};
            }}
        """)
    
    def add_button(self, text, callback, tooltip=""):
        """Aggiungi pulsante alla toolbar"""
        action = self.addAction(text, callback)
        if tooltip:
            action.setToolTip(tooltip)
        return action
    
    def add_separator(self):
        """Aggiungi separatore"""
        super().addSeparator()


class SplashScreen(QWidget):
    """Splash screen professionale"""
    
    def __init__(self, parent=None, duration=2500):
        super().__init__(parent)
        self.duration = duration
        
        # Finestra senza bordi, al centro
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Frame container
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {C['dark_surface']};
                border-radius: {B['radius_lg']}px;
                border: 2px solid {C['primary']};
            }}
        """)
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(20)
        
        # Titolo
        title = QLabel("SD Card Photo Importer")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont(F['family_primary'], F['size_huge'], F['weight_bold']))
        title.setStyleSheet(f"color: {C['primary']};")
        frame_layout.addWidget(title)
        
        # Sottotitolo
        subtitle = QLabel("Professional Edition")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont(F['family_primary'], F['size_large']))
        subtitle.setStyleSheet(f"color: {C['text_secondary']};")
        frame_layout.addWidget(subtitle)
        
        # Progress bar
        progress = QProgressBar()
        progress.setRange(0, 0)  # Indeterminato
        progress.setTextVisible(False)
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: {B['radius_sm']}px;
                background-color: {C['dark_bg']};
                height: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {C['primary']};
            }}
        """)
        frame_layout.addWidget(progress)
        
        # Loading text
        loading = QLabel("Caricamento...")
        loading.setAlignment(Qt.AlignCenter)
        loading.setStyleSheet(f"color: {C['text_secondary']};")
        frame_layout.addWidget(loading)
        
        layout.addWidget(frame)
        self.setLayout(layout)
        
        # Dimensioni e posizione
        self.setFixedSize(500, 300)
        self.center_on_screen()
        
        # Timer per chiusura automatica
        QTimer.singleShot(duration, self.close)
    
    def center_on_screen(self):
        """Centra finestra sullo schermo"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)


class AboutDialog(QDialog):
    """Dialogo About professionale"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Informazioni")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Titolo
        title = QLabel("SD Card Photo Importer")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont(F['family_primary'], F['size_xlarge'], F['weight_bold']))
        title.setStyleSheet(f"color: {C['primary']};")
        layout.addWidget(title)
        
        # Versione
        version = QLabel("Professional Edition v2.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet(f"color: {C['text_secondary']};")
        layout.addWidget(version)
        
        # Descrizione
        description = QTextEdit()
        description.setReadOnly(True)
        description.setHtml(f"""
        <div style='color: {C["text_primary"]}; font-size: {F["size_normal"]}px;'>
        <p><b>Caratteristiche:</b></p>
        <ul>
            <li>Importazione foto da SD con multi-threading</li>
            <li>Visualizzazione doppio monitor professionale</li>
            <li>Stampa con spooler interno intelligente</li>
            <li>Report e statistiche stampe</li>
            <li>Interfaccia Qt ad alte prestazioni</li>
        </ul>
        <p><b>Scorciatoie:</b></p>
        <ul>
            <li>Ctrl+O: Apri cartella</li>
            <li>Ctrl+I: Importa da SD</li>
            <li>Ctrl+P: Stampa foto</li>
            <li>Ctrl+A: Seleziona tutto</li>
            <li>F11: Fullscreen (finestra secondaria)</li>
        </ul>
        <p style='margin-top: 20px; color: {C["text_secondary"]};'>
        Sviluppato con PySide6 e Python<br>
        © 2025 - Professional Edition
        </p>
        </div>
        """)
        description.setStyleSheet(f"""
            QTextEdit {{
                background-color: {C['dark_surface']};
                border: 1px solid {C['light_border']};
                border-radius: {B['radius_md']}px;
                padding: {S['md']}px;
            }}
        """)
        layout.addWidget(description)
        
        # Pulsante chiudi
        close_btn = ModernButton("Chiudi")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Stile dialog
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {C['dark_bg']};
            }}
        """)


class ToastNotification(QWidget):
    """Notifica toast moderna"""
    
    def __init__(self, message, parent=None, duration=3000):
        super().__init__(parent, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Frame
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {C['dark_surface']};
                border-left: 4px solid {C['success']};
                border-radius: {B['radius_md']}px;
            }}
        """)
        
        frame_layout = QHBoxLayout(frame)
        
        # Icona (emoji)
        icon = QLabel("✓")
        icon.setFont(QFont(F['family_primary'], F['size_xlarge']))
        icon.setStyleSheet(f"color: {C['success']};")
        frame_layout.addWidget(icon)
        
        # Messaggio
        label = QLabel(message)
        label.setFont(QFont(F['family_primary'], F['size_normal']))
        label.setStyleSheet(f"color: {C['text_primary']};")
        frame_layout.addWidget(label)
        
        layout.addWidget(frame)
        self.setLayout(layout)
        
        # Posizione (angolo basso destro)
        self.adjustSize()
        self.position_bottom_right()
        
        # Animazione fade in
        self.setWindowOpacity(0)
        self.fade_in()
        
        # Timer per chiusura
        QTimer.singleShot(duration, self.fade_out)
    
    def position_bottom_right(self):
        """Posiziona in basso a destra"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 20
        y = screen.height() - self.height() - 60
        self.move(x, y)
    
    def fade_in(self):
        """Animazione fade in"""
        self.show()
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(200)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
        self._fade_in_anim = animation  # Keep reference
    
    def fade_out(self):
        """Animazione fade out"""
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(200)
        animation.setStartValue(1)
        animation.setEndValue(0)
        animation.setEasingCurve(QEasingCurve.InCubic)
        animation.finished.connect(self.close)
        animation.start()
        self._fade_out_anim = animation  # Keep reference


class ToolTip:
    """Helper per tooltip (Qt li gestisce nativamente)"""
    
    @staticmethod
    def create_tooltip(widget, text):
        """Imposta tooltip su widget"""
        widget.setToolTip(text)
