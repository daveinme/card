"""
SD Card Photo Importer - PySide6 Version
Interfaccia ultra professionale con doppio monitor
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton, QProgressBar, QGridLayout, QFrame,
                                QFileDialog, QMessageBox, QCheckBox, QRadioButton, QComboBox,
                                QButtonGroup, QScrollArea, QTabWidget, QTreeWidget, QTreeWidgetItem,
                                QDialog, QLineEdit, QGroupBox)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QThread
from PySide6.QtGui import QPixmap, QFont, QIcon, QShortcut, QKeySequence
from PIL import Image
try:
    from plyer import notification
    HAS_NOTIFICATION = True
except:
    HAS_NOTIFICATION = False

# Importa moduli
from config import (DESTINATION_BASE, SD_DRIVE_LETTER, PHOTO_EXTENSIONS, PRINT_LOG_FILE,
                    THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, GRID_ROWS, GRID_COLUMNS, PHOTOS_PER_PAGE,
                    C, F, S, B)
from secondary_window_qt import SecondaryDisplayWindow
from print_manager_qt import PrintManager
from photo_manager import PhotoManager
from professional_features_qt import (ModernButton, StatusBar, Toolbar,
                                      SplashScreen, AboutDialog, ToastNotification)


class ImportWorker(QObject):
    """Worker per importazione foto in background"""
    progress = Signal(int, int, str)  # completed, total, filename
    finished = Signal(int, int)  # completed, errors

    def __init__(self, photo_files, dest_folder, cut_mode):
        super().__init__()
        self.photo_files = photo_files
        self.dest_folder = dest_folder
        self.cut_mode = cut_mode

    def run(self):
        completed = 0
        errors = 0

        def process_photo(source_path):
            filename = os.path.basename(source_path)
            dest_path = os.path.join(self.dest_folder, filename)

            if os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                num = 1
                while os.path.exists(dest_path):
                    dest_path = os.path.join(self.dest_folder, f"{name}_{num}{ext}")
                    num += 1

            try:
                if self.cut_mode:
                    shutil.move(source_path, dest_path)
                else:
                    shutil.copy2(source_path, dest_path)
                return True, filename
            except Exception as e:
                print(f"Errore: {e}")
                return False, filename

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_photo = {executor.submit(process_photo, photo): photo
                              for photo in self.photo_files}

            for future in as_completed(future_to_photo):
                success, filename = future.result()

                if success:
                    completed += 1
                else:
                    errors += 1

                self.progress.emit(completed, len(self.photo_files), filename)

        self.finished.emit(completed, errors)


class MainWindow(QMainWindow):
    """Finestra principale con interfaccia Qt"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SD Card Photo Importer - Professional Edition (Qt)")
        self.setGeometry(100, 100, 1600, 1000)

        # Variabili
        self.current_folder = None
        self.all_photos = []
        self.selected_photos = set()
        self.photo_copies = {}  # {photo_path: num_copies}
        self.current_page = 0
        self.show_only_selected = False
        self.thumbnail_cache = {}

        # Print Manager
        self.print_manager = PrintManager(self)

        # Finestra secondaria
        self.secondary_window = SecondaryDisplayWindow(main_window=self)

        # Import thread
        self.import_thread = None
        self.import_worker = None

        # Setup UI
        self.create_ui()
        self.setup_shortcuts()

        # Carica stampanti e controlla SD
        self.load_printers()
        self.check_sd_card()

    def create_ui(self):
        """Crea interfaccia"""
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principale
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header con gradiente
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C['dark_surface']}, stop:1 {C['dark_panel']});
                padding: 15px;
                border-bottom: 2px solid {C['primary']};
            }}
        """)
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)

        title = QLabel("📸 SD CARD PHOTO IMPORTER")
        title.setFont(QFont(F['family_primary'], F['size_xlarge'], F['weight_bold']))
        title.setStyleSheet(f"color: {C['primary']};")
        header_layout.addWidget(title)

        subtitle = QLabel("Professional Edition (Qt)")
        subtitle.setFont(QFont(F['family_primary'], F['size_normal']))
        subtitle.setStyleSheet(f"color: {C['text_secondary']};")
        header_layout.addWidget(subtitle)
        header_layout.addStretch()

        main_layout.addWidget(header)

        # Container contenuto
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # === PANNELLO SINISTRO ===
        left_panel = QFrame()
        left_panel.setFixedWidth(350)
        left_panel.setStyleSheet(f"background-color: {C['dark_bg']};")
        left_layout = QVBoxLayout(left_panel)

        # 1. IMPORTAZIONE
        import_group = QGroupBox("📥 IMPORTAZIONE DA SD")
        import_group.setStyleSheet(f"""
            QGroupBox {{
                color: {C['text_primary']};
                font-weight: bold;
                font-size: {F['size_normal']}px;
                background-color: {C['dark_surface']};
                border: 1px solid {C['dark_panel']};
                border-radius: {B['radius_md']}px;
                margin-top: 12px;
                padding: 15px 10px 10px 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 8px;
                background-color: {C['dark_surface']};
            }}
        """)
        import_layout = QVBoxLayout(import_group)

        # SD status
        sd_row = QHBoxLayout()
        sd_label_text = QLabel("Unità SD:")
        sd_label_text.setStyleSheet(f"color: {C['text_primary']};")
        self.sd_label = QLabel("Non rilevata")
        self.sd_label.setStyleSheet(f"color: {C['danger']}; font-weight: bold;")
        sd_row.addWidget(sd_label_text)
        sd_row.addWidget(self.sd_label)
        sd_row.addStretch()

        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedWidth(40)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['dark_panel']};
                color: {C['text_primary']};
                border: 1px solid {C['dark_panel']};
                border-radius: {B['radius_sm']}px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {C['primary']};
                border-color: {C['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {C['primary_active']};
            }}
        """)
        refresh_btn.clicked.connect(self.check_sd_card)
        sd_row.addWidget(refresh_btn)

        import_layout.addLayout(sd_row)

        # Pulsante importa
        self.import_btn = ModernButton("📥 IMPORTA FOTO DA SD CARD")
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self.import_photos)
        import_layout.addWidget(self.import_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(24)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {C['dark_panel']};
                border-radius: {B['radius_md']}px;
                text-align: center;
                background-color: {C['dark_panel']};
                color: {C['text_primary']};
                font-weight: bold;
                font-size: {F['size_normal']}px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C['primary']}, stop:1 {C['primary_hover']});
                border-radius: {B['radius_sm']}px;
            }}
        """)
        import_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet(f"color: {C['text_secondary']};")
        import_layout.addWidget(self.progress_label)

        left_layout.addWidget(import_group)

        # 2. CARTELLA
        folder_group = QGroupBox("📁 CARTELLA CORRENTE")
        folder_group.setStyleSheet(import_group.styleSheet())
        folder_layout = QVBoxLayout(folder_group)

        btn_row = QHBoxLayout()

        browse_btn = QPushButton("📂 Sfoglia")
        browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['dark_panel']};
                color: {C['text_primary']};
                border: 1px solid {C['dark_panel']};
                border-radius: {B['radius_sm']}px;
                padding: 8px 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {C['primary']};
                border-color: {C['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {C['primary_active']};
            }}
        """)
        browse_btn.clicked.connect(self.browse_folder)

        base_btn = QPushButton("🏠 Base")
        base_btn.setStyleSheet(browse_btn.styleSheet())
        base_btn.clicked.connect(self.go_to_base)

        btn_row.addWidget(browse_btn)
        btn_row.addWidget(base_btn)
        folder_layout.addLayout(btn_row)

        self.folder_label = QLabel("Nessuna cartella")
        self.folder_label.setWordWrap(True)
        self.folder_label.setStyleSheet(f"color: {C['text_secondary']};")
        folder_layout.addWidget(self.folder_label)

        self.folder_info_label = QLabel("")
        self.folder_info_label.setStyleSheet(f"color: {C['text_primary']}; font-weight: bold;")
        folder_layout.addWidget(self.folder_info_label)

        left_layout.addWidget(folder_group)

        # 3. SELEZIONE
        select_group = QGroupBox("✓ SELEZIONE FOTO")
        select_group.setStyleSheet(import_group.styleSheet())
        select_layout = QVBoxLayout(select_group)

        self.selection_label = QLabel("0 foto selezionate")
        self.selection_label.setStyleSheet(f"color: {C['success']}; font-weight: bold;")
        select_layout.addWidget(self.selection_label)

        button_style = f"""
            QPushButton {{
                background-color: {C['dark_panel']};
                color: {C['text_primary']};
                border: 1px solid {C['dark_panel']};
                border-radius: {B['radius_sm']}px;
                padding: 8px 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {C['success']};
                border-color: {C['success_light']};
            }}
            QPushButton:pressed {{
                background-color: #0d9668;
            }}
        """

        sel_row = QHBoxLayout()
        page_btn = QPushButton("✓ Pagina")
        page_btn.setStyleSheet(button_style)
        page_btn.clicked.connect(self.select_current_page)
        all_btn = QPushButton("✓✓ Tutte")
        all_btn.setStyleSheet(button_style)
        all_btn.clicked.connect(self.select_all)
        sel_row.addWidget(page_btn)
        sel_row.addWidget(all_btn)
        select_layout.addLayout(sel_row)

        deselect_btn = QPushButton("✗ Deseleziona Tutte")
        deselect_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['dark_panel']};
                color: {C['text_primary']};
                border: 1px solid {C['dark_panel']};
                border-radius: {B['radius_sm']}px;
                padding: 8px 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {C['danger']};
                border-color: #f87171;
            }}
            QPushButton:pressed {{
                background-color: #dc2626;
            }}
        """)
        deselect_btn.clicked.connect(self.deselect_all)
        select_layout.addWidget(deselect_btn)

        left_layout.addWidget(select_group)

        # 4. STAMPA
        print_group = QGroupBox("🖨️ STAMPA")
        print_group.setStyleSheet(import_group.styleSheet())
        print_layout = QVBoxLayout(print_group)

        printer_label = QLabel("Stampante:")
        printer_label.setStyleSheet(f"color: {C['text_primary']};")
        print_layout.addWidget(printer_label)

        printer_row = QHBoxLayout()
        self.printer_combo = QComboBox()
        self.printer_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {C['dark_panel']};
                color: {C['text_primary']};
                border: 1px solid {C['dark_panel']};
                border-radius: {B['radius_sm']}px;
                padding: 6px 10px;
                font-size: {F['size_normal']}px;
            }}
            QComboBox:hover {{
                border-color: {C['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {C['text_primary']};
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {C['dark_panel']};
                color: {C['text_primary']};
                selection-background-color: {C['primary']};
                border: 1px solid {C['primary']};
            }}
        """)
        printer_row.addWidget(self.printer_combo, 1)

        refresh_printer_btn = QPushButton("🔄")
        refresh_printer_btn.setFixedWidth(40)
        refresh_printer_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['dark_panel']};
                color: {C['text_primary']};
                border: 1px solid {C['dark_panel']};
                border-radius: {B['radius_sm']}px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {C['primary']};
            }}
            QPushButton:pressed {{
                background-color: {C['primary_active']};
            }}
        """)
        refresh_printer_btn.clicked.connect(self.load_printers)
        printer_row.addWidget(refresh_printer_btn)
        print_layout.addLayout(printer_row)

        self.print_btn = ModernButton("🖨️ STAMPA SELEZIONATE")
        self.print_btn.setEnabled(False)
        self.print_btn.clicked.connect(self.print_photos)
        print_layout.addWidget(self.print_btn)

        left_layout.addWidget(print_group)
        left_layout.addStretch()

        content_layout.addWidget(left_panel)

        # === PANNELLO DESTRO ===
        right_panel = QFrame()
        right_panel.setStyleSheet(f"background-color: {C['dark_bg']};")
        right_layout = QVBoxLayout(right_panel)

        # Header griglia
        grid_header = QFrame()
        grid_header.setStyleSheet(f"background-color: {C['dark_bg']};")
        grid_header.setFixedHeight(40)
        grid_header_layout = QHBoxLayout(grid_header)

        self.grid_header_label = QLabel("🖼️ MINIATURE")
        self.grid_header_label.setFont(QFont(F['family_primary'], F['size_normal'], F['weight_semibold']))
        self.grid_header_label.setStyleSheet(f"color: {C['text_secondary']};")
        grid_header_layout.addWidget(self.grid_header_label)

        right_layout.addWidget(grid_header)

        # Barra controlli
        controls_bar = QFrame()
        controls_bar.setStyleSheet(f"background-color: {C['dark_bg']};")
        controls_bar.setFixedHeight(50)
        controls_layout = QHBoxLayout(controls_bar)

        nav_button_style = f"""
            QPushButton {{
                background-color: {C['dark_panel']};
                color: {C['text_primary']};
                border: 1px solid {C['dark_panel']};
                border-radius: {B['radius_sm']}px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: {F['size_normal']}px;
            }}
            QPushButton:hover:enabled {{
                background-color: {C['primary']};
                border-color: {C['primary_hover']};
            }}
            QPushButton:pressed:enabled {{
                background-color: {C['primary_active']};
            }}
            QPushButton:disabled {{
                background-color: {C['dark_bg']};
                color: {C['text_disabled']};
            }}
        """

        self.prev_btn = QPushButton("◄ Indietro")
        self.prev_btn.setStyleSheet(nav_button_style)
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(self.prev_page)
        controls_layout.addWidget(self.prev_btn)

        self.page_label = QLabel("0 / 0")
        self.page_label.setFont(QFont(F['family_primary'], F['size_xlarge'], F['weight_bold']))
        self.page_label.setStyleSheet(f"color: {C['primary']};")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setFixedWidth(100)
        controls_layout.addWidget(self.page_label)

        self.next_btn = QPushButton("Avanti ►")
        self.next_btn.setStyleSheet(nav_button_style)
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self.next_page)
        controls_layout.addWidget(self.next_btn)

        controls_layout.addStretch()

        self.filter_btn = QPushButton("👁️ Mostra SOLO Selezionate")
        self.filter_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['dark_panel']};
                color: {C['text_primary']};
                border: 1px solid {C['dark_panel']};
                border-radius: {B['radius_sm']}px;
                padding: 10px 16px;
                font-weight: 600;
            }}
            QPushButton:hover:enabled {{
                background-color: {C['warning']};
                border-color: #fbbf24;
            }}
            QPushButton:pressed:enabled {{
                background-color: #d97706;
            }}
            QPushButton:disabled {{
                background-color: {C['dark_bg']};
                color: {C['text_disabled']};
            }}
        """)
        self.filter_btn.setEnabled(False)
        self.filter_btn.clicked.connect(self.toggle_filter)
        controls_layout.addWidget(self.filter_btn)

        right_layout.addWidget(controls_bar)

        # Griglia foto
        grid_scroll = QScrollArea()
        grid_scroll.setWidgetResizable(True)
        grid_scroll.setStyleSheet(f"background-color: {C['dark_bg']}; border: none;")

        grid_widget = QWidget()
        self.grid_layout = QGridLayout(grid_widget)
        self.grid_layout.setSpacing(12)

        self.thumbnail_widgets = []
        for row in range(GRID_ROWS):
            for col in range(GRID_COLUMNS):
                # Frame cella con stile migliorato
                cell_frame = QFrame()
                cell_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: transparent;
                        border: none;
                    }}
                """)
                cell_frame.setCursor(Qt.PointingHandCursor)

                cell_layout = QVBoxLayout(cell_frame)
                cell_layout.setContentsMargins(0, 0, 0, 0)
                cell_layout.setSpacing(0)

                # Container foto con numero overlay
                photo_container = QWidget()
                photo_container_layout = QVBoxLayout(photo_container)
                photo_container_layout.setContentsMargins(0, 0, 0, 0)
                photo_container_layout.setSpacing(2)

                # Spinbox copie
                from PySide6.QtWidgets import QSpinBox
                copies_spin = QSpinBox()
                copies_spin.setRange(1, 10)
                copies_spin.setValue(1)
                copies_spin.setFixedWidth(60)
                copies_spin.setPrefix("×")
                copies_spin.setAlignment(Qt.AlignCenter)
                copies_spin.setStyleSheet(f"""
                    QSpinBox {{
                        background-color: {C['dark_panel']};
                        color: {C['text_primary']};
                        border: 1px solid {C['primary']};
                        border-radius: {B['radius_sm']}px;
                        padding: 4px;
                        font-weight: bold;
                    }}
                    QSpinBox::up-button, QSpinBox::down-button {{
                        background-color: {C['primary']};
                        border: none;
                        width: 16px;
                    }}
                    QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                        background-color: {C['primary_hover']};
                    }}
                """)
                copies_spin.setVisible(False)
                photo_container_layout.addWidget(copies_spin)

                # Foto
                photo_label = QLabel()
                photo_label.setAlignment(Qt.AlignCenter)
                photo_label.setStyleSheet("background-color: black;")
                photo_label.setScaledContents(True)
                photo_container_layout.addWidget(photo_label)

                # Numero overlay (top-left)
                num_label = QLabel("", photo_label)
                num_label.setFont(QFont(F['family_primary'], 8, F['weight_bold']))
                num_label.setStyleSheet(f"""
                    background-color: rgba(0, 0, 0, 180);
                    color: {C['text_primary']};
                    padding: 2px 6px;
                    border-radius: 3px;
                """)
                num_label.setFixedHeight(16)
                num_label.move(4, 4)

                cell_layout.addWidget(photo_container)

                # Click handler
                idx = row * GRID_COLUMNS + col
                cell_frame.mousePressEvent = lambda e, i=idx: self.toggle_photo_selection(i)

                self.grid_layout.addWidget(cell_frame, row, col)

                self.thumbnail_widgets.append({
                    'frame': cell_frame,
                    'num_label': num_label,
                    'copies_spin': copies_spin,
                    'photo_label': photo_label,
                    'photo_path': None
                })

        grid_scroll.setWidget(grid_widget)
        right_layout.addWidget(grid_scroll, 1)

        content_layout.addWidget(right_panel, 1)

        main_layout.addWidget(content, 1)

        # Status bar
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.set_status("Pronto")

    def setup_shortcuts(self):
        """Configura scorciatoie"""
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.browse_folder)
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.go_to_base)
        QShortcut(QKeySequence("Ctrl+I"), self).activated.connect(self.import_photos)
        QShortcut(QKeySequence("Ctrl+A"), self).activated.connect(self.select_all)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self.deselect_all)
        QShortcut(QKeySequence("Ctrl+P"), self).activated.connect(self.print_photos)
        QShortcut(QKeySequence("Left"), self).activated.connect(self.prev_page)
        QShortcut(QKeySequence("Right"), self).activated.connect(self.next_page)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.check_sd_card)

        # Selezione foto con numeri 1-9
        for num in range(1, 10):
            QShortcut(QKeySequence(str(num)), self).activated.connect(
                lambda n=num: self.select_photo_by_number(n)
            )

    def update_copies(self, photo_path, copies):
        """Aggiorna numero copie per una foto"""
        self.photo_copies[photo_path] = copies

    def select_photo_by_number(self, number):
        """Seleziona foto tramite tastiera numerica (1-9)"""
        if not self.all_photos:
            return

        # Converti numero (1-9) in indice griglia (0-8)
        idx = number - 1

        # Verifica che l'indice sia valido (0-8 per griglia 3x3)
        if 0 <= idx < PHOTOS_PER_PAGE:
            self.toggle_photo_selection(idx)

    def check_sd_card(self):
        """Controlla presenza SD"""
        if SD_DRIVE_LETTER:
            drive = f"{SD_DRIVE_LETTER.upper()}:\\"
            if os.path.exists(drive):
                photo_count = 0
                try:
                    for root, dirs, files in os.walk(drive):
                        for file in files:
                            if Path(file).suffix.lower() in {'.jpg', '.jpeg', '.png', '.heic'}:
                                photo_count += 1
                except:
                    pass

                self.sd_label.setText(f"{drive} ({photo_count} foto)")
                self.sd_label.setStyleSheet(f"color: {C['success']}; font-weight: bold;")
                self.import_btn.setEnabled(True)
            else:
                self.sd_label.setText("Non rilevata")
                self.sd_label.setStyleSheet(f"color: {C['danger']}; font-weight: bold;")
                self.import_btn.setEnabled(False)

    def import_photos(self):
        """Importa foto da SD"""
        if not SD_DRIVE_LETTER:
            QMessageBox.warning(self, "Errore", "Nessuna unità SD configurata")
            return

        drive = f"{SD_DRIVE_LETTER.upper()}:\\"
        if not os.path.exists(drive):
            QMessageBox.warning(self, "Errore", "SD card non trovata")
            return

        # Crea cartella destinazione
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_folder = os.path.join(DESTINATION_BASE, date_str)
        os.makedirs(date_folder, exist_ok=True)

        counter = 1
        while True:
            dest_folder = os.path.join(date_folder, str(counter))
            if not os.path.exists(dest_folder):
                break
            counter += 1

        os.makedirs(dest_folder, exist_ok=True)

        # Trova foto
        photo_files = []
        for root, dirs, files in os.walk(drive):
            for file in files:
                if Path(file).suffix.lower() in {'.jpg', '.jpeg', '.png', '.heic', '.raw', '.cr2', '.nef', '.arw'}:
                    photo_files.append(os.path.join(root, file))

        if not photo_files:
            QMessageBox.information(self, "Info", "Nessuna foto trovata sulla SD card")
            return

        # Conferma
        action = "copiare"
        reply = QMessageBox.question(self, "Conferma",
                                    f"Trovate {len(photo_files)} foto.\n"
                                    f"Verranno {action} in:\n{dest_folder}\n\n"
                                    f"Continuare?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        # Importa in thread
        self.import_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(photo_files))

        self.import_thread = QThread()
        self.import_worker = ImportWorker(photo_files, dest_folder, False)
        self.import_worker.moveToThread(self.import_thread)

        self.import_worker.progress.connect(self.on_import_progress)
        self.import_worker.finished.connect(lambda c, e: self.on_import_finished(c, e, dest_folder))
        self.import_thread.started.connect(self.import_worker.run)

        self.import_thread.start()

    def on_import_progress(self, completed, total, filename):
        """Aggiorna progress"""
        self.progress_bar.setValue(completed)
        progress = (completed / total) * 100
        self.progress_label.setText(f"{progress:.0f}% - {filename}")

    def on_import_finished(self, completed, errors, dest_folder):
        """Import completato"""
        self.import_thread.quit()
        self.import_thread.wait()

        result_text = f"Importate {completed} foto!" + (f" ({errors} errori)" if errors else "")
        self.progress_label.setText(result_text)
        self.import_btn.setEnabled(True)

        # Differire caricamento per evitare timeout
        QTimer.singleShot(100, lambda: self.load_folder(dest_folder))
        QTimer.singleShot(200, self.check_sd_card)

        if HAS_NOTIFICATION:
            try:
                notification.notify(
                    title="Importazione Completata",
                    message=f"{completed} foto importate",
                    app_name="SD Card Importer",
                    timeout=5
                )
            except:
                pass

    def browse_folder(self):
        """Sfoglia cartella"""
        folder = QFileDialog.getExistingDirectory(self, "Seleziona cartella con foto",
                                                  DESTINATION_BASE)
        if folder:
            self.load_folder(folder)

    def go_to_base(self):
        """Vai a cartella base"""
        if os.path.exists(DESTINATION_BASE):
            self.load_folder(DESTINATION_BASE)

    def load_folder(self, folder_path):
        """Carica foto da cartella"""
        self.current_folder = folder_path
        self.status_bar.set_status("Caricamento cartella...", C['primary'])
        QApplication.processEvents()

        folder_display = folder_path if len(folder_path) <= 50 else "..." + folder_path[-47:]
        self.folder_label.setText(folder_display)

        # Trova foto
        self.all_photos = []
        try:
            for file in os.listdir(folder_path):
                filepath = os.path.join(folder_path, file)
                if os.path.isfile(filepath) and Path(file).suffix.lower() in {'.jpg', '.jpeg', '.png', '.heic'}:
                    self.all_photos.append(filepath)
        except Exception as e:
            self.status_bar.set_status("Errore caricamento", C['danger'])
            QMessageBox.critical(self, "Errore", f"Impossibile leggere la cartella:\n{e}")
            return

        self.all_photos.sort()
        self.current_page = 0
        self.selected_photos.clear()
        self.thumbnail_cache.clear()
        self.secondary_window.clear_cache()

        QApplication.processEvents()
        self.folder_info_label.setText(f"📷 {len(self.all_photos)} foto")
        self.update_displays()

        self.status_bar.set_status(f"Caricate {len(self.all_photos)} foto", C['success'])

    def toggle_filter(self):
        """Toggle filtro selezionate"""
        if not self.selected_photos:
            return

        self.show_only_selected = not self.show_only_selected
        self.current_page = 0

        if self.show_only_selected:
            self.filter_btn.setText("📋 Mostra TUTTE")
            self.grid_header_label.setText("✓ SELEZIONATE")
        else:
            self.filter_btn.setText("👁️ Solo Selezionate")
            self.grid_header_label.setText("🖼️ MINIATURE")

        self.update_displays()

    def get_display_photos(self):
        """Ritorna foto da visualizzare"""
        if self.show_only_selected:
            return [p for p in self.all_photos if p in self.selected_photos]
        else:
            return self.all_photos

    def prev_page(self):
        """Pagina precedente"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_displays()

    def next_page(self):
        """Pagina successiva"""
        display_photos = self.get_display_photos()
        total_pages = (len(display_photos) + PHOTOS_PER_PAGE - 1) // PHOTOS_PER_PAGE
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_displays()

    def toggle_photo_selection(self, idx):
        """Toggle selezione foto"""
        widget = self.thumbnail_widgets[idx]

        if widget['photo_path'] is None:
            return

        photo_path = widget['photo_path']

        if photo_path in self.selected_photos:
            self.selected_photos.remove(photo_path)
            if photo_path in self.photo_copies:
                del self.photo_copies[photo_path]
            widget['frame'].setStyleSheet(f"""
                QFrame {{
                    background-color: transparent;
                    border: none;
                }}
            """)
            widget['num_label'].setStyleSheet(f"background-color: rgba(0,0,0,180); color: {C['text_disabled']}; padding: 2px 6px; border-radius: 3px;")
            widget['copies_spin'].setVisible(False)
        else:
            self.selected_photos.add(photo_path)
            self.photo_copies[photo_path] = 1
            widget['frame'].setStyleSheet(f"""
                QFrame {{
                    background-color: transparent;
                    border: 2px solid {C['success']};
                    border-radius: 6px;
                }}
            """)
            widget['num_label'].setStyleSheet(f"background-color: rgba(0,0,0,180); color: {C['success']}; padding: 2px 6px; border-radius: 3px; font-weight: bold;")
            widget['copies_spin'].setVisible(True)
            widget['copies_spin'].blockSignals(True)
            widget['copies_spin'].setValue(1)
            widget['copies_spin'].blockSignals(False)

            # Disconnect previous connection if exists
            if hasattr(widget, 'copies_signal_connection'):
                try:
                    widget['copies_spin'].valueChanged.disconnect(widget['copies_signal_connection'])
                except (TypeError, RuntimeError):
                    pass

            # Create and connect new handler
            widget['copies_signal_connection'] = lambda v, p=photo_path: self.update_copies(p, v)
            widget['copies_spin'].valueChanged.connect(widget['copies_signal_connection'])

        # Aggiorna labels
        self.selection_label.setText(f"{len(self.selected_photos)} foto selezionate")
        self.print_btn.setEnabled(len(self.selected_photos) > 0)
        self.filter_btn.setEnabled(len(self.selected_photos) > 0)

        if self.show_only_selected:
            self.update_displays()
        else:
            self.secondary_window.update_display(self.all_photos, self.current_page,
                                                self.selected_photos, self.show_only_selected)

    def select_current_page(self):
        """Seleziona pagina corrente"""
        display_photos = self.get_display_photos()
        start_idx = self.current_page * PHOTOS_PER_PAGE
        end_idx = min(start_idx + PHOTOS_PER_PAGE, len(display_photos))

        for i in range(start_idx, end_idx):
            photo = display_photos[i]
            self.selected_photos.add(photo)
            if photo not in self.photo_copies:
                self.photo_copies[photo] = 1

        self.update_displays()

    def select_all(self):
        """Seleziona tutte"""
        self.selected_photos = set(self.all_photos)
        for photo in self.all_photos:
            if photo not in self.photo_copies:
                self.photo_copies[photo] = 1
        self.update_displays()

    def deselect_all(self):
        """Deseleziona tutte"""
        self.selected_photos.clear()
        self.photo_copies.clear()

        if self.show_only_selected:
            self.show_only_selected = False
            self.filter_btn.setText("👁️ Mostra SOLO Selezionate")
            self.grid_header_label.setText("🖼️ MINIATURE - Click per selezionare")

        self.update_displays()

    def update_displays(self):
        """Aggiorna display"""
        display_photos = self.get_display_photos()
        total_pages = (len(display_photos) + PHOTOS_PER_PAGE - 1) // PHOTOS_PER_PAGE if display_photos else 0

        if self.current_page >= total_pages and total_pages > 0:
            self.current_page = total_pages - 1

        self.page_label.setText(f"{self.current_page + 1} / {total_pages}" if total_pages > 0 else "0 / 0")

        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)

        self.selection_label.setText(f"{len(self.selected_photos)} foto selezionate")
        self.print_btn.setEnabled(len(self.selected_photos) > 0)
        self.filter_btn.setEnabled(len(self.selected_photos) > 0)

        # Aggiorna griglia
        start_idx = self.current_page * PHOTOS_PER_PAGE
        end_idx = min(start_idx + PHOTOS_PER_PAGE, len(display_photos))
        page_photos = display_photos[start_idx:end_idx] if display_photos else []

        for i, widget in enumerate(self.thumbnail_widgets):
            if i < len(page_photos):
                photo_path = page_photos[i]
                widget['photo_path'] = photo_path

                try:
                    global_num = self.all_photos.index(photo_path) + 1
                except ValueError:
                    global_num = start_idx + i + 1

                widget['num_label'].setText(f"#{global_num}")

                # Carica thumbnail
                if photo_path in self.thumbnail_cache:
                    pixmap = self.thumbnail_cache[photo_path]
                else:
                    try:
                        # Carica direttamente da file
                        pixmap = QPixmap(photo_path)
                        if pixmap.isNull():
                            raise Exception("Impossibile caricare immagine")

                        # Scala mantenendo proporzioni
                        pixmap = pixmap.scaled(225, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.thumbnail_cache[photo_path] = pixmap
                    except Exception as e:
                        print(f"Errore caricamento: {e}")
                        pixmap = QPixmap()

                widget['photo_label'].setPixmap(pixmap)

                # Evidenzia se selezionata
                if photo_path in self.selected_photos:
                    widget['frame'].setStyleSheet(f"""
                        QFrame {{
                            background-color: transparent;
                            border: 2px solid {C['success']};
                            border-radius: 6px;
                        }}
                    """)
                    widget['num_label'].setStyleSheet(f"background-color: rgba(0,0,0,180); color: {C['success']}; padding: 2px 6px; border-radius: 3px; font-weight: bold;")
                    widget['copies_spin'].setVisible(True)
                    widget['copies_spin'].blockSignals(True)
                    widget['copies_spin'].setValue(self.photo_copies.get(photo_path, 1))
                    widget['copies_spin'].blockSignals(False)

                    # Disconnect previous connection if exists
                    if hasattr(widget, 'copies_signal_connection'):
                        try:
                            widget['copies_spin'].valueChanged.disconnect(widget['copies_signal_connection'])
                        except (TypeError, RuntimeError):
                            pass

                    # Create and connect new handler
                    widget['copies_signal_connection'] = lambda v, p=photo_path: self.update_copies(p, v)
                    widget['copies_spin'].valueChanged.connect(widget['copies_signal_connection'])
                else:
                    widget['frame'].setStyleSheet(f"""
                        QFrame {{
                            background-color: transparent;
                            border: none;
                        }}
                    """)
                    widget['num_label'].setStyleSheet(f"background-color: rgba(0,0,0,180); color: {C['text_disabled']}; padding: 2px 6px; border-radius: 3px;")
                    widget['copies_spin'].setVisible(False)

            else:
                # Cella vuota
                widget['photo_path'] = None
                widget['num_label'].setText("")
                widget['copies_spin'].setVisible(False)
                widget['photo_label'].clear()
                widget['frame'].setStyleSheet(f"""
                    QFrame {{
                        background-color: transparent;
                        border: none;
                    }}
                """)

        # Aggiorna finestra secondaria
        self.secondary_window.update_display(self.all_photos, self.current_page,
                                           self.selected_photos, self.show_only_selected)

    def load_printers(self):
        """Carica stampanti"""
        printers = self.print_manager.get_available_printers()
        self.printer_combo.clear()
        self.printer_combo.addItems(printers)

        if printers:
            default_printer = self.print_manager.get_default_printer()
            if default_printer and default_printer in printers:
                self.printer_combo.setCurrentText(default_printer)

    def print_photos(self):
        """Stampa foto"""
        if not self.selected_photos:
            return

        printer_name = self.printer_combo.currentText()
        if not printer_name:
            QMessageBox.warning(self, "Errore", "Seleziona una stampante")
            return

        num_photos = len(self.selected_photos)
        total_prints = sum(self.photo_copies.get(p, 1) for p in self.selected_photos)

        reply = QMessageBox.question(self, "Conferma Stampa",
                                    f"Stampare {num_photos} foto = {total_prints} fogli totali\n"
                                    f"Stampante: {printer_name}",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        # Finestra progresso
        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle("Stampa in corso...")
        progress_dialog.setModal(True)
        progress_dialog.setFixedSize(500, 200)

        layout = QVBoxLayout(progress_dialog)

        title_label = QLabel("Stampa con Spooler Interno")
        title_label.setFont(QFont(F['family_primary'], F['size_large'], F['weight_bold']))
        layout.addWidget(title_label)

        progress_var = QProgressBar()
        progress_var.setMaximum(total_prints)
        layout.addWidget(progress_var)

        status_label = QLabel("Inizializzazione...")
        layout.addWidget(status_label)

        info_label = QLabel("Lo spooler attende che ogni foto\nsia processata prima di inviare la successiva")
        info_label.setStyleSheet(f"color: {C['text_secondary']};")
        layout.addWidget(info_label)

        # Callbacks
        def update_progress(completed):
            progress_var.setValue(completed)

        def update_status(message):
            status_label.setText(message)

        def on_completion(success):
            if success:
                progress_dialog.accept()
            else:
                QTimer.singleShot(2000, progress_dialog.reject)

        # Setup print manager
        class PrinterVar:
            def __init__(self, text):
                self.text = text
            def get(self):
                return self.text

        self.print_manager.printer_var = PrinterVar(printer_name)

        # Stampa
        photos_with_copies = [(p, self.photo_copies.get(p, 1)) for p in sorted(self.selected_photos)]
        self.print_manager.print_photos_with_spooler(
            photos=photos_with_copies,
            printer_name=printer_name,
            photo_format="auto",
            progress_callback=update_progress,
            status_callback=update_status,
            completion_callback=on_completion
        )

        progress_dialog.exec()


def main():
    """Avvia applicazione"""
    app = QApplication(sys.argv)

    # Crea cartella base
    os.makedirs(DESTINATION_BASE, exist_ok=True)

    # Finestra principale
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
