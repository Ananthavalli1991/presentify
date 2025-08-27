from typing import List, Tuple, Optional
import re

def safe_filename(name: str, suffix: str) -> str:
    base = re.sub(r'[^a-zA-Z0-9._-]+', '_', name).strip('_')
    if not base:
        base = 'presentation'
    if not base.lower().endswith(suffix.lower()):
        base += suffix
    return base

def chunk_text_to_sections(text: str) -> List[str]:
    """Heuristic fallback: split by markdown headings or long paragraphs."""
    parts = re.split(r'\n(?=#+\s)|\n\n+', text.strip())
    sections = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p) > 1200:
            chunks = re.findall(r'.{1,800}(?:\s+|$)', p)
            sections.extend([c.strip() for c in chunks if c.strip()])
        else:
            sections.append(p)
    return sections[:30]

def extract_title_and_bullets(section: str) -> Tuple[str, List[str]]:
    lines = [l.strip() for l in section.splitlines() if l.strip()]
    if not lines:
        return ("", [])
    if re.match(r'^#+\s', lines[0]):
        title = re.sub(r'^#+\s*', '', lines[0]).strip()
        bullets = lines[1:]
    else:
        title = re.split(r'[.!?]\s', lines[0], maxsplit=1)[0]
        bullets = lines[1:] if len(lines) > 1 else []
    bullets = [re.sub(r'^[-*]\s*', '', b) for b in bullets]
    return (title[:120], [b[:300] for b in bullets][:8])