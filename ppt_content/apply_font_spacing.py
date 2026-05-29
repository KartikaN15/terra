"""
Apply Google Sans font and fix spacing/clash issues across all 11 Terra slide HTML files.
"""
from pathlib import Path
import re

DIR = Path(__file__).parent

def r(name): return (DIR / name).read_text(encoding="utf-8")
def w(name, c): (DIR / name).write_text(c, encoding="utf-8")

GOOGLE_FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Google+Sans:ital,wght@0,300;0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">'

def swap_fonts(s):
    # Replace font <link>
    s = re.sub(
        r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*" rel="stylesheet">',
        GOOGLE_FONT_LINK, s
    )
    # Replace all font-family declarations in CSS and inline styles
    for old, new in [
        ("'Inter', sans-serif",        "'Google Sans', sans-serif"),
        ('"Inter", sans-serif',        '"Google Sans", sans-serif'),
        ("'Space Grotesk', sans-serif","'Google Sans', sans-serif"),
        ('"Space Grotesk", sans-serif','"Google Sans", sans-serif'),
        ("'Space Grotesk',sans-serif", "'Google Sans', sans-serif"),
        ('"Space Grotesk",sans-serif', '"Google Sans", sans-serif'),
    ]:
        s = s.replace(old, new)
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1
# ─────────────────────────────────────────────────────────────────────────────
s = r("slide_01_variant.html")
s = swap_fonts(s)

# Fix broken duplicate .content rule (selector had "{ position: relative; z-index: 1;" on same line)
s = s.replace(
    "        /* Content */\n"
    "        .content { position: relative; z-index: 1;\n"
    "            position: relative;\n"
    "            z-index: 10;\n"
    "            max-width: 55%;\n"
    "        }",
    "        /* Content */\n"
    "        .content {\n"
    "            position: relative;\n"
    "            z-index: 10;\n"
    "            max-width: 52%;\n"
    "        }"
)

# Reduce title letter-spacing (Google Sans handles tight tracking differently)
s = s.replace("letter-spacing: -2px;", "letter-spacing: -1px;")

w("slide_01_variant.html", s)
print("Slide 01: fonts + .content CSS fix + title spacing")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2
# ─────────────────────────────────────────────────────────────────────────────
s = r("slide_02_variant.html")
s = swap_fonts(s)

# Fix analogy-box: remove position:absolute so it flows as a flex item,
# change the wrapping div to flex-end so it pushes to bottom of the col
old_analogy_css = """        .analogy-box {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(16, 185, 129, 0.15);
            border-radius: 16px;
            padding: 16px 20px;
            font-style: italic;
            font-size: 14px;
            color: #065f46;
            text-align: center;
        }"""
new_analogy_css = """        .analogy-box {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(16, 185, 129, 0.15);
            border-radius: 16px;
            padding: 16px 20px;
            font-style: italic;
            font-size: 13px;
            color: #065f46;
            text-align: center;
            position: relative;
            z-index: 2;
        }"""
s = s.replace(old_analogy_css, new_analogy_css)

# Fix right-col: give it flex-direction:column so image is separate from analogy-box
old_right_col = '        .right-col { width: 420px; display: flex; align-items: center; justify-content: center; position: relative; }'
new_right_col = '        .right-col { width: 420px; display: flex; flex-direction: column; justify-content: flex-end; position: relative; }'
s = s.replace(old_right_col, new_right_col)

# Fix the right-col HTML: wrap analogy-box properly
old_right_html = (
    '            <div class="right-col" style="position:relative;">\n'
    '                <img src="slide_02_scopes_nobg.png" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:90%; object-fit:contain; opacity:1;">\n'
    '                <div style="position:relative; z-index:1; margin-top:auto;">\n'
    '                    <div class="analogy-box">\n'
    '                        "Trying to reduce your carbon footprint without data is like trying to save money without looking at your bank statement."\n'
    '                    </div>\n'
    '                </div>\n'
    '            </div>'
)
new_right_html = (
    '            <div class="right-col">\n'
    '                <img src="slide_02_scopes_nobg.png" style="position:absolute; top:44%; left:50%; transform:translate(-50%,-50%); width:82%; object-fit:contain; opacity:1; z-index:1;">\n'
    '                <div class="analogy-box" style="margin-bottom:8px;">\n'
    '                    "Trying to reduce your carbon footprint without data is like trying to save money without looking at your bank statement."\n'
    '                </div>\n'
    '            </div>'
)
s = s.replace(old_right_html, new_right_html)

w("slide_02_variant.html", s)
print("Slide 02: fonts + analogy-box layout fix")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3
# ─────────────────────────────────────────────────────────────────────────────
s = r("slide_03_variant.html")
s = swap_fonts(s)

# Reduce companion image opacity so it doesn't bleed through the card
s = s.replace(
    'style="position:absolute; bottom:0; left:50%; transform:translateX(-50%); width:85%; object-fit:contain; opacity:0.92;"',
    'style="position:absolute; bottom:0; left:50%; transform:translateX(-50%); width:85%; object-fit:contain; opacity:0.18; z-index:0;"'
)

# Ensure vertical-card has z-index above image
s = s.replace(
    "        .vertical-card { position: relative; z-index: 1; }",
    "        .vertical-card { position: relative; z-index: 2; }"
)

w("slide_03_variant.html", s)
print("Slide 03: fonts + companion image opacity fix")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4
# ─────────────────────────────────────────────────────────────────────────────
s = r("slide_04_variant.html")
s = swap_fonts(s)

# Reduce timeline image opacity so diary entries stay readable
s = s.replace(
    'style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); height:95%; object-fit:contain; opacity:0.95; z-index:0;"',
    'style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); height:92%; object-fit:contain; opacity:0.22; z-index:0;"'
)

w("slide_04_variant.html", s)
print("Slide 04: fonts + timeline image opacity fix")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDES 5-11: fonts only (layout already correct)
# ─────────────────────────────────────────────────────────────────────────────
for i in range(5, 12):
    fname = f"slide_{i:02d}_variant.html"
    s = r(fname)
    s = swap_fonts(s)
    w(fname, s)
    print(f"Slide {i:02d}: fonts swapped")

# ─────────────────────────────────────────────────────────────────────────────
# Verify
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Verification ---")
for i in range(1, 12):
    fname = f"slide_{i:02d}_variant.html"
    s = r(fname)
    has_inter        = "'Inter'" in s or '"Inter"' in s
    has_space_grotesk = "Space Grotesk" in s
    has_google_sans  = "Google Sans" in s
    ok = not has_inter and not has_space_grotesk and has_google_sans
    print(f"  Slide {i:02d}: Google Sans={has_google_sans}  Inter={has_inter}  SpaceGrotesk={has_space_grotesk}  {'OK' if ok else 'NEEDS CHECK'}")
