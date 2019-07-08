# pyLocker 2.6

## Description
pyLocker is a python script which enables you to lock your machine with a usb 'key'.  
Whenever you remove a registered key from your machine; it will lock immediately.  

pyLocker supports Windows, OSX and Linux and requires python 3 and pyautogui.

## Optional Arguments

| Argument name |     Example usage     |                                                 Effect |
| :------------ | :-------------------: | -----------------------------------------------------: |
| help          |     -h or --help      |                        displays all optional arguments |
| version       |    -v or --version    |                        displays current version number |
| init          |     -i  or --init     |             re-initialises machine (clearing old data) |
| add_key       |    -a or --add_key    |                 add another key to list of usable keys |
| remove_key    |  -r or --remove_key   | remove keys not currently present in machine from list |
| lock_command  | -lc or --lock_command |      set lock command after initial setup (linux only) |