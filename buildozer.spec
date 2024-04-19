[app]
title = connector
package.name = connector
package.domain = com.connector
source.dir = .
#source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 0.1
requirements = python3,kivy
orientation = all
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 1
#android.presplash_color = #1d3b3e
android.permissions = WRITE_EXTERNAL_STORAGE
android.api = 19
android.minapi = 13
android.sdk = 23
#private = False
android.ndk_path = /home/kivy/Android/crystax-ndk-10.3.2/
android.arch = armeabi-v7a
p4a.source_dir = /home/kivy/Repos/python-for-android/
[buildozer]
log_level = 2
warn_on_root = 1