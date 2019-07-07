import argparse
import ctypes
import datetime
import os
from pathlib import Path
import platform
import sys
import time
import uuid
import pyautogui

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)
parser.add_argument('-v', '--version', action='version',
                    version='%(prog)s 1.0', help="Show program's version number and exit.")
parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                    help='** = required')
parser.add_argument('-i', "--init", action='store_true',
    help='add -i to clear old keys from system and use key from usb if one exists')
parser.add_argument('-s', "--strong", action='store_true',
    help='add -s to disable unlocking without key')
args = parser.parse_args()

home = str(Path.home())
UUID = uuid.uuid4()
lockFile = Path(os.path.join(home, '.pyLock'))
keyLocCache = Path(os.path.join(home, '.keyLoc'))
keyLoc = None
keyFile = None
osname = platform.system()
lockCommandFile = Path(os.path.join(home, '.locCom'))
lockCommand = None


def init():
    global home
    global keyFile
    global keyLoc
    global keyLocCache
    global lockCommand
    global lockCommandFile
    global lockFile
    global osname
    global UUID

    if(args.init):
        print('Clearing old locker data..')
        if(os.path.exists(lockFile)):
            os.remove(lockFile)
        if(os.path.exists(keyLocCache)):
            os.remove(keyLocCache)
        if(os.path.exists(lockCommandFile)):
            os.remove(lockCommandFile)
        print('Done.')
        sys.exit()

    if(osname.startswith('Linux')):
        if not(os.path.exists(lockCommandFile)):
            print("Leave this blank to use winleft + L hotkey to lock screen")
            lockCommand = input('Please enter command to lock screen : ')
            lockCommandFileHandle = open(lockCommandFile, 'w')
            if(lockCommand == ''):
                lockCommandFileHandle.write('hotkey')
            else:
                lockCommandFileHandle.write(lockCommand)
        else:
            lockCommandFileHandle = open(lockCommandFile, 'r')
            lockCommand = lockCommandFileHandle.read()

    if not(os.path.exists(lockFile)):
        print('You will need to enter the path to your usb stick to be used as a physical key')
        keyLoc = input('Path usb root : ')
        keyFile = Path(os.path.join(keyLoc, '.pyLock'))
        if(os.path.exists(keyFile)):
            keyHandle = open(keyFile, 'r')
            UUID = keyHandle.read()
            keyLocHandle = open(keyLocCache, 'w')
            keyLocHandle.write(str(keyFile))
        else:
            keyHandle = open(keyFile, 'w')
            keyHandle.write(str(UUID))
            keyLocHandle = open(keyLocCache, 'w')
            keyLocHandle.write(str(keyFile))

        lockHandle = open(lockFile, 'w')
        lockHandle.write(str(UUID))
    else:
        lockHandle = open(lockFile, 'r')
        UUID = lockHandle.read()
        if(os.path.exists(keyLocCache)):
            keyLocHandle = open(keyLocCache, 'r')
            keyFile = keyLocHandle.read()



    if(keyFile is None):
        gettingKey = True
        print('key file found on machine but no key has been registered')

        while gettingKey:
            print('You will need to enter the path to your usb stick to be used as a physical key')
            keyLoc = input('Path usb root : ')
            keyHandle = open(keyFile, 'w')
            keyHandle.write(str(UUID))
            keyLocHandle = open(keyLocCache, 'w')
            keyLocHandle.write(str(keyFile))
            gettingKey = not (os.path.exists(keyFile))


def lock():

    if(osname == 'Windows'):
        ctypes.windll.user32.LockWorkStation()
    elif(osname.startswith('Linux')):
        if(lockCommand == 'hotkey'):
            pyautogui.hotkey('winleft', 'l')
        else:
            os.system(lockCommand)
    else:
        pyautogui.hotkey('ctrlleft', 'command', 'q')


def lockCheck():
    print('System is now secured by usb')
    global keyFile
    try:
        kh = open(keyFile, 'r')
        secure = kh.read() == str(UUID)
    except Exception as ex:
        print(ex)
        secure = False
        lock()
        print(f'locked @{datetime.datetime.now()}')

    while True:
        try:
            if(secure and not os.path.exists(keyFile)):
                kh.close()
                secure = False
                lock()
                print(f'locked @ {datetime.datetime.now()}')
            elif not(secure):
                if(os.path.exists(keyFile)):
                    kh = open(keyFile, 'r')
                    secure = kh.read() == str(UUID)
                    if(secure):
                        print(f'unlocked @ {datetime.datetime.now()}')
                    elif(args.strong):
                        time.sleep(1)
                        lock()
                elif(args.strong):
                    time.sleep(1)
                    lock()
        except Exception as ex:
            print(ex)
            secure = False
            lock()
            print(f'locked @ {datetime.datetime.now()}')


init()
lockCheck()
