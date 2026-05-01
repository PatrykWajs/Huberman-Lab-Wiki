# CLAUDE.md — Huberman Lab Wiki

## What This Is

A static MkDocs website containing summaries + full transcripts for 397 Huberman Lab episodes, deployed to GitHub Pages. Built and maintained by AI. Not affiliated with Huberman Lab officially.

**Live site:** https://patrykwajs.github.io/Huberman-Lab-Wiki/
**GitHub repo:** https://github.com/PatrykWajs/Huberman-Lab-Wiki
**Local path:** `Wiki/active/execution/Huberman-Lab-Wiki/`

---

## Directory Structure

```
Huberman-Lab-Wiki/
├── CLAUDE.md              # This file — full SOP
├── mkdocs.yml             # MkDocs config (theme, nav, plugins)
├── overrides/
│   └── main.html          # Jinja2 template — adds og:image, Twitter card meta
├── docs/
│   ├── index.md           # Home page — episode count, latest episode embed, nav dashboard
│   ├── MAP.md             # All episodes in chronological order as bullet list
│   ├── GUESTS.md          # Guest directory — all expert guests alphabetically
│   ├── MECHANISMS.md      # Biological mechanisms index (nav page linking to 3 sub-pages)
│   ├── MECHANISMS-A-E.md  # Mechanisms A–E (Acetylcholine → Estrogen)
│   ├── MECHANISMS-G-N.md  # Mechanisms G–N (GABA → Norepinephrine)
│   ├── MECHANISMS-S-T.md  # Mechanisms S–T (Serotonin → Thyroid)
│   ├── 404.md             # Custom 404 page
│   ├── robots.txt         # SEO robots file
│   ├── assets/
│   │   ├── stylesheets/extra.css  # Blue palette + card styles
│   │   └── images/
│   │       ├── favicon.svg        # Blue HL favicon
│   │       └── social-card.png    # og:image for social sharing (1200×630)
│   ├── Episodes/
│   │   ├── index.md               # Episodes section landing page
│   │   └── EP-001 - Title/
│   │       ├── summary.md         # AI-generated structured summary
│   │       └── transcript.md      # Full timestamped transcript (search-excluded)
│   └── Conclusions/
│       ├── index.md               # Topic grid with 29 categories
│       └── ... (29 topic files)
├── scripts/
│   ├── fix_links.py               # Fixed 3183 broken double-prefix links (run once)
│   ├── fix_hash_folders.py        # Fixed 22 folders with # in name (run once)
│   └── add_topic_intros.py        # Scraped hubermanlab.com + rephrased via GPT-4o-mini
└── .github/
    └── workflows/deploy.yml       # CI: push to main → mkdocs build → GitHub Pages
```

---

## How the Site Works

1. All content lives in `docs/`
2. `mkdocs build` compiles everything into `site/` (gitignored)
3. GitHub Actions (`deploy.yml`) runs `mkdocs build` on every push to `main` and deploys `site/` to GitHub Pages
4. Changes are live within ~60 seconds of push

**CI install command:**
```
pip install mkdocs-material mkdocs-minify-plugin mkdocs-literate-nav pymdown-extensions
```

**Local build/preview:**
```bash
cd Wiki/active/execution/Huberman-Lab-Wiki
pip install mkdocs-material mkdocs-minify-plugin mkdocs-literate-nav pymdown-extensions
python3 -m mkdocs build        # build only — check for WARNING lines
python3 -m mkdocs serve        # local preview at http://127.0.0.1:8000
```

**Build health check** — run this after every episode addition. Should return 0 lines:
```bash
python3 -m mkdocs build 2>&1 | grep "^WARNING -  Doc file"
```

---

## Episode File Format

### `summary.md` (frontmatter + content)
```markdown
---
title: "Episode Title"
episode_number: 386
guest: Guest Name   # use "None" for solo/Essentials episodes
date: YYYY-MM-DD
topics:
- Memory and Learning
- The Brain and Neuroplasticity
---

# Episode Title

> 📄 [View Full Transcript](transcript.md)

## Key Findings

- Finding text. Factual, actionable, 1–3 sentences. — *[00:00:00](transcript.md#000000-intro)*

## Timestamps

- [00:00:00](transcript.md#000000-intro) Introduction
- [00:05:00](transcript.md#000500-topic) Topic Name

## Tools & Protocols

### Protocol Name
- **What:** ...
- **How:** ...
- **When:** ...
- **Ref:** [00:00:00](transcript.md#000000-anchor)

## Resources Mentioned

### Studies
- Study description

### Supplements / Compounds
- Supplement name and context
```

**Critical rules for summary.md:**
- Always add `> 📄 [View Full Transcript](transcript.md)` immediately after the H1 heading
- Never add a `## See Also` section — all 278 existing ones were deleted in April 2026 and must never return
- Never use `[[wiki links]]` — MkDocs does not support Obsidian syntax; always use `[Title](../EP-NNN - Title/summary.md)`
- Timestamp anchors: 6-digit no-colons format — `[00:05:00](transcript.md#000500-slug)`

### `transcript.md` (frontmatter required — DO NOT omit)
```markdown
---
title: "Episode Title"
type: transcript
episode_date: YYYY-MM-DD
episode_number: 386
speakers: [Andrew Huberman]
youtube_id: VIDEO_ID
search:
  exclude: true
---

## [00:00:00] Section Title

Transcript text...
```

**Critical:** `search: exclude: true` must be in every transcript frontmatter. Without it, the transcript gets indexed and inflates the search index from 9MB to 51MB.

### Folder naming convention
```
EP-{zero-padded-number} - {Full Episode Title}
```
Examples:
- `EP-001 - How Your Brain Works and Changes`
- `EP-386 - Essentials - Understand and Improve Memory Using Science-Based Tools`

Rules:
- Use full title from YouTube (no truncation)
- Replace `&` with `and`, `#` with nothing (e.g., `AMA #1` → `AMA 1`)
- Strip YouTube channel suffixes: `| Huberman Lab Podcast` → remove
- No special URL-unsafe characters: `#`, `%`, `?`
- Spaces are fine (MkDocs handles them)
- Essentials episodes: `EP-N - Essentials - {Topic Title}` (no guest)

---

## Workflow: Adding a New Episode

### Step 1 — Get the Episode Info

From the YouTube URL, extract the video ID (11 characters after `?v=`).

Fetch the title and publish date:
```python
import urllib.request, re
req = urllib.request.Request('https://www.youtube.com/watch?v=VIDEO_ID', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')
title = re.search(r'property="og:title" content="([^"]+)"', html).group(1)
date = re.search(r'"publishDate":"([^"]+)"', html).group(1)
print(title, date)
```

### Step 2 — Get the Transcript

**Current API method (v1.0+ uses instance, not class method):**
```python
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
t = api.fetch('VIDEO_ID')          # fetches English by default
data = t.to_raw_data()             # list of dicts: [{'text': ..., 'start': ..., 'duration': ...}]
```

**If IP-blocked** (~15 requests before block): use Google Colab (different IP).

**Format timestamps for anchors:**
```python
def fmt(s):
    return f'{int(s//3600):02d}:{int((s%3600)//60):02d}:{int(s%60):02d}'

def anchor(s):
    return f'{int(s//3600):02d}{int((s%3600)//60):02d}{int(s%60):02d}'
# e.g. 305 seconds → "00:05:05" display, "000505" anchor
```

### Step 3 — Create Episode Folder + Files

```
docs/Episodes/EP-{N} - {Title}/
├── summary.md
└── transcript.md
```

Use 1 Claude Sonnet agent to generate `summary.md` from the transcript. Agent prompt:
```
Read this transcript and create a structured summary.md with:
- YAML frontmatter (title, episode_number, guest, date, topics list)
- > 📄 [View Full Transcript](transcript.md) immediately after the H1 heading
- ## Key Findings: 10–15 bullet points ending with — *[HH:MM:SS](transcript.md#HHMMSS-slug)*
- ## Timestamps: every major section as [HH:MM:SS](transcript.md#HHMMSS-slug) link
- ## Tools & Protocols: What/How/When/Ref for each actionable protocol
- ## Resources Mentioned: studies, supplements
Never add a ## See Also section.
Keep findings factual, concise, actionable.
```

### Step 4 — Update MAP.md

Add a bullet at the end of the episode list in chronological order:
```markdown
- [EP-N - Episode Title](Episodes/EP-N - Title/summary.md)
```

MAP.md uses a flat bullet list — NOT a table. The list starts after the Topic Conclusions section.

### Step 5 — Update GUESTS.md

- **If guest is new:** add an alphabetical `### Guest Full Name` section with the episode link
- **If guest already exists:** append the episode link under their existing section
- **Essentials / solo episodes (no guest):** skip GUESTS.md entirely

```markdown
### Dr. Guest Name
- [EP-N - Episode Title](Episodes/EP-N - Title/summary.md)
```

### Step 6 — Update Conclusions (most important)

For each topic in the episode's frontmatter `topics:` list, append relevant findings to the corresponding `docs/Conclusions/{topic-slug}.md` file.

Each finding format:
```markdown
- Finding text here. — *from [Episode Title](../Episodes/EP-N - Title/summary.md)*
```

**Topic slug → file mapping:**
| Topic | File |
|-------|------|
| Sleep Hygiene | `sleep-hygiene.md` |
| Memory and Learning | `memory-and-learning.md` |
| Focus and Concentration | `focus-and-concentration.md` |
| Diet and Nutrition | `diet-and-nutrition.md` |
| Supplementation | `supplementation.md` |
| Fitness and Workout Routines | `fitness-and-workout-routines.md` |
| Hormone Health | `hormone-health.md` |
| Mental Health | `mental-health.md` |
| The Brain and Neuroplasticity | `the-brain-and-neuroplasticity.md` |
| How to Regulate Your Nervous System | `how-to-regulate-your-nervous-system.md` |
| Light Exposure and Circadian Rhythm | `light-exposure-and-circadian-rhythm.md` |
| Achieving Goals and Building Habits | `achieving-goals-and-building-habits.md` |
| Motivation and Willpower | `motivation-and-willpower.md` |
| NSDR, Meditation and Breathwork | `nsdr-meditation-and-breathwork.md` |
| Sauna and Heat Exposure | `sauna-and-heat-exposure.md` |
| Cold Plunges and Deliberate Cooling | `cold-plunges-and-deliberate-cooling.md` |
| Caffeine Science | `caffeine-science.md` |
| Aging and Longevity Science | `aging-and-longevity-science.md` |
| General Health | `general-health.md` |
| Building Your Daily Routine | `building-your-daily-routine.md` |
| Happiness and Wellbeing | `happiness-and-wellbeing.md` |
| Emotional Intelligence and Relationships | `emotional-intelligence-and-relationships.md` |
| Society and Technology | `society-and-technology.md` |
| Alcohol, Tobacco and Cannabis | `alcohol-tobacco-and-cannabis.md` |
| Optimizing Your Environment | `optimizing-your-environment.md` |
| Male Sexual Health | `male-sexual-health.md` |
| Female Sexual Health | `female-sexual-health.md` |
| Unlocking Creativity | `unlocking-creativity.md` |
| The Science of ADHD | `the-science-of-adhd.md` |

### Step 7 — Update MECHANISMS (if applicable)

If the episode covers a biological mechanism (dopamine, serotonin, cortisol, BDNF, etc.), add the episode link to the relevant section in `MECHANISMS-A-E.md`, `MECHANISMS-G-N.md`, or `MECHANISMS-S-T.md`.

### Step 8 — Regenerate Social Card (`og:image`)

The social card (`docs/assets/images/social-card.png`) displays the episode count and is shown when the site is shared on Facebook, Twitter, etc. Regenerate it every time the episode count changes:

```python
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 630
img = Image.new("RGB", (W, H), "#1A56DB")
draw = ImageDraw.Draw(img)
draw.rectangle([0, 380, W, H], fill="#0D2E6E")

def get_font(size):
    for name in ["/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Arial.ttf"]:
        if os.path.exists(name):
            try: return ImageFont.truetype(name, size)
            except: pass
    return ImageFont.load_default()

draw.text((80, 100), "Huberman Lab Wiki", font=get_font(90), fill="white")
draw.text((80, 240), "Science-backed protocols from 395 episodes", font=get_font(42), fill="#93C5FD")
draw.text((80, 440), "29 topics  ·  21 mechanisms  ·  Expert guests indexed", font=get_font(34), fill="#93C5FD")

img.save("docs/assets/images/social-card.png", "PNG")
```

Update the episode count number in the script each time.

### Step 9 — Update `docs/index.md`

Two things to update on every new episode:

**1. Episode count** — bump the number in two places:
```markdown
# Intro sentence (line ~3):
...detailed summaries, full transcripts, and aggregated topic-based conclusions from **395 episodes**.

# Repository Stats section:
- **Total Episodes:** 395
```

**2. Latest Episode section** — replace the existing embed block (it appears above the Navigation Dashboard):
```markdown
## 🎬 Latest Episode

**EP-N — Episode Title** *(Month DD, YYYY)*

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:8px;">
  <iframe src="https://www.youtube.com/embed/VIDEO_ID" style="position:absolute;top:0;left:0;width:100%;height:100%;" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

[:octicons-arrow-right-24: Read Summary & Transcript](Episodes/EP-N - Title/summary.md)
```

Replace `VIDEO_ID` with the 11-character YouTube ID, update the title, date, and episode link.

### Step 10 — Build Check + Commit and Push

```bash
# verify 0 broken links
python3 -m mkdocs build 2>&1 | grep "^WARNING -  Doc file"

# commit and push
git add -A
git commit -m "add: EP-N - Episode Title"
git push
```

CI deploys automatically. Live within ~60 seconds.

---

## Scripts Reference

All scripts below are **one-time fixes already applied**. Do NOT re-run them.

| Script | Purpose | Status |
|--------|---------|--------|
| `scripts/fix_links.py` | Fixed 3183 double-prefix broken links in Conclusions | ✅ Run once (April 2026) |
| `scripts/fix_hash_folders.py` | Renamed 22 episode folders with `#` in name | ✅ Run once (April 2026) |
| `scripts/add_topic_intros.py` | Scraped hubermanlab.com topics + rephrased via GPT-4o-mini, prepended overviews to all 29 Conclusion files | ✅ Run once (April 2026) |

---

## Fixes Applied to All Existing Files (Do Not Repeat)

These were bulk fixes applied in April 2026. New episodes should follow the formats above and will not have these problems.

### 1. `[[wiki links]]` removed from See Also sections
All episode `summary.md` files originally used Obsidian-style `[[Page Title]]` links. MkDocs does not support them. Fixed: 322 links resolved to proper markdown paths, 655 concept slugs stripped to plain text.

**Rule:** Never use `[[wiki links]]`. Use `[Title](../EP-NNN - Title/summary.md)`.

### 2. See Also sections deleted entirely
278 episode summaries had a `## See Also` section. These were removed in April 2026 — they confused readers and contained unresolvable links to local Obsidian pages. **Never add a See Also section to any episode.**

### 3. EP-200 broken cross-episode links
Two links in `EP-200/summary.md` used URL-encoded paths without `EP-XXX` prefix. Fixed to EP-196 and EP-198.

### 4. `search: exclude: true` added to all transcript frontmatter
391 `transcript.md` files had this added in April 2026. Without it the search index is 51MB. Any new transcript MUST include this from day one.

### 5. `View Full Transcript` link added to all summaries
All 394 original `summary.md` files got `> 📄 [View Full Transcript](transcript.md)` added after the H1. Add this to every new summary.

### 6. EP-169 double-prefix malformed links
8 links across 5 Conclusion files had `EP-169 - EP-169 - ...` double prefix. Fixed manually.

### 7. Supplementation.md renamed to lowercase
`Supplementation.md` → `supplementation.md` — Linux CI is case-sensitive, macOS is not. All new Conclusion files must be lowercase.

---

## Known Non-Critical Warnings

MkDocs build produces INFO-level anchor warnings for EP-384 and EP-385 transcripts (timestamp anchors in summaries don't match the transcript). Pre-existing, do not break navigation.

---

## Tech Stack

- **MkDocs Material** — static site generator with Material theme
- **GitHub Actions** — CI/CD: push to main → build → deploy
- **GitHub Pages** — hosting (free)
- **youtube-transcript-api** — transcript fetching (use instance method: `YouTubeTranscriptApi().fetch('ID').to_raw_data()`)
- **Claude Sonnet** — 1 agent per episode for summary generation
- **GPT-4o-mini** — topic intro rephrasing (add_topic_intros.py, already run)
- **Pillow** — social card PNG generation

---

## What Was Built (History)

| Date | What |
|------|------|
| April 2026 | Initial 394 episodes ingested, site scaffolded |
| April 2026 | MkDocs Material theme, blue palette, GitHub Pages CI |
| April 2026 | 3183 broken conclusion links fixed (`fix_links.py`) |
| April 2026 | 22 hash folders renamed — `#` breaks URLs (`fix_hash_folders.py`) |
| April 2026 | 29 topic intro overviews scraped + rephrased (`add_topic_intros.py`) |
| April 2026 | Search index reduced 51MB → 9MB (`search: exclude: true` in all transcripts) |
| April 2026 | MECHANISMS split into 3 pages (A-E, G-N, S-T), og:image, favicon, custom 404 |
| April 2026 | 322 `[[wiki links]]` converted to proper markdown links |
| April 2026 | `> 📄 View Full Transcript` link added to top of all 394 summaries |
| April 2026 | EP-200 two broken cross-episode links fixed (EP-196, EP-198) |
| April 2026 | EP-169 double-prefix links fixed in 5 Conclusion files |
| April 2026 | Supplementation.md renamed to lowercase (Linux CI case-sensitivity) |
| April 2026 | 0 broken link warnings in build — site fully clean |
| April 2026 | 278 See Also sections deleted from all episode summaries |
| April 2026 | EP-386 added — Essentials: Understand & Improve Memory Using Science-Based Tools |
| April 2026 | Homepage updated: 395 count, Latest Episode YouTube embed above nav dashboard |
| April 2026 | EP-387 added — How to Better Regulate Your Emotions - Dr. Marc Brackett |
| April 2026 | EP-388 added — Essentials: The Neuroscience of Speech, Language and Music - Dr. Erich Jarvis |
| April 2026 | Homepage updated: 397 count, Latest Episode YouTube embed updated |
