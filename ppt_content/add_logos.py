"""Remove backgrounds from logos and inject them into all 11 slide HTML files."""
from pathlib import Path
from rembg import remove

DIR = Path(__file__).parent

# ── rembg both logos ──────────────────────────────────────────────────────
for src, dst in [
    ("J2W logo.png",          "j2w_nobg.png"),
    ("Netflix_Logo_RGB.png",  "netflix_nobg.png"),
]:
    print(f"rembg {src} ...", end=" ", flush=True)
    data = (DIR / src).read_bytes()
    (DIR / dst).write_bytes(remove(data))
    print("done")

# ── shared logo bar HTML (injected just before </div> closing slide-container)
# For most slides: small bottom-left strip
LOGO_BAR = '''
        <!-- Logo strip -->
        <div style="position:absolute; bottom:20px; left:32px; display:flex; align-items:center; gap:14px; z-index:20;">
            <img src="j2w_nobg.png"      style="height:28px; object-fit:contain; opacity:0.85;">
            <div style="width:1px; height:22px; background:rgba(6,95,70,0.25);"></div>
            <img src="netflix_nobg.png"  style="height:20px; object-fit:contain; opacity:0.85;">
        </div>'''

# For slide 1 (title): bigger, more prominent, placed after tagline-box
LOGO_HERO = '''
                <div style="display:flex; align-items:center; gap:20px; margin-top:32px;">
                    <span style="font-family:\'Space Grotesk\',sans-serif; font-size:13px; font-weight:500; color:#6b7280; letter-spacing:0.5px;">Presented by</span>
                    <img src="j2w_nobg.png"     style="height:36px; object-fit:contain; opacity:0.90;">
                    <span style="font-family:\'Space Grotesk\',sans-serif; font-size:13px; font-weight:500; color:#6b7280;">for</span>
                    <img src="netflix_nobg.png" style="height:26px; object-fit:contain; opacity:0.90;">
                </div>'''

def r(name): return (DIR / name).read_text(encoding="utf-8")
def w(name, c): (DIR / name).write_text(c, encoding="utf-8")

# ── Slide 1: hero treatment ───────────────────────────────────────────────
s1 = r("slide_01_variant.html")
# Remove existing Terra logo-mark (replaced by below)
# Add "Presented by J2W for Netflix" right after the tagline-box div
s1 = s1.replace(
    "            </div>\n\n        </div>\n\n        <!-- Right illustration -->",
    f"            </div>{LOGO_HERO}\n\n        </div>\n\n        <!-- Right illustration -->"
)
w("slide_01_variant.html", s1)
print("Slide 1: hero logo block added")

# ── Slides 2-11: logo bar in bottom-left ─────────────────────────────────
for i in range(2, 12):
    fname = f"slide_{i:02d}_variant.html"
    s = r(fname)
    # Insert logo bar just before the closing </div> of slide-container
    # Marker: page-number div is always the last element before closing
    page_num = f'        <div class="page-number">{i:02d} / 11</div>'
    if page_num in s:
        s = s.replace(page_num, LOGO_BAR + "\n" + page_num)
        w(fname, s)
        print(f"Slide {i}: logo bar added")
    else:
        # fallback: inject before last </div></body>
        s = s.replace("    </div>\n</body>", LOGO_BAR + "\n    </div>\n</body>", 1)
        w(fname, s)
        print(f"Slide {i}: logo bar added (fallback)")

print("\nAll slides updated.")
