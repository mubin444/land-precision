[app]

# (str) Title of your application
title = Precision Land Calculator

# (str) Package name
package.name = landprecision

# (str) Package domain
package.domain = org.landprecision

# (str) Source code directory
source.dir = .

# (str) Main Python file
source.main = main.py

# (list) Source files to include
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf

# (str) Version
version = 1.0

# (list) Python dependencies
requirements = python3,kivy,pillow

# (str) Orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 0

# (str) Android API
android.api = 35

# (str) Android minimum API
android.minapi = 21

# (str) Android architecture
android.arch = arm64-v8a

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (bool) Android backup
android.allow_backup = True

# (str) Android app theme
android.apptheme = "@android:style/Theme.Material.Light.NoActionBar"

# (list) Android permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (str) Presplash
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon
# icon.filename = %(source.dir)s/data/icon.png


[buildozer]

# (str) Log level
log_level = 2

# (str) Warn if running as root
warn_on_root = 1
