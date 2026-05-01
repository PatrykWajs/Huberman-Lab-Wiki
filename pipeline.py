#!/usr/bin/env python3
"""
pipeline.py — Huberman Lab Wiki episode ingestion pipeline

Automates adding a new episode to the wiki:
  1. Fetch title + publish date from YouTube
  2. Fetch transcript via YouTubeTranscriptApi
  3. Generate summary.md via Claude Haiku
  4. Write episode folder (summary.md + transcript.md)
  5. Append to MAP.md
  6. Update GUESTS.md (if guest)
  7. Append findings to relevant Conclusions/*.md files

Usage:
    python3 pipeline.py --video VIDEO_ID_OR_URL
    python3 pipeline.py --video https://www.youtube.com/watch?v=XYZ
    python3 pipeline.py --dry-run --video XYZ
"""

import argparse
import re
import sys
import time
import urllib.request
from pathlib import Path

import anthropic
from dotenv import load_dotenv

# ── Config ─────────────────────────────────────────────────────────────────────
WIKI_ROOT = Path(__file__).parent
DOCS_DIR = WIKI_ROOT / "docs"
EPISODES_DIR = DOCS_DIR / "Episodes"
CONCLUSIONS_DIR = DOCS_DIR / "Conclusions"

load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

# Map topic names → conclusion filenames (must match mkdocs.yml nav)
TOPIC_MAP = {
    "Sleep Hygiene": "sleep-hygiene.md",
    "Memory and Learning": "memory-and-learning.md",
    "Focus and Concentration": "focus-and-concentration.md",
    "Diet and Nutrition": "diet-and-nutrition.md",
    "Supplementation": "supplementation.md",
    "Fitness and Workout Routines": "fitness-and-workout-routines.md",
    "Hormone Health": "hormone-health.md",
    "Mental Health": "mental-health.md",
    "The Brain and Neuroplasticity": "the-brain-and-neuroplasticity.md",
    "How to Regulate Your Nervous System": "how-to-regulate-your-nervous-system.md",
    "Light Exposure and Circadian Rhythm": "light-exposure-and-circadian-rhythm.md",
    "Achieving Goals and Building Habits": "achieving-goals-and-building-habits.md",
    "Motivation and Willpower": "motivation-and-willpower.md",
    "NSDR, Meditation and Breathwork": "nsdr-meditation-and-breathwork.md",
    "Sauna and Heat Exposure": "sauna-and-heat-exposure.md",
    "Cold Plunges and Deliberate Cooling": "cold-plunges-and-deliberate-cooling.md",
    "Caffeine Science": "caffeine-science.md",
    "Aging and Longevity Science": "aging-and-longevity-science.md",
    "General Health": "general-health.md",
    "Building Your Daily Routine": "building-your-daily-routine.md",
    "Happiness and Wellbeing": "happiness-and-wellbeing.md",
    "Emotional Intelligence and Relationships": "emotional-intelligence-and-relationships.md",
    "Society and Technology": "society-and-technology.md",
    "Alcohol, Tobacco and Cannabis": "alcohol-tobacco-and-cannabis.md",
    "Optimizing Your Environment": "optimizing-your-environment.md",
    "Male Sexual Health": "male-sexual-health.md",
    "Female Sexual Health": "female-sexual-health.md",
    "Unlocking Creativity": "unlocking-creativity.md",
    "The Science of ADHD": "the-science-of-adhd.md",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def extract_video_id(url_or_id: str) -> str:
    patterns = [
        r'(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})',
        r'^([A-Za-z0-9_-]{11})$'
    ]
    for p in patterns:
        m = re.search(p, url_or_id)
        if m:
            return m.group(1)
    raise ValueError(f"Cannot extract video ID from: {url_or_id}")


def get_video_metadata(video_id: str) -> tuple[str, str]:
    url = f'https://www.youtube.com/watch?v={video_id}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    title_m = re.search(r'property="og:title" content="([^"]+)"', html)
    date_m = re.search(r'"publishDate":"([^"]+)"', html)
    if not title_m or not date_m:
        raise ValueError("Could not extract title or date from YouTube page")
    title = title_m.group(1)
    date = date_m.group(1)[:10]  # YYYY-MM-DD
    return title, date


def get_transcript(video_id: str) -> list[dict]:
    from youtube_transcript_api import YouTubeTranscriptApi
    api = YouTubeTranscriptApi()
    t = api.fetch(video_id)
    return t.to_raw_data()


def fmt_ts(s: float) -> str:
    return f'{int(s//3600):02d}:{int((s%3600)//60):02d}:{int(s%60):02d}'


def anchor_ts(s: float) -> str:
    return f'{int(s//3600):02d}{int((s%3600)//60):02d}{int(s%60):02d}'


def build_transcript_md(title: str, video_id: str, date: str, episode_num: int, segments: list[dict]) -> str:
    lines = [
        "---",
        f'title: "{title}"',
        "type: transcript",
        f"episode_date: {date}",
        f"episode_number: {episode_num}",
        "speakers: [Andrew Huberman]",
        f"youtube_id: {video_id}",
        "search:",
        "  exclude: true",
        "---",
        "",
    ]
    current_section = None
    for seg in segments:
        ts = fmt_ts(seg['start'])
        text = seg['text'].replace('\n', ' ').strip()
        lines.append(f"[{ts}] {text}")

    return '\n'.join(lines)


def clean_folder_name(title: str) -> str:
    # Remove YouTube channel suffix
    title = re.sub(r'\s*\|\s*Huberman Lab.*$', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*\|\s*Huberman Lab Podcast.*$', '', title, flags=re.IGNORECASE)
    # Replace problematic chars
    title = title.replace('&', 'and')
    title = title.replace('|', ' - ')
    title = title.replace('#', '')
    title = title.replace('%', '')
    title = re.sub(r'[<>:"/\\?*]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title


def detect_episode_number() -> int:
    """Find the next episode number based on existing episode folders."""
    folders = sorted(EPISODES_DIR.iterdir()) if EPISODES_DIR.exists() else []
    ep_nums = []
    for f in folders:
        m = re.match(r'EP-(\d+)', f.name)
        if m:
            ep_nums.append(int(m.group(1)))
    return max(ep_nums) + 1 if ep_nums else 1


def generate_summary(title: str, date: str, episode_num: int, video_id: str,
                     transcript_text: str, dry_run: bool = False) -> str:
    """Call Claude Haiku to generate structured summary.md content."""
    if dry_run:
        return f"""---
title: "{title}"
episode_number: {episode_num}
guest: None
date: {date}
topics:
- General Health
---

# {title}

> 📄 [View Full Transcript](transcript.md)

## Key Findings

- [DRY RUN — no summary generated]

## Timestamps

- [00:00:00](transcript.md#000000-intro) Introduction
"""

    client = anthropic.Anthropic()

    # Cap transcript at 60k chars
    text_for_llm = transcript_text[:60000]

    prompt = f"""Read this Huberman Lab podcast transcript and create a structured summary.md file.

Episode: {title}
Date: {date}
Episode Number: {episode_num}
Video ID: {video_id}

TRANSCRIPT:
{text_for_llm}

Create a summary.md with EXACTLY this structure:

---
title: "{title}"
episode_number: {episode_num}
guest: [Guest Full Name with title, or "None" for solo/Essentials]
date: {date}
topics:
- [Topic from approved list only]
- [Topic 2]
---

# {title}

> 📄 [View Full Transcript](transcript.md)

## Key Findings

- Finding text. Factual, actionable, 1–3 sentences. — *[HH:MM:SS](transcript.md#HHMMSS-slug)*
[10–15 bullet findings total]

## Timestamps

- [HH:MM:SS](transcript.md#HHMMSS-slug) Section Title
[All major sections]

## Tools & Protocols

### Protocol Name
- **What:** ...
- **How:** ...
- **When:** ...
- **Ref:** [HH:MM:SS](transcript.md#HHMMSS-slug)

## Resources Mentioned

### Studies
- Study description

### Supplements / Compounds
- Supplement name and context

RULES:
- Never add a ## See Also section
- Approved topics list: Sleep Hygiene, Memory and Learning, Focus and Concentration, Diet and Nutrition, Supplementation, Fitness and Workout Routines, Hormone Health, Mental Health, The Brain and Neuroplasticity, How to Regulate Your Nervous System, Light Exposure and Circadian Rhythm, Achieving Goals and Building Habits, Motivation and Willpower, NSDR, Meditation and Breathwork, Sauna and Heat Exposure, Cold Plunges and Deliberate Cooling, Caffeine Science, Aging and Longevity Science, General Health, Building Your Daily Routine, Happiness and Wellbeing, Emotional Intelligence and Relationships, Society and Technology, Alcohol, Tobacco and Cannabis, Optimizing Your Environment, Male Sexual Health, Female Sexual Health, Unlocking Creativity, The Science of ADHD
- Timestamp anchors: 6 digits no colons — [00:05:00](transcript.md#000500-slug)
- Output ONLY the markdown content, nothing else"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip()
    # Strip markdown code fence if Haiku wrapped the output
    if text.startswith("```"):
        lines = text.split('\n')
        lines = lines[1:]  # remove opening fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]  # remove closing fence
        text = '\n'.join(lines)
    return text


def parse_frontmatter(md: str) -> dict:
    """Extract frontmatter fields from generated summary.md."""
    result = {"guest": "None", "topics": []}
    in_fm = False
    lines = md.split('\n')
    i = 0
    for line in lines:
        if line.strip() == '---':
            if not in_fm:
                in_fm = True
                continue
            else:
                break
        if in_fm:
            if line.startswith('guest:'):
                result['guest'] = line.split(':', 1)[1].strip().strip('"')
            elif line.startswith('- ') and 'topics' not in result.get('_last', ''):
                result['topics'].append(line[2:].strip())
            elif line.startswith('topics:'):
                result['_last'] = 'topics'
            else:
                result['_last'] = ''
    return result


def update_map(episode_num: int, title: str, folder_name: str, dry_run: bool):
    map_path = DOCS_DIR / "MAP.md"
    entry = f"- [EP-{episode_num} - {title}](Episodes/{folder_name}/summary.md)"
    if dry_run:
        print(f"  [DRY RUN] Would append to MAP.md: {entry}")
        return
    with open(map_path, 'a', encoding='utf-8') as f:
        f.write(f"\n{entry}")
    print(f"  Updated MAP.md")


def update_guests(guest: str, episode_num: int, title: str, folder_name: str, dry_run: bool):
    if not guest or guest.lower() == 'none':
        return
    guests_path = DOCS_DIR / "GUESTS.md"
    entry = f"- [EP-{episode_num} - {title}](Episodes/{folder_name}/summary.md)"
    if dry_run:
        print(f"  [DRY RUN] Would add to GUESTS.md under '{guest}': {entry}")
        return
    content = guests_path.read_text(encoding='utf-8') if guests_path.exists() else "# Guests\n\n"
    section_header = f"### {guest}"
    if section_header in content:
        content = content.replace(section_header, f"{section_header}\n{entry}", 1)
    else:
        content += f"\n{section_header}\n{entry}\n"
    guests_path.write_text(content, encoding='utf-8')
    print(f"  Updated GUESTS.md for guest: {guest}")


def update_conclusions(topics: list, episode_num: int, title: str, folder_name: str,
                       findings: list, dry_run: bool):
    for topic in topics:
        filename = TOPIC_MAP.get(topic)
        if not filename:
            print(f"  WARN: Unknown topic '{topic}' — skipping conclusions update")
            continue
        conclusion_path = CONCLUSIONS_DIR / filename
        # Use first 3 findings as conclusions entries
        entries = []
        for finding in findings[:3]:
            finding_clean = re.sub(r'\s*—\s*\*\[.*?\]\(.*?\)\*', '', finding).strip()
            if finding_clean:
                entries.append(
                    f"- {finding_clean} — *from [EP-{episode_num} - {title}](../Episodes/{folder_name}/summary.md)*"
                )
        if not entries:
            continue
        if dry_run:
            print(f"  [DRY RUN] Would append {len(entries)} findings to Conclusions/{filename}")
            continue
        with open(conclusion_path, 'a', encoding='utf-8') as f:
            f.write('\n' + '\n'.join(entries) + '\n')
        print(f"  Updated Conclusions/{filename} ({len(entries)} findings)")


def extract_findings(summary_md: str) -> list[str]:
    findings = []
    in_findings = False
    for line in summary_md.split('\n'):
        if '## Key Findings' in line:
            in_findings = True
            continue
        if in_findings and line.startswith('## '):
            break
        if in_findings and line.startswith('- '):
            findings.append(line[2:].strip())
    return findings


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Huberman Lab Wiki — Add new episode")
    parser.add_argument("--video", required=True, help="YouTube video ID or URL")
    parser.add_argument("--episode-num", type=int, help="Episode number (auto-detected if omitted)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only — write no files")
    args = parser.parse_args()

    video_id = extract_video_id(args.video)
    print(f"Video ID: {video_id}")

    # 1. Metadata
    print("Fetching metadata...")
    title, date = get_video_metadata(video_id)
    clean_title = clean_folder_name(title)
    episode_num = args.episode_num or detect_episode_number()
    folder_name = f"EP-{episode_num} - {clean_title}"
    print(f"  Title: {title}")
    print(f"  Date:  {date}")
    print(f"  EP:    {episode_num}")
    print(f"  Folder: {folder_name}")

    # 2. Transcript
    print("Fetching transcript...")
    try:
        segments = get_transcript(video_id)
        print(f"  {len(segments)} segments fetched")
    except Exception as e:
        print(f"  ERROR: {e}")
        print("  → Try Google Colab if IP-blocked, or use Chrome MCP via /youtube-transcript skill")
        sys.exit(1)

    # Build plain text for LLM
    transcript_text = '\n'.join(
        f"[{fmt_ts(s['start'])}] {s['text'].replace(chr(10), ' ').strip()}"
        for s in segments
    )

    # 3. Generate summary
    print("Generating summary via Claude Haiku...")
    summary_md = generate_summary(title, date, episode_num, video_id, transcript_text, args.dry_run)

    # 4. Build transcript.md
    transcript_md = build_transcript_md(title, video_id, date, episode_num, segments)

    # 5. Write files
    episode_dir = EPISODES_DIR / folder_name
    if not args.dry_run:
        episode_dir.mkdir(parents=True, exist_ok=True)
        (episode_dir / "summary.md").write_text(summary_md, encoding='utf-8')
        (episode_dir / "transcript.md").write_text(transcript_md, encoding='utf-8')
        print(f"  Wrote: {episode_dir}/summary.md")
        print(f"  Wrote: {episode_dir}/transcript.md")
    else:
        print(f"  [DRY RUN] Would create: {episode_dir}/")

    # 6. Parse frontmatter for guest and topics
    meta = parse_frontmatter(summary_md)
    guest = meta.get('guest', 'None')
    topics = meta.get('topics', [])
    print(f"  Guest: {guest}")
    print(f"  Topics: {topics}")

    # 7. Update MAP.md
    update_map(episode_num, title, folder_name, args.dry_run)

    # 8. Update GUESTS.md
    update_guests(guest, episode_num, title, folder_name, args.dry_run)

    # 9. Update Conclusions
    findings = extract_findings(summary_md)
    update_conclusions(topics, episode_num, title, folder_name, findings, args.dry_run)

    print("\nDone.")
    if not args.dry_run:
        print("Next steps:")
        print("  1. Review summary.md for accuracy")
        print("  2. python3 -m mkdocs build 2>&1 | grep '^WARNING -  Doc file'  → must be 0 lines")
        print("  3. git add -A && git commit -m 'add: EP-{N} - {title}' && git push")


if __name__ == "__main__":
    main()
