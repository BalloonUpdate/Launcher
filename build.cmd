@echo off
pyinstaller --noconfirm --version-file version-file.txt -i icon.ico -w -F -n Launcher LauncherMain.py
echo Build finished!