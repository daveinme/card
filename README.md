# SD Card Photo Importer

Programma per Windows e Linux che monitora automaticamente l'inserimento di schede SD e importa le foto in cartelle organizzate per data.

## Versioni disponibili

- **Windows**: `sd_card_importer.py`
- **Linux**: `sd_card_importer_linux.py`

## Funzionalità

- ✅ Rileva automaticamente quando viene inserita una scheda SD
- ✅ Importa foto e video in cartelle con data + numero sequenziale (es: `2025-12-06_1`, `2025-12-06_2`)
- ✅ Notifiche Windows all'inizio e alla fine dell'importazione
- ✅ Supporta formati: JPG, PNG, RAW, CR2, NEF, ARW, MP4, MOV, HEIC, DNG, etc.
- ✅ Gestisce file duplicati automaticamente

## Installazione

### Windows

#### 1. Installa Python
Scarica Python da [python.org](https://www.python.org/downloads/) (versione 3.8+)

#### 2. Installa le dipendenze
Apri il Prompt dei comandi nella cartella del progetto ed esegui:

```bash
pip install -r requirements.txt
```

#### 3. Configura il percorso di destinazione
Apri `sd_card_importer.py` e modifica la riga 17:

```python
DESTINATION_BASE = r"C:\Users\TuoNome\Pictures\SD_Import"
```

Sostituisci con il percorso completo dove vuoi salvare le foto.

### Linux

#### 1. Verifica Python
Python è già installato nella maggior parte delle distro Linux (3.8+)

#### 2. Installa notify-send (per notifiche)
```bash
# Ubuntu/Debian
sudo apt install libnotify-bin

# Fedora
sudo dnf install libnotify

# Arch
sudo pacman -S libnotify
```

#### 3. Configura il percorso di destinazione
Apri `sd_card_importer_linux.py` e modifica la riga 14:

```python
DESTINATION_BASE = os.path.expanduser("~/Pictures/SD_Import")
```

Puoi lasciare così (userà la tua home) oppure specificare un percorso assoluto.

## Utilizzo

### Linux (per testare)
Apri il terminale ed esegui:

```bash
python3 sd_card_importer_linux.py
```

### Windows
Apri il Prompt dei comandi e esegui:

```bash
python sd_card_importer.py
```

Il programma rimarrà in esecuzione e monitorerà le schede SD. Premi `CTRL+C` per terminarlo.

### Avvio automatico con Windows (opzionale)

#### Metodo 1: Collegamento nella cartella Avvio
1. Premi `Win+R` e digita `shell:startup`
2. Crea un file `.bat` in questa cartella con:
   ```batch
   @echo off
   cd /d "C:\percorso\della\cartella\card"
   pythonw sd_card_importer.py
   ```
3. Salva come `SD_Importer.bat`

#### Metodo 2: Utilità di pianificazione
1. Cerca "Utilità di pianificazione" in Windows
2. Crea attività di base → Nome: "SD Card Importer"
3. Trigger: All'avvio del computer
4. Azione: Avvia programma → `pythonw.exe`
5. Argomenti: percorso completo di `sd_card_importer.py`

## Esempio di struttura cartelle create

```
C:\Users\TuoNome\Pictures\SD_Import\
├── 2025-12-06\
│   ├── 1\
│   │   ├── IMG_001.jpg
│   │   ├── IMG_002.jpg
│   │   └── ...
│   ├── 2\
│   │   ├── IMG_050.jpg
│   │   └── ...
│   └── 3\
│       └── ...
└── 2025-12-07\
    └── 1\
        └── ...
```

## Note

- Il programma copia i file (non li sposta), quindi le foto rimarranno sulla scheda SD
- Per eliminare le foto dalla SD dopo l'importazione, puoi farlo manualmente
- Le notifiche Windows mostrano il progresso dell'importazione
- Il programma rileva qualsiasi unità rimovibile (SD, USB, etc.)

## Troubleshooting

**Errore "module not found":**
Assicurati di aver installato le dipendenze con `pip install -r requirements.txt`

**Le notifiche non appaiono:**
Verifica che le notifiche siano abilitate per Python nelle impostazioni di Windows

**Il programma non rileva la scheda SD:**
Assicurati che la scheda SD sia riconosciuta da Windows in "Questo PC"
