import argparse
import ctypes
import datetime
import json
import os
from pathlib import Path
import platform
import sys
import uuid
import pyautogui

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)
parser.add_argument('-v', '--version', action='version',
                    version='%(prog)s 1.0', help="Show program's version number and exit.")
parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                    help='** = required')
parser.add_argument('-i', "--init", action='store_true',
    help='add -i to clear old keys from system and use key from usb if one exists')
parser.add_argument('-a', "--add_key", action='store_true',
    help='add -a to add another key using lock files already on machine')
parser.add_argument('-r', "--remove_key", action='store_true',
    help='add -r to remove a key')
parser.add_argument('-lc', "--lock_command", action='store_true',
    help='add -lc to set lock command (linux only)')
args = parser.parse_args()
args.stong = False

home = str(Path.home())
osname = platform.system()

lockFile = Path(os.path.join(home, '.pyLocker'))
lockSettings = None
defaultLockSettings = {
    'uuid': str(uuid.uuid4()),
    'keyFile': None,
    'lockCommand': None,
}


def getSettings():
    if(os.path.exists(lockFile)):
        lockFileHandle = open(lockFile, 'r')
        settings = lockFileHandle.read()
        return json.loads(settings)
    else:
        return defaultLockSettings


def saveSettings(settings):
    lockFileHandle = open(lockFile, 'w')
    lockFileHandle.write(json.dumps(settings))


def setLockCommand(force):
    global lockSettings
    if(lockSettings['lockCommand'] is None or force):
        print("Leave this blank to use winleft + L hotkey to lock screen")
        lockCommand = input('Please enter command to lock screen : ')
        if(lockCommand == ''):
            lockSettings['lockCommand'] = 'hotkey'
        else:
            lockSettings['lockCommand'] = lockCommand

    saveSettings(lockSettings)
    if(force):
        sys.exit()


def clearOldData():
    print('Clearing old locker data..')
    if(os.path.exists(lockFile)):
        os.remove(lockFile)
    print('Done.')
    sys.exit()


def keysPresent(keyFiles):
    results = []
    for keyFile in keyFiles:
        if(os.path.exists(keyFile)):
            results.append(keyFile)
    return results


def gotSecureKey():
    try:
        keyFiles = keysPresent(lockSettings['keyFile'].split(','))
        for keyFile in keyFiles:
            kh = open(keyFile, 'r')
            secure = kh.read() == lockSettings['uuid']
            if(secure):
                return True
        return False
    except Exception as ex:
        print(ex)
        return False


def init():
    global lockFile
    global lockSettings

    if(args.init):
        clearOldData()

    lockSettings = getSettings()
    saveSettings(lockSettings)

    if(osname.startswith('Linux')):
        setLockCommand(args.lock_command)

    if (lockSettings['keyFile'] is None):
        print('Starting initial setup')
        print('You will need to enter the path to your usb stick to be used as a physical key')
        gotKey = False
        while not gotKey:
            keyRoot = input('Path usb root : ')
            lockSettings['keyFile'] = os.path.join(keyRoot, '.pyLock')
            if(os.path.exists(lockSettings['keyFile'])):
                keyHandle = open(lockSettings['keyFile'], 'r')
                lockSettings['uuid'] = keyHandle.read()
            else:
                keyHandle = open(lockSettings['keyFile'], 'w')
                keyHandle.write(lockSettings['uuid'])

            gotKey = os.path.exists(lockSettings['keyFile'])

        saveSettings(lockSettings)

    elif(args.add_key):
        gotKey = False
        while not gotKey:
            keyRoot = input('Path usb root : ')
            newKeyFile = os.path.join(keyRoot, '.pyLock')
            keyHandle = open(newKeyFile, 'w')
            keyHandle.write(lockSettings['uuid'])

            gotKey = os.path.exists(newKeyFile)
        lockSettings['keyFile'] += f',{newKeyFile}'
        saveSettings(lockSettings)
        sys.exit()
    elif(args.remove_key):
        keyFiles = lockSettings['keyFile'].split(',')
        if(len(keyFiles)<2):
            print('You only have 1 key')
            print('You cannot have 0 keys')
            print('if you want to remove everything then use pyLocker with -i argument')
        else:
            proceed = input('remove all keys except ones currently inserted into machine (yes/no) : ')
            if(proceed == 'yes'):
                presentKeys = keysPresent(keyFiles)
                if(len(keyFiles)==len(presentKeys)):
                    print('You have insterted all keys associated with this machine')
                    print('You cannot have 0 keys, and therfore cannot remove them all')
                    print('if you want to remove everything then use pyLocker with -i argument')
                elif(len(presentKeys) < 1):
                    print('you must insert at least 1 valid key into this machine to remove all others')
                else:
                    lockSettings['keyFile'] = ','.join(presentKeys)
                    print(f'{len(keyFiles) - len(presentKeys)} removed')
                    print(f'{len(presentKeys)} remain registered')
        saveSettings(lockSettings)
        sys.exit()


def lock():
    if(osname == 'Windows'):
        ctypes.windll.user32.LockWorkStation()
    elif(osname.startswith('Linux')):
        if(lockSettings['lockCommand'] == 'hotkey'):
            pyautogui.hotkey('winleft', 'l')
        else:
            os.system(lockSettings['lockCommand'])
    else:
        pyautogui.hotkey('ctrlleft', 'command', 'q')


def lockCheck():
    if(lockSettings['keyFile'] is not None):
        print('System is now secured by usb')
        secure = gotSecureKey()
        if(not secure):
            lock()
        while True:
            try:
                if(secure and not gotSecureKey()):
                    secure = False
                    lock()
                    print(f'locked @ {datetime.datetime.now()}')
                elif not(secure):
                    secure = gotSecureKey()
                    if(secure):
                        print(f'unlocked @ {datetime.datetime.now()}')
            except Exception as ex:
                print(ex)
                secure = False
                lock()
                print(f'locked @ {datetime.datetime.now()}')
    else:
        print('No key registered')
        print('try running pyLocker again')
        print('if this problem continues try running pyLocker with -i to clear old data')
        input('press enter to exit')
        sys.exit()


init()
lockCheck()
