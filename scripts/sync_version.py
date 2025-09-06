#!/usr/bin/env python3
"""
Synchronize pyproject.toml's [project].version with the VERSION file.
"""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
version_file = ROOT / "VERSION"
pyproject_file = ROOT / "pyproject.toml"

ver = version_file.read_text().strip()

txt = pyproject_file.read_text()
txt = re.sub(r'(?m)^(version\s*=\s*")[^"]*(")$', rf'\\1{ver}\\2', txt)
pyproject_file.write_text(txt)

print(f"Synchronized pyproject.toml to version {ver}")
