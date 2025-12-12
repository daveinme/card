# SD Card Photo Importer - Professional Edition

Applicazione professionale per importare, visualizzare e stampare foto da schede SD.

## 🎯 Caratteristiche Principali

### ✨ Importazione Foto
- Importazione automatica da scheda SD
- Multi-threading per velocità massima
- Modalità copia o taglia (sposta)
- Organizzazione automatica per data

### 🖼️ Visualizzazione
- Doppio monitor support (finestra principale + finestra visualizzazione)
- Griglia 3x3 con 9 foto per pagina
- Thumbnails ad alta qualità con cache
- Navigazione veloce con tastiera
- Selezione multipla foto

### 🖨️ Stampa Professionale con Spooler Interno
- **1 foto per foglio** (la stampante gestisce le dimensioni)
- **Spooler interno**: attende che ogni foto sia completata prima di inviare la successiva
- Monitora lo stato dei job di stampa in tempo reale
- Report stampe con statistiche
- Export CSV dello storico

### 🛡️ Sicurezza
- Controllo integrità file prima di cancellare dalla SD
- Verifica dimensioni e presenza file
- Backup automatico

## 📦 Installazione

### Requisiti
- Windows 10/11
- Python 3.8 o superiore
- Tkinter (incluso in Python)

### Setup

1. **Clona o scarica il progetto**
```bash
cd /path/to/sd_card_importer
```

2. **Installa le dipendenze**
```bash
pip install -r requirements.txt
```

3. **Configura il programma**
Modifica `config.py`:
```python
DESTINATION_BASE = r"C:\Users\TuoNome\Desktop\foto"  # Cartella destinazione
SD_DRIVE_LETTER = "D"  # Lettera dell'unità SD
```

## 🚀 Avvio

```bash
python sd_card_importer2.py
```

## ⌨️ Scorciatoie da Tastiera

### Navigazione
- `←` / `→` - Pagina precedente/successiva
- `Home` / `End` - Prima/ultima pagina
- `1-9` - Seleziona foto (dalla finestra secondaria)

### Selezione
- `Ctrl+A` - Seleziona tutte le foto
- `Ctrl+D` - Deseleziona tutte
- `Ctrl+F` - Mostra solo foto selezionate

### Operazioni
- `Ctrl+O` - Apri cartella
- `Ctrl+H` - Vai a cartella base
- `Ctrl+I` - Importa da SD
- `Ctrl+P` - Stampa foto selezionate
- `Ctrl+R` - Report stampe

### Display Secondario
- `F11` - Fullscreen
- `Esc` - Esci da fullscreen

## 📁 Struttura Moduli

```
card/
├── config.py                    # Configurazioni e costanti
├── print_manager.py             # Gestione stampa con spooler
├── photo_manager.py             # Gestione foto e importazione
├── secondary_window.py          # Finestra visualizzazione secondaria
├── professional_features.py     # Componenti UI professionali
├── sd_card_importer2.py         # File principale
└── print_log.json              # Log stampe (generato automaticamente)
```

## 🖨️ Come Funziona lo Spooler di Stampa

1. L'utente seleziona le foto e clicca "Stampa"
2. Per ogni foto:
   - Crea un job di stampa singolo
   - Invia la foto alla stampante (1 foto = 1 foglio)
   - Monitora lo stato del job con `win32print.EnumJobs()`
   - **Attende che il job sia completato** prima di inviare la prossima
3. La stampante gestisce le dimensioni finali (es. 15x20 cm)
4. Log automatico di tutte le stampe

### Testare con Windows PDF Printer

⚠️ **IMPORTANTE**: Windows PDF Printer elabora i job quasi istantaneamente, quindi **NON è affidabile** per testare lo spooler.

È utile per:
- ✅ Verificare che non ci siano errori nel codice
- ✅ Controllare i PDF generati
- ✅ Testare la logica base

Per test realistici serve una stampante fisica o di rete.

## 🔧 Configurazione Stampante

1. Vai in `Impostazioni > Stampanti` di Windows
2. Imposta la tua stampante predefinita
3. Configura formato carta (es. A4, 10x15 cm)
4. Il programma rileverà automaticamente la stampante

## 📊 Report Stampe

Il programma registra automaticamente:
- Data e ora di ogni stampa
- Numero di foto stampate
- Formato richiesto
- Stampante utilizzata

Report accessibile da: `Menu > Report Stampe` o `Ctrl+R`

## 🐛 Troubleshooting

### "SD card non trovata"
- Verifica che la lettera unità in `config.py` sia corretta
- Controlla che la SD sia inserita

### "Errore caricamento stampanti"
- Verifica che `pywin32` sia installato: `pip install pywin32`
- Riavvia il programma

### "Errore durante la stampa"
- Controlla che la stampante sia accesa e online
- Verifica carta e inchiostro
- Guarda i log per dettagli: cerca `[ERROR]` nel terminale

## 📝 Log e Debug

Il programma stampa informazioni nel terminale:
- `[LOG]` - Operazioni normali
- `[SPOOLER]` - Stato job di stampa
- `[ERROR]` - Errori
- `[WARNING]` - Avvisi

## 🔮 Sviluppi Futuri

- [ ] Migrazione a PySide6 (se necessario per prestazioni)
- [ ] Support Linux/Mac
- [ ] Cloud backup automatico
- [ ] OCR per riconoscimento testo nelle foto
- [ ] Organizzazione automatica con AI

## 📄 Licenza

Uso personale/professionale

## 👨‍💻 Autore

Sviluppato con ❤️ e Claude Code
