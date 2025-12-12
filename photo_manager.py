"""
SD Card Photo Importer - Photo Manager
Gestione importazione e caricamento foto
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import SD_DRIVE_LETTER, DESTINATION_BASE, PHOTO_EXTENSIONS


class PhotoManager:
    """Gestisce operazioni su foto"""

    @staticmethod
    def find_photos_on_sd():
        """
        Trova tutte le foto sulla scheda SD

        Returns:
            list: Lista di percorsi completi delle foto trovate
        """
        if not SD_DRIVE_LETTER:
            raise ValueError("Nessuna unità SD configurata")

        drive = f"{SD_DRIVE_LETTER.upper()}:\\"
        if not os.path.exists(drive):
            raise FileNotFoundError("SD card non trovata")

        photo_files = []
        for root, dirs, files in os.walk(drive):
            for file in files:
                if Path(file).suffix.lower() in {'.jpg', '.jpeg', '.png', '.heic', '.raw', '.cr2', '.nef', '.arw'}:
                    photo_files.append(os.path.join(root, file))

        return photo_files

    @staticmethod
    def create_destination_folder():
        """
        Crea cartella di destinazione con data e numero progressivo

        Returns:
            str: Percorso della cartella creata
        """
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
        return dest_folder

    @staticmethod
    def process_single_photo(source_path, dest_folder, cut_mode=False):
        """
        Copia o sposta una singola foto

        Args:
            source_path: Percorso file sorgente
            dest_folder: Cartella destinazione
            cut_mode: Se True sposta, altrimenti copia

        Returns:
            tuple: (success: bool, filename: str, error: str or None)
        """
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
            if cut_mode:
                shutil.move(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)
            return True, filename, None
        except Exception as e:
            return False, filename, str(e)

    @staticmethod
    def import_photos_batch(photo_files, dest_folder, cut_mode=False,
                           progress_callback=None, max_workers=4):
        """
        Importa un batch di foto con multi-threading

        Args:
            photo_files: Lista di file sorgente
            dest_folder: Cartella destinazione
            cut_mode: Se True sposta, altrimenti copia
            progress_callback: Funzione chiamata per ogni foto processata
                              (completed: int, errors: int, filename: str, total: int)
            max_workers: Numero massimo di thread paralleli

        Returns:
            tuple: (completed: int, errors: int, error_list: list)
        """
        completed = 0
        errors = 0
        error_list = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Invia tutti i task
            future_to_photo = {
                executor.submit(PhotoManager.process_single_photo, photo, dest_folder, cut_mode): photo
                for photo in photo_files
            }

            # Processa i risultati man mano che completano
            for future in as_completed(future_to_photo):
                success, filename, error = future.result()

                if success:
                    completed += 1
                else:
                    errors += 1
                    error_list.append((filename, error))

                # Callback progresso
                if progress_callback:
                    progress_callback(completed, errors, filename, len(photo_files))

        return completed, errors, error_list

    @staticmethod
    def load_photos_from_folder(folder_path):
        """
        Carica lista di foto da una cartella

        Args:
            folder_path: Percorso cartella

        Returns:
            list: Lista di percorsi completi delle foto
        """
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Cartella non trovata: {folder_path}")

        photos = []
        try:
            for file in os.listdir(folder_path):
                filepath = os.path.join(folder_path, file)
                if os.path.isfile(filepath) and Path(file).suffix.lower() in {'.jpg', '.jpeg', '.png', '.heic'}:
                    photos.append(filepath)
        except Exception as e:
            raise RuntimeError(f"Errore lettura cartella: {e}")

        return sorted(photos)

    @staticmethod
    def verify_files_before_delete(source_folder, dest_folder):
        """
        Verifica che tutti i file siano stati copiati correttamente prima di cancellarli

        Args:
            source_folder: Cartella sorgente (es. SD card)
            dest_folder: Cartella destinazione

        Returns:
            tuple: (verified: bool, missing_files: list, message: str)
        """
        source_files = []
        dest_files = []

        # Raccogli tutti i file dalla sorgente
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if Path(file).suffix.lower() in {'.jpg', '.jpeg', '.png', '.heic', '.raw', '.cr2', '.nef', '.arw'}:
                    source_files.append(file)

        # Raccogli tutti i file dalla destinazione
        for root, dirs, files in os.walk(dest_folder):
            for file in files:
                dest_files.append(file)

        # Verifica che tutti i file sorgente siano presenti
        missing_files = []
        for src_file in source_files:
            # Verifica anche con suffisso _1, _2, ecc. per i duplicati
            base_name = Path(src_file).stem
            found = False
            for dest_file in dest_files:
                if dest_file.startswith(base_name):
                    found = True
                    break
            if not found:
                missing_files.append(src_file)

        if missing_files:
            return False, missing_files, f"Mancano {len(missing_files)} file nella destinazione"

        # Verifica anche le dimensioni
        size_mismatch = []
        for src_file in source_files:
            src_path = None
            for root, dirs, files in os.walk(source_folder):
                if src_file in files:
                    src_path = os.path.join(root, src_file)
                    break

            if src_path:
                src_size = os.path.getsize(src_path)
                # Trova il file corrispondente nella destinazione
                dest_path = None
                base_name = Path(src_file).stem
                for root, dirs, files in os.walk(dest_folder):
                    for file in files:
                        if file.startswith(base_name):
                            dest_path = os.path.join(root, file)
                            break
                    if dest_path:
                        break

                if dest_path:
                    dest_size = os.path.getsize(dest_path)
                    if src_size != dest_size:
                        size_mismatch.append((src_file, src_size, dest_size))

        if size_mismatch:
            return False, size_mismatch, f"Dimensioni non corrispondenti per {len(size_mismatch)} file"

        return True, [], "Tutti i file verificati correttamente"

    @staticmethod
    def safe_delete_from_sd(verification_result):
        """
        Cancella i file dalla SD solo dopo verifica

        Args:
            verification_result: Risultato di verify_files_before_delete

        Returns:
            tuple: (success: bool, message: str)
        """
        verified, missing, message = verification_result

        if not verified:
            return False, f"Impossibile cancellare: {message}"

        # TODO: Implementare cancellazione sicura
        # Per ora restituisce solo il messaggio
        return True, "File verificati, cancellazione sicura abilitata"
