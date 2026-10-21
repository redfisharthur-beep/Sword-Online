#!/usr/bin/env python3
"""Build a static deployment containing only public game files."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'public'
FILES = ('index.html', '_headers')
DIRECTORIES = ('src', 'assets', 'game-assets')

def build():
    for name in (*FILES, *DIRECTORIES):
        if not (ROOT / name).exists():
            raise SystemExit(f'Missing required game asset: {name}')
    if OUTPUT.is_symlink():
        raise SystemExit('Refusing to replace a symlink at public/')
    OUTPUT.mkdir(exist_ok=True)
    for child in OUTPUT.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()
    for name in FILES:
        shutil.copy2(ROOT / name, OUTPUT / name)
    for name in DIRECTORIES:
        shutil.copytree(ROOT / name, OUTPUT / name)
    print(f'Built {sum(f.is_file() for f in OUTPUT.rglob("*"))} public files in {OUTPUT}')

if __name__ == '__main__':
    build()
