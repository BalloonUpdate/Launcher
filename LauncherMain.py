import subprocess
import sys
import time
import traceback

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

    def check(targetState=True, timeout=60):
        count = timeout  # seconds
        while True:
            result2 = subprocess.check_output('tasklist.exe', shell=True).decode('gb2312')

            found = False
            for line in result2.splitlines():
                if 'UpdaterHotupdatePackage' in line:  # UpdaterHotupdatePackage.exe
                    found = True

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
    check(False, 15)  # 等待程序启动15s内
    check(timeout=3*60)

    if hotupdateSignalFile.exists:  # 正在进行热更新
        hotupdateSignalFile.delete()

        print('prepare to hotupdate')
        time.sleep(3)

        subprocess.call(statement, shell=True)
        check(False, 15)  # 等待程序启动
        check(timeout=3*60)

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
