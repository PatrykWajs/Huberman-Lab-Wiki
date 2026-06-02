"""
Backfill the first-topic Conclusion write that was silently dropped from
every episode by the parse_frontmatter() bug fixed in commit c2d9ae2.

Iterates docs/Episodes/, reads each summary.md, identifies the first
topic in the frontmatter, resolves it through TOPIC_ALIASES then
TOPIC_MAP to a Conclusion file, and (if that file doesn't already cite
this episode) appends the first 3 Key Findings using the same citation
format the live pipeline writes.

Idempotent. Re-runnable. --dry-run prints what would happen without
touching disk.
"""

import argparse
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# Load pipeline.py without invoking its main()
spec = importlib.util.spec_from_file_location("pipeline", ROOT / "pipeline.py")
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)

EPISODES_DIR = ROOT / "docs" / "Episodes"
CONCLUSIONS_DIR = ROOT / "docs" / "Conclusions"

# Historical summaries used different findings-section headers. extract_findings()
# in pipeline.py only matches "Key Findings" (modern style, 15 eps). For backfill,
# also accept "Key Takeaways" (139 eps) and "Topics Covered" (9 eps).
FINDINGS_HEADERS = ("Key Findings", "Key Takeaways", "Topics Covered")


_NUMBERED = re.compile(r"^\d+\.\s+(.*)$")
# Strip every [anything](transcript.md#anything) reference — bulk-ingest
# summaries weave timestamp links into prose, not just at the trailing position.
# Including links that span the trailing position would otherwise leak relative
# transcript.md links into Conclusion files (which then resolve to
# Conclusions/transcript.md and break the mkdocs build).
_INLINE_TS_LINK = re.compile(r"\[[^\]]*\]\(transcript\.md#[^)]+\)")
# Also strip bare [HH:MM:SS] anchors with no link (occasionally appears alone).
_BARE_TIMESTAMP = re.compile(r"\[\d{1,2}:\d{2}(:\d{2})?\]")


def extract_first_bullets(summary_md: str) -> list:
    """Walk H2 sections in order; return entries from the first section
    whose header matches one of FINDINGS_HEADERS. Accepts both dash
    bullets (modern, 15 eps) and numbered lists (bulk-ingest, 139 eps).
    Strips any trailing [timestamp](transcript.md#anchor) tail so the
    Conclusion entry is a clean prose sentence."""
    in_target = False
    out = []
    for line in summary_md.split("\n"):
        if line.startswith("## "):
            header = line[3:].strip()
            # Match exact OR prefix — historical headers include
            # "Key Takeaways (10-12 bullets with [HH:MM:SS] links)".
            in_target = any(header == h or header.startswith(h + " ") for h in FINDINGS_HEADERS)
            if in_target:
                out = []
            continue
        if not in_target:
            continue
        body = None
        if line.startswith("- "):
            body = line[2:].strip()
        else:
            m = _NUMBERED.match(line)
            if m:
                body = m.group(1).strip()
        if not body:
            continue
        if body.startswith("["):  # standalone timestamp anchor
            continue
        body = _INLINE_TS_LINK.sub("", body)
        body = _BARE_TIMESTAMP.sub("", body)
        body = re.sub(r"\s+", " ", body).strip()
        body = re.sub(r"\s+([,.;:!?])", r"\1", body)  # tighten punctuation
        if body:
            out.append(body)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    stats = {
        "scanned": 0,
        "no_summary": 0,
        "no_topics": 0,
        "unmapped_first": 0,
        "already_cited": 0,
        "written": 0,
        "no_findings": 0,
    }
    unmapped_pairs = []
    written_pairs = []

    for ep_folder in sorted(EPISODES_DIR.iterdir()):
        if not ep_folder.is_dir():
            continue
        summary_path = ep_folder / "summary.md"
        if not summary_path.exists():
            stats["no_summary"] += 1
            continue
        stats["scanned"] += 1
        text = summary_path.read_text(encoding="utf-8")
        meta = pipeline.parse_frontmatter(text)
        topics = meta.get("topics", [])
        if not topics:
            stats["no_topics"] += 1
            continue
        first_topic = topics[0]
        canonical = pipeline.TOPIC_ALIASES.get(first_topic, first_topic)
        target_file = pipeline.TOPIC_MAP.get(canonical)
        if not target_file:
            stats["unmapped_first"] += 1
            unmapped_pairs.append((ep_folder.name, first_topic))
            continue

        target_path = CONCLUSIONS_DIR / target_file
        if not target_path.exists():
            print(f"  WARN target file missing: {target_file}")
            continue

        target_text = target_path.read_text(encoding="utf-8")
        # Idempotency: skip if this episode's folder is already referenced
        # in the target Conclusion file. Catches both pipeline-written
        # entries (for items 2+) and manual patches like EP-408 NSDR.
        if ep_folder.name in target_text:
            stats["already_cited"] += 1
            continue

        findings = extract_first_bullets(text)[:3]
        if not findings:
            stats["no_findings"] += 1
            continue

        # Match the live pipeline citation format (pipeline.py:374).
        # Strip the trailing — *[HH:MM:SS](transcript.md#anchor)* tag
        # from each finding to leave a clean sentence.
        episode_num_match = re.search(r"^EP-(\d+)", ep_folder.name)
        episode_num = int(episode_num_match.group(1)) if episode_num_match else 0
        # Title comes from the H1 / folder name. Strip the EP-N prefix.
        title_for_citation = ep_folder.name.split(" - ", 1)[-1] if " - " in ep_folder.name else ep_folder.name

        entries = []
        for finding in findings:
            finding_clean = re.sub(r"\s*—\s*\*\[.*?\]\(.*?\)\*", "", finding).strip()
            if finding_clean:
                entries.append(
                    f"- {finding_clean} — "
                    f"*from [EP-{episode_num} - {title_for_citation}]"
                    f"(../Episodes/{ep_folder.name}/summary.md)*"
                )

        if not entries:
            stats["no_findings"] += 1
            continue

        if args.dry_run:
            stats["written"] += 1
            written_pairs.append((ep_folder.name, target_file, len(entries)))
            continue

        with open(target_path, "a", encoding="utf-8") as fp:
            fp.write("\n" + "\n".join(entries) + "\n")
        stats["written"] += 1
        written_pairs.append((ep_folder.name, target_file, len(entries)))

    print("\n=== Backfill summary ===")
    for k, v in stats.items():
        print(f"  {k:18} {v}")
    if unmapped_pairs:
        print("\n  Unmapped first topics:")
        for name, topic in unmapped_pairs:
            print(f"    {name!r}: {topic!r}")
    if args.dry_run:
        print("\n  (dry-run — no files written)")
    else:
        print(f"\n  Wrote {stats['written']} episodes × ~3 findings each.")


if __name__ == "__main__":
    main()
