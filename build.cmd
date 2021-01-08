@echo off
pyinstaller --noconfirm --version-file version-file.txt -i icon.ico -w -F -n NULauncher LauncherMain.py %1
echo Build finished!