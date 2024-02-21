# from github import Github
# from github import Auth
# import github
# from datetime import datetime
# from git import Repo
# import os
# import datetime
# import pytz
import os
from pathlib import Path    
from pathlib import PurePosixPath
from pathlib import PureWindowsPath, PurePosixPath

def doesPathExist(path):
    isExist = os.path.exists(path)  
    
    if not isExist:
        print ("Does not exist")
        return False

    if not os.access(path, os.R_OK):
        print ("Not readable")
        return False
    if not os.access(path, os.W_OK):
        print ("Not writable")
        return False
    if not os.access(path, os.X_OK):
        print ("Not executable")
        return False
    
    # chech that it is a directory
    if not os.path.isdir(path):
        print ("Not a directory")
        return False
    
    return True


def windows_to_unix_path(windows_path):
    # Convert backslashes to forward slashes
    unix_path = windows_path.replace('\\', '/')
    
    # Check if the path starts with a drive letter
    if len(unix_path) > 1 and unix_path[1] == ':':
        drive_letter = unix_path[0].lower()
        path_without_drive = unix_path[2:]
        unix_path = '/mnt/' + drive_letter + path_without_drive

    return unix_path + "/"



if __name__ == "__main__":

    # Example usage
    windows_path = r'C:\Users\marke\Desktop\TFG\MarkHub'
    windows_path = r'C:\Users\\marke\Desktop\\TFG\MarkHub'
    # windows_path = r'/sys/dev/char'
    unix_path = windows_to_unix_path(windows_path)
    print("Unix-style path:", unix_path)

    print (doesPathExist(unix_path))
