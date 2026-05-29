"""Patch HTML files to use nobg PNGs (slides 2-8). Slide 1 already patched."""
from pathlib import Path

DIR = Path(__file__).parent

def r(name): return (DIR / name).read_text(encoding="utf-8")
def w(name, c): (DIR / name).write_text(c, encoding="utf-8")

# SLIDE 2
s2 = r("slide_02_variant.html")
s2 = s2.replace(
    '<img src="slide_02_scopes.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:contain; object-position:center; opacity:1; border-radius:16px;">',
    '<img src="slide_02_scopes_nobg.png" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:90%; object-fit:contain; opacity:1;">'
)
w("slide_02_variant.html", s2)
print("Slide 2 patched")

# SLIDE 3
s3 = r("slide_03_variant.html")
s3 = s3.replace(
    '<img src="slide_03_companion.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; object-position:60% center; opacity:0.35; border-radius:24px;">',
    '<img src="slide_03_companion_nobg.png" style="position:absolute; bottom:0; left:50%; transform:translateX(-50%); width:85%; object-fit:contain; opacity:0.92;">'
)
w("slide_03_variant.html", s3)
print("Slide 3 patched")

# SLIDE 4
s4 = r("slide_04_variant.html")
s4 = s4.replace(
    '<img src="slide_04_timeline.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:contain; object-position:center; opacity:0.55; border-radius:16px; z-index:0;">',
    '<img src="slide_04_timeline_nobg.png" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); height:95%; object-fit:contain; opacity:0.95; z-index:0;">'
)
w("slide_04_variant.html", s4)
print("Slide 4 patched")

# SLIDE 5
s5 = r("slide_05_variant.html")
s5 = s5.replace(
    '            background-image: url("slide_05_steps.png");\n'
    '            background-size: cover;\n'
    '            background-position: center;\n',
    ""
)
s5 = s5.replace(
    '<div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(236,253,245,0.92) 0%, rgba(254,252,232,0.90) 35%, rgba(240,253,244,0.92) 70%, rgba(220,252,231,0.94) 100%); z-index:0;"></div>',
    '<img src="slide_05_steps_nobg.png" style="position:absolute; right:-40px; bottom:-20px; height:75%; object-fit:contain; opacity:0.18; z-index:0; pointer-events:none;">'
)
w("slide_05_variant.html", s5)
print("Slide 5 patched")

# SLIDE 6
s6 = r("slide_06_variant.html")
s6 = s6.replace(
    '<img src="slide_06_architecture.png" style="width:100%; height:100%; object-fit:contain; object-position:center; display:block; background:rgba(255,255,255,0.5);">',
    '<img src="slide_06_architecture_nobg.png" style="width:100%; height:100%; object-fit:contain; object-position:center; display:block;">'
)
w("slide_06_variant.html", s6)
print("Slide 6 patched")

# SLIDE 7
s7 = r("slide_07_variant.html")
s7 = s7.replace(
    '<img src="slide_07_crystal_ball.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; object-position:40% center; opacity:0.30; border-radius:18px;">',
    '<img src="slide_07_crystal_ball_nobg.png" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:90%; object-fit:contain; opacity:0.90;">'
)
w("slide_07_variant.html", s7)
print("Slide 7 patched")

# SLIDE 8
s8 = r("slide_08_variant.html")
s8 = s8.replace(
    '            background-image: url("slide_08_oed_pillars.png");\n'
    '            background-size: cover;\n'
    '            background-position: center;\n',
    ""
)
s8 = s8.replace(
    '<div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(236,253,245,0.88) 0%, rgba(254,252,232,0.86) 35%, rgba(240,253,244,0.88) 70%, rgba(220,252,231,0.90) 100%); z-index:0;"></div>',
    '<img src="slide_08_oed_pillars_nobg.png" style="position:absolute; right:-30px; bottom:-10px; height:80%; object-fit:contain; opacity:0.20; z-index:0; pointer-events:none;">'
)
w("slide_08_variant.html", s8)
print("Slide 8 patched")

print("Done.")
