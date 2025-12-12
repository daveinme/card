# Changelog - Versione Qt

## Modifiche Effettuate

### Interfaccia Grafica
- ✅ Convertito da Tkinter → PySide6
- ✅ Design minimal e leggero
- ✅ Bordi visibili SOLO su foto selezionate
- ✅ Numeri foto discreti (piccoli e grigi)
- ✅ Palette colori dark ottimizzata

### Controlli Tastiera
- ✅ Frecce ← → per navigazione pagine
- ✅ Numeri 1-9 per selezione foto rapida
- ✅ F11 per fullscreen (finestra secondaria)
- ✅ ESC per uscire da fullscreen
- ✅ Ctrl+A/D/P/O/H/I per operazioni comuni

### Finestra Secondaria
- ✅ Ultra minimal
- ✅ Sfondo nero
- ✅ Bordi verdi SOLO su foto selezionate
- ✅ F11 funzionante
- ✅ Click mouse per selezionare/deselezionare foto
- ✅ Pulsante 👁️ e shortcut F/Ctrl+F per filtro solo selezionate
- ✅ Pulsanti ◄ ► e frecce tastiera per navigazione pagine

### Stampa
- ✅ Rimossi controlli layout (gestito da stampante)
- ✅ Dialogo semplificato
- ✅ 1 foto per foglio

## File Creati
- `sd_card_importer_qt_main.py` - Main Qt
- `secondary_window_qt.py` - Finestra secondaria Qt
- `print_manager_qt.py` - Gestione stampa Qt
- `test_imports.py` - Test dipendenze
- `DEBUG.bat` - Debug launcher

## File Modificati
- `START.bat` - Lancia versione Qt
- `professional_features_qt.py` - Fix QSize import

## Come Usare

### Versione Qt (Consigliata)
```
START.bat
```
oppure
```
python sd_card_importer_qt_main.py
```

### Versione Tkinter (Legacy)
```
START_TKINTER.bat
```
oppure
```
python sd_card_importer2.py
```

## Controlli Tastiera

### Finestra Principale
- `←` / `→` - Pagina prec/succ
- `1-9` - Seleziona foto
- `Ctrl+A` - Seleziona tutte
- `Ctrl+D` - Deseleziona tutte
- `Ctrl+P` - Stampa
- `Ctrl+O` - Apri cartella
- `Ctrl+I` - Importa da SD
- `F5` - Aggiorna stato SD

### Finestra Secondaria
- `F11` - Fullscreen
- `ESC` - Esci fullscreen
- `←` / `→` - Pagina precedente/successiva
- `F` o `Ctrl+F` - Mostra solo selezionate / Mostra tutte
- `Click Mouse` - Seleziona/Deseleziona foto
- Pulsanti ◄ ► per navigazione pagine
- Pulsante 👁️ per filtro

## Requisiti
- Python 3.8+
- PySide6
- Pillow
- pywin32
- plyer

Installa con:
```
pip install -r requirements.txt
```
