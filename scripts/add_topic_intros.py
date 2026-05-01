#!/usr/bin/env python3
"""
Scrape Huberman Lab topic descriptions, rephrase via OpenAI GPT-4o,
and prepend as intro sections to each conclusion .md file.

Run from repo root: python3 scripts/add_topic_intros.py
"""
import os
import re
import time
import urllib.request
from html.parser import HTMLParser
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

TOPICS = [
    ("achieving-goals-and-building-habits",    "docs/Conclusions/achieving-goals-and-building-habits.md",    "goals-and-habits"),
    ("aging-and-longevity-science",            "docs/Conclusions/aging-and-longevity-science.md",            "aging-and-longevity"),
    ("alcohol-tobacco-and-cannabis",           "docs/Conclusions/alcohol-tobacco-and-cannabis.md",           "alcohol-tobacco-and-cannabis"),
    ("building-your-daily-routine",            "docs/Conclusions/building-your-daily-routine.md",            "daily-routines"),
    ("caffeine-science",                       "docs/Conclusions/caffeine-science.md",                       "caffeine-science"),
    ("cold-plunges-and-deliberate-cooling",    "docs/Conclusions/cold-plunges-and-deliberate-cooling.md",    "cold-plunges-and-deliberate-cooling"),
    ("diet-and-nutrition",                     "docs/Conclusions/diet-and-nutrition.md",                     "diet-and-nutrition"),
    ("emotional-intelligence-and-relationships","docs/Conclusions/emotional-intelligence-and-relationships.md","emotional-intelligence-and-relationships"),
    ("female-sexual-health",                   "docs/Conclusions/female-sexual-health.md",                   "female-sexual-health"),
    ("fitness-and-workout-routines",           "docs/Conclusions/fitness-and-workout-routines.md",           "fitness-and-workout-routines"),
    ("focus-and-concentration",                "docs/Conclusions/focus-and-concentration.md",                "focus-and-concentration"),
    ("general-health",                         "docs/Conclusions/general-health.md",                         "general-health"),
    ("happiness-and-wellbeing",                "docs/Conclusions/happiness-and-wellbeing.md",                "happiness-and-wellbeing"),
    ("hormone-health",                         "docs/Conclusions/hormone-health.md",                         "hormone-health"),
    ("how-to-regulate-your-nervous-system",    "docs/Conclusions/how-to-regulate-your-nervous-system.md",   "regulate-your-nervous-system"),
    ("light-exposure-and-circadian-rhythm",    "docs/Conclusions/light-exposure-and-circadian-rhythm.md",   "light-exposure-and-circadian-rhythm"),
    ("male-sexual-health",                     "docs/Conclusions/male-sexual-health.md",                     "male-sexual-health"),
    ("memory-and-learning",                    "docs/Conclusions/memory-and-learning.md",                    "memory-and-learning"),
    ("mental-health",                          "docs/Conclusions/mental-health.md",                          "mental-health"),
    ("motivation-and-willpower",               "docs/Conclusions/motivation-and-willpower.md",               "motivation-and-willpower"),
    ("nsdr-meditation-and-breathwork",         "docs/Conclusions/nsdr-meditation-and-breathwork.md",         "nsdr-meditation-and-breathwork"),
    ("optimizing-your-environment",            "docs/Conclusions/optimizing-your-environment.md",            "optimizing-your-environment"),
    ("sauna-and-heat-exposure",                "docs/Conclusions/sauna-and-heat-exposure.md",                "sauna-and-heat-exposure"),
    ("sleep-hygiene",                          "docs/Conclusions/sleep-hygiene.md",                          "sleep-hygiene"),
    ("society-and-technology",                 "docs/Conclusions/society-and-technology.md",                 "society-and-technology"),
    ("supplementation",                        "docs/Conclusions/Supplementation.md",                        "supplementation"),
    ("the-brain-and-neuroplasticity",          "docs/Conclusions/the-brain-and-neuroplasticity.md",          "brain-and-neuroplasticity"),
    ("the-science-of-adhd",                    "docs/Conclusions/the-science-of-adhd.md",                    "science-of-adhd"),
    ("unlocking-creativity",                   "docs/Conclusions/unlocking-creativity.md",                   "creativity"),
]

MARKER = "<!-- topic-intro-added -->"


def fetch_description(slug: str) -> str:
    url = f"https://www.hubermanlab.com/topics/{slug}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")

    # Strip all HTML tags
    class Stripper(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts = []
            self.in_script = False

        def handle_starttag(self, tag, attrs):
            if tag in ("script", "style", "noscript"):
                self.in_script = True

        def handle_endtag(self, tag):
            if tag in ("script", "style", "noscript"):
                self.in_script = False

        def handle_data(self, data):
            if not self.in_script:
                self.parts.append(data)

    s = Stripper()
    s.feed(html)
    text = " ".join(s.parts)
    text = re.sub(r'\s+', ' ', text).strip()

    # Find description: after stats block (episodes/timestamps), before Table of Contents
    # Pattern: find the first long sentence that mentions the topic
    toc_match = re.search(r'Table of Contents', text)
    end = toc_match.start() if toc_match else min(3000, len(text))

    # Skip the "X episodes Y timestamps" stats
    stats_match = re.search(r'\d+\s+experts?\s+(.+)', text[:end])
    if stats_match:
        raw = stats_match.group(1).strip()
    else:
        # Fallback: take everything up to Table of Contents
        raw = text[:end]

    # Cut at a reasonable length (first 1200 chars)
    raw = raw[:1500].strip()
    return raw


def rephrase(client: OpenAI, topic_name: str, original: str) -> str:
    prompt = f"""You are a science writer for a knowledge base about the Huberman Lab podcast.

Rewrite the following description for the topic "{topic_name}" completely in your own words.
Rules:
- Same factual content, different wording — no plagiarism
- 2-4 paragraphs, professional and clear tone
- No fluff, no filler phrases like "In conclusion" or "It is important to note"
- Start with a strong opening sentence about the topic's significance
- End with a sentence about why tracking these findings matters for daily application
- Do NOT mention "Huberman Lab" by name — write as a standalone science resource

Original text to rephrase:
---
{original}
---

Output ONLY the rephrased text, nothing else."""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=600,
    )
    return resp.choices[0].message.content.strip()


def prepend_intro(filepath: str, topic_name: str, intro_text: str):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if already added
    if MARKER in content:
        print(f"  [skip] already has intro: {filepath}")
        return False

    # Find the first heading (# Topic Name)
    heading_match = re.match(r'^(#[^\n]+\n)', content)
    if not heading_match:
        print(f"  [warn] no heading found in {filepath}")
        return False

    heading = heading_match.group(1)

    intro_block = f"""{heading}
{MARKER}
> **Overview**
>
> {intro_text.replace(chr(10), chr(10) + '> ')}

"""
    new_content = intro_block + content[len(heading):]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def main():
    client = OpenAI(api_key=OPENAI_API_KEY)
    total = len(TOPICS)

    for i, (name, filepath, slug) in enumerate(TOPICS, 1):
        print(f"\n[{i}/{total}] {name}")

        # Check if already done
        try:
            with open(filepath) as f:
                if MARKER in f.read():
                    print(f"  [skip] already done")
                    continue
        except FileNotFoundError:
            print(f"  [warn] file not found: {filepath}")
            continue

        # Fetch
        try:
            raw = fetch_description(slug)
            print(f"  scraped {len(raw)} chars")
        except Exception as e:
            print(f"  [error] fetch failed: {e}")
            continue

        if len(raw) < 50:
            print(f"  [skip] description too short: {repr(raw)}")
            continue

        # Rephrase
        try:
            rephrased = rephrase(client, name.replace("-", " ").title(), raw)
            print(f"  rephrased {len(rephrased)} chars")
        except Exception as e:
            print(f"  [error] OpenAI failed: {e}")
            continue

        # Write to file
        updated = prepend_intro(filepath, name.replace("-", " ").title(), rephrased)
        if updated:
            print(f"  [ok] updated {filepath}")

        time.sleep(0.5)  # gentle rate limit

    print("\nDone.")


if __name__ == "__main__":
    main()
