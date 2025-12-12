"""
SD Card Photo Importer - Print Manager (PySide6)
Gestione stampa con spooler interno
"""

import os
import time
import json
import threading
from datetime import datetime
from PIL import Image, ImageWin
import win32print
import win32ui
import pywintypes
from win32.lib import win32con as pywintypes_con
from plyer import notification

from config import PRINT_LOG_FILE


class PrintManager:
    """Gestisce le operazioni di stampa con spooler interno"""

    def __init__(self, parent=None):
        self.parent = parent
        self.printer_var = None

    def get_available_printers(self):
        """Restituisce lista di stampanti disponibili"""
        try:
            return [printer[2] for printer in win32print.EnumPrinters(2)]
        except Exception as e:
            print(f"Errore caricamento stampanti: {e}")
            return []

    def get_default_printer(self):
        """Restituisce stampante predefinita"""
        try:
            return win32print.GetDefaultPrinter()
        except:
            return None

    def wait_for_print_job_completion(self, printer_name, job_id, timeout=300):
        """Monitora lo stato di un job di stampa fino al completamento"""
        try:
            hPrinter = win32print.OpenPrinter(printer_name)
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    jobs = win32print.EnumJobs(hPrinter, 0, 100)
                    job_found = False

                    for job in jobs:
                        if job['JobId'] == job_id:
                            job_found = True
                            status = job['Status']

                            if status & win32print.JOB_STATUS_ERROR:
                                win32print.ClosePrinter(hPrinter)
                                return False

                            if status & win32print.JOB_STATUS_DELETED:
                                win32print.ClosePrinter(hPrinter)
                                return False
                            break

                    if not job_found:
                        win32print.ClosePrinter(hPrinter)
                        return True

                    time.sleep(2)

                except Exception as e:
                    print(f"[SPOOLER] Errore controllo job: {e}")
                    time.sleep(2)

            win32print.ClosePrinter(hPrinter)
            return False

        except Exception as e:
            print(f"[SPOOLER] Errore apertura stampante: {e}")
            return False

    def print_photos_with_spooler(self, photos, printer_name, photo_format,
                                   progress_callback=None, status_callback=None,
                                   completion_callback=None):
        """Stampa foto con spooler interno"""
        def print_thread():
            from PySide6.QtCore import QMetaObject, Qt, Q_ARG

            try:
                total_prints = sum(copies for _, copies in photos)

                if status_callback:
                    try:
                        status_callback(f"Preparazione stampa di {total_prints} fogli...")
                    except:
                        pass

                print_count = 0
                for photo_path, copies in photos:
                    for copy_num in range(copies):
                        print_count += 1
                        if status_callback:
                            try:
                                status_callback(f"Stampa {print_count}/{total_prints}...")
                            except:
                                pass

                        try:
                            hDC = win32ui.CreateDC()
                            hDC.CreatePrinterDC(printer_name)

                            dpi_x = hDC.GetDeviceCaps(pywintypes_con.LOGPIXELSX)
                            dpi_y = hDC.GetDeviceCaps(pywintypes_con.LOGPIXELSY)
                            page_width = hDC.GetDeviceCaps(pywintypes_con.HORZRES)
                            page_height = hDC.GetDeviceCaps(pywintypes_con.VERTRES)

                            hDC.StartDoc(f"Foto {print_count}")
                            hDC.StartPage()

                            img = Image.open(photo_path)
                            if img.mode != 'RGB':
                                img = img.convert('RGB')

                            img_ratio = img.width / img.height
                            page_ratio = page_width / page_height

                            if img_ratio > page_ratio:
                                target_w = page_width
                                target_h = int(page_width / img_ratio)
                            else:
                                target_h = page_height
                                target_w = int(page_height * img_ratio)

                            x = (page_width - target_w) // 2
                            y = (page_height - target_h) // 2

                            img_resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                            temp_bmp = os.path.join(os.path.dirname(photo_path), f"temp_print_{print_count}.bmp")
                            img_resized.save(temp_bmp, "BMP")

                            bmp = Image.open(temp_bmp)
                            dib = ImageWin.Dib(bmp)
                            dib.draw(hDC.GetHandleOutput(), (x, y, x + target_w, y + target_h))

                            try:
                                os.remove(temp_bmp)
                            except:
                                pass

                            hDC.EndPage()
                            hDC.EndDoc()
                            hDC.DeleteDC()

                            print(f"[SPOOLER] Stampa {print_count} inviata")

                        except Exception as e:
                            print(f"[SPOOLER] Errore: {e}")

                        if progress_callback:
                            try:
                                progress_callback(print_count)
                            except:
                                pass

                if status_callback:
                    try:
                        status_callback(f"Completato! {total_prints} fogli stampati")
                    except:
                        pass

                # Log stampa
                self.log_print_job(total_prints, photo_format)

                notification.notify(
                    title="Stampa Completata",
                    message=f"{total_prints} fogli inviati alla stampante",
                    app_name="SD Card Importer",
                    timeout=5
                )

                if completion_callback:
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(0, lambda: completion_callback(True))

            except Exception as e:
                print(f"[SPOOLER] Errore generale: {e}")
                if status_callback:
                    try:
                        status_callback(f"Errore: {str(e)}")
                    except:
                        pass
                if completion_callback:
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(0, lambda: completion_callback(False))

        threading.Thread(target=print_thread, daemon=True).start()

    def log_print_job(self, num_photos, layout):
        """Registra stampa nel log"""
        now = datetime.now()

        log_entry = {
            'date': now.strftime("%Y-%m-%d"),
            'time': now.strftime("%H:%M:%S"),
            'num_photos': num_photos,
            'layout': layout,
            'printer': self.printer_var.get() if self.printer_var else "Sconosciuta"
        }

        if os.path.exists(PRINT_LOG_FILE):
            with open(PRINT_LOG_FILE, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        else:
            log_data = {'prints': []}

        log_data['prints'].append(log_entry)

        with open(PRINT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
