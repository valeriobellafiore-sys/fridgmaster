[app]
# (str) Titolo dell'applicazione
title = Fridgmaster

# (str) Nome del pacchetto
package.name = fridgmaster

# (str) Dominio del pacchetto
package.domain = org.test

# (str) Cartella sorgente del progetto (. indica la cartella corrente)
source.dir = .

# (list) Estensioni dei file da includere
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Versione
version = 0.1

# (list) Requisiti (aggiungi qui eventuali librerie extra, es: requests, pillow)
requirements = python3,kivy

# (str) Orientamento
orientation = portrait

# (bool) Schermo intero
fullscreen = 0

# (int) API Android target
android.api = 33

# (int) API Android minima supportata
android.minapi = 21

# (str) Versione NDK
android.ndk = 25b

# (str) Versione SDK Build-Tools
android.sdk_build_tools_version = 34.0.0

# (list) Permessi necessari
android.permissions = INTERNET

[buildozer]
# (int) Livello di log (0 = critico, 1 = avviso, 2 = info, 3 = debug)
log_level = 2

# (int) Opzioni di compilazione
warn_on_root = 1
