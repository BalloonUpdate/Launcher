import subprocess
import sys
import time

from file import File

def main():

    exe = File(sys.executable)
    mainExe = '.minecraft\\updater\\NewUpdater.exe' if exe.parent.name != '.minecraft' else 'updater\\NewUpdater.exe'
    signalFile = File('.minecraft\\updater.signal' if exe.parent.name != '.minecraft' else 'updater.signal')


    def check():
        count = 60 * 5
        while True:
            result2 = subprocess.check_output('tasklist.exe', shell=True).decode('gb2312')

            found = False
            for line in result2.splitlines():
                if 'NewUpdater.exe' in line:
                    found = True

            if not found:
                break

            count -= 1
            if count <= 0:
                exit()

            print('holding.. '+str(int(count*5)/10))
            time.sleep(0.2)


    statement = f'cd /D "{exe.parent.windowsPath}" && start {mainExe}'
    subprocess.call(statement, shell=True)
    time.sleep(1)
    check()

    if signalFile.exists:  # 正在进行热更新
        signalFile.delete()

        print('waiting for hotupdating')
        time.sleep(3)

        statement = f'cd /D "{exe.parent.windowsPath}" && start {mainExe}'
        subprocess.call(statement, shell=True)
        time.sleep(1)
        check()


if __name__ == '__main__':
    try:
        main()
    except BaseException as e:
        pass
