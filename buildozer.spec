[app]
title = Fridgmaster
package.name = fridgmaster
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 25b
android.permissions = INTERNET
# Rimuoviamo qualsiasi riferimento a build-tools qui, 
# lasciamo che sia buildozer a usare i predefiniti dell'SDK
