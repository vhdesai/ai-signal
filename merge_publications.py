#!/usr/bin/env python3
"""Merge publication email files into date-based news digest files.

Reads each publication .md file, extracts dated email entries with article links,
filters out generic/noise links, and appends them to existing date-stamped digest
files (or creates new ones for dates without existing digests).
"""

import re, os, glob, sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

NEWS_DIR = Path(__file__).parent / "news"

PUBLICATION_FILES = [
    "Berkeley RDI.md",
    "Business Insider.md",
    "CIO Dive.md",
    "DealBook.md",
    "PitchBook.md",
    "The Information.md",
    "The Tactical Allocation Letter.md",
    "Wall Street Journal.md",
    "WSJ Pro CyberSecurity.md",
    "WSJ Wealth Advisor.md",
]

# Link texts to skip (generic newsletter chrome, not real articles)
SKIP_LINK_PATTERNS = [
    r"^subscribe",
    r"^sign up",
    r"^start writing",
    r"^unsubscribe",
    r"^manage your",
    r"^view in browser",
    r"^view online",
    r"^get your tickets?$",
    r"^sponsorship",
    r"^read more$",
    r"^here$",
    r"^click here",
    r"^learn more$",
    r"^download",
    r"^share$",
    r"^tweet$",
    r"^forward$",
    r"^privacy policy",
    r"^terms of (use|service)",
    r"^contact us",
    r"^help center",
    r"^our partners",
    r"^founding dev",
    r"^sprint \d+ submission",
]

SKIP_URL_PATTERNS = [
    r"favicon",
    r"unsubscribe",
    r"email-preferences",
    r"manage-your",
    r"tradepub\.com",
    r"resources\.industrydive\.com",
    r"/signup",
    r"/subscribe",
    r"/feedback",
    r"sendibm1\.com",
]


def should_skip_link(text: str, url: str) -> bool:
    """Return True if link is generic newsletter chrome."""
    t = text.strip().lower()
    if len(t) < 4:
        return True
    for pat in SKIP_LINK_PATTERNS:
        if re.search(pat, t, re.IGNORECASE):
            return True
    for pat in SKIP_URL_PATTERNS:
        if re.search(pat, url, re.IGNORECASE):
            return True
    return False


def parse_publication(filepath: Path) -> dict:
    """Parse a publication file and return {date: [(subject, [(link_text, url)])]}.
    
    Returns dict mapping date string -> list of (email_subject, article_links) tuples.
    """
    content = filepath.read_text(encoding="utf-8", errors="replace")
    pub_name = filepath.stem  # e.g., "Business Insider"
    
    # Split on entry headers
    entry_pattern = re.compile(
        r'^## (\d{4}-\d{2}-\d{2})\s+\d{0,2}:?\d{0,2}\s*-\s*\[EXTERNAL\]\s*(.+?)$',
        re.MULTILINE
    )
    
    entries = defaultdict(list)
    
    matches = list(entry_pattern.finditer(content))
    for i, m in enumerate(matches):
        date_str = m.group(1)
        subject = m.group(2).strip()
        
        # Get text between this match and next
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(content)
        body = content[start:end]
        
        # Extract article links: [text](url)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        links = []
        seen_texts = set()
        for lm in link_pattern.finditer(body):
            text = lm.group(1).strip()
            url = lm.group(2).strip()
            text_lower = text.lower()
            if should_skip_link(text, url):
                continue
            if text_lower in seen_texts:
                continue
            seen_texts.add(text_lower)
            links.append((text, url))
        
        if links:  # Only add entries that have useful links
            entries[date_str].append((subject, pub_name, links))
    
    return dict(entries)


def find_digest_for_date(date_str: str) -> Path | None:
    """Find existing digest file for a given date."""
    pattern = str(NEWS_DIR / f"{date_str}_*.md")
    matches = glob.glob(pattern)
    if matches:
        # Return the "Final" one if it exists, else the last one
        for m in matches:
            if "Final" in m:
                return Path(m)
        return Path(matches[-1])
    return None


def create_publication_section(date_str: str, entries: list) -> str:
    """Create markdown section for publication entries.
    
    entries: list of (subject, pub_name, [(link_text, url)])
    """
    lines = []
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Publication Newsletter Sources")
    lines.append("")
    lines.append(f"*Additional coverage from newsletter subscriptions for {date_str}*")
    lines.append("")
    
    for subject, pub_name, links in entries:
        # Clean subject line
        subject_clean = subject.strip()
        # Remove common prefixes
        for prefix in ["DealBook: ", "RE: "]:
            if subject_clean.startswith(prefix):
                subject_clean = subject_clean[len(prefix):]
        
        lines.append(f"### {subject_clean}")
        lines.append(f"[{date_str}] · {pub_name}")
        lines.append("")
        
        # Add article links as bullet points
        for text, url in links[:10]:  # Cap at 10 links per email
            lines.append(f"- [{text}]({url})")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def create_new_digest(date_str: str, entries: list) -> str:
    """Create a minimal new digest file for dates without existing digests."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        date_formatted = dt.strftime("%B %d, %Y")
    except ValueError:
        date_formatted = date_str
    
    lines = []
    lines.append(f"# Daily AI News Digest – {date_formatted}")
    lines.append("")
    lines.append("**Generated by:** Publication Email Sources")
    lines.append(f"**Date:** {date_str}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Publication Newsletter Sources")
    lines.append("")
    lines.append(f"*Coverage from newsletter subscriptions for {date_str}*")
    lines.append("")
    
    for subject, pub_name, links in entries:
        subject_clean = subject.strip()
        for prefix in ["DealBook: ", "RE: "]:
            if subject_clean.startswith(prefix):
                subject_clean = subject_clean[len(prefix):]
        
        lines.append(f"### {subject_clean}")
        lines.append(f"[{date_str}] · {pub_name}")
        lines.append("")
        for text, url in links[:10]:
            lines.append(f"- [{text}]({url})")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def main():
    print("=" * 60)
    print("Publication Email Merger")
    print("=" * 60)
    
    # Collect all entries by date across all publications
    all_entries = defaultdict(list)  # date -> [(subject, pub_name, links)]
    
    for fname in PUBLICATION_FILES:
        fpath = NEWS_DIR / fname
        if not fpath.exists():
            print(f"  SKIP: {fname} (not found)")
            continue
        
        entries = parse_publication(fpath)
        total_articles = sum(len(links) for subj, pub, links in 
                           [item for items in entries.values() for item in items])
        print(f"  {fname}: {len(entries)} dates, {total_articles} article links")
        
        for date_str, entry_list in entries.items():
            all_entries[date_str].extend(entry_list)
    
    print(f"\nTotal unique dates: {len(all_entries)}")
    
    # Process each date
    appended = 0
    created = 0
    skipped = 0
    
    for date_str in sorted(all_entries.keys()):
        entries = all_entries[date_str]
        total_links = sum(len(links) for _, _, links in entries)
        
        if total_links < 1:
            skipped += 1
            continue
        
        digest_file = find_digest_for_date(date_str)
        
        if digest_file:
            # Check if already has publication section
            existing = digest_file.read_text(encoding="utf-8", errors="replace")
            if "## Publication Newsletter Sources" in existing:
                print(f"  {date_str}: already has publication section, skipping")
                skipped += 1
                continue
            
            # Append to existing digest
            section = create_publication_section(date_str, entries)
            with open(digest_file, "a", encoding="utf-8") as f:
                f.write(section)
            print(f"  {date_str}: appended {len(entries)} emails ({total_links} links) to {digest_file.name}")
            appended += 1
        else:
            # Create new digest file
            new_content = create_new_digest(date_str, entries)
            new_filename = f"{date_str}_000000_Publication-Sources.md"
            new_path = NEWS_DIR / new_filename
            new_path.write_text(new_content, encoding="utf-8")
            print(f"  {date_str}: created {new_filename} ({len(entries)} emails, {total_links} links)")
            created += 1
    
    print(f"\n{'=' * 60}")
    print(f"Summary: {appended} digests updated, {created} new digests created, {skipped} skipped")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
