import zipfile
import os
import tempfile
from pathlib import Path

def extract_uploaded_zip(zip_file_path):
    workdir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_file_path, 'r') as z:
        z.extractall(workdir)
    # Se houver só uma pasta dentro, retorná-la
    entries = [e for e in os.listdir(workdir) if not e.startswith('__MACOSX')]
    if len(entries) == 1 and os.path.isdir(os.path.join(workdir, entries[0])):
        return os.path.join(workdir, entries[0])
    return workdir
