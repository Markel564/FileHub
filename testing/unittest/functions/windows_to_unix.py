

def windows_to_unix_path(windows_path):
    # Remove trailing backslashes and forward slashes
    windows_path = windows_path.rstrip('\\')
    windows_path = windows_path.rstrip('/')

    # Convert backslashes to forward slashes
    unix_path = windows_path.replace('\\', '/')

    # Check if the path starts with a drive letter
    if len(unix_path) > 1 and unix_path[1] == ':':
        drive_letter = unix_path[0].lower()
        path_without_drive = unix_path[2:]
        unix_path = '/mnt/' + drive_letter + path_without_drive

    return unix_path + "/"