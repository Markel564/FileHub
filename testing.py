import hashlib
import os

def calcular_firma_archivo(ruta_archivo):
    """Calcula la firma (hash) SHA-256 de un archivo."""
    sha256 = hashlib.sha256()
    with open(ruta_archivo, 'rb') as archivo:
        # Lee el archivo en bloques para manejar archivos grandes
        bloque = archivo.read(4096)
        while len(bloque) > 0:
            sha256.update(bloque)
            bloque = archivo.read(4096)
    return sha256.hexdigest()


def calcular_firma_directorio(ruta_directorio):

    """Calcula la firma (hash) SHA-256 de un directorio."""
    sha256 = hashlib.sha256()
    for ruta, directorios, archivos in os.walk(ruta_directorio):
        for nombre_archivo in sorted(archivos):
            ruta_archivo = os.path.join(ruta, nombre_archivo)
            sha256.update(calcular_firma_archivo(ruta_archivo).encode('utf-8'))
    return sha256.hexdigest()

ruta_archivo = '/mnt/c/Users/marke/Desktop/TFG/TestingClone/word1.docx'
firma = calcular_firma_archivo(ruta_archivo)
print("Firma SHA-256 del archivo:", firma)
ruta_directorio = '/mnt/c/Users/marke/Desktop/TFG/TestingClone'
firma = calcular_firma_directorio(ruta_directorio)
print("Firma SHA-256 del directorio:", firma)
