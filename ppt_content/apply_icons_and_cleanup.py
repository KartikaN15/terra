"""
apply_icons_and_cleanup.py
Processes all 11 slide_XX_variant.html files:
1. Replaces emoji characters with inline Lucide-style SVG icons
2. Fixes em dash usage
3. Removes duplicate CSS rules
"""

import re
import os

# ── Icon path data (Lucide SVG paths) ────────────────────────────────────────
ICONS = {
    "film":         '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M7 3v18"/><path d="M17 3v18"/><path d="M3 7h4"/><path d="M3 11h4"/><path d="M3 15h4"/><path d="M17 7h4"/><path d="M17 11h4"/><path d="M17 15h4"/>',
    "fuel":         '<path d="M3 22V8a2 2 0 0 1 2-2h7a2 2 0 0 1 2 2v14"/><path d="M2 22h14"/><path d="M6 10h3"/><path d="M6 14h3"/><path d="M16 5h1a2 2 0 0 1 2 2v2a2 2 0 0 0 2 2h0a2 2 0 0 0 2-2v-5"/><path d="M16 22V8"/>',
    "link":         '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "globe":        '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "book-open":    '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "users":        '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "cpu":          '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/>',
    "lightbulb":    '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    "bus":          '<path d="M8 6v6"/><path d="M15 6v6"/><path d="M2 12h19.6"/><path d="M18 18h3s.5-1.7.8-2.8c.1-.4.2-.8.2-1.2 0-.4-.1-.8-.2-1.2l-1.4-5C20.1 6.8 19.1 6 18 6H4a2 2 0 0 0-2 2v10h3"/><circle cx="7" cy="18" r="2"/><path d="M9 18h5"/><circle cx="16" cy="18" r="2"/>',
    "zap":          '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "utensils":     '<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>',
    "trash":        '<path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>',
    "plane":        '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',
    "sparkles":     '<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/>',
    "trending-up":  '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "wrench":       '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "bot":          '<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>',
    "trophy":       '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>',
    "monitor":      '<rect width="20" height="15" x="2" y="7" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/>',
    "flask-conical":'<path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"/><path d="M8.5 2h7"/><path d="M7 16h10"/>',
    "van":          '<path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v3m0 0h2l3 4v3h-2m-5-7v7m-7 0a2 2 0 1 0 4 0 2 2 0 0 0-4 0m10 0a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/>',
    "sprout":       '<path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 1 1.1 7.7c-1.7-.1-3.1-.8-4.3-1.9 1.1-2.9 2-5.4 3.2-5.8z"/>',
    "user":         '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "building-2":   '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>',
    "tree":         '<path d="M12 22v-7l-2-2"/><path d="M17 8v.8A6 6 0 0 1 13.8 20v0H10v0A6.5 6.5 0 0 1 7 8h0a5 5 0 0 1 10 0Z"/>',
    "leaf":         '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    "laptop":       '<path d="M20 16V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v9m16 0H4m16 0 1.28 2.55a1 1 0 0 1-.9 1.45H3.62a1 1 0 0 1-.9-1.45L4 16"/>',
    "hard-hat":     '<path d="M2 18a1 1 0 0 0 1 1h18a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v2z"/><path d="M10 10V5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v5"/><path d="M4 15v-3a6 6 0 0 1 6-6h0"/><path d="M14 6h0a6 6 0 0 1 6 6v3"/>',
    "truck":        '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
    "bar-chart":    '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
}


def svg(name: str, size: int = 22, stroke: str = "currentColor") -> str:
    paths = ICONS.get(name, "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{stroke}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'style="display:inline-block;vertical-align:middle;">'
        f'{paths}</svg>'
    )


# ── Emoji → (icon_name, size) mapping ────────────────────────────────────────
EMOJI_MAP = {
    "🎬": ("film", 22),
    "⛽": ("fuel", 22),
    "🔗": ("link", 22),
    "🇬🇧": ("globe", 22),
    "📓": ("book-open", 22),
    "🤝": ("users", 22),
    "🧠": ("cpu", 22),
    "💡": ("lightbulb", 22),
    "🚌": ("bus", 22),
    "⚡": ("zap", 22),
    "🍽️": ("utensils", 22),
    "🍽": ("utensils", 22),
    "🗑️": ("trash", 22),
    "🗑": ("trash", 22),
    "✈️": ("plane", 22),
    "✈": ("plane", 22),
    "🔮": ("sparkles", 22),
    "📈": ("trending-up", 22),
    "🔧": ("wrench", 22),
    "🤖": ("bot", 22),
    "🏆": ("trophy", 22),
    "📺": ("monitor", 22),
    "🧪": ("flask-conical", 22),
    "🚐": ("van", 22),
    "🌱": ("sprout", 22),
    "🧑": ("user", 22),
    "🏢": ("building-2", 22),
    "🌍": ("globe", 22),
    "🌐": ("globe", 22),
    "🌳": ("tree", 22),
    "🍃": ("leaf", 22),
    "🌿": ("leaf", 22),
    "💻": ("laptop", 22),
    "🏗️": ("hard-hat", 22),
    "🏗": ("hard-hat", 22),
    "🚛": ("truck", 22),
    "📊": ("bar-chart", 22),
}

# Sort by length descending so multi-codepoint sequences are matched first
SORTED_EMOJIS = sorted(EMOJI_MAP.keys(), key=len, reverse=True)


def replace_all_emojis(s: str) -> str:
    for emoji in SORTED_EMOJIS:
        if emoji in s:
            icon_name, size = EMOJI_MAP[emoji]
            s = s.replace(emoji, svg(icon_name, size))
    return s


# ── Em dash fixes ─────────────────────────────────────────────────────────────

def fix_em_dashes(s: str) -> str:
    # 1. Title pattern: "Some Title —<br>" or "Some Title —\n" → remove dash
    s = re.sub(r'\s*—\s*(<br\s*/?>)', r'\1', s)
    s = re.sub(r'\s*—\s*\n(\s*</h)', r'\n\1', s)

    # 2. Quote attributions: "— FirstName LastName" at end of element content
    #    Match: — followed by a name (capitalised words, possibly with spaces)
    def attribution_replace(m):
        name = m.group(1).strip()
        return (
            f'<span style="display:block;font-style:normal;font-size:13px;'
            f'color:#6b7280;margin-top:8px;">{name}</span>'
        )
    # Inside blockquote / cite / em / p: — Name pattern
    s = re.sub(
        r'—\s+([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+){0,3})\s*(?=</)',
        attribution_replace,
        s
    )

    # 3. Flowing prose separators: " — " → " · "
    s = s.replace(" — ", " · ")
    s = s.replace("— ", " · ")

    return s


# ── Duplicate CSS rule cleaner ────────────────────────────────────────────────

def fix_duplicate_css(s: str) -> str:
    # Collapse repeated "position: relative; z-index: N;" lines inside a rule
    # Strategy: within any CSS rule block, deduplicate property declarations
    def collapse_rule(m):
        selector = m.group(1)
        block_content = m.group(2)
        # Split into declarations
        decls = re.findall(r'[^;]+;', block_content)
        seen = {}
        for decl in decls:
            stripped = decl.strip()
            if stripped:
                prop = stripped.split(':')[0].strip()
                seen[prop] = stripped  # last wins
        clean = ' '.join(seen.values())
        return f'{selector} {{ {clean} }}'

    # Target rules that contain duplicated position/z-index
    s = re.sub(
        r'(\.[^\{]+)\{([^}]*(?:position\s*:[^;]+;\s*){2,}[^}]*)\}',
        collapse_rule,
        s
    )
    return s


# ── Main processing ────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

for i in range(1, 12):
    filename = f"slide_{i:02d}_variant.html"
    filepath = os.path.join(BASE_DIR, filename)

    if not os.path.exists(filepath):
        print(f"  SKIP  {filename}  (file not found)")
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()

    content = original

    # Step 1: Replace emojis
    content = replace_all_emojis(content)

    # Step 2: Fix em dashes
    content = fix_em_dashes(content)

    # Step 3: Fix duplicate CSS
    content = fix_duplicate_css(content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    emoji_count = sum(original.count(e) for e in SORTED_EMOJIS)
    dash_count = original.count("—")
    changed = "changed" if content != original else "no changes"
    print(f"  OK    {filename}  — {emoji_count} emoji(s) replaced, {dash_count} em dash(es) fixed  [{changed}]")

print("\nDone.")
