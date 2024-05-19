""" 
This module contains a function that is used to create
a hash of a file (SHA-256). It will be used to sign the file and 
keep track of changes made to it.
"""
import hashlib


def sign_file(file_path: str):
    """ 
    input:
        - file_path: the path to the file to be signed (within the filesystem)
    output:
        - the hash of the file if the file was signed, False otherwise
    
    Hashes the file and returns the hash
    """
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