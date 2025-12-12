"""
SD Card Photo Importer - Secondary Display Window (PySide6)
Finestra secondaria per visualizzazione foto su secondo monitor
"""

from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont, QCursor

from config import GRID_ROWS, GRID_COLUMNS, PHOTOS_PER_PAGE, C


class SecondaryDisplayWindow(QWidget):
    """Finestra ULTRA-MINIMALE per secondo monitor - SOLO FOTO"""

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.is_fullscreen = False
        self.photo_cache = {}

        self.setWindowTitle("Visualizzatore Foto")
        self.setGeometry(100, 100, 1600, 900)
        self.setMinimumSize(800, 600)  # Dimensioni minime ragionevoli
        self.setStyleSheet(f"background-color: {C['dark_bg']};")

        # Layout principale
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Griglia foto
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)

        self.photo_widgets = []
        for row in range(GRID_ROWS):
            for col in range(GRID_COLUMNS):
                # Frame foto (minimal)
                photo_frame = QFrame()
                photo_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {C['dark_bg']};
                        border: none;
                    }}
                """)

                # Layout frame
                frame_layout = QVBoxLayout(photo_frame)
                frame_layout.setContentsMargins(0, 0, 0, 0)

                # Numero foto
                num_label = QLabel("")
                num_label.setFont(QFont("Arial", 10))
                num_label.setStyleSheet(f"color: {C['text_disabled']};")
                num_label.setAlignment(Qt.AlignCenter)
                frame_layout.addWidget(num_label)

                # Label foto
                photo_label = QLabel()
                photo_label.setAlignment(Qt.AlignCenter)
                photo_label.setStyleSheet("background-color: black;")
                photo_label.setScaledContents(False)
                frame_layout.addWidget(photo_label, 1)

                # Click handler per selezione
                idx = row * GRID_COLUMNS + col
                photo_frame.setCursor(Qt.PointingHandCursor)
                photo_frame.mousePressEvent = lambda e, i=idx: self.on_photo_click(i)

                self.grid_layout.addWidget(photo_frame, row, col)
                self.photo_widgets.append({
                    'frame': photo_frame,
                    'num_label': num_label,
                    'label': photo_label,
                    'photo_path': None
                })

        main_layout.addLayout(self.grid_layout, 1)
        self.setLayout(main_layout)

        # Shortcuts
        self.setup_shortcuts()
        self.show()

    def setup_shortcuts(self):
        """Configura scorciatoie tastiera"""
        from PySide6.QtGui import QShortcut, QKeySequence

        # F11 per fullscreen
        QShortcut(QKeySequence("F11"), self).activated.connect(self.toggle_fullscreen)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self.exit_fullscreen)

        # F/H per filtro solo selezionate
        QShortcut(QKeySequence("F"), self).activated.connect(self.toggle_filter)
        QShortcut(QKeySequence("H"), self).activated.connect(self.toggle_filter)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.toggle_filter)

        # Frecce per navigazione pagine
        QShortcut(QKeySequence("Left"), self).activated.connect(self.prev_page)
        QShortcut(QKeySequence("Right"), self).activated.connect(self.next_page)

    def toggle_filter(self):
        """Attiva/disattiva filtro solo selezionate"""
        if self.main_window:
            self.main_window.toggle_filter()

    def prev_page(self):
        """Pagina precedente"""
        if self.main_window:
            self.main_window.prev_page()

    def next_page(self):
        """Pagina successiva"""
        if self.main_window:
            self.main_window.next_page()

    def on_photo_click(self, idx):
        """Gestisce click su foto per selezione"""
        widget = self.photo_widgets[idx]

        if widget['photo_path'] is None:
            return

        photo_path = widget['photo_path']

        # Notifica la finestra principale per aggiornare selezione
        if self.main_window:
            # Trova l'indice nella griglia principale
            try:
                # Calcola l'indice nella pagina corrente della main window
                display_photos = self.main_window.get_display_photos()
                start_idx = self.main_window.current_page * PHOTOS_PER_PAGE
                page_photos = display_photos[start_idx:start_idx + PHOTOS_PER_PAGE]

                if idx < len(page_photos) and page_photos[idx] == photo_path:
                    # Chiama il toggle sulla main window
                    self.main_window.toggle_photo_selection(idx)
            except Exception as e:
                print(f"Errore click: {e}")

    def clear_cache(self):
        """Pulisce cache immagini"""
        self.photo_cache.clear()

    def update_display(self, all_photos, current_page, selected_photos, show_only_selected):
        """Aggiorna visualizzazione foto"""
        # Determina foto da visualizzare
        if show_only_selected:
            display_photos = [p for p in all_photos if p in selected_photos]
        else:
            display_photos = all_photos

        # Calcola pagina
        total_pages = (len(display_photos) + PHOTOS_PER_PAGE - 1) // PHOTOS_PER_PAGE if display_photos else 0

        # Foto della pagina corrente
        start_idx = current_page * PHOTOS_PER_PAGE
        end_idx = min(start_idx + PHOTOS_PER_PAGE, len(display_photos))
        page_photos = display_photos[start_idx:end_idx] if display_photos else []

        # Aggiorna griglia
        for i, widget in enumerate(self.photo_widgets):
            if i < len(page_photos):
                photo_path = page_photos[i]
                widget['photo_path'] = photo_path

                # Numero foto
                try:
                    global_num = all_photos.index(photo_path) + 1
                except ValueError:
                    global_num = start_idx + i + 1
                widget['num_label'].setText(f"#{global_num}")

                # Carica immagine
                if photo_path in self.photo_cache:
                    pixmap = self.photo_cache[photo_path]
                else:
                    try:
                        # Carica direttamente da file con Qt
                        pixmap = QPixmap(photo_path)
                        if pixmap.isNull():
                            raise Exception("Impossibile caricare immagine")

                        # Scala a dimensione grande per riempire
                        pixmap = pixmap.scaled(600, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.photo_cache[photo_path] = pixmap
                    except Exception as e:
                        print(f"Errore caricamento: {e}")
                        pixmap = QPixmap()

                widget['label'].setPixmap(pixmap)

                # Evidenzia SOLO se selezionata (minimal)
                if photo_path in selected_photos:
                    widget['frame'].setStyleSheet(f"""
                        QFrame {{
                            background-color: {C['dark_bg']};
                            border: 4px solid {C['success']};
                        }}
                    """)
                else:
                    widget['frame'].setStyleSheet(f"""
                        QFrame {{
                            background-color: {C['dark_bg']};
                            border: none;
                        }}
                    """)
            else:
                # Cella vuota
                widget['photo_path'] = None
                widget['num_label'].setText("")
                widget['label'].clear()
                widget['frame'].setStyleSheet(f"""
                    QFrame {{
                        background-color: {C['dark_bg']};
                        border: none;
                    }}
                """)

    def toggle_fullscreen(self):
        """Toggle fullscreen"""
        if self.is_fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.is_fullscreen = not self.is_fullscreen

    def exit_fullscreen(self):
        """Esci da fullscreen"""
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
