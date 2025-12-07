"""
Componenti UI Professionali per SD Card Importer
Libreria di widget e utilità per creare un'interfaccia ultra professionale
"""

import tkinter as tk
from tkinter import ttk
import time
import threading


# ===== TOOLTIP PROFESSIONALE =====
class ToolTip:
    """
    Tooltip professionale con ritardo e stile moderno
    Uso: ToolTip(widget, "Testo del tooltip")
    """
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay  # millisecondi
        self.tooltip_window = None
        self.schedule_id = None

        self.widget.bind('<Enter>', self.on_enter)
        self.widget.bind('<Leave>', self.on_leave)
        self.widget.bind('<Button>', self.on_leave)

    def on_enter(self, event=None):
        """Mouse entra nel widget"""
        self.schedule_id = self.widget.after(self.delay, self.show_tooltip)

    def on_leave(self, event=None):
        """Mouse esce dal widget"""
        if self.schedule_id:
            self.widget.after_cancel(self.schedule_id)
            self.schedule_id = None
        self.hide_tooltip()

    def show_tooltip(self):
        """Mostra tooltip"""
        if self.tooltip_window:
            return

        # Posizione
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        # Crea finestra tooltip
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Stile moderno
        frame = tk.Frame(self.tooltip_window,
                        background='#2c3e50',
                        borderwidth=1,
                        relief=tk.SOLID)
        frame.pack()

        label = tk.Label(frame,
                        text=self.text,
                        background='#2c3e50',
                        foreground='#ecf0f1',
                        font=('Segoe UI', 9),
                        padx=10,
                        pady=5,
                        justify=tk.LEFT)
        label.pack()

    def hide_tooltip(self):
        """Nascondi tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


# ===== PULSANTE MODERNO CON HOVER =====
class ModernButton(tk.Button):
    """
    Pulsante con effetti hover professionali
    Uso: ModernButton(parent, text="Click", command=func, style="primary")
    Stili: primary, success, danger, secondary
    """
    def __init__(self, parent, text="", command=None, style="primary", **kwargs):
        # Colori per stili
        styles = {
            'primary': {
                'bg': '#3498db',
                'hover': '#2980b9',
                'active': '#21618c',
                'fg': 'white'
            },
            'success': {
                'bg': '#27ae60',
                'hover': '#229954',
                'active': '#1e8449',
                'fg': 'white'
            },
            'danger': {
                'bg': '#e74c3c',
                'hover': '#c0392b',
                'active': '#a93226',
                'fg': 'white'
            },
            'secondary': {
                'bg': '#95a5a6',
                'hover': '#7f8c8d',
                'active': '#707b7c',
                'fg': 'white'
            }
        }

        self.style_colors = styles.get(style, styles['primary'])

        super().__init__(parent,
                        text=text,
                        command=command,
                        bg=self.style_colors['bg'],
                        fg=self.style_colors['fg'],
                        font=('Segoe UI', 10, 'bold'),
                        relief=tk.FLAT,
                        borderwidth=0,
                        padx=20,
                        pady=10,
                        cursor='hand2',
                        activebackground=self.style_colors['active'],
                        activeforeground='white',
                        **kwargs)

        # Bind hover events
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_enter(self, event):
        """Hover effect"""
        if self['state'] != tk.DISABLED:
            self.config(bg=self.style_colors['hover'])

    def on_leave(self, event):
        """Rimuovi hover"""
        if self['state'] != tk.DISABLED:
            self.config(bg=self.style_colors['bg'])


# ===== STATUS BAR PROFESSIONALE =====
class StatusBar(tk.Frame):
    """
    Status bar professionale con sezioni multiple
    Uso: status_bar = StatusBar(root)
         status_bar.pack(side=tk.BOTTOM, fill=tk.X)
         status_bar.set_status("Pronto")
    """
    def __init__(self, parent):
        super().__init__(parent, bg='#2c3e50', height=30)
        self.pack_propagate(False)

        # Label principale (sinistra)
        self.status_label = tk.Label(self,
                                     text="Pronto",
                                     bg='#2c3e50',
                                     fg='#ecf0f1',
                                     font=('Segoe UI', 9),
                                     anchor=tk.W,
                                     padx=10)
        self.status_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Separator
        tk.Frame(self, bg='#34495e', width=1).pack(side=tk.LEFT, fill=tk.Y, padx=2)

        # Label info (centro-destra)
        self.info_label = tk.Label(self,
                                   text="",
                                   bg='#2c3e50',
                                   fg='#95a5a6',
                                   font=('Segoe UI', 9),
                                   anchor=tk.E,
                                   padx=10)
        self.info_label.pack(side=tk.LEFT)

        # Separator
        tk.Frame(self, bg='#34495e', width=1).pack(side=tk.LEFT, fill=tk.Y, padx=2)

        # Progress indicator (opzionale - nascosto di default)
        self.progress_frame = tk.Frame(self, bg='#2c3e50')
        self.progress_label = tk.Label(self.progress_frame,
                                       text="⚙",
                                       bg='#2c3e50',
                                       fg='#3498db',
                                       font=('Segoe UI', 10))
        self.progress_label.pack(side=tk.LEFT, padx=10)

        # Versione/data (destra)
        self.version_label = tk.Label(self,
                                      text="v2.0 Pro",
                                      bg='#2c3e50',
                                      fg='#7f8c8d',
                                      font=('Segoe UI', 9),
                                      padx=10)
        self.version_label.pack(side=tk.RIGHT)

    def set_status(self, text, color='#ecf0f1'):
        """Imposta testo status principale"""
        self.status_label.config(text=text, fg=color)

    def set_info(self, text):
        """Imposta testo informativo"""
        self.info_label.config(text=text)

    def show_progress(self, show=True):
        """Mostra/nascondi indicator progresso"""
        if show:
            self.progress_frame.pack(side=tk.LEFT, before=self.version_label)
            self._animate_progress()
        else:
            self.progress_frame.pack_forget()

    def _animate_progress(self):
        """Animazione spinner"""
        if self.progress_frame.winfo_ismapped():
            current = self.progress_label.cget('text')
            symbols = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            next_idx = (symbols.index(current) + 1) % len(symbols) if current in symbols else 0
            self.progress_label.config(text=symbols[next_idx])
            self.after(100, self._animate_progress)


# ===== SPLASH SCREEN =====
class SplashScreen:
    """
    Splash screen professionale all'avvio
    Uso: splash = SplashScreen(root, duration=2000)
    """
    def __init__(self, parent, duration=2500):
        self.parent = parent
        self.duration = duration

        # Crea finestra splash
        self.splash = tk.Toplevel()
        self.splash.overrideredirect(True)

        # Dimensioni e posizione centrale
        width = 600
        height = 400
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.splash.geometry(f'{width}x{height}+{x}+{y}')

        # Sfondo gradiente (simulato con frame)
        main_frame = tk.Frame(self.splash, bg='#1a1d23')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Container centrale
        center_frame = tk.Frame(main_frame, bg='#1a1d23')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Icona/Logo (emoji grande)
        icon_label = tk.Label(center_frame,
                             text="📸",
                             font=('Segoe UI', 80),
                             bg='#1a1d23',
                             fg='#3498db')
        icon_label.pack(pady=20)

        # Titolo app
        title_label = tk.Label(center_frame,
                              text="SD CARD IMPORTER",
                              font=('Segoe UI', 28, 'bold'),
                              bg='#1a1d23',
                              fg='#ecf0f1')
        title_label.pack(pady=10)

        # Sottotitolo
        subtitle_label = tk.Label(center_frame,
                                 text="Professional Edition",
                                 font=('Segoe UI', 14),
                                 bg='#1a1d23',
                                 fg='#95a5a6')
        subtitle_label.pack(pady=5)

        # Progress bar moderna
        progress_container = tk.Frame(main_frame, bg='#1a1d23')
        progress_container.pack(side=tk.BOTTOM, fill=tk.X, padx=50, pady=30)

        # Progress track (sfondo)
        self.progress_track = tk.Canvas(progress_container,
                                       height=6,
                                       bg='#2c3e50',
                                       highlightthickness=0)
        self.progress_track.pack(fill=tk.X)

        # Progress fill (barra animata)
        self.progress_fill = self.progress_track.create_rectangle(
            0, 0, 0, 6,
            fill='#3498db',
            outline=''
        )

        # Status text
        self.status_label = tk.Label(progress_container,
                                     text="Caricamento...",
                                     font=('Segoe UI', 9),
                                     bg='#1a1d23',
                                     fg='#7f8c8d')
        self.status_label.pack(pady=5)

        # Versione (in basso a destra)
        version_label = tk.Label(main_frame,
                                text="v2.0.0",
                                font=('Segoe UI', 8),
                                bg='#1a1d23',
                                fg='#4a5568')
        version_label.place(relx=0.95, rely=0.95, anchor=tk.SE)

        # Anima progress bar
        self._animate_progress()

        # Chiudi dopo duration
        self.splash.after(duration, self.close)

    def _animate_progress(self):
        """Animazione barra progresso"""
        if self.splash.winfo_exists():
            current_width = self.progress_track.coords(self.progress_fill)[2]
            max_width = self.progress_track.winfo_width()

            if max_width > 1:  # Canvas renderizzato
                progress = (current_width / max_width) * 100

                if progress < 100:
                    # Incrementa
                    new_width = min(current_width + (max_width / 50), max_width)
                    self.progress_track.coords(self.progress_fill, 0, 0, new_width, 6)

                    # Aggiorna status
                    if progress < 30:
                        self.status_label.config(text="Inizializzazione...")
                    elif progress < 60:
                        self.status_label.config(text="Caricamento componenti...")
                    elif progress < 90:
                        self.status_label.config(text="Preparazione interfaccia...")
                    else:
                        self.status_label.config(text="Quasi pronto...")

            self.splash.after(50, self._animate_progress)

    def close(self):
        """Chiudi splash screen"""
        self.splash.destroy()


# ===== ABOUT DIALOG =====
class AboutDialog:
    """
    Dialog About professionale con info app
    Uso: AboutDialog(parent)
    """
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Informazioni")
        self.dialog.geometry("500x550")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Centra finestra
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (550 // 2)
        self.dialog.geometry(f'+{x}+{y}')

        # Header con gradiente
        header = tk.Frame(self.dialog, bg='#2c3e50', height=150)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Icona grande
        icon_label = tk.Label(header,
                             text="📸",
                             font=('Segoe UI', 60),
                             bg='#2c3e50',
                             fg='#3498db')
        icon_label.pack(pady=20)

        # Titolo
        title_label = tk.Label(header,
                              text="SD Card Photo Importer",
                              font=('Segoe UI', 18, 'bold'),
                              bg='#2c3e50',
                              fg='white')
        title_label.pack()

        # Corpo
        body = tk.Frame(self.dialog, bg='white')
        body.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Versione
        version_frame = tk.Frame(body, bg='white')
        version_frame.pack(pady=10)

        tk.Label(version_frame,
                text="Versione:",
                font=('Segoe UI', 10),
                bg='white',
                fg='#7f8c8d').pack(side=tk.LEFT, padx=5)

        tk.Label(version_frame,
                text="2.0.0 Professional Edition",
                font=('Segoe UI', 10, 'bold'),
                bg='white',
                fg='#2c3e50').pack(side=tk.LEFT)

        # Separator
        tk.Frame(body, height=1, bg='#ecf0f1').pack(fill=tk.X, pady=15)

        # Descrizione
        desc_text = (
            "Software professionale per l'importazione automatica "
            "di foto da schede SD.\n\n"
            "Caratteristiche:\n"
            "• Importazione automatica da SD card\n"
            "• Organizzazione per data\n"
            "• Visualizzazione griglia foto\n"
            "• Stampa professionale\n"
            "• Report e statistiche\n"
            "• Interfaccia dual-monitor"
        )

        desc_label = tk.Label(body,
                             text=desc_text,
                             font=('Segoe UI', 10),
                             bg='white',
                             fg='#2c3e50',
                             justify=tk.LEFT,
                             wraplength=420)
        desc_label.pack(pady=10)

        # Separator
        tk.Frame(body, height=1, bg='#ecf0f1').pack(fill=tk.X, pady=15)

        # Copyright
        copyright_label = tk.Label(body,
                                   text="© 2025 - Tutti i diritti riservati",
                                   font=('Segoe UI', 9),
                                   bg='white',
                                   fg='#95a5a6')
        copyright_label.pack(pady=5)

        # Footer con pulsante
        footer = tk.Frame(self.dialog, bg='#ecf0f1')
        footer.pack(fill=tk.X, pady=10)

        close_btn = ModernButton(footer,
                                text="Chiudi",
                                command=self.dialog.destroy,
                                style='primary')
        close_btn.pack(pady=10)


# ===== TOOLBAR PROFESSIONALE =====
class Toolbar(tk.Frame):
    """
    Toolbar professionale con pulsanti icone
    Uso: toolbar = Toolbar(parent)
         toolbar.pack(side=tk.TOP, fill=tk.X)
         toolbar.add_button("📂", command, "Apri")
    """
    def __init__(self, parent):
        super().__init__(parent, bg='#34495e', height=50, relief=tk.FLAT)
        self.pack_propagate(False)

        self.buttons = []

    def add_button(self, icon, command, tooltip_text="", style='normal'):
        """Aggiungi pulsante alla toolbar"""
        # Colori
        bg = '#34495e'
        hover_bg = '#415a77'
        active_bg = '#2c3e50'

        if style == 'primary':
            bg = '#3498db'
            hover_bg = '#2980b9'
            active_bg = '#21618c'

        btn = tk.Button(self,
                       text=icon,
                       font=('Segoe UI', 16),
                       bg=bg,
                       fg='white',
                       relief=tk.FLAT,
                       borderwidth=0,
                       padx=15,
                       pady=5,
                       cursor='hand2',
                       command=command,
                       activebackground=active_bg,
                       activeforeground='white')

        btn.pack(side=tk.LEFT, padx=2)

        # Hover effect
        def on_enter(e):
            if btn['state'] != tk.DISABLED:
                btn.config(bg=hover_bg)

        def on_leave(e):
            if btn['state'] != tk.DISABLED:
                btn.config(bg=bg)

        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

        # Tooltip
        if tooltip_text:
            ToolTip(btn, tooltip_text)

        self.buttons.append(btn)
        return btn

    def add_separator(self):
        """Aggiungi separatore verticale"""
        sep = tk.Frame(self, bg='#2c3e50', width=1)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)
        return sep


# ===== NOTIFICATION TOAST =====
class ToastNotification:
    """
    Notifica toast in-app (angolo basso destro)
    Uso: ToastNotification(root, "Operazione completata!", duration=3000, type="success")
    """
    def __init__(self, parent, message, duration=3000, notification_type="info"):
        self.parent = parent

        # Colori per tipo
        colors = {
            'info': {'bg': '#3498db', 'fg': 'white'},
            'success': {'bg': '#27ae60', 'fg': 'white'},
            'warning': {'bg': '#f39c12', 'fg': 'white'},
            'error': {'bg': '#e74c3c', 'fg': 'white'}
        }

        color = colors.get(notification_type, colors['info'])

        # Crea finestra toast
        self.toast = tk.Toplevel(parent)
        self.toast.overrideredirect(True)
        self.toast.attributes('-topmost', True)

        # Frame principale
        frame = tk.Frame(self.toast,
                        bg=color['bg'],
                        relief=tk.RAISED,
                        borderwidth=2)
        frame.pack(fill=tk.BOTH, expand=True)

        # Messaggio
        label = tk.Label(frame,
                        text=message,
                        bg=color['bg'],
                        fg=color['fg'],
                        font=('Segoe UI', 10, 'bold'),
                        padx=20,
                        pady=15)
        label.pack()

        # Posiziona in basso a destra
        self.toast.update_idletasks()
        toast_width = self.toast.winfo_width()
        toast_height = self.toast.winfo_height()

        screen_width = self.toast.winfo_screenwidth()
        screen_height = self.toast.winfo_screenheight()

        x = screen_width - toast_width - 20
        y = screen_height - toast_height - 60

        self.toast.geometry(f'+{x}+{y}')

        # Animazione fade-in (opacità)
        self.toast.attributes('-alpha', 0.0)
        self._fade_in()

        # Auto-chiudi dopo duration
        self.toast.after(duration, self._fade_out)

    def _fade_in(self, alpha=0.0):
        """Animazione fade in"""
        if alpha < 1.0:
            alpha += 0.1
            self.toast.attributes('-alpha', alpha)
            self.toast.after(30, lambda: self._fade_in(alpha))

    def _fade_out(self, alpha=1.0):
        """Animazione fade out"""
        if alpha > 0.0:
            alpha -= 0.1
            self.toast.attributes('-alpha', alpha)
            self.toast.after(30, lambda: self._fade_out(alpha))
        else:
            self.toast.destroy()


# ===== ESPORTAZIONE =====
__all__ = [
    'ToolTip',
    'ModernButton',
    'StatusBar',
    'SplashScreen',
    'AboutDialog',
    'Toolbar',
    'ToastNotification'
]
