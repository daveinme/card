"""
SD Card Photo Importer - Configurazione
Tutte le costanti e configurazioni dell'applicazione
"""

# ===== CONFIGURAZIONE BASE =====
DESTINATION_BASE = r"C:\Users\Dave\Desktop\natale"
SD_DRIVE_LETTER = "I"
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
        # Toni scuri eleganti (più profondi e ricchi)
        'dark_bg': '#0f1218',           # Sfondo principale scuro profondo
        'dark_surface': '#1a1f2e',      # Superfici rialzate
        'dark_panel': '#252d3d',        # Pannelli laterali

        # Accenti brand (più vivaci e moderni)
        'primary': '#3b82f6',           # Blu primario vivace
        'primary_hover': '#60a5fa',     # Blu hover luminoso
        'primary_active': '#2563eb',    # Blu pressed intenso

        'success': '#10b981',           # Verde successo moderno
        'success_light': '#34d399',     # Verde chiaro
        'warning': '#f59e0b',           # Arancione warning
        'danger': '#ef4444',            # Rosso errore

        # Toni chiari
        'light_bg': '#f8fafc',          # Sfondo chiaro
        'light_surface': '#ffffff',     # Superficie bianca
        'light_border': '#e2e8f0',      # Bordi sottili

        # Testo (maggior contrasto)
        'text_primary': '#f1f5f9',      # Testo principale (su scuro)
        'text_secondary': '#94a3b8',    # Testo secondario
        'text_disabled': '#475569',     # Testo disabilitato
        'text_dark': '#1e293b',         # Testo su chiaro

        # Stati foto
        'photo_selected': '#3b82f6',    # Foto selezionata
        'photo_hover': '#334155',       # Hover foto
        'photo_bg': '#1e293b',          # Sfondo foto

        # Client display
        'client_bg': '#0a0a0a',         # Nero puro client
        'client_selected': '#10b981',   # Verde brillante selezione
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

        'weight_bold': 700,             # Qt usa valori numerici (700 = bold)
        'weight_semibold': 600,         # Qt supporta semibold (600)
        'weight_normal': 400,           # Normal weight (400)
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
