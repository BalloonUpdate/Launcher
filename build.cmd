@echo off

python version.py > temp.txt
set /p filename=< temp.txt
del temp.txt

echo Build for %filename%

pyinstaller --noconfirm --version-file version-file.txt -i icon.ico -c -F -n %filename% LauncherMain.py %1
echo Build finished!