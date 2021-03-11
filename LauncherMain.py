import subprocess
import sys
import time
import traceback

import psutil

from ci.version import productVersion
from file import File


def main():
    parentDir = File(sys.executable).parent
    prefix = ('.minecraft\\' if '.minecraft' in parentDir else '') + ''
    packagePath = prefix + 'updater\\UpdaterHotupdatePackage.exe'
    hotupdateSignalPath = prefix + 'updater\\updater.hotupdate.signal'
    errorSignalPath = prefix + 'updater\\updater.error.signal'

    packageFile = File(packagePath)
    hotupdateSignalFile = File(hotupdateSignalPath)
    errorSignalFile = File(errorSignalPath)

    # 清理
    hotupdateSignalFile.delete()
    errorSignalFile.delete()

    # 单实例模式
    kill = []
    for pid_ in psutil.pids():
        if psutil.pid_exists(pid_):
            process = psutil.Process(pid_)
            if process.name() in ['UpdaterClient-'+productVersion+'.exe']:
                kill += [process]
            if process.name() in ['UpdaterHotupdatePackage.exe']:
                process.kill()
    if len(kill) >= 4:
        kill = sorted(kill, key=lambda el: el.create_time())
        for i in kill:
            print(i.name() + ': ' + str(i.create_time()))
        kill[0].kill()
        kill[1].kill()

    def check(targetState=True, timeout=60):
        count = timeout  # seconds
        while True:
            processes = [
                psutil.Process(pid=pid).name()
                for pid in psutil.pids()
                if psutil.pid_exists(pid)
            ]
            found = 'UpdaterHotupdatePackage.exe' in processes

            if not found == targetState:
                break

            count -= 1
            if count <= 0:
                sys.exit()

            print('count down of force exiting '+str(int(count))+('(reversed)' if not targetState else ''))
            time.sleep(1)

    if not packageFile.exists:
        print('file not found: '+packageFile.windowsPath)
        sys.exit(1)

    statement = f'cd /D "{packageFile.parent.windowsPath}" && start {packageFile.name}'
    print(statement)
    subprocess.call(statement, shell=True)
    check(False, 5)  # 等待程序启动5s内
    check(timeout=6*60)

    if hotupdateSignalFile.exists:  # 正在进行热更新
        hotupdateSignalFile.delete()

        print('prepare to hotupdate')
        time.sleep(3)

        subprocess.call(statement, shell=True)
        check(False, 5)  # 等待程序启动
        check(timeout=6*60)

    if errorSignalFile.exists:  # 程序发生了错误
        errorSignalFile.delete()

        print('something went wrong')

        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except SystemExit as e:
        raise e
    except BaseException:
        print(traceback.format_exc())
        File('updater.error1.log').content = traceback.format_exc()
