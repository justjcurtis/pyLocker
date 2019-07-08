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
    'strongAccept': False
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


def strongAcceptWarning():
    global lockSettings
    if(args.strong):
        if(not lockSettings['strongAccept']):
            print('!!!WARNING!!!')
            print('strong locking is experimental at this time')
            print('using strong locking can be dangerous')
            print('you may permanently lock yourself out of your machine')
            print('please ensure you know what you are doing')
            if(osname.startswith('Linux')):
                print('please ensure you have set your machine to automount your usb key')
            print('')
            getting = True
            while getting:
                proceed = input('type "lock" to proceed')
                if(proceed != 'lock' or proceed != '"lock"'):
                    sys.exit()
                else:
                    lockSettings['strongAccept'] = True
                    saveSettings(lockSettings)
            proceed = input('Press enter to proceed with strong locking enabled or ctrl+c to exit')


def setLockCommand():
    global lockSettings
    if(lockSettings['lockCommand'] is None):
        print("Leave this blank to use winleft + L hotkey to lock screen")
        lockCommand = input('Please enter command to lock screen : ')
        if(lockCommand == ''):
            lockSettings['lockCommand'] = 'hotkey'
        else:
            lockSettings['lockCommand'] = lockCommand

    saveSettings(lockSettings)


def clearOldData():
    print('Clearing old locker data..')
    if(os.path.exists(lockFile)):
        os.remove(lockFile)
    print('Done.')
    sys.exit()


def init():
    global lockFile
    global lockSettings

    if(args.init):
        clearOldData()

    lockSettings = getSettings()
    saveSettings(lockSettings)

    if(osname.startswith('Linux')):
        setLockCommand()

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
