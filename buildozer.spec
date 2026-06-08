[app]
# (str) Titolo dell'applicazione
title = Fridgmaster

# (str) Nome del pacchetto
package.name = fridgmaster

# (str) Dominio del pacchetto
package.domain = org.test

# (str) Cartella sorgente del progetto
source.dir = .

# (list) Estensioni dei file da includere
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Versione
version = 0.1

# (list) Requisiti
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

# (str) Versione SDK Build-Tools (Fissata alla 33.0.1 per includere AIDL correttamente)
android.sdk_build_tools_version = 33.0.1

# (list) Permessi necessari
android.permissions = INTERNET

[buildozer]
# (int) Livello di log
log_level = 2

# (int) Opzioni di compilazione
warn_on_root = 1
