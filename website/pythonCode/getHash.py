import hashlib
import os


def sign_file(file_path):
    sha = hashlib.sha256()
    
    with open(file_path, 'rb') as file:
        block = file.read(4096)
        while len(block) > 0:
            sha.update(block)
            block = file.read(4096)
    
    return sha.hexdigest()


def sign_folder(folder_path):
    sha = hashlib.sha256()

    for root, dirs, files in os.walk(folder_path):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            sha.update(sign_file(file_path).encode('utf-8'))
    
    return sha.hexdigest()

