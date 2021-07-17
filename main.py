import subprocess
import sys
import time
import traceback

import psutil
import win32api
import win32con

from file import File

inDev = not getattr(sys, 'frozen', False)
mainProgramName = 'Project1-attached.exe'
wrapperName = 'Project1.exe'


def get_basename(filename: str):
    if '.' not in filename:
        return filename
    return filename[:filename.rfind('.')]


def single_instance():
    exe = File(sys.executable)
    kill = []
    for pid_ in psutil.pids():
        if psutil.pid_exists(pid_):
            process = psutil.Process(pid_)
            if process.name() in [exe.name]:
                kill += [process]
            if process.name() in [mainProgramName]:
                process.kill()
    if len(kill) >= 4:
        kill = sorted(kill, key=lambda el: el.create_time())
        for i in kill:
            print(i.name() + ': ' + str(i.create_time()))
        kill[0].kill()
        kill[1].kill()


def get_prefix():
    exe_dir = File(sys.executable).parent
    if '.minecraft' in exe_dir:
        prefix = exe_dir
    elif '.minecraft' in exe_dir.parent:
        prefix = exe_dir.parent
    elif '.minecraft' in exe_dir.parent.parent:
        prefix = exe_dir.parent.parent
    else:
        raise Exception('文件放置位置不正确，只能放置.minecraft旁边，.minecraft/下，或者.minecraft/updater/里')
    return prefix.append('.minecraft/updater')


def check_run_state(runningStateExpected: bool, timeout=60):
    count = timeout  # seconds
    while True:
        isRunning = mainProgramName in [
            psutil.Process(pid=pid).name()
            for pid in psutil.pids()
            if psutil.pid_exists(pid)
        ]
        if isRunning == runningStateExpected:
            break

        count -= 1
        if count <= 0:
            raise Exception('主程序未能及时' + ('启动' if runningStateExpected else '退出'))

        print('check: ' + str(int(count)) + str())
        time.sleep(1)


def start_main_program(mainProgram: File, workDir: File):
    return subprocess.call([mainProgram.path, *sys.argv[1:]], shell=False, cwd=workDir.path)


def main():
    single_instance()

    prefix = get_prefix()
    mainProgramFile = prefix.append(mainProgramName)

    if not mainProgramFile.exists:
        raise FileNotFoundError('找不到主程序: '+mainProgramFile.windowsPath)

    # 启动主程序
    exitcode = start_main_program(mainProgramFile, prefix.parent.parent)

    print('code: '+str(exitcode))

    if exitcode == 2:  # 刚进行了升级，需要重新打包然后重启
        # 获取临时路径
        repackageFile = prefix.append('repackage.txt')
        electronDir = File(repackageFile.content)
        repackageFile.delete()

        if not inDev:
            # 重新打包
            # progDir = File(getattr(sys, '_MEIPASS', ''))
            wrapperFile = electronDir.append(wrapperName)
            tempDir = prefix.append('upgrade-temp')
            tempDir.mkdirs()
            newWrapper = tempDir.append('wrapper.exe')
            wrapperFile.copyTo(newWrapper)

            ec = subprocess.call(['start', '/wait', newWrapper.path, '--attach', electronDir.path], shell=True)
            # ec = subprocess.call([newWrapper.path, '--attach', electronDir.path], shell=True)
            if ec != 0:
                raise Exception('打包程序出现错误: '+str(ec))

            wrapped = newWrapper.parent.append(get_basename(newWrapper.name)+'-attached.exe')
            mainProgramFile.delete()
            wrapped.copyTo(mainProgramFile)

            # 重启
            exitcode = start_main_program(mainProgramFile, prefix.parent.parent)
            if exitcode == 1:
                raise Exception('主程序出现错误.: ' + exitcode)

    elif exitcode == 1:
        raise Exception('主程序出现错误: ' + exitcode)


if __name__ == '__main__':
    try:
        main()
    except SystemExit as e:
        raise e
    except BaseException as e:
        print(traceback.format_exc())
        win32api.MessageBox(0, str(e), '发生错误', win32con.MB_ICONERROR)
