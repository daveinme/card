"""
SD Card Photo Importer - Professional Edition
Interfaccia ultra professionale con doppio monitor
Finestra principale: controlli, importazione, selezione
Finestra secondaria: visualizzazione foto
"""

import os
import shutil
import time
from datetime import datetime
from pathlib import Path
import win32file
import win32con
from plyer import notification
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import win32print
import win32ui
from PIL import ImageWin
from win32.lib import win32con as pywintypes_con
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Importa componenti professionali
from professional_features import (
    ToolTip, ModernButton, StatusBar, SplashScreen,
    AboutDialog, Toolbar, ToastNotification
)

# ===== CONFIGURAZIONE =====
DESTINATION_BASE = r"C:\Users\Dave\Desktop\sdcard\foto"
SD_DRIVE_LETTER = "G"
PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.raw', '.cr2', '.nef', '.arw',
                    '.mp4', '.mov', '.avi', '.heic', '.dng'}

# File log stampe (nella stessa cartella del programma)
PRINT_LOG_FILE = "print_log.json"

# Configurazione griglia foto
THUMBNAIL_WIDTH = 300   # Larghezza foto (aspect ratio 3:2 - ORIZZONTALE)
THUMBNAIL_HEIGHT = 200  # Altezza foto
GRID_ROWS = 3           # Righe per pagina
GRID_COLUMNS = 3        # Colonne per pagina
PHOTOS_PER_PAGE = GRID_ROWS * GRID_COLUMNS  # 9 foto per pagina

# ===== DESIGN SYSTEM PROFESSIONALE =====
DESIGN = {
    # Palette colori moderna e professionale
    'colors': {
        # Toni scuri eleganti
        'dark_bg': '#1a1d23',           # Sfondo principale scuro
        'dark_surface': '#242830',      # Superfici rialzate
        'dark_panel': '#2d333d',        # Pannelli laterali
        
        # Accenti brand
        'primary': '#4a90e2',           # Blu primario
        'primary_hover': '#5ba3ff',     # Blu hover
        'primary_active': '#3a7bc8',    # Blu pressed
        
        'success': '#52c41a',           # Verde successo
        'success_light': '#73d13d',
        'warning': '#faad14',           # Arancione warning
        'danger': '#ff4d4f',            # Rosso errore
        
        # Toni chiari
        'light_bg': '#f5f7fa',          # Sfondo chiaro
        'light_surface': '#ffffff',     # Superficie bianca
        'light_border': '#e8eaed',      # Bordi sottili
        
        # Testo
        'text_primary': '#e8e9ed',      # Testo principale (su scuro)
        'text_secondary': '#9fa3b0',    # Testo secondario
        'text_disabled': '#5a5e6a',     # Testo disabilitato
        'text_dark': '#2c3e50',         # Testo su chiaro
        
        # Stati foto
        'photo_selected': '#4a90e2',    # Foto selezionata
        'photo_hover': '#363c47',       # Hover foto
        'photo_bg': '#1e2229',          # Sfondo foto
        
        # Client display
        'client_bg': '#0a0a0a',         # Nero puro client
        'client_selected': '#00ff88',   # Verde brillante selezione
    },
    
    # Tipografia professionale
    'fonts': {
        'family_primary': 'Segoe UI',   # Font principale Windows
        'family_mono': 'Consolas',      # Font monospace
        
        'size_huge': 28,
        'size_xlarge': 20,
        'size_large': 16,
        'size_normal': 13,
        'size_small': 11,
        'size_tiny': 9,
        
        'weight_bold': 'bold',
        'weight_semibold': 'normal',    # Tkinter non supporta semibold
        'weight_normal': 'normal',
    },
    
    # Spaziatura e dimensioni
    'spacing': {
        'xs': 4,
        'sm': 8,
        'md': 12,
        'lg': 16,
        'xl': 24,
        'xxl': 32,
    },
    
    # Bordi e ombre
    'borders': {
        'radius_sm': 4,
        'radius_md': 8,
        'radius_lg': 12,
        'width_thin': 1,
        'width_medium': 2,
        'width_thick': 3,
    },
    
    # Animazioni (per riferimento - Tkinter limitato)
    'animation': {
        'duration_fast': 150,
        'duration_normal': 250,
        'duration_slow': 400,
    }
}

# Shortcut per accesso rapido
C = DESIGN['colors']
F = DESIGN['fonts']
S = DESIGN['spacing']
B = DESIGN['borders']

# ===== FINE CONFIGURAZIONE =====


class SecondaryDisplayWindow:
    """Finestra ULTRA-MINIMALE per secondo monitor - SOLO FOTO"""
    
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Visualizzatore Foto")
        
        # Dimensioni grandi ma movibile
        self.window.geometry("1600x900")
        self.is_fullscreen = False
        self.window.configure(bg='#000000')  # Nero puro
        
        # Shortcut (solo F11, ESC nascosti)
        self.window.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.window.bind('<Escape>', lambda e: self.exit_fullscreen())
        
        # Container principale - PADDING MINIMO
        main_container = tk.Frame(self.window, bg='#000000')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame per griglia 3x3 (occupa TUTTO lo spazio)
        self.grid_frame = tk.Frame(main_container, bg='#000000')
        self.grid_frame.pack(expand=True, fill=tk.BOTH)
        
        # Configura griglia per espansione proporzionale
        for i in range(GRID_ROWS):
            self.grid_frame.grid_rowconfigure(i, weight=1, uniform="row")
        for i in range(GRID_COLUMNS):
            self.grid_frame.grid_columnconfigure(i, weight=1, uniform="col")
        
        # Crea celle - ULTRA MINIMALI
        self.photo_widgets = []
        for row in range(GRID_ROWS):
            for col in range(GRID_COLUMNS):
                # Container minimale
                cell_container = tk.Frame(self.grid_frame, bg='#000000')
                cell_container.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
                
                # Frame interno per centrare contenuto
                inner_frame = tk.Frame(cell_container, bg='#000000')
                inner_frame.pack(expand=True, fill=tk.BOTH)
                
                # Numero foto (GRANDE, in alto, centrato)
                num_label = tk.Label(inner_frame, text="", 
                                    font=('Arial', 28, 'bold'), 
                                    fg='#ffffff', bg='#000000')
                num_label.pack(pady=(5, 2))
                
                # Label foto (riempie TUTTO lo spazio disponibile)
                photo_label = tk.Label(inner_frame, bg='#000000', bd=0)
                photo_label.pack(expand=True, fill=tk.BOTH)
                
                self.photo_widgets.append({
                    'container': cell_container,
                    'num_label': num_label,
                    'photo_label': photo_label
                })
        
        # Cache per performance
        self.photo_cache = {}
        self.current_photos = []
        self.current_page = 0
        self.total_pages = 0
    
    def toggle_fullscreen(self):
        """Attiva/disattiva fullscreen"""
        self.is_fullscreen = not self.is_fullscreen
        self.window.attributes('-fullscreen', self.is_fullscreen)
    
    def exit_fullscreen(self):
        """Esci da fullscreen"""
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.window.attributes('-fullscreen', False)
    
    def update_display(self, all_photos, current_page, selected_photos, show_only_selected=False):
        """Aggiorna visualizzazione con foto MASSIMIZZATE (ORIZZONTALI 3:2)"""
        # Filtra foto se richiesto
        if show_only_selected:
            display_photos = [p for p in all_photos if p in selected_photos]
        else:
            display_photos = all_photos
        
        self.current_photos = display_photos
        self.current_page = current_page
        self.total_pages = (len(display_photos) + PHOTOS_PER_PAGE - 1) // PHOTOS_PER_PAGE
        
        # Calcola foto da mostrare
        start_idx = current_page * PHOTOS_PER_PAGE
        end_idx = min(start_idx + PHOTOS_PER_PAGE, len(display_photos))
        page_photos = display_photos[start_idx:end_idx]
        
        # Dimensione target per foto (MASSIMIZZA spazio disponibile)
        # Calcola in base alle dimensioni attuali della finestra
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        
        # Usa dimensioni minime se finestra non ancora renderizzata
        if window_width < 100:
            window_width = 1600
            window_height = 900
        
        # Calcola spazio disponibile per cella (tolgo padding minimo)
        cell_width = (window_width - 40) // GRID_COLUMNS
        cell_height = (window_height - 40) // GRID_ROWS
        
        # Lascia spazio solo per numero (40px) e padding minimo
        available_width = cell_width - 10
        available_height = cell_height - 50
        
        # Calcola dimensioni foto con aspect ratio 3:2 (ORIZZONTALE) - MASSIMIZZA
        if available_width / available_height > 3/2:
            # Limitato dall'altezza
            photo_height = available_height
            photo_width = int(photo_height * 3 / 2)
        else:
            # Limitato dalla larghezza
            photo_width = available_width
            photo_height = int(photo_width * 2 / 3)
        
        # Mostra foto
        for i, widget in enumerate(self.photo_widgets):
            if i < len(page_photos):
                photo_path = page_photos[i]
                
                # Numero globale (dall'array originale completo)
                global_num = all_photos.index(photo_path) + 1
                widget['num_label'].config(text=f"#{global_num}")
                
                # Cache key
                cache_key = f"{photo_path}_{photo_width}x{photo_height}_{'sel' if photo_path in selected_photos else 'norm'}"
                
                if cache_key in self.photo_cache:
                    photo = self.photo_cache[cache_key]
                    widget['photo_label'].config(image=photo)
                    widget['photo_label'].image = photo
                else:
                    try:
                        img = Image.open(photo_path)
                        
                        # NUOVO: Letterbox invece di crop per foto verticali
                        img_ratio = img.width / img.height
                        target_ratio = 3 / 2
                        
                        # Calcola dimensioni mantenendo proporzioni
                        if img_ratio > target_ratio:
                            # Foto più larga - limita per larghezza
                            new_width = photo_width
                            new_height = int(photo_width / img_ratio)
                        else:
                            # Foto più alta - limita per altezza
                            new_height = photo_height
                            new_width = int(photo_height * img_ratio)
                        
                        # Ridimensiona
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Canvas nero (3:2)
                        canvas = Image.new('RGB', (photo_width, photo_height), (0, 0, 0))
                        
                        # Centra foto sul canvas
                        x_offset = (photo_width - new_width) // 2
                        y_offset = (photo_height - new_height) // 2
                        canvas.paste(img, (x_offset, y_offset))
                        
                        # Bordo GROSSO se selezionata
                        if photo_path in selected_photos:
                            from PIL import ImageDraw
                            draw = ImageDraw.Draw(canvas)
                            border_width = 12
                            for offset in range(border_width):
                                draw.rectangle(
                                    [(offset, offset), (photo_width-1-offset, photo_height-1-offset)],
                                    outline='#00ff00',
                                    width=2
                                )
                        
                        photo = ImageTk.PhotoImage(canvas)
                        self.photo_cache[cache_key] = photo
                        
                        widget['photo_label'].config(image=photo)
                        widget['photo_label'].image = photo
                        
                        # Evidenzia numero se selezionata
                        if photo_path in selected_photos:
                            widget['num_label'].config(fg='#00ff00')
                        else:
                            widget['num_label'].config(fg='#ffffff')
                        
                    except Exception as e:
                        print(f"Errore caricamento {photo_path}: {e}")
                        widget['photo_label'].config(image='', text='')
            else:
                # Cella vuota
                widget['num_label'].config(text='')
                widget['photo_label'].config(image='', text='')
    
    def clear_cache(self):
        """Pulisci cache"""
        self.photo_cache.clear()


class MainControlWindow:
    """Finestra principale con tutti i controlli - DESIGN PROFESSIONALE"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SD Card Photo Importer - Professional Edition")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#f0f0f0')

        # Stile professionale
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabelframe', background='#f0f0f0', borderwidth=2)
        style.configure('TLabelframe.Label', font=('Arial', 10, 'bold'), foreground='#333333')
        style.configure('TButton', font=('Arial', 9), padding=5)
        style.configure('TLabel', background='#f0f0f0')
        style.configure('Header.TButton', font=('Arial', 11, 'bold'), padding=10)

        # Variabili
        self.current_folder = None
        self.all_photos = []
        self.selected_photos = set()
        self.current_page = 0
        self.show_only_selected = False

        # Cache per performance
        self.thumbnail_cache = {}

        # Finestra secondaria
        self.secondary_window = SecondaryDisplayWindow()

        # KEYBOARD SHORTCUTS
        self.setup_shortcuts()

        # Crea interfaccia
        self.create_ui()

        # Aggiorna display
        self.update_displays()
    
    def create_ui(self):
        """Crea interfaccia ultra professionale"""

        # ==== MENU BAR ====
        self.create_menu_bar()

        # ==== TOOLBAR ====
        self.toolbar = Toolbar(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Aggiungi pulsanti toolbar
        self.toolbar.add_button("📂", self.browse_folder, "Apri Cartella (Ctrl+O)")
        self.toolbar.add_button("🏠", self.go_to_base, "Cartella Base (Ctrl+H)")
        self.toolbar.add_separator()
        self.toolbar.add_button("📥", self.import_photos, "Importa da SD (Ctrl+I)")
        self.toolbar.add_separator()
        self.toolbar.add_button("◄", self.prev_page, "Pagina Precedente (←)")
        self.toolbar.add_button("►", self.next_page, "Pagina Successiva (→)")
        self.toolbar.add_separator()
        self.toolbar.add_button("🖨", self.print_photos, "Stampa Selezionate (Ctrl+P)")
        self.toolbar.add_separator()
        self.toolbar.add_button("📊", self.show_print_report, "Report Stampe (Ctrl+R)")
        self.toolbar.add_button("❓", lambda: AboutDialog(self.root), "Informazioni (F1)")

        # ==== HEADER ====
        header = tk.Frame(self.root, bg='#2c3e50', height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        tk.Label(header, text="📸 SD CARD PHOTO IMPORTER",
                font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50').pack(side=tk.LEFT, padx=20, pady=15)

        tk.Label(header, text="Professional Edition",
                font=('Arial', 10), fg='#95a5a6', bg='#2c3e50').pack(side=tk.LEFT)
        
        # ==== LAYOUT PRINCIPALE ====
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Colonna SINISTRA (controlli)
        left_panel = tk.Frame(main_container, bg='#f0f0f0', width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Colonna DESTRA (griglia foto)
        right_panel = tk.Frame(main_container, bg='#ffffff', relief=tk.SOLID, bd=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # ==== PANNELLO SINISTRO - CONTROLLI ====
        
        # 1. IMPORTAZIONE
        import_frame = ttk.LabelFrame(left_panel, text="📥 IMPORTAZIONE DA SD", padding=10)
        import_frame.pack(fill=tk.X, pady=(0, 8))
        
        sd_row = tk.Frame(import_frame, bg='white')
        sd_row.pack(fill=tk.X, pady=5)
        
        tk.Label(sd_row, text="Unità SD:", font=('Arial', 9), bg='white').pack(side=tk.LEFT, padx=5)
        self.sd_label = tk.Label(sd_row, text="Non rilevata", font=('Arial', 9, 'bold'), 
                                fg='#e74c3c', bg='white')
        self.sd_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(sd_row, text="🔄", command=self.check_sd_card, width=4).pack(side=tk.RIGHT, padx=2)
        ttk.Button(sd_row, text="⚙️", command=self.open_settings, width=4).pack(side=tk.RIGHT, padx=2)
        
        self.import_btn = ttk.Button(import_frame, text="📥 IMPORTA FOTO DA SD CARD", 
                                     command=self.import_photos, state=tk.DISABLED,
                                     style='Header.TButton')
        self.import_btn.pack(fill=tk.X, pady=8)
        
        self.cut_var = tk.BooleanVar(value=True)
        cut_check = ttk.Checkbutton(import_frame, text="✂ Taglia da SD (sposta file)", 
                                    variable=self.cut_var)
        cut_check.pack(anchor=tk.W, pady=3)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(import_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = tk.Label(import_frame, text="", font=('Arial', 8), 
                                       fg='#7f8c8d', bg='white')
        self.progress_label.pack()
        
        # 2. CARTELLA
        folder_frame = ttk.LabelFrame(left_panel, text="📁 CARTELLA CORRENTE", padding=10)
        folder_frame.pack(fill=tk.X, pady=(0, 8))
        
        btn_row = tk.Frame(folder_frame, bg='white')
        btn_row.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_row, text="📂 Sfoglia", command=self.browse_folder).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_row, text="🏠 Base", command=self.go_to_base).pack(side=tk.LEFT, padx=3)
        
        self.folder_label = tk.Label(folder_frame, text="Nessuna cartella", 
                                     font=('Arial', 8), fg='#95a5a6', bg='white', 
                                     wraplength=300, justify=tk.LEFT)
        self.folder_label.pack(fill=tk.X, pady=5)
        
        self.folder_info_label = tk.Label(folder_frame, text="", font=('Arial', 9, 'bold'),
                                         fg='#2c3e50', bg='white')
        self.folder_info_label.pack()

        # 3. SELEZIONE
        select_frame = ttk.LabelFrame(left_panel, text="✓ SELEZIONE FOTO", padding=10)
        select_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.selection_label = tk.Label(select_frame, text="0 foto selezionate", 
                                        font=('Arial', 10, 'bold'), fg='#27ae60', bg='white')
        self.selection_label.pack(pady=5)
        
        sel_row1 = tk.Frame(select_frame, bg='white')
        sel_row1.pack(fill=tk.X, pady=3)
        
        ttk.Button(sel_row1, text="✓ Pagina", command=self.select_current_page).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(sel_row1, text="✓✓ Tutte", command=self.select_all).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        ttk.Button(select_frame, text="✗ Deseleziona Tutte", command=self.deselect_all).pack(fill=tk.X, pady=3)

        # 4. STAMPA
        print_frame = ttk.LabelFrame(left_panel, text="🖨️ STAMPA", padding=10)
        print_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Formato stampa
        layout_label = tk.Label(print_frame, text="Formato Foto (A4):", font=('Arial', 9, 'bold'), bg='white')
        layout_label.pack(anchor=tk.W, pady=(0, 3))

        layout_options = tk.Frame(print_frame, bg='white')
        layout_options.pack(fill=tk.X, pady=5)

        self.print_layout = tk.StringVar(value="15x20")
        layouts = [
            ("15×20 cm", "15x20"),
            ("10×15 cm", "10x15"),
            ("9×13 cm", "9x13")
        ]

        for i, (text, value) in enumerate(layouts):
            rb = ttk.Radiobutton(layout_options, text=text, value=value,
                          variable=self.print_layout)
            rb.grid(row=i, column=0, sticky='w', padx=5, pady=2)

            # Aggiungi descrizione
            if value == "15x20":
                desc = "1 foto per foglio"
            elif value == "10x15":
                desc = "2 foto per foglio"
            else:
                desc = "4 foto per foglio"

            tk.Label(layout_options, text=f"({desc})", font=('Arial', 8),
                    fg='#7f8c8d', bg='white').grid(row=i, column=1, sticky='w', padx=2)
        
        printer_row = tk.Frame(print_frame, bg='white')
        printer_row.pack(fill=tk.X, pady=5)
        
        tk.Label(printer_row, text="Stampante:", font=('Arial', 9), bg='white').pack(side=tk.TOP, anchor=tk.W)
        
        printer_select = tk.Frame(print_frame, bg='white')
        printer_select.pack(fill=tk.X, pady=5)
        
        self.printer_var = tk.StringVar()
        self.printer_combo = ttk.Combobox(printer_select, textvariable=self.printer_var,
                                         state='normal', font=('Arial', 9), width=30)
        self.printer_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.printer_combo.config(background='white')
        
        ttk.Button(printer_select, text="🔄", command=self.load_printers, width=4).pack(side=tk.RIGHT)
        
        self.print_btn = ttk.Button(print_frame, text="🖨️ STAMPA SELEZIONATE", 
                                   command=self.print_photos, state=tk.DISABLED,
                                   style='Header.TButton')
        self.print_btn.pack(fill=tk.X, pady=8)
        
        # Report stampe
        ttk.Button(print_frame, text="📊 Report Stampe", 
                  command=self.show_print_report).pack(fill=tk.X, pady=3)
        
        # ==== PANNELLO DESTRO - GRIGLIA FOTO ====
        
        grid_header = tk.Frame(right_panel, bg='#34495e', height=50)
        grid_header.pack(fill=tk.X)
        grid_header.pack_propagate(False)
        
        self.grid_header_label = tk.Label(grid_header, text="🖼️ MINIATURE - Click per selezionare", 
                font=('Arial', 12, 'bold'), fg='white', bg='#34495e')
        self.grid_header_label.pack(side=tk.LEFT, padx=15, pady=12)
        
        # Container griglia
        grid_container = tk.Frame(right_panel, bg='#ffffff')
        grid_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ==== BARRA CONTROLLI GRIGLIA ====
        controls_bar = tk.Frame(grid_container, bg='#ecf0f1', height=60)
        controls_bar.pack(fill=tk.X, pady=(0, 15))
        controls_bar.pack_propagate(False)

        # Frame sinistra - Navigazione
        nav_left = tk.Frame(controls_bar, bg='#ecf0f1')
        nav_left.pack(side=tk.LEFT, padx=15, pady=10)

        self.prev_btn = ttk.Button(nav_left, text="◄ Indietro", command=self.prev_page,
                                   state=tk.DISABLED, width=12)
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.page_label = tk.Label(nav_left, text="0 / 0", font=('Arial', 16, 'bold'),
                                   fg='#2c3e50', bg='#ecf0f1', width=10)
        self.page_label.pack(side=tk.LEFT, padx=10)

        self.next_btn = ttk.Button(nav_left, text="Avanti ►", command=self.next_page,
                                   state=tk.DISABLED, width=12)
        self.next_btn.pack(side=tk.LEFT, padx=5)

        # Frame destra - Filtro
        nav_right = tk.Frame(controls_bar, bg='#ecf0f1')
        nav_right.pack(side=tk.RIGHT, padx=15, pady=10)

        self.filter_btn = ttk.Button(nav_right, text="👁️ Mostra SOLO Selezionate",
                                     command=self.toggle_filter, state=tk.DISABLED,
                                     width=25)
        self.filter_btn.pack(side=tk.RIGHT)

        # Griglia 3x3 con foto MOLTO PIÙ GRANDI (225x150 per 3:2 orizzontale)
        self.grid_frame = tk.Frame(grid_container, bg='#ffffff')
        self.grid_frame.pack(expand=True)
        
        self.thumbnail_widgets = []
        for row in range(GRID_ROWS):
            for col in range(GRID_COLUMNS):
                # Container cella
                cell = tk.Frame(self.grid_frame, bg='#ffffff')
                cell.grid(row=row, column=col, padx=12, pady=12)
                
                # Numero foto
                num_label = tk.Label(cell, text="", font=('Arial', 16, 'bold'), 
                                    fg='#3498db', bg='#ffffff')
                num_label.pack()
                
                # Frame foto
                photo_frame = tk.Frame(cell, relief=tk.RAISED, borderwidth=2, 
                                      bg='#ecf0f1', cursor='hand2')
                photo_frame.pack()
                
                # Label immagine (aspect ratio 3:2 ORIZZONTALE, DIMENSIONI FISSE)
                photo_label = tk.Label(photo_frame, bg='#ecf0f1')
                photo_label.pack(padx=5, pady=5)
                
                # Click handler
                idx = row * GRID_COLUMNS + col
                photo_label.bind('<Button-1>', lambda e, i=idx: self.toggle_photo_selection(i))
                photo_frame.bind('<Button-1>', lambda e, i=idx: self.toggle_photo_selection(i))
                num_label.bind('<Button-1>', lambda e, i=idx: self.toggle_photo_selection(i))
                
                self.thumbnail_widgets.append({
                    'cell': cell,
                    'num_label': num_label,
                    'photo_frame': photo_frame,
                    'photo_label': photo_label,
                    'photo_path': None
                })
        
        # ==== STATUS BAR (FONDO) ====
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.set_status("Pronto")

        # Carica stampanti
        self.load_printers()

        # Controlla SD
        self.check_sd_card()

        # Aggiungi tooltips ai pulsanti principali
        self.add_tooltips()

    def create_menu_bar(self):
        """Crea menu bar professionale"""
        menubar = tk.Menu(self.root, bg='#2c3e50', fg='white', font=('Segoe UI', 10))
        self.root.config(menu=menubar)

        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0, font=('Segoe UI', 10))
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Apri Cartella...", command=self.browse_folder, accelerator="Ctrl+O")
        file_menu.add_command(label="Vai a Cartella Base", command=self.go_to_base, accelerator="Ctrl+H")
        file_menu.add_separator()
        file_menu.add_command(label="Importa da SD Card", command=self.import_photos, accelerator="Ctrl+I")
        file_menu.add_separator()
        file_menu.add_command(label="Impostazioni...", command=self.open_settings, accelerator="Ctrl+,")
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.root.quit, accelerator="Alt+F4")

        # Menu Modifica
        edit_menu = tk.Menu(menubar, tearoff=0, font=('Segoe UI', 10))
        menubar.add_cascade(label="Modifica", menu=edit_menu)
        edit_menu.add_command(label="Seleziona Tutto", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Seleziona Pagina Corrente", command=self.select_current_page, accelerator="Ctrl+Shift+A")
        edit_menu.add_command(label="Deseleziona Tutto", command=self.deselect_all, accelerator="Ctrl+D")
        edit_menu.add_separator()
        edit_menu.add_command(label="Mostra Solo Selezionate", command=self.toggle_filter, accelerator="Ctrl+F")

        # Menu Visualizza
        view_menu = tk.Menu(menubar, tearoff=0, font=('Segoe UI', 10))
        menubar.add_cascade(label="Visualizza", menu=view_menu)
        view_menu.add_command(label="Pagina Successiva", command=self.next_page, accelerator="→")
        view_menu.add_command(label="Pagina Precedente", command=self.prev_page, accelerator="←")
        view_menu.add_separator()
        view_menu.add_command(label="Prima Pagina", command=lambda: self.goto_page(0), accelerator="Home")
        view_menu.add_command(label="Ultima Pagina", command=self.goto_last_page, accelerator="End")

        # Menu Strumenti
        tools_menu = tk.Menu(menubar, tearoff=0, font=('Segoe UI', 10))
        menubar.add_cascade(label="Strumenti", menu=tools_menu)
        tools_menu.add_command(label="Stampa Foto Selezionate...", command=self.print_photos, accelerator="Ctrl+P")
        tools_menu.add_command(label="Report Stampe", command=self.show_print_report, accelerator="Ctrl+R")
        tools_menu.add_separator()
        tools_menu.add_command(label="Verifica SD Card", command=self.check_sd_card, accelerator="F5")

        # Menu Aiuto
        help_menu = tk.Menu(menubar, tearoff=0, font=('Segoe UI', 10))
        menubar.add_cascade(label="Aiuto", menu=help_menu)
        help_menu.add_command(label="Scorciatoie da Tastiera", command=self.show_shortcuts_help, accelerator="F1")
        help_menu.add_separator()
        help_menu.add_command(label="Informazioni", command=lambda: AboutDialog(self.root))

    def setup_shortcuts(self):
        """Configura scorciatoie da tastiera"""
        # File
        self.root.bind('<Control-o>', lambda e: self.browse_folder())
        self.root.bind('<Control-h>', lambda e: self.go_to_base())
        self.root.bind('<Control-i>', lambda e: self.import_photos())
        self.root.bind('<Control-comma>', lambda e: self.open_settings())

        # Modifica
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-Shift-A>', lambda e: self.select_current_page())
        self.root.bind('<Control-d>', lambda e: self.deselect_all())
        self.root.bind('<Control-f>', lambda e: self.toggle_filter())

        # Visualizza
        self.root.bind('<Left>', lambda e: self.prev_page())
        self.root.bind('<Right>', lambda e: self.next_page())
        self.root.bind('<Home>', lambda e: self.goto_page(0))
        self.root.bind('<End>', lambda e: self.goto_last_page())

        # Strumenti
        self.root.bind('<Control-p>', lambda e: self.print_photos())
        self.root.bind('<Control-r>', lambda e: self.show_print_report())
        self.root.bind('<F5>', lambda e: self.check_sd_card())

        # Aiuto
        self.root.bind('<F1>', lambda e: self.show_shortcuts_help())

    def add_tooltips(self):
        """Aggiunge tooltips a tutti i controlli"""
        # Tooltips per importazione
        ToolTip(self.import_btn, "Importa tutte le foto dalla scheda SD\nalla cartella di destinazione (Ctrl+I)")
        ToolTip(self.sd_label, "Stato della scheda SD inserita")

        # Tooltips navigazione (ora nella griglia)
        ToolTip(self.prev_btn, "Vai alla pagina precedente (tasto ←)")
        ToolTip(self.next_btn, "Vai alla pagina successiva (tasto →)")
        ToolTip(self.page_label, "Numero di pagina corrente / totale")

        # Tooltip filtro (ora nella griglia)
        ToolTip(self.filter_btn, "Mostra solo le foto selezionate\no tutte le foto (Ctrl+F)")

        # Tooltips stampa
        ToolTip(self.print_btn, "Stampa le foto selezionate (Ctrl+P)")
        ToolTip(self.printer_combo, "Seleziona la stampante da utilizzare.\nClicca per aprire il menu a tendina.")

    def show_shortcuts_help(self):
        """Mostra finestra con scorciatoie da tastiera"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Scorciatoie da Tastiera")
        help_window.geometry("600x700")
        help_window.transient(self.root)
        help_window.grab_set()

        # Centra finestra
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (help_window.winfo_screenheight() // 2) - (700 // 2)
        help_window.geometry(f'+{x}+{y}')

        # Header
        header = tk.Frame(help_window, bg='#34495e', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="⌨ SCORCIATOIE DA TASTIERA",
                font=('Arial', 14, 'bold'), fg='white', bg='#34495e').pack(pady=15)

        # Contenuto
        content = tk.Frame(help_window, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        shortcuts = [
            ("FILE", [
                ("Ctrl+O", "Apri cartella"),
                ("Ctrl+H", "Vai a cartella base"),
                ("Ctrl+I", "Importa da SD card"),
                ("Ctrl+,", "Impostazioni"),
            ]),
            ("MODIFICA", [
                ("Ctrl+A", "Seleziona tutte le foto"),
                ("Ctrl+Shift+A", "Seleziona pagina corrente"),
                ("Ctrl+D", "Deseleziona tutto"),
                ("Ctrl+F", "Filtra solo foto selezionate"),
            ]),
            ("NAVIGAZIONE", [
                ("→ (Freccia destra)", "Pagina successiva"),
                ("← (Freccia sinistra)", "Pagina precedente"),
                ("Home", "Prima pagina"),
                ("End", "Ultima pagina"),
            ]),
            ("STRUMENTI", [
                ("Ctrl+P", "Stampa foto selezionate"),
                ("Ctrl+R", "Report stampe"),
                ("F5", "Verifica SD card"),
            ]),
            ("ALTRO", [
                ("F1", "Mostra aiuto"),
                ("Alt+F4", "Chiudi programma"),
            ]),
        ]

        for section, items in shortcuts:
            # Titolo sezione
            section_frame = tk.Frame(content, bg='#ecf0f1')
            section_frame.pack(fill=tk.X, pady=(10, 5))
            tk.Label(section_frame, text=section, font=('Arial', 11, 'bold'),
                    bg='#ecf0f1', fg='#2c3e50', anchor=tk.W, padx=10, pady=5).pack(fill=tk.X)

            # Scorciatoie
            for key, desc in items:
                item_frame = tk.Frame(content, bg='white')
                item_frame.pack(fill=tk.X, pady=2)

                tk.Label(item_frame, text=key, font=('Consolas', 10, 'bold'),
                        bg='#3498db', fg='white', padx=10, pady=5, width=20, anchor=tk.W).pack(side=tk.LEFT, padx=(10, 5))
                tk.Label(item_frame, text=desc, font=('Arial', 10),
                        bg='white', fg='#2c3e50', anchor=tk.W).pack(side=tk.LEFT, padx=5)

        # Footer
        footer = tk.Frame(help_window, bg='#ecf0f1')
        footer.pack(fill=tk.X, pady=10)
        ModernButton(footer, text="Chiudi", command=help_window.destroy, style='primary').pack(pady=10)

    def goto_page(self, page_num):
        """Vai a una pagina specifica"""
        display_photos = self.get_display_photos()
        total_pages = (len(display_photos) + PHOTOS_PER_PAGE - 1) // PHOTOS_PER_PAGE if display_photos else 0
        if 0 <= page_num < total_pages:
            self.current_page = page_num
            self.update_displays()

    def goto_last_page(self):
        """Vai all'ultima pagina"""
        display_photos = self.get_display_photos()
        total_pages = (len(display_photos) + PHOTOS_PER_PAGE - 1) // PHOTOS_PER_PAGE if display_photos else 0
        if total_pages > 0:
            self.current_page = total_pages - 1
            self.update_displays()

    def open_settings(self):
        """Apri finestra impostazioni"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Impostazioni")
        settings_window.geometry("500x250")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Header
        header = tk.Frame(settings_window, bg='#34495e', height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="⚙️ IMPOSTAZIONI", font=('Arial', 14, 'bold'), 
                fg='white', bg='#34495e').pack(pady=12)
        
        # Content
        content = tk.Frame(settings_window, bg='white', padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        # 1. Lettera unità SD
        tk.Label(content, text="Lettera Unità SD:", font=('Arial', 10, 'bold'), 
                bg='white').grid(row=0, column=0, sticky='w', pady=10)
        
        sd_frame = tk.Frame(content, bg='white')
        sd_frame.grid(row=0, column=1, sticky='ew', pady=10)
        
        self.sd_drive_var = tk.StringVar(value=SD_DRIVE_LETTER if SD_DRIVE_LETTER else "")
        sd_entry = ttk.Entry(sd_frame, textvariable=self.sd_drive_var, width=5, font=('Arial', 10))
        sd_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(sd_frame, text="(es: G, H, E)", font=('Arial', 8), 
                fg='#7f8c8d', bg='white').pack(side=tk.LEFT)
        
        # 2. Percorso destinazione
        tk.Label(content, text="Cartella Destinazione:", font=('Arial', 10, 'bold'), 
                bg='white').grid(row=1, column=0, sticky='w', pady=10)
        
        dest_frame = tk.Frame(content, bg='white')
        dest_frame.grid(row=1, column=1, sticky='ew', pady=10)
        
        self.dest_path_var = tk.StringVar(value=DESTINATION_BASE)
        dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_path_var, width=35, font=('Arial', 9))
        dest_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(dest_frame, text="📂", command=self.browse_destination, 
                  width=4).pack(side=tk.LEFT)
        
        # Info
        info_label = tk.Label(content, text="ℹ️ Le modifiche saranno applicate immediatamente", 
                             font=('Arial', 8), fg='#3498db', bg='white')
        info_label.grid(row=2, column=0, columnspan=2, pady=15)
        
        content.columnconfigure(1, weight=1)
        
        # Pulsanti
        btn_frame = tk.Frame(settings_window, bg='#ecf0f1')
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="✅ Salva", command=lambda: self.save_settings(settings_window),
                  style='Header.TButton').pack(side=tk.RIGHT, padx=10)
        ttk.Button(btn_frame, text="✖ Annulla", command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def browse_destination(self):
        """Sfoglia per cartella destinazione"""
        folder = filedialog.askdirectory(initialdir=self.dest_path_var.get(),
                                        title="Seleziona Cartella Destinazione")
        if folder:
            self.dest_path_var.set(folder)
    
    def save_settings(self, settings_window):
        """Salva impostazioni"""
        global SD_DRIVE_LETTER, DESTINATION_BASE
        
        # Lettera SD (togli spazi e converti a maiuscolo)
        new_sd = self.sd_drive_var.get().strip().upper()
        if new_sd and len(new_sd) == 1 and new_sd.isalpha():
            SD_DRIVE_LETTER = new_sd
            print(f"[SETTINGS] Unità SD: {SD_DRIVE_LETTER}")
        elif not new_sd:
            SD_DRIVE_LETTER = None
            print(f"[SETTINGS] Auto-detect unità SD")
        else:
            messagebox.showwarning("Errore", "Lettera unità non valida (usa A-Z)")
            return
        
        # Percorso destinazione
        new_dest = self.dest_path_var.get().strip()
        if new_dest and os.path.exists(os.path.dirname(new_dest)):
            DESTINATION_BASE = new_dest
            os.makedirs(DESTINATION_BASE, exist_ok=True)
            print(f"[SETTINGS] Destinazione: {DESTINATION_BASE}")
        else:
            messagebox.showwarning("Errore", "Percorso non valido")
            return
        
        # Aggiorna UI
        self.check_sd_card()
        messagebox.showinfo("✅ Salvato", "Impostazioni salvate correttamente!")
        settings_window.destroy()
    
    def check_sd_card(self):
        """Controlla presenza SD card"""
        if SD_DRIVE_LETTER:
            drive = f"{SD_DRIVE_LETTER.upper()}:\\"
            if os.path.exists(drive):
                # Conta foto
                photo_count = 0
                try:
                    for root, dirs, files in os.walk(drive):
                        for file in files:
                            if Path(file).suffix.lower() in {'.jpg', '.jpeg', '.png', '.heic'}:
                                photo_count += 1
                except:
                    pass
                
                self.sd_label.config(text=f"{drive} ({photo_count} foto)", fg='#27ae60')
                self.import_btn.config(state=tk.NORMAL)
            else:
                self.sd_label.config(text="Non rilevata", fg='#e74c3c')
                self.import_btn.config(state=tk.DISABLED)
    
    def import_photos(self):
        """Importa foto da SD card"""
        if not SD_DRIVE_LETTER:
            messagebox.showwarning("Errore", "Nessuna unità SD configurata")
            return
        
        drive = f"{SD_DRIVE_LETTER.upper()}:\\"
        if not os.path.exists(drive):
            messagebox.showwarning("Errore", "SD card non trovata")
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
            messagebox.showinfo("Info", "Nessuna foto trovata sulla SD card")
            return
        
        # Conferma
        action = "tagliare" if self.cut_var.get() else "copiare"
        if not messagebox.askyesno("Conferma", 
                                   f"Trovate {len(photo_files)} foto.\n"
                                   f"Verranno {action}e in:\n{dest_folder}\n\n"
                                   f"Continuare?"):
            return
        
        # Importa con MULTI-THREADING
        def import_thread():
            self.progress_var.set(0)
            self.import_btn.config(state=tk.DISABLED)
            
            completed = 0
            errors = 0
            
            # Funzione per copiare/spostare singola foto
            def process_photo(source_path):
                filename = os.path.basename(source_path)
                dest_path = os.path.join(dest_folder, filename)
                
                # Gestisci duplicati
                if os.path.exists(dest_path):
                    name, ext = os.path.splitext(filename)
                    num = 1
                    while os.path.exists(dest_path):
                        dest_path = os.path.join(dest_folder, f"{name}_{num}{ext}")
                        num += 1
                
                try:
                    if self.cut_var.get():
                        shutil.move(source_path, dest_path)
                    else:
                        shutil.copy2(source_path, dest_path)
                    return True, filename
                except Exception as e:
                    print(f"Errore: {e}")
                    return False, filename
            
            # Usa ThreadPoolExecutor per parallelizzare (max 4 thread)
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Invia tutti i task
                future_to_photo = {executor.submit(process_photo, photo): photo 
                                  for photo in photo_files}
                
                # Processa i risultati man mano che completano
                for future in as_completed(future_to_photo):
                    success, filename = future.result()
                    
                    if success:
                        completed += 1
                    else:
                        errors += 1
                    
                    # Aggiorna progress bar
                    progress = (completed + errors) / len(photo_files) * 100
                    self.progress_var.set(progress)
                    self.root.after(0, lambda f=filename, p=progress: 
                                   self.progress_label.config(text=f"{p:.0f}% - {f}"))
            
            # Completato
            result_text = f"Importate {completed} foto!" + (f" ({errors} errori)" if errors else "")
            self.root.after(0, lambda: self.progress_label.config(text=result_text))
            self.root.after(0, lambda: self.import_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.load_folder(dest_folder))
            self.root.after(0, self.check_sd_card)
            
            notification.notify(
                title="Importazione Completata",
                message=f"{completed} foto importate in {os.path.basename(dest_folder)}",
                app_name="SD Card Importer",
                timeout=5
            )
        
        threading.Thread(target=import_thread, daemon=True).start()
    
    def browse_folder(self):
        """Apri browser cartelle"""
        folder = filedialog.askdirectory(initialdir=DESTINATION_BASE,
                                         title="Seleziona cartella con foto")
        if folder:
            self.load_folder(folder)
    
    def go_to_base(self):
        """Vai alla cartella base"""
        if os.path.exists(DESTINATION_BASE):
            self.load_folder(DESTINATION_BASE)
    
    def load_folder(self, folder_path):
        """Carica foto da una cartella"""
        self.current_folder = folder_path
        self.status_bar.set_status("Caricamento cartella in corso...", '#3498db')
        self.status_bar.show_progress(True)

        # Mostra solo nome cartella se troppo lungo
        folder_display = folder_path
        if len(folder_path) > 50:
            folder_display = "..." + folder_path[-47:]
        self.folder_label.config(text=folder_display)

        # Trova foto
        self.all_photos = []
        try:
            for file in os.listdir(folder_path):
                filepath = os.path.join(folder_path, file)
                if os.path.isfile(filepath) and Path(file).suffix.lower() in {'.jpg', '.jpeg', '.png', '.heic'}:
                    self.all_photos.append(filepath)
        except Exception as e:
            self.status_bar.show_progress(False)
            self.status_bar.set_status("Errore caricamento cartella", '#e74c3c')
            messagebox.showerror("Errore", f"Impossibile leggere la cartella:\n{e}")
            return

        self.all_photos.sort()
        self.current_page = 0
        self.selected_photos.clear()

        # Pulisci cache quando cambi cartella
        self.thumbnail_cache.clear()
        self.secondary_window.clear_cache()

        self.folder_info_label.config(text=f"📷 {len(self.all_photos)} foto")

        self.update_displays()

        self.status_bar.show_progress(False)
        self.status_bar.set_status(f"Caricate {len(self.all_photos)} foto da {os.path.basename(folder_path)}", '#27ae60')
        self.status_bar.set_info(f"{len(self.all_photos)} foto totali")
    
    def toggle_filter(self):
        """Attiva/disattiva filtro solo foto selezionate (SWITCH)"""
        if not self.selected_photos:
            # Se non ci sono foto selezionate, non permettere attivazione filtro
            return
        
        self.show_only_selected = not self.show_only_selected
        self.current_page = 0  # Torna alla prima pagina
        
        if self.show_only_selected:
            self.filter_btn.config(text="📋 Mostra TUTTE le Foto")
            self.grid_header_label.config(text="✓ SOLO FOTO SELEZIONATE - Click per deselezionare")
            print(f"[FILTRO ON] Visualizzando {len(self.selected_photos)} foto selezionate")
        else:
            self.filter_btn.config(text="👁️ Mostra SOLO Selezionate")
            self.grid_header_label.config(text="🖼️ MINIATURE - Click per selezionare")
            print(f"[FILTRO OFF] Visualizzando tutte le {len(self.all_photos)} foto")
        
        self.update_displays()
    
    def get_display_photos(self):
        """Ritorna le foto da visualizzare (tutte o solo selezionate)"""
        if self.show_only_selected:
            # Filtra solo le foto selezionate, mantenendo l'ordine originale
            return [p for p in self.all_photos if p in self.selected_photos]
        else:
            return self.all_photos
    
    def preload_adjacent_pages(self):
        """Pre-carica le miniature delle pagine adiacenti in background"""
        if not self.all_photos:
            return
        
        display_photos = self.get_display_photos()
        total_pages = (len(display_photos) + PHOTOS_PER_PAGE - 1) // PHOTOS_PER_PAGE
        
        # Pagine da precaricare
        pages_to_preload = []
        if self.current_page > 0:
            pages_to_preload.append(self.current_page - 1)  # Pagina precedente
        if self.current_page < total_pages - 1:
            pages_to_preload.append(self.current_page + 1)  # Pagina successiva
        
        def preload_in_background():
            for page_num in pages_to_preload:
                start_idx = page_num * PHOTOS_PER_PAGE
                end_idx = min(start_idx + PHOTOS_PER_PAGE, len(display_photos))
                
                for i in range(start_idx, end_idx):
                    photo_path = display_photos[i]
                    
                    # Se già in cache, salta
                    if photo_path in self.thumbnail_cache:
                        continue
                    
                    # Carica e metti in cache
                    try:
                        img = Image.open(photo_path)
                        
                        target_width = 225
                        target_height = 150
                        
                        # Ridimensiona mantenendo proporzioni + letterbox
                        img_ratio = img.width / img.height
                        target_ratio = target_width / target_height
                        
                        if img_ratio > target_ratio:
                            new_width = target_width
                            new_height = int(target_width / img_ratio)
                        else:
                            new_height = target_height
                            new_width = int(target_height * img_ratio)
                        
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Canvas nero
                        canvas = Image.new('RGB', (target_width, target_height), (0, 0, 0))
                        x_offset = (target_width - new_width) // 2
                        y_offset = (target_height - new_height) // 2
                        canvas.paste(img, (x_offset, y_offset))
                        
                        photo = ImageTk.PhotoImage(canvas)
                        
                        self.thumbnail_cache[photo_path] = photo
                        
                    except Exception as e:
                        print(f"Errore preload {photo_path}: {e}")
        
        # Avvia in thread separato per non bloccare UI
        threading.Thread(target=preload_in_background, daemon=True).start()
    
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
        """Toggle selezione foto (ottimizzato)"""
        widget = self.thumbnail_widgets[idx]
        
        if widget['photo_path'] is None:
            return
        
        photo_path = widget['photo_path']
        
        if photo_path in self.selected_photos:
            self.selected_photos.remove(photo_path)
            widget['photo_frame'].config(relief=tk.RAISED, borderwidth=2, bg='#ecf0f1')
            widget['photo_label'].config(bg='#ecf0f1')
            widget['num_label'].config(fg='#3498db')
            
            # Se era l'ultima foto selezionata e il filtro è attivo, disattivalo
            if not self.selected_photos and self.show_only_selected:
                self.show_only_selected = False
                self.filter_btn.config(text="👁️ Mostra SOLO Selezionate")
                self.grid_header_label.config(text="🖼️ MINIATURE - Click per selezionare")
                print("[AUTO] Filtro disattivato - nessuna foto selezionata")
        else:
            self.selected_photos.add(photo_path)
            widget['photo_frame'].config(relief=tk.SOLID, borderwidth=4, bg='#27ae60')
            widget['photo_label'].config(bg='#d5f4e6')
            widget['num_label'].config(fg='#27ae60')
        
        # Aggiorna solo le label necessarie (non ricaricare tutto)
        if self.selected_photos:
            self.selection_label.config(text=f"{len(self.selected_photos)} foto selezionate")
        else:
            self.selection_label.config(text="0 foto selezionate")
            
        self.print_btn.config(state=tk.NORMAL if self.selected_photos else tk.DISABLED)
        self.filter_btn.config(state=tk.NORMAL if self.selected_photos else tk.DISABLED)
        
        # Se filtro attivo, aggiorna tutto (potrebbe cambiare cosa si vede)
        if self.show_only_selected:
            self.update_displays()
        else:
            # Altrimenti aggiorna solo finestra secondaria (non ricaricare miniature)
            self.secondary_window.update_display(self.all_photos, self.current_page, self.selected_photos, self.show_only_selected)
    
    def select_current_page(self):
        """Seleziona tutte le foto della pagina corrente"""
        start_idx = self.current_page * PHOTOS_PER_PAGE
        end_idx = min(start_idx + PHOTOS_PER_PAGE, len(self.all_photos))
        
        for i in range(start_idx, end_idx):
            self.selected_photos.add(self.all_photos[i])
        
        self.update_displays()
    
    def select_all(self):
        """Seleziona tutte le foto"""
        self.selected_photos = set(self.all_photos)
        self.update_displays()
    
    def deselect_all(self):
        """Deseleziona tutte"""
        self.selected_photos.clear()
        
        # Se il filtro è attivo e non ci sono più selezioni, disattivalo automaticamente
        if self.show_only_selected:
            self.show_only_selected = False
            self.filter_btn.config(text="👁️ Mostra SOLO Selezionate")
            self.grid_header_label.config(text="🖼️ MINIATURE - Click per selezionare")
            print("[AUTO] Filtro disattivato - nessuna foto selezionata")
        
        self.update_displays()
    
    def update_displays(self):
        """Aggiorna entrambe le finestre (ottimizzato con cache)"""
        # Usa foto filtrate se il filtro è attivo
        display_photos = self.get_display_photos()
        total_pages = (len(display_photos) + PHOTOS_PER_PAGE - 1) // PHOTOS_PER_PAGE if display_photos else 0
        
        # DEBUG
        print(f"\n[DEBUG] Totale: {len(self.all_photos)} | Visualizzate: {len(display_photos)} | Filtro: {self.show_only_selected} | Pag: {self.current_page+1}/{total_pages}")
        
        # Assicurati che current_page sia valido
        if self.current_page >= total_pages and total_pages > 0:
            self.current_page = total_pages - 1
        
        # Aggiorna label pagina
        self.page_label.config(text=f"{self.current_page + 1} / {total_pages}" if total_pages > 0 else "0 / 0")
        
        # Abilita/disabilita pulsanti navigazione
        self.prev_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_page < total_pages - 1 else tk.DISABLED)
        
        # Aggiorna label selezione
        if self.selected_photos:
            self.selection_label.config(text=f"{len(self.selected_photos)} foto selezionate")
        else:
            self.selection_label.config(text="0 foto selezionate")
        
        # Abilita pulsanti
        self.print_btn.config(state=tk.NORMAL if self.selected_photos else tk.DISABLED)
        self.filter_btn.config(state=tk.NORMAL if self.selected_photos else tk.DISABLED)
        
        # Aggiorna griglia miniature CON CACHE (GRANDI: 225x150 per ratio 3:2 ORIZZONTALE)
        start_idx = self.current_page * PHOTOS_PER_PAGE
        end_idx = min(start_idx + PHOTOS_PER_PAGE, len(display_photos))
        page_photos = display_photos[start_idx:end_idx] if display_photos else []
        
        print(f"   -> Mostrando foto {start_idx+1} a {end_idx} ({len(page_photos)} foto)")
        
        for i, widget in enumerate(self.thumbnail_widgets):
            if i < len(page_photos):
                photo_path = page_photos[i]
                widget['photo_path'] = photo_path
                
                # Numero globale della foto (dall'array originale completo)
                try:
                    global_num = self.all_photos.index(photo_path) + 1
                except ValueError:
                    global_num = start_idx + i + 1
                    print(f"[WARNING] Foto non trovata: {os.path.basename(photo_path)}")
                
                widget['num_label'].config(text=f"#{global_num}")
                
                # PRIMA controlla cache
                if photo_path in self.thumbnail_cache:
                    # Usa immagine dalla cache (VELOCE!)
                    photo = self.thumbnail_cache[photo_path]
                    widget['photo_label'].config(image=photo, text='')
                    widget['photo_label'].image = photo
                else:
                    # SOLO se non in cache, carica e processa
                    try:
                        img = Image.open(photo_path)
                        
                        # Aspect ratio 3:2 ORIZZONTALE per miniature
                        target_width = 225
                        target_height = 150
                        
                        # NUOVO: Ridimensiona mantenendo proporzioni + letterbox
                        img_ratio = img.width / img.height
                        target_ratio = target_width / target_height  # 3:2 = 1.5
                        
                        # Calcola dimensioni mantenendo aspect ratio
                        if img_ratio > target_ratio:
                            # Foto più larga del target - limita per larghezza
                            new_width = target_width
                            new_height = int(target_width / img_ratio)
                        else:
                            # Foto più alta del target - limita per altezza
                            new_height = target_height
                            new_width = int(target_height * img_ratio)
                        
                        # Ridimensiona foto
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Crea canvas 3:2 con sfondo nero
                        canvas = Image.new('RGB', (target_width, target_height), (0, 0, 0))
                        
                        # Centra foto sul canvas
                        x_offset = (target_width - new_width) // 2
                        y_offset = (target_height - new_height) // 2
                        canvas.paste(img, (x_offset, y_offset))
                        
                        photo = ImageTk.PhotoImage(canvas)
                        
                        # SALVA in cache per prossime volte
                        self.thumbnail_cache[photo_path] = photo
                        
                        # Configura label (l'immagine definisce la dimensione)
                        widget['photo_label'].config(image=photo, text='')
                        widget['photo_label'].image = photo
                        
                    except Exception as e:
                        print(f"[ERROR] Errore caricamento #{global_num}: {e}")
                        widget['photo_label'].config(image='', text='ERROR')
                
                # Evidenzia se selezionata (VELOCE - solo colori)
                if photo_path in self.selected_photos:
                    widget['photo_frame'].config(relief=tk.SOLID, borderwidth=4, bg='#27ae60')
                    widget['photo_label'].config(bg='#d5f4e6')
                    widget['num_label'].config(fg='#27ae60')
                else:
                    widget['photo_frame'].config(relief=tk.RAISED, borderwidth=2, bg='#ecf0f1')
                    widget['photo_label'].config(bg='#ecf0f1')
                    widget['num_label'].config(fg='#3498db')
                
            else:
                # Cella vuota
                widget['photo_path'] = None
                widget['num_label'].config(text='')
                widget['photo_label'].config(image='', text='')
                widget['photo_frame'].config(bg='#ffffff', relief=tk.FLAT, borderwidth=0)
        
        # Aggiorna finestra secondaria (con filtro sincronizzato)
        self.secondary_window.update_display(self.all_photos, self.current_page, self.selected_photos, self.show_only_selected)

        # Pre-carica pagine adiacenti in background per navigazione istantanea
        self.preload_adjacent_pages()

        # Aggiorna status bar
        if self.selected_photos:
            self.status_bar.set_info(f"Pagina {self.current_page+1}/{total_pages} | {len(self.selected_photos)} selezionate")
        else:
            self.status_bar.set_info(f"Pagina {self.current_page+1}/{total_pages}")
    
    def load_printers(self):
        """Carica lista stampanti"""
        try:
            printers = [printer[2] for printer in win32print.EnumPrinters(2)]
            self.printer_combo['values'] = printers
            
            if printers:
                default_printer = win32print.GetDefaultPrinter()
                if default_printer in printers:
                    self.printer_var.set(default_printer)
                else:
                    self.printer_var.set(printers[0])
        except Exception as e:
            print(f"Errore caricamento stampanti: {e}")
            self.printer_combo['values'] = []
    
    def log_print_job(self, num_photos, layout):
        """Registra stampa nel log"""
        try:
            # Carica log esistente
            if os.path.exists(PRINT_LOG_FILE):
                with open(PRINT_LOG_FILE, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = {"prints": []}
            
            # Aggiungi nuova stampa
            print_entry = {
                "timestamp": datetime.now().isoformat(),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "num_photos": num_photos,
                "layout": layout,
                "printer": self.printer_var.get()
            }
            
            log_data["prints"].append(print_entry)
            
            # Salva log
            with open(PRINT_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            print(f"[LOG] Registrata stampa: {num_photos} foto, layout {layout}")
            
        except Exception as e:
            print(f"[ERROR] Errore log stampa: {e}")
    
    def show_print_report(self):
        """Mostra report stampe"""
        if not os.path.exists(PRINT_LOG_FILE):
            messagebox.showinfo("Report Stampe", "Nessuna stampa registrata")
            return
        
        try:
            with open(PRINT_LOG_FILE, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        except:
            messagebox.showerror("Errore", "Impossibile leggere il log stampe")
            return
        
        prints = log_data.get("prints", [])
        
        if not prints:
            messagebox.showinfo("Report Stampe", "Nessuna stampa registrata")
            return
        
        # Crea finestra report
        report_window = tk.Toplevel(self.root)
        report_window.title("Report Stampe")
        report_window.geometry("900x650")
        report_window.transient(self.root)
        
        # Header
        header = tk.Frame(report_window, bg='#34495e', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="REPORT STAMPE", font=('Arial', 16, 'bold'), 
                fg='white', bg='#34495e').pack(side=tk.LEFT, padx=20, pady=15)
        
        # Statistiche
        stats_frame = tk.Frame(report_window, bg='#ecf0f1', height=100)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        stats_frame.pack_propagate(False)
        
        # Calcola statistiche
        total_prints = len(prints)
        total_photos = sum(p['num_photos'] for p in prints)
        
        # Stampe per giorno
        by_date = {}
        for p in prints:
            date = p['date']
            if date not in by_date:
                by_date[date] = {'count': 0, 'photos': 0}
            by_date[date]['count'] += 1
            by_date[date]['photos'] += p['num_photos']
        
        # Oggi
        today = datetime.now().strftime("%Y-%m-%d")
        today_stats = by_date.get(today, {'count': 0, 'photos': 0})
        
        # Mostra statistiche
        stats_container = tk.Frame(stats_frame, bg='#ecf0f1')
        stats_container.pack(expand=True)
        
        stats_items = [
            ("Totale Stampe", str(total_prints)),
            ("Totale Foto", str(total_photos)),
            ("Oggi Stampe", str(today_stats['count'])),
            ("Oggi Foto", str(today_stats['photos']))
        ]
        
        for label, value in stats_items:
            col = tk.Frame(stats_container, bg='#ecf0f1')
            col.pack(side=tk.LEFT, padx=25)
            tk.Label(col, text=label, font=('Arial', 9), fg='#7f8c8d', 
                    bg='#ecf0f1').pack()
            tk.Label(col, text=value, font=('Arial', 22, 'bold'), fg='#2c3e50', 
                    bg='#ecf0f1').pack()
        
        # Tab per visualizzazioni
        notebook = ttk.Notebook(report_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # TAB 1: Storico completo
        tab_all = tk.Frame(notebook, bg='white')
        notebook.add(tab_all, text="Storico Completo")
        
        list_frame = tk.Frame(tab_all)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree = ttk.Treeview(list_frame, columns=('data', 'ora', 'foto', 'layout', 'stampante'),
                           show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        tree.heading('data', text='Data')
        tree.heading('ora', text='Ora')
        tree.heading('foto', text='N Foto')
        tree.heading('layout', text='Layout')
        tree.heading('stampante', text='Stampante')
        
        tree.column('data', width=100)
        tree.column('ora', width=80)
        tree.column('foto', width=80)
        tree.column('layout', width=100)
        tree.column('stampante', width=400)
        
        for p in reversed(prints):
            tree.insert('', 'end', values=(
                p['date'],
                p['time'],
                p['num_photos'],
                f"{p['layout']} foto/foglio",
                p['printer']
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # TAB 2: Per giorno
        tab_daily = tk.Frame(notebook, bg='white')
        notebook.add(tab_daily, text="Per Giorno")
        
        daily_frame = tk.Frame(tab_daily)
        daily_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar2 = ttk.Scrollbar(daily_frame)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree2 = ttk.Treeview(daily_frame, columns=('data', 'stampe', 'foto'),
                            show='headings', yscrollcommand=scrollbar2.set)
        scrollbar2.config(command=tree2.yview)
        
        tree2.heading('data', text='Data')
        tree2.heading('stampe', text='N Stampe')
        tree2.heading('foto', text='Totale Foto')
        
        tree2.column('data', width=200)
        tree2.column('stampe', width=150)
        tree2.column('foto', width=150)
        
        for date in sorted(by_date.keys(), reverse=True):
            stats = by_date[date]
            tree2.insert('', 'end', values=(
                date,
                stats['count'],
                stats['photos']
            ))
        
        tree2.pack(fill=tk.BOTH, expand=True)
        
        # Pulsanti azioni
        btn_frame = tk.Frame(report_window, bg='#ecf0f1')
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Esporta CSV", 
                  command=lambda: self.export_print_report(prints)).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Pulisci Log", 
                  command=lambda: self.clear_print_log(report_window)).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Chiudi", 
                  command=report_window.destroy).pack(side=tk.RIGHT, padx=10)
    
    def export_print_report(self, prints):
        """Esporta report in CSV"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"report_stampe_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("Data,Ora,Numero Foto,Layout,Stampante\n")
                for p in prints:
                    f.write(f"{p['date']},{p['time']},{p['num_photos']},"
                           f"{p['layout']} foto/foglio,{p['printer']}\n")
            
            messagebox.showinfo("Esportato", f"Report esportato in:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile esportare: {e}")
    
    def clear_print_log(self, report_window):
        """Pulisci log stampe"""
        if messagebox.askyesno("Conferma", "Eliminare tutto lo storico stampe?"):
            try:
                if os.path.exists(PRINT_LOG_FILE):
                    os.remove(PRINT_LOG_FILE)
                messagebox.showinfo("Completato", "Storico stampe eliminato")
                report_window.destroy()
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile eliminare: {e}")
    
    def print_photos(self):
        """Stampa foto selezionate con formati fotografici professionali"""
        if not self.selected_photos:
            return

        printer_name = self.printer_var.get()
        if not printer_name:
            messagebox.showwarning("Errore", "Seleziona una stampante")
            return

        # Ottieni formato selezionato
        photo_format = self.print_layout.get()

        # Descrizioni formati
        format_desc = {
            "15x20": "15×20 cm (1 foto/foglio)",
            "10x15": "10×15 cm (2 foto/foglio)",
            "9x13": "9×13 cm (4 foto/foglio)"
        }

        # Calcola numero fogli
        photos_per_sheet = {"15x20": 1, "10x15": 2, "9x13": 4}[photo_format]
        num_sheets = (len(self.selected_photos) + photos_per_sheet - 1) // photos_per_sheet

        if not messagebox.askyesno("Conferma Stampa",
                                   f"Stampare {len(self.selected_photos)} foto\n"
                                   f"Formato: {format_desc[photo_format]}\n"
                                   f"Fogli necessari: {num_sheets}\n"
                                   f"Stampante: {printer_name}?"):
            return
        
        # Finestra progresso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Stampa in corso...")
        progress_window.geometry("500x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="Stampa in corso...", 
                 font=('Arial', 12, 'bold')).pack(pady=20)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var,
                                       maximum=len(self.selected_photos))
        progress_bar.pack(pady=10, padx=20, fill=tk.X)
        
        status_label = ttk.Label(progress_window, text="")
        status_label.pack(pady=10)
        
        def print_thread():
            try:
                # Raggruppa foto per foglio
                sorted_photos = sorted(self.selected_photos)
                photo_groups = [sorted_photos[i:i+photos_per_sheet]
                              for i in range(0, len(sorted_photos), photos_per_sheet)]

                # Crea contesto stampa
                hDC = win32ui.CreateDC()
                hDC.CreatePrinterDC(printer_name)
                hDC.StartDoc(f"Stampa {len(sorted_photos)} foto")

                # Ottieni DPI e dimensioni stampante
                dpi_x = hDC.GetDeviceCaps(pywintypes_con.LOGPIXELSX)
                dpi_y = hDC.GetDeviceCaps(pywintypes_con.LOGPIXELSY)
                page_width = hDC.GetDeviceCaps(pywintypes_con.HORZRES)
                page_height = hDC.GetDeviceCaps(pywintypes_con.VERTRES)

                # Converti cm in pixel (1 cm = 0.393701 pollici)
                def cm_to_pixels(cm, dpi):
                    return int(cm * 0.393701 * dpi)

                # Definisci dimensioni foto in pixel per ogni formato
                if photo_format == "15x20":
                    photo_w = cm_to_pixels(15, dpi_x)
                    photo_h = cm_to_pixels(20, dpi_y)
                    positions = [(page_width // 2 - photo_w // 2, page_height // 2 - photo_h // 2)]
                elif photo_format == "10x15":
                    photo_w = cm_to_pixels(10, dpi_x)
                    photo_h = cm_to_pixels(15, dpi_y)
                    margin_y = cm_to_pixels(2, dpi_y)  # Margine verticale
                    positions = [
                        (page_width // 2 - photo_w // 2, margin_y),
                        (page_width // 2 - photo_w // 2, page_height - photo_h - margin_y)
                    ]
                else:  # 9x13
                    photo_w = cm_to_pixels(9, dpi_x)
                    photo_h = cm_to_pixels(13, dpi_y)
                    margin = cm_to_pixels(1.5, dpi_x)
                    spacing_x = (page_width - 2 * photo_w - 2 * margin) // 3
                    spacing_y = (page_height - 2 * photo_h - 2 * margin) // 3
                    positions = [
                        (margin + spacing_x, margin + spacing_y),
                        (page_width - photo_w - margin - spacing_x, margin + spacing_y),
                        (margin + spacing_x, page_height - photo_h - margin - spacing_y),
                        (page_width - photo_w - margin - spacing_x, page_height - photo_h - margin - spacing_y)
                    ]

                sheet_num = 0
                for group in photo_groups:
                    sheet_num += 1
                    hDC.StartPage()

                    progress_window.after(0, lambda s=sheet_num: status_label.config(
                        text=f"Stampa foglio {s}/{len(photo_groups)}..."))

                    for i, photo_path in enumerate(group):
                        if i >= len(positions):
                            break

                        # Carica foto
                        img = Image.open(photo_path)
                        if img.mode != 'RGB':
                            img = img.convert('RGB')

                        # Ridimensiona mantenendo proporzioni (letterbox)
                        img_ratio = img.width / img.height
                        target_ratio = photo_w / photo_h

                        if img_ratio > target_ratio:
                            # Foto più larga - limita per larghezza
                            new_w = photo_w
                            new_h = int(photo_w / img_ratio)
                        else:
                            # Foto più alta - limita per altezza
                            new_h = photo_h
                            new_w = int(photo_h * img_ratio)

                        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                        # Crea canvas nero per letterbox
                        canvas = Image.new('RGB', (photo_w, photo_h), (255, 255, 255))
                        offset_x = (photo_w - new_w) // 2
                        offset_y = (photo_h - new_h) // 2
                        canvas.paste(img_resized, (offset_x, offset_y))

                        # Salva come BMP temporaneo
                        temp_bmp = os.path.join(os.path.dirname(photo_path), f"temp_print_{i}.bmp")
                        canvas.save(temp_bmp, "BMP")

                        # Stampa nella posizione
                        x, y = positions[i]
                        bmp = Image.open(temp_bmp)
                        dib = ImageWin.Dib(bmp)
                        dib.draw(hDC.GetHandleOutput(), (x, y, x + photo_w, y + photo_h))

                        # Rimuovi temp
                        try:
                            os.remove(temp_bmp)
                        except:
                            pass

                    hDC.EndPage()
                    progress_window.after(0, lambda v=sheet_num: progress_var.set(v * photos_per_sheet))

                hDC.EndDoc()
                hDC.DeleteDC()

                progress_window.after(0, lambda: status_label.config(text="Stampa completata!"))
                time.sleep(2)
                progress_window.after(0, progress_window.destroy)

                # Registra stampa nel log
                self.root.after(0, lambda: self.log_print_job(len(self.selected_photos), photo_format))

                notification.notify(
                    title="Stampa Completata",
                    message=f"{len(self.selected_photos)} foto stampate - Formato {photo_format} cm",
                    app_name="SD Card Importer",
                    timeout=5
                )

            except Exception as e:
                error_msg = f"Errore: {e}"
                progress_window.after(0, lambda: status_label.config(text=error_msg))
                time.sleep(3)
                progress_window.after(0, progress_window.destroy)

        threading.Thread(target=print_thread, daemon=True).start()
    
    def run(self):
        """Avvia applicazione"""
        self.root.mainloop()


def main():
    """Avvia applicazione con splash screen professionale"""
    print("=== SD Card Photo Importer - Professional Edition ===")
    print("Avvio interfaccia grafica...")

    # Crea cartella base se non esiste
    os.makedirs(DESTINATION_BASE, exist_ok=True)

    # Crea root temporaneo per splash screen
    root_temp = tk.Tk()
    root_temp.withdraw()  # Nascondi finestra principale

    # Mostra splash screen
    splash = SplashScreen(root_temp, duration=2500)

    # Avvia app dopo che splash è chiuso
    def start_app():
        root_temp.destroy()  # Distruggi root temporaneo
        app = MainControlWindow()
        app.run()

    root_temp.after(2600, start_app)  # Aspetta che splash finisca
    root_temp.mainloop()


if __name__ == "__main__":
    main()