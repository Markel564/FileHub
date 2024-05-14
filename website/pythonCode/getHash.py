import hashlib
import os


def sign_file(file_path):
    sha = hashlib.sha256()
    try:
        with open(file_path, 'rb') as file:
            block = file.read(4096)
            while len(block) > 0:
                sha.update(block)
                block = file.read(4096)
        
        return sha.hexdigest()
    
    except:
        return False