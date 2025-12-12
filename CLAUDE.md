In questo file ci sono tutte le informazioni che devi tenere a mente prima di iniziare a lavorare.

- Il progetto deve essere prestante ed affidabile e ridurre perdite di tempo e di dati ( ancora non si è verificato per fortuna )
- Se ti chiedo una modifica è importantissimo che venga eseguita sfruttando il minor numero possibile di token.
- Voglio risposte brevi per i cambiamenti apportati e spesso basta soltanto "Fatto."
- Se una mofifica richiede attenzione o chiarimenti allora puoi formulare le risposte in maniera più verbosa.
- Se una modifica richiede troppo tempo dobbiamo trovare una "via di mezzo" per poter fare test e magari limare ancora per cercare la perfezione.

Strategie:

  1. Prima di modificare: chiedo sempre conferma su scope esatto
  2. Grep invece di Read: cerco solo le linee necessarie
  3. Batch Edit: raggruppo modifiche simili in 1 Edit invece di tante
  4. Modifiche incrementali: una funzionalità alla volta, testo solo se chiedi
  5. Zero letture inutili: leggo solo se strettamente necessario

  Esempio workflow ottimizzato:
  - Tu: "Cambia colore bottone X in rosso"
  - Io: Grep per trovare la riga esatta → Edit singola → "Fatto."

  Invece di leggere 950 righe + 15 Edit come questo.

  Esempio workflow ottimizzato:
  - Utente: "Cambia colore bottone X in rosso"
  - Claude: Grep per trovare la riga esatta → Edit singola → "Fatto."

card/
  ├── sd_card_importer_qt_main.py (950 righe) # Main PySide6
  ├── config.py                                # Configurazioni
  ├── photo_manager.py                         # Gestione foto
  ├── print_manager_qt.py                      # Gestione stampe Qt
  ├── secondary_window_qt.py                   # Monitor secondario Qt
  ├── professional_features_qt.py              # UI professionale Qt

Il file principale che contiene la logica è sd_card_importer_qt_main.py

