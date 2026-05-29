"""
Remove backgrounds from Terra slide images and update HTML files.

Panel slides (2,3,4,6,7): images placed in columns — rembg lets them float at full opacity.
Hero/icon slides (1,5,8): rembg lets us position illustrations properly without bg clash.
Scene slides (9,10,11): rich landscape scenes — keep as full background, no rembg needed.
"""
import os
from pathlib import Path
from PIL import Image
from rembg import remove

DIR = Path(__file__).parent

def rembg_image(src_name, dst_name):
    src = DIR / src_name
    dst = DIR / dst_name
    print(f"  Processing {src_name} -> {dst_name} ...", end=" ", flush=True)
    with open(src, "rb") as f:
        data = f.read()
    result = remove(data)
    with open(dst, "wb") as f:
        f.write(result)
    print("done")

def read_html(name):
    return (DIR / name).read_text(encoding="utf-8")

def write_html(name, content):
    (DIR / name).write_text(content, encoding="utf-8")

# ── Step 1: generate nobg PNGs ─────────────────────────────────────────────
print("=== Removing backgrounds ===")
targets = [
    ("slide_01_hero.png",          "slide_01_hero_nobg.png"),
    ("slide_02_scopes.png",        "slide_02_scopes_nobg.png"),
    ("slide_03_companion.png",     "slide_03_companion_nobg.png"),
    ("slide_04_timeline.png",      "slide_04_timeline_nobg.png"),
    ("slide_05_steps.png",         "slide_05_steps_nobg.png"),
    ("slide_06_architecture.png",  "slide_06_architecture_nobg.png"),
    ("slide_07_crystal_ball.png",  "slide_07_crystal_ball_nobg.png"),
    ("slide_08_oed_pillars.png",   "slide_08_oed_pillars_nobg.png"),
]
for src, dst in targets:
    rembg_image(src, dst)

# ── Step 2: patch HTML files ───────────────────────────────────────────────
print("\n=== Patching HTML files ===")

# ------------------------------------------------------------------
# SLIDE 1 — hero: switch from full-bg to right-side positioned PNG
# ------------------------------------------------------------------
s1 = read_html("slide_01_variant.html")
# Remove background-image from .slide-container CSS
s1 = s1.replace(
    '            background-image: url("slide_01_hero.png");\n'
    '            background-size: cover;\n'
    '            background-position: center;\n',
    ""
)
# Remove the existing gradient overlay div (was for bg image)
s1 = s1.replace(
    '        <div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(100deg, rgba(236,253,245,0.95) 0%, rgba(236,253,245,0.80) 40%, rgba(236,253,245,0.50) 70%, rgba(236,253,245,0.20) 100%); z-index:0;"></div>\n',
    ""
)
# Un-hide illustration-area and replace with positioned img
s1 = s1.replace(
    ".illustration-area { display: none !important; /* using real image background */",
    ".illustration-area { /* illustration positioned on right */"
)
# Replace the illustration-area inner content with the nobg PNG
old_illus = """        <!-- Right illustration -->
        <div class="illustration-area">
            <div class="globe-container">
                <div class="orbit-ring">
                    <div class="orbit-item">☀️</div>
                    <div class="orbit-item">💨</div>
                    <div class="orbit-item">🎬</div>
                    <div class="orbit-item">⚡</div>
                </div>
                <div class="globe">
                    <div class="continent continent-1"></div>
                    <div class="continent continent-2"></div>
                    <div class="continent continent-3"></div>
                    <div class="continent continent-4"></div>
                </div>
                <div class="leaf-character">🌿</div>
            </div>
        </div>"""
new_illus = """        <!-- Right illustration -->
        <div class="illustration-area">
            <img src="slide_01_hero_nobg.png"
                 style="width:100%; height:100%; object-fit:contain; object-position:center; display:block;">
        </div>"""
s1 = s1.replace(old_illus, new_illus)
# Make illustration-area properly visible and sized
s1 = s1.replace(
    """        .illustration-area { /* illustration positioned on right */
            position: absolute;
            right: 60px;
            top: 50%;
            transform: translateY(-50%);
            width: 420px;
            height: 420px;
            display: flex;
            align-items: center;
            justify-content: center;
        }""",
    """        .illustration-area {
            position: absolute;
            right: 40px;
            top: 50%;
            transform: translateY(-50%);
            width: 480px;
            height: 480px;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 5;
        }"""
)
write_html("slide_01_variant.html", s1)
print("  Slide 1: hero → positioned nobg PNG on right")

# ------------------------------------------------------------------
# SLIDE 2 — scopes planets in right column
# ------------------------------------------------------------------
s2 = read_html("slide_02_variant.html")
s2 = s2.replace(
    '<img src="slide_02_scopes.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:contain; object-position:center; opacity:1; border-radius:16px;">',
    '<img src="slide_02_scopes_nobg.png" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:90%; object-fit:contain; opacity:1;">'
)
write_html("slide_02_variant.html", s2)
print("  Slide 2: scopes → centered nobg PNG")

# ------------------------------------------------------------------
# SLIDE 3 — companion character in right section
# ------------------------------------------------------------------
s3 = read_html("slide_03_variant.html")
s3 = s3.replace(
    '<img src="slide_03_companion.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; object-position:60% center; opacity:0.35; border-radius:24px;">',
    '<img src="slide_03_companion_nobg.png" style="position:absolute; bottom:0; left:50%; transform:translateX(-50%); width:85%; object-fit:contain; opacity:0.92;">'
)
write_html("slide_03_variant.html", s3)
print("  Slide 3: companion → bottom-anchored nobg PNG at 0.92 opacity")

# ------------------------------------------------------------------
# SLIDE 4 — timeline in left column
# ------------------------------------------------------------------
s4 = read_html("slide_04_variant.html")
s4 = s4.replace(
    '<img src="slide_04_timeline.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:contain; object-position:center; opacity:0.55; border-radius:16px; z-index:0;">',
    '<img src="slide_04_timeline_nobg.png" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); height:95%; object-fit:contain; opacity:0.95; z-index:0;">'
)
write_html("slide_04_variant.html", s4)
print("  Slide 4: timeline → centered nobg PNG at 0.95 opacity")

# ------------------------------------------------------------------
# SLIDE 5 — steps icons: switch from full-bg to centred floating element
# ------------------------------------------------------------------
s5 = read_html("slide_05_variant.html")
# Remove background-image from .slide-container
s5 = s5.replace(
    '            background-image: url("slide_05_steps.png");\n'
    '            background-size: cover;\n'
    '            background-position: center;\n',
    ""
)
# Replace overlay with a lighter one that won't fight the gradient
s5 = s5.replace(
    '<div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(236,253,245,0.92) 0%, rgba(254,252,232,0.90) 35%, rgba(240,253,244,0.92) 70%, rgba(220,252,231,0.94) 100%); z-index:0;"></div>',
    '<img src="slide_05_steps_nobg.png" style="position:absolute; right:-40px; bottom:-20px; height:75%; object-fit:contain; opacity:0.18; z-index:0; pointer-events:none;">'
)
write_html("slide_05_variant.html", s5)
print("  Slide 5: steps → subtle ghost in bottom-right corner")

# ------------------------------------------------------------------
# SLIDE 6 — architecture cubes in container
# ------------------------------------------------------------------
s6 = read_html("slide_06_variant.html")
s6 = s6.replace(
    '<img src="slide_06_architecture.png" style="width:100%; height:100%; object-fit:contain; object-position:center; display:block; background:rgba(255,255,255,0.5);">',
    '<img src="slide_06_architecture_nobg.png" style="width:100%; height:100%; object-fit:contain; object-position:center; display:block;">'
)
write_html("slide_06_variant.html", s6)
print("  Slide 6: architecture → nobg PNG, bg removed from container")

# ------------------------------------------------------------------
# SLIDE 7 — crystal ball in right section
# ------------------------------------------------------------------
s7 = read_html("slide_07_variant.html")
s7 = s7.replace(
    '<img src="slide_07_crystal_ball.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; object-position:40% center; opacity:0.30; border-radius:18px;">',
    '<img src="slide_07_crystal_ball_nobg.png" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:90%; object-fit:contain; opacity:0.90;">'
)
write_html("slide_07_variant.html", s7)
print("  Slide 7: crystal ball → centered nobg PNG at 0.90 opacity")

# ------------------------------------------------------------------
# SLIDE 8 — OED pillars: switch from full-bg to right-side element
# ------------------------------------------------------------------
s8 = read_html("slide_08_variant.html")
# Remove background-image from .slide-container
s8 = s8.replace(
    '            background-image: url("slide_08_oed_pillars.png");\n'
    '            background-size: cover;\n'
    '            background-position: center;\n',
    ""
)
# Replace overlay with the nobg positioned image
s8 = s8.replace(
    '<div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(236,253,245,0.88) 0%, rgba(254,252,232,0.86) 35%, rgba(240,253,244,0.88) 70%, rgba(220,252,231,0.90) 100%); z-index:0;"></div>',
    '<img src="slide_08_oed_pillars_nobg.png" style="position:absolute; right:-30px; bottom:-10px; height:80%; object-fit:contain; opacity:0.20; z-index:0; pointer-events:none;">'
)
write_html("slide_08_variant.html", s8)
print("  Slide 8: pillars → subtle ghost in bottom-right corner")

print("\n=== All done! ===")
