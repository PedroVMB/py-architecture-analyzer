import requests
import os
import tempfile
import zipfile
from urllib.parse import urlparse
import re

GITHUB_API = "https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"

def parse_github_url(url):
    """
    aceita:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - https://github.com/owner/repo/tree/branch
    retorna (owner, repo, branch_or_default)
    """
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    parts = path.split('/')
    if len(parts) < 2:
        raise ValueError("URL de GitHub inválida")
    owner, repo = parts[0], parts[1].replace('.git','')
    branch = 'main'
    if 'tree' in parts:
        try:
            idx = parts.index('tree')
            branch = parts[idx+1]
        except Exception:
            branch = 'main'
    return owner, repo, branch

def download_repo_zip(url_or_fullname, dest_folder=None, token=None):
    """
    Se `url_or_fullname` for uma URL -> parse.
    Se for 'owner/repo' assume main branch.
    Retorna caminho do zip baixado.
    """
    if dest_folder is None:
        dest_folder = tempfile.mkdtemp()
    if url_or_fullname.startswith('http'):
        owner, repo, branch = parse_github_url(url_or_fullname)
    else:
        owner_repo = url_or_fullname.strip()
        if '/' not in owner_repo:
            raise ValueError("Formato esperado owner/repo")
        owner, repo = owner_repo.split('/')
        branch = 'main'
    download_url = GITHUB_API.format(owner=owner, repo=repo, branch=branch)
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    r = requests.get(download_url, headers=headers, stream=True)
    r.raise_for_status()
    zip_path = os.path.join(dest_folder, f"{owner}-{repo}-{branch}.zip")
    with open(zip_path, 'wb') as f:
        for chunk in r.iter_content(1024*32):
            f.write(chunk)
    return zip_path

def unzip_to_folder(zip_path, target_folder=None):
    if target_folder is None:
        target_folder = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(target_folder)
    # GitHub zips usually contain a single top-level folder, return its path
    members = z.namelist()
    top_dirs = set([m.split('/')[0] for m in members if m.strip()!=''])
    if len(top_dirs) == 1:
        first = list(top_dirs)[0]
        return os.path.join(target_folder, first)
    return target_folder
