[app]

title = VGX SPACE 8
package.name = vgxspace8
package.domain = org.kiyyofficial

source.dir = .
source.include_exts = py,png,jpg,jpeg,gif,ttf,dat

version = 1.0.0

requirements = python3,kivy==2.2.0

orientation = landscape
osx.python_version = 3
osx.kivy_version = 2.0.0

fullscreen = 0

icon.filename = icon.png

android.permissions = INTERNET, ACCESS_NETWORK_STATE, WAKE_LOCK

android.api = 31
android.minapi = 21
android.ndk = 23b
android.sdk = 30

android.gradle_dependencies = 'com.android.support:support-annotations:28.0.0'

[buildozer]

log_level = 2
warn_on_root = 1
