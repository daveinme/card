"""
SD Card Photo Importer for Windows
Monitora l'inserimento di schede SD e importa automaticamente le foto
"""

import os
import shutil
import time
from datetime import datetime
from pathlib import Path
import win32file
import win32con
from plyer import notification

# ===== CONFIGURAZIONE =====
# Modifica questo percorso con la tua cartella di destinazione
DESTINATION_BASE = r"C:\Users\YourUsername\Pictures\SD_Import"

# Lettera dell'unità SD (lascia None per auto-detect, oppure specifica es: "E")
SD_DRIVE_LETTER = None  # Cambia in "E" o "F" se vuoi fissare la lettera

# Estensioni file da importare (foto/video)
PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.raw', '.cr2', '.nef', '.arw',
                    '.mp4', '.mov', '.avi', '.heic', '.dng'}

# ===== FINE CONFIGURAZIONE =====


def show_notification(title, message, timeout=5):
    """Mostra notifica Windows"""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="SD Card Importer",
            timeout=timeout
        )
    except Exception as e:
        print(f"Errore notifica: {e}")


def get_next_folder_number(base_path, date_str):
    """
    Trova il prossimo numero sequenziale per la cartella
    Struttura: base_path/2025-12-06/1, base_path/2025-12-06/2, etc.
    """
    date_folder = os.path.join(base_path, date_str)
    os.makedirs(date_folder, exist_ok=True)

    counter = 1
    while True:
        folder_path = os.path.join(date_folder, str(counter))
        if not os.path.exists(folder_path):
            return folder_path, f"{date_str}/{counter}"
        counter += 1


def is_photo_file(filepath):
    """Verifica se il file è una foto/video"""
    return Path(filepath).suffix.lower() in PHOTO_EXTENSIONS


def get_removable_drives():
    """Rileva tutte le unità rimovibili (schede SD, USB, etc.)"""
    # Se è specificata una lettera fissa, usa solo quella
    if SD_DRIVE_LETTER:
        drive = f"{SD_DRIVE_LETTER.upper()}:\\"
        if os.path.exists(drive):
            return [drive]
        else:
            return []

    # Altrimenti auto-detect
    drives = []
    bitmask = win32file.GetLogicalDrives()
    for letter in range(65, 91):  # A-Z
        if bitmask & (1 << (letter - 65)):
            drive = f"{chr(letter)}:\\"
            try:
                drive_type = win32file.GetDriveType(drive)
                if drive_type == win32con.DRIVE_REMOVABLE:
                    drives.append(drive)
            except:
                pass
    return drives


def count_photos_in_drive(drive):
    """Conta le foto nella scheda SD"""
    count = 0
    try:
        for root, dirs, files in os.walk(drive):
            for file in files:
                if is_photo_file(file):
                    count += 1
    except Exception as e:
        print(f"Errore nel conteggio foto: {e}")
    return count


def import_photos(source_drive, dest_folder):
    """Importa le foto dalla scheda SD alla cartella di destinazione"""
    imported = 0
    errors = 0

    try:
        for root, dirs, files in os.walk(source_drive):
            for file in files:
                if is_photo_file(file):
                    source_path = os.path.join(root, file)
                    dest_path = os.path.join(dest_folder, file)

                    # Gestisci file duplicati aggiungendo un numero
                    if os.path.exists(dest_path):
                        name, ext = os.path.splitext(file)
                        counter = 1
                        while os.path.exists(dest_path):
                            dest_path = os.path.join(dest_folder, f"{name}_{counter}{ext}")
                            counter += 1

                    try:
                        shutil.copy2(source_path, dest_path)
                        imported += 1
                        print(f"Importato: {file}")
                    except Exception as e:
                        print(f"Errore copia {file}: {e}")
                        errors += 1
    except Exception as e:
        print(f"Errore durante l'importazione: {e}")
        errors += 1

    return imported, errors


def main():
    """Loop principale del programma"""
    print("=== SD Card Photo Importer ===")
    print(f"Cartella destinazione: {DESTINATION_BASE}")
    if SD_DRIVE_LETTER:
        print(f"Unità SD fissa: {SD_DRIVE_LETTER}:\\")
    else:
        print("Modalità: auto-detect unità rimovibili")
    print("Monitoraggio schede SD in corso...")
    print("Premi CTRL+C per terminare\n")

    # Crea cartella base se non esiste
    os.makedirs(DESTINATION_BASE, exist_ok=True)

    # Monitora unità presenti
    known_drives = set(get_removable_drives())

    try:
        while True:
            current_drives = set(get_removable_drives())

            # Rileva nuove schede SD inserite
            new_drives = current_drives - known_drives

            if new_drives:
                for drive in new_drives:
                    print(f"\n🔵 Rilevata nuova scheda SD: {drive}")

                    # Conta foto
                    photo_count = count_photos_in_drive(drive)

                    if photo_count == 0:
                        print("Nessuna foto trovata nella scheda SD")
                        show_notification(
                            "SD Card Importer",
                            f"Nessuna foto trovata in {drive}"
                        )
                    else:
                        print(f"Trovate {photo_count} foto")

                        # Crea cartella con data e numero sequenziale
                        date_str = datetime.now().strftime("%Y-%m-%d")
                        dest_folder, folder_name = get_next_folder_number(DESTINATION_BASE, date_str)
                        os.makedirs(dest_folder, exist_ok=True)

                        print(f"Cartella destinazione: {folder_name}")

                        # Notifica inizio
                        show_notification(
                            "Importazione Iniziata",
                            f"Importazione di {photo_count} foto da {drive}\nin {folder_name}"
                        )

                        # Importa foto
                        start_time = time.time()
                        imported, errors = import_photos(drive, dest_folder)
                        elapsed = time.time() - start_time

                        # Notifica fine
                        if errors == 0:
                            msg = f"✅ {imported} foto importate con successo\nin {folder_name}\n({elapsed:.1f}s)"
                            print(f"\n{msg}")
                            show_notification("Importazione Completata", msg, timeout=10)
                        else:
                            msg = f"⚠️ {imported} foto importate, {errors} errori\nin {folder_name}"
                            print(f"\n{msg}")
                            show_notification("Importazione Completata con Errori", msg, timeout=10)

            # Aggiorna drives conosciute
            known_drives = current_drives

            # Aspetta prima del prossimo controllo
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\nProgramma terminato dall'utente")
        show_notification("SD Card Importer", "Monitoraggio terminato")


if __name__ == "__main__":
    main()
