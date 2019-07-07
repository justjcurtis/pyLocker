import os
from pathlib import Path
import platform
import uuid
import pyautogui

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
    if(osname.startswith('Linux')):
        if not(os.path.exists(lockCommandFile)):
            lockCommand = input('Please enter command to lock screen : ')
            lockCommandFileHandle = open(lockCommandFile, 'w')
            lockCommandFileHandle.write(lockCommand)
        else:
            lockCommandFileHandle = open(lockCommandFile, 'r')
            lockCommand = lockCommandFileHandle.read()

    if not(os.path.exists(lockFile)):
        lockHandle = open(lockFile, 'w')
        lockHandle.write(str(UUID))
        print('You will need to enter the path to your usb stick to be used as a physical key')
        keyLoc = input('Path usb root : ')
        keyFile = Path(os.path.join(keyLoc, '.pyLock'))
        keyHandle = open(keyFile, 'w')
        keyHandle.write(str(UUID))
        keyLocHandle = open(keyLocCache, 'w')
        keyLocHandle.write(str(keyFile))
    else:
        lockHandle = open(lockFile, 'r')
        UUID = lockHandle.read()
        if(os.path.exists(keyLocCache)):
            keyLocHandle = open(keyLocCache, 'r')
            keyFile = keyLocHandle.read()



    if(keyFile is None):
        gettingKey = True

        while gettingKey:
            keyFile = input('Path to key file : ')
            gettingKey = not (os.path.exists(keyFile))


def lock():
    if(osname == 'Windows'):
        pyautogui.hotkey('winleft', 'l')
    elif(osname.startswith('Linux')):
        os.system(lockCommand)
    else:
        pyautogui.hotkey('ctrlleft', 'command', 'q')



def lockCheck():
    global keyFile
    kh = open(keyFile, 'r')
    secure = kh.read() == str(UUID)
    while True:
        if(secure and not os.path.exists(keyFile)):
            kh.close()
            secure = False
            print('lock')
            lock()
        elif not(secure):
            if(os.path.exists(keyFile)):
                kh = open(keyFile, 'r')
                secure = kh.read() == str(UUID)
                if(secure):
                    print('unlock')


init()
lockCheck()
