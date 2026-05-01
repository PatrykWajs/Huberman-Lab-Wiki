#!/usr/bin/env python3
"""
Rename episode folders containing '#' (breaks URLs) and update all links.
'#' in a URL path is treated as a fragment identifier by browsers.

Run from repo root: python3 scripts/fix_hash_folders.py
"""
import os
import re
import shutil

EPISODES_DIR = "docs/Episodes"
FILES_TO_UPDATE = [
    "docs/MAP.md",
    "docs/GUESTS.md",
    "docs/MECHANISMS.md",
] + [
    f"docs/Conclusions/{f}"
    for f in os.listdir("docs/Conclusions")
    if f.endswith(".md")
]


def new_name(folder: str) -> str:
    """Replace '#' with '' in folder name, clean up spacing."""
    result = folder.replace("#", "").replace("  ", " ").strip()
    return result


# Build rename map
renames = {}
for folder in sorted(os.listdir(EPISODES_DIR)):
    if "#" in folder:
        old_path = os.path.join(EPISODES_DIR, folder)
        new_folder = new_name(folder)
        new_path = os.path.join(EPISODES_DIR, new_folder)
        renames[folder] = new_folder
        print(f"RENAME: {folder}")
        print(f"    TO: {new_folder}")

print(f"\n{len(renames)} folders to rename\n")

# Rename folders on disk
for old, new in renames.items():
    old_path = os.path.join(EPISODES_DIR, old)
    new_path = os.path.join(EPISODES_DIR, new)
    if os.path.exists(old_path) and not os.path.exists(new_path):
        os.rename(old_path, new_path)
        print(f"  [ok] renamed {old[:60]}")

# Update all links in markdown files
total_replaced = 0
for filepath in FILES_TO_UPDATE:
    if not os.path.exists(filepath):
        continue
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    for old_folder, new_folder in renames.items():
        # Replace URL-encoded version (spaces as %20) - shouldn't exist but just in case
        old_encoded = old_folder.replace(" ", "%20").replace("#", "%23")
        new_encoded = new_folder.replace(" ", "%20")
        content = content.replace(old_encoded, new_encoded)

        # Replace raw folder name in links
        content = content.replace(old_folder, new_folder)

    if content != original:
        count = sum(content.count(nf) - original.count(nf) for nf in renames.values())
        print(f"  updated {filepath} (~{abs(count)} refs)")
        total_replaced += 1
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

print(f"\nDone. {len(renames)} folders renamed, {total_replaced} files updated.")
