#!/usr/bin/env python3
"""
fetch_cdp.py — Fetch transcript via Playwright CDP and run full pipeline.
Usage: python3 fetch_cdp.py --video VIDEO_ID [--video VIDEO_ID ...]
"""

import asyncio
import argparse
import sys
import re
import os
from pathlib import Path
from dotenv import load_dotenv

# Load API keys
load_dotenv(Path("/Users/patrykwajs/Documents/BUSINESS/AGENTIC AI/.env"))

# Add pipeline module to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline import (
    extract_video_id, get_video_metadata, clean_folder_name, detect_episode_number,
    generate_summary, build_transcript_md, parse_frontmatter,
    update_map, update_guests, update_conclusions, extract_findings,
    fmt_ts, EPISODES_DIR
)


def _parse_combined_panel_text(text: str) -> list[dict]:
    """Parse transcript from the combined 'In this video' panel innerText.
    Format: timestamp line → optional 'N seconds' label → text line(s)
    """
    SKIP = {'In this video', 'Chapters', 'Transcript', 'Search transcript', 'Timeline'}
    lines = text.split('\n')
    segments = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line in SKIP:
            continue
        if re.match(r'^Chapter \d+:', line):
            continue
        # Timestamp: M:SS or H:MM:SS
        ts_m = re.match(r'^(\d+):(\d{2})$', line) or re.match(r'^(\d+):(\d{2}):(\d{2})$', line)
        if ts_m:
            parts = [int(x) for x in line.split(':')]
            start = parts[-1] + parts[-2] * 60 + (parts[-3] * 3600 if len(parts) == 3 else 0)
            # Skip "N seconds" accessibility label that follows the timestamp
            if i < len(lines) and re.match(r'^\d+ seconds?$', lines[i].strip()):
                i += 1
            # Collect text lines until next timestamp or chapter
            text_parts = []
            while i < len(lines):
                nxt = lines[i].strip()
                if not nxt:
                    i += 1
                    break
                if (re.match(r'^\d+:\d{2}$', nxt) or re.match(r'^\d+:\d{2}:\d{2}$', nxt)
                        or re.match(r'^Chapter \d+:', nxt) or nxt in SKIP):
                    break
                if re.match(r'^\d+ seconds?$', nxt):
                    i += 1
                    continue
                text_parts.append(nxt)
                i += 1
            if text_parts:
                segments.append({'start': float(start), 'text': ' '.join(text_parts), 'duration': 5.0})
    return segments


async def get_transcript_cdp(video_id: str):
    """Fetch transcript via Playwright CDP on port 9223."""
    from playwright.async_api import async_playwright
    import urllib.request

    cdp_url = "http://127.0.0.1:9223"
    try:
        urllib.request.urlopen(f"{cdp_url}/json/version", timeout=2)
    except Exception:
        print("  CDP not available — run ~/start-chrome-debug.sh first")
        return None

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await context.new_page()

        try:
            url = f"https://www.youtube.com/watch?v={video_id}&hl=en"
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4)

            # Step 1: Click "Show transcript" button in video description section
            clicked = await page.evaluate("""() => {
                const btn = document.querySelector(
                    'ytd-video-description-transcript-section-renderer button[aria-label="Show transcript"]'
                );
                if (btn) { btn.scrollIntoView(); btn.click(); return true; }
                // Fallback: any Show transcript button
                const btns = document.querySelectorAll('button[aria-label="Show transcript"]');
                for (const b of btns) { b.scrollIntoView(); b.click(); return true; }
                return false;
            }""")

            if not clicked:
                print("  'Show transcript' button not found in description section")
                return None

            await asyncio.sleep(2)

            # Step 2: Click the "Transcript" tab inside the engagement panel
            await page.evaluate("""() => {
                const panel = document.querySelector(
                    'ytd-engagement-panel-section-list-renderer[target-id="engagement-panel-searchable-transcript"]'
                );
                if (!panel) return;
                const btns = panel.querySelectorAll('button');
                for (const btn of btns) {
                    if (btn.innerText?.trim() === 'Transcript') { btn.click(); break; }
                }
            }""")

            await asyncio.sleep(2)

            await asyncio.sleep(2)

            # Wait for segments (standard panel)
            segs_count = 0
            for _ in range(8):
                await asyncio.sleep(1)
                segs_count = await page.evaluate("() => document.querySelectorAll('ytd-transcript-segment-renderer').length")
                if segs_count > 0:
                    break

            if segs_count > 0:
                # Standard extraction via ytd-transcript-segment-renderer
                raw = await page.evaluate("""() => {
                    const segs = document.querySelectorAll('ytd-transcript-segment-renderer');
                    return Array.from(segs).map(s => {
                        const tsEl = s.querySelector('.segment-timestamp');
                        const textEl = s.querySelector('.segment-text, [class*="segment-text"]');
                        return {
                            ts: tsEl ? tsEl.innerText.trim() : '',
                            text: textEl ? textEl.innerText.trim() : s.innerText.trim()
                        };
                    }).filter(x => x.text.length > 0);
                }""")
            else:
                # Fallback: parse from combined "In this video" panel innerText
                panel_text = await page.evaluate("""() => {
                    const panels = document.querySelectorAll('ytd-engagement-panel-section-list-renderer');
                    for (const panel of panels) {
                        if (!panel.getAttribute('target-id') && panel.offsetParent !== null) {
                            return panel.innerText || '';
                        }
                    }
                    return '';
                }""")
                if not panel_text:
                    print("  No transcript segments found")
                    return None
                raw = _parse_combined_panel_text(panel_text)

            if not raw:
                return None

            # Combined panel path already returns proper dicts; standard path returns {ts, text}
            if 'start' in raw[0]:
                return raw  # already formatted

            def ts_to_seconds(ts: str) -> float:
                parts = ts.strip().split(':')
                try:
                    if len(parts) == 2:
                        return int(parts[0]) * 60 + float(parts[1])
                    elif len(parts) == 3:
                        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                except Exception:
                    pass
                return 0.0

            segments = []
            for i, item in enumerate(raw):
                start = ts_to_seconds(item['ts'])
                next_start = ts_to_seconds(raw[i+1]['ts']) if i+1 < len(raw) else start + 5.0
                segments.append({
                    'start': start,
                    'text': item['text'],
                    'duration': next_start - start
                })

            return segments

        finally:
            await page.close()


def process_video(video_id: str, dry_run: bool = False):
    print(f"\n{'='*60}")
    print(f"Processing: {video_id}")

    # Metadata
    print("Fetching metadata...")
    import html as _html
    title, date = get_video_metadata(video_id)
    title = _html.unescape(title)  # fix &amp; &quot; etc.
    clean_title = clean_folder_name(title)
    episode_num = detect_episode_number()
    folder_name = f"EP-{episode_num} - {clean_title}"
    print(f"  Title: {title}")
    print(f"  Date:  {date}")
    print(f"  EP:    {episode_num}")
    print(f"  Folder: {folder_name}")

    # Transcript via CDP
    print("Fetching transcript via CDP...")
    segments = asyncio.run(get_transcript_cdp(video_id))
    if not segments:
        print("  FAILED — no transcript")
        return False
    print(f"  {len(segments)} segments fetched")

    # Build transcript text for LLM
    transcript_text = '\n'.join(
        f"[{fmt_ts(s['start'])}] {s['text'].replace(chr(10), ' ').strip()}"
        for s in segments
    )

    # Generate summary
    print("Generating summary via Claude Haiku...")
    summary_md = generate_summary(title, date, episode_num, video_id, transcript_text, dry_run)

    # Build transcript.md
    transcript_md = build_transcript_md(title, video_id, date, episode_num, segments)

    # Write files
    episode_dir = EPISODES_DIR / folder_name
    if not dry_run:
        episode_dir.mkdir(parents=True, exist_ok=True)
        (episode_dir / "summary.md").write_text(summary_md, encoding='utf-8')
        (episode_dir / "transcript.md").write_text(transcript_md, encoding='utf-8')
        print(f"  Wrote: {episode_dir}/summary.md")
        print(f"  Wrote: {episode_dir}/transcript.md")

    # Parse metadata
    meta = parse_frontmatter(summary_md)
    guest = meta.get('guest', 'None')
    topics = meta.get('topics', [])
    print(f"  Guest: {guest}")
    print(f"  Topics: {topics}")

    # Update site files
    update_map(episode_num, title, folder_name, dry_run)
    update_guests(guest, episode_num, title, folder_name, dry_run)
    findings = extract_findings(summary_md)
    update_conclusions(topics, episode_num, title, folder_name, findings, dry_run)

    print(f"  Done: EP-{episode_num}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", action="append", required=True, help="Video ID(s)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for vid in args.video:
        video_id = extract_video_id(vid)
        ok = process_video(video_id, args.dry_run)
        if not ok:
            print(f"SKIP: {vid}")

    print("\nAll done.")
    if not args.dry_run:
        print("Run: python3 -m mkdocs build 2>&1 | grep '^WARNING -  Doc file'")
        print("Then: git add -A && git commit -m 'add: EP-389 + EP-390' && git push")


if __name__ == "__main__":
    main()
