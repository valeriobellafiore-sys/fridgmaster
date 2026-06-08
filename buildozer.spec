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
# Questa versione specifica è nota per includere correttamente aidl
android.sdk_build_tools_version = 33.0.1
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
