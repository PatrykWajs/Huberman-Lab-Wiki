#!/usr/bin/env python3
"""Fix broken episode links in Conclusions/ and index files.

Problems this fixes:
1. Double episode prefix: EP-179 - EP-179%20-... → EP-179 - Title
2. URL-encoded paths: %20 %23 %26 etc → raw characters
3. Broken paths that don't match actual episode folders

Run from repo root: python3 scripts/fix_links.py
"""
import re
import os
from urllib.parse import unquote

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EPISODES_DIR = os.path.join(REPO_ROOT, "Episodes")
CONCLUSIONS_DIR = os.path.join(REPO_ROOT, "Conclusions")

# Build lookup: EP-XXX -> actual folder name
ep_lookup = {}
for folder in os.listdir(EPISODES_DIR):
    full = os.path.join(EPISODES_DIR, folder)
    if not os.path.isdir(full):
        continue
    m = re.match(r'^(EP-\d+)\s*-\s*.+$', folder)
    if m:
        ep_num = m.group(1)
        ep_lookup[ep_num] = folder

print(f"Loaded {len(ep_lookup)} episode folders")

# Patterns to fix
# Standard: [Text](../Episodes/EP-179 - EP-179%20-%20.../summary.md)
LINK_PATTERN = re.compile(
    r'\[([^\]]*)\]\((\.\./Episodes/[^)]+/summary\.md)\)'
)
# Malformed: link text contains path fragment before |
PIPE_LINK_PATTERN = re.compile(
    r'\[([^\]]*?/summary\.md\|[^\]]*)\]\((\.\./Episodes/[^)]+)\)'
)


def fix_episode_path(raw_path):
    """Decode and fix an episode path, return corrected relative path or None."""
    # URL decode
    decoded = unquote(raw_path)

    # Extract episode number
    m = re.search(r'EP-(\d+)', decoded)
    if not m:
        return None

    ep_num = f"EP-{m.group(1)}"
    actual_folder = ep_lookup.get(ep_num)
    if not actual_folder:
        return None

    return f"../Episodes/{actual_folder}/summary.md"


def fix_content(content):
    """Fix all episode links in a markdown string."""
    fixed = 0
    skipped = 0

    # Fix malformed pipe-style links first
    def fix_pipe(m):
        nonlocal fixed, skipped
        text_raw = m.group(1)
        path_raw = m.group(2)
        # Extract display text after the |
        pipe_idx = text_raw.rfind('|')
        display = text_raw[pipe_idx + 1:].strip() if pipe_idx >= 0 else text_raw
        new_path = fix_episode_path(path_raw)
        if new_path:
            fixed += 1
            return f"[{display}]({new_path})"
        skipped += 1
        return m.group(0)

    content = PIPE_LINK_PATTERN.sub(fix_pipe, content)

    # Fix standard (but broken) links
    def fix_standard(m):
        nonlocal fixed, skipped
        text = m.group(1)
        path_raw = m.group(2)
        new_path = fix_episode_path(path_raw)
        if new_path:
            if new_path != path_raw:
                fixed += 1
            return f"[{text}]({new_path})"
        skipped += 1
        return m.group(0)

    content = LINK_PATTERN.sub(fix_standard, content)
    return content, fixed, skipped


def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()

    fixed_content, fixed, skipped = fix_content(original)

    if fixed_content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        return fixed, skipped
    return 0, 0


total_fixed = 0
total_skipped = 0

# Fix Conclusions/
for fname in sorted(os.listdir(CONCLUSIONS_DIR)):
    if not fname.endswith('.md'):
        continue
    path = os.path.join(CONCLUSIONS_DIR, fname)
    fixed, skipped = process_file(path)
    if fixed or skipped:
        print(f"  {fname}: fixed={fixed} skipped={skipped}")
    total_fixed += fixed
    total_skipped += skipped

# Fix top-level index files
for fname in ['MAP.md', 'GUESTS.md', 'MECHANISMS.md']:
    path = os.path.join(REPO_ROOT, fname)
    if os.path.exists(path):
        fixed, skipped = process_file(path)
        if fixed or skipped:
            print(f"  {fname}: fixed={fixed} skipped={skipped}")
        total_fixed += fixed
        total_skipped += skipped

print(f"\nDone. Fixed: {total_fixed} | Skipped (no match): {total_skipped}")
