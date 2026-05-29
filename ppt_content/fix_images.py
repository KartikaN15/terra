"""Fix image integration issues in Terra HTML slides."""
import os
import re

PPT_DIR = os.path.dirname(os.path.abspath(__file__))

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# ============================================================
# SLIDE 1: Title — hero image as full background
# ============================================================
s1 = read_file(os.path.join(PPT_DIR, 'slide_01_variant.html'))
# Remove old gradient background on .slide-container, keep only image
s1 = re.sub(
    r'\.slide-container \{[^}]*background: linear-gradient\(160deg, #ecfdf5 0%, #fefce8 35%, #f0fdf4 70%, #dcfce7 100%\);[^}]*\}',
    '.slide-container {\n            width: 1280px;\n            height: 720px;\n            background-image: url("slide_01_hero.png");\n            background-size: cover;\n            background-position: center;\n            border-radius: 24px;\n            box-shadow: 0 24px 80px -20px rgba(6, 95, 70, 0.15), 0 8px 24px -12px rgba(16, 24, 40, 0.08);\n            position: relative;\n            overflow: hidden;\n            padding: 80px;\n            display: flex;\n            align-items: center;\n        }',
    s1, count=1
)
# Remove any duplicate background-image declarations
s1 = re.sub(r'background-image: url\(\'slide_01_hero\.png\'\); background-size: cover; background-position: center;', '', s1, count=1)
# Fix overlay to cover whole slide
s1 = s1.replace(
    '<div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(90deg, rgba(236,253,245,0.92) 0%, rgba(236,253,245,0.75) 45%, rgba(236,253,245,0.3) 100%); z-index:0;"></div>',
    '<div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(100deg, rgba(236,253,245,0.95) 0%, rgba(236,253,245,0.80) 40%, rgba(236,253,245,0.50) 70%, rgba(236,253,245,0.20) 100%); z-index:0;"></div>'
)
# Ensure content z-index
s1 = s1.replace('.content {\n            position: relative; z-index: 1;', '.content {\n            position: relative; z-index: 1;')
s1 = s1.replace('.illustration-area { display: none;', '.illustration-area { display: none !important;')
write_file(os.path.join(PPT_DIR, 'slide_01_variant.html'), s1)
print('Slide 1: fixed hero background')

# ============================================================
# SLIDE 2: Sustainability — scopes image in right column
# ============================================================
s2 = read_file(os.path.join(PPT_DIR, 'slide_02_variant.html'))
# Fix the planets container to show image properly
old_right = '''            <div class="right-col">
                <div class="planets-container" style="position:relative;">
                    <img src="slide_02_scopes.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:contain; opacity:0.95; z-index:0;">
                    <div style="position:relative; z-index:1; margin-top:auto;">
                        <div class="analogy-box">
                            "Trying to reduce your carbon footprint without data is like trying to save money without looking at your bank statement."
                        </div>
                    </div>
                </div>
            </div>'''
new_right = '''            <div class="right-col" style="position:relative;">
                <img src="slide_02_scopes.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:contain; object-position:center; opacity:1; border-radius:16px;">
                <div style="position:relative; z-index:1; margin-top:auto;">
                    <div class="analogy-box">
                        "Trying to reduce your carbon footprint without data is like trying to save money without looking at your bank statement."
                    </div>
                </div>
            </div>'''
s2 = s2.replace(old_right, new_right)
write_file(os.path.join(PPT_DIR, 'slide_02_variant.html'), s2)
print('Slide 2: fixed scopes image')

# ============================================================
# SLIDE 3: What is Terra — companion image as right section bg
# ============================================================
s3 = read_file(os.path.join(PPT_DIR, 'slide_03_variant.html'))
# Clean up old empty bg reference
s3 = re.sub(r'background-image: url\(\'\'\);\s*', '', s3)
# Fix the image to be visible and well-positioned
s3 = s3.replace(
    '<img src="slide_03_companion.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; opacity:0.2; border-radius:24px;">',
    '<img src="slide_03_companion.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; object-position:60% center; opacity:0.35; border-radius:24px;">'
)
write_file(os.path.join(PPT_DIR, 'slide_03_variant.html'), s3)
print('Slide 3: fixed companion image')

# ============================================================
# SLIDE 4: Atomic Diary — timeline image as left column bg
# ============================================================
s4 = read_file(os.path.join(PPT_DIR, 'slide_04_variant.html'))
# The timeline image is portrait (1536x2752) in a landscape column. Use object-fit:contain instead.
s4 = s4.replace(
    '<img src="slide_04_timeline.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; object-position:center; opacity:0.18; border-radius:16px; z-index:0;">',
    '<img src="slide_04_timeline.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:contain; object-position:center; opacity:0.55; border-radius:16px; z-index:0;">'
)
write_file(os.path.join(PPT_DIR, 'slide_04_variant.html'), s4)
print('Slide 4: fixed timeline image (portrait->contain, higher opacity)')

# ============================================================
# SLIDE 5: How Terra Works — steps image as full background
# ============================================================
s5 = read_file(os.path.join(PPT_DIR, 'slide_05_variant.html'))
# Remove old technical diagram references
s5 = re.sub(r'background-image: url\(\'\.\./images/[^\']+\'\);', '', s5)
# Remove empty bg divs
s5 = re.sub(r'<div class="slide-bg-image"></div>', '', s5)
# Remove old confidence story image if still there
s5 = re.sub(r'<div style="margin-top:10px;[^>]*>\s*<img src="[^"]*07-audit[^"]*"[^>]*>\s*</div>', '', s5)
# Fix slide-container: remove inline style and set proper CSS
s5 = re.sub(
    r'<div class="slide-container" style="background-image: url\(\'slide_05_steps\.png\'\); background-size: cover; background-position: center;">',
    '<div class="slide-container">',
    s5
)
# Replace the .slide-container CSS rule completely
old_s5_container = re.search(r'\.slide-container \{[^}]*\}', s5).group(0)
new_s5_container = '''.slide-container {
            width: 1280px;
            height: 720px;
            background-image: url("slide_05_steps.png");
            background-size: cover;
            background-position: center;
            border-radius: 24px;
            box-shadow: 0 24px 80px -20px rgba(6, 95, 70, 0.15), 0 8px 24px -12px rgba(16, 24, 40, 0.08);
            position: relative;
            overflow: hidden;
            padding: 60px 80px;
            display: flex;
            flex-direction: column;
        }'''
s5 = s5.replace(old_s5_container, new_s5_container, 1)
# Ensure overlay exists
if '<div style="position:absolute; top:0; left:0; right:0; bottom:0;' not in s5:
    s5 = s5.replace(
        '<div class="slide-container">',
        '<div class="slide-container">\n        <div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(236,253,245,0.92) 0%, rgba(254,252,232,0.90) 35%, rgba(240,253,244,0.92) 70%, rgba(220,252,231,0.94) 100%); z-index:0;"></div>'
    )
# Ensure content z-index
s5 = s5.replace('.header {', '.header { position: relative; z-index: 1;')
s5 = s5.replace('.formula-bar {', '.formula-bar { position: relative; z-index: 1;')
s5 = s5.replace('.steps-container {', '.steps-container { position: relative; z-index: 1;')
write_file(os.path.join(PPT_DIR, 'slide_05_variant.html'), s5)
print('Slide 5: fixed steps background, removed old refs')

# ============================================================
# SLIDE 6: Architecture — architecture image replacing ER
# ============================================================
s6 = read_file(os.path.join(PPT_DIR, 'slide_06_variant.html'))
# The image is currently in a 180px height container - too small. Make it bigger.
s6 = s6.replace(
    '<div class="er-diagram-container" style="border-radius:20px; overflow:hidden; height:180px;">\n                    <img src="slide_06_architecture.png" style="width:100%; height:100%; object-fit:cover; object-position:center; display:block;">\n                </div>',
    '<div class="er-diagram-container" style="border-radius:20px; overflow:hidden; height:220px; border:1px solid rgba(16,185,129,0.15);">\n                    <img src="slide_06_architecture.png" style="width:100%; height:100%; object-fit:contain; object-position:center; display:block; background:rgba(255,255,255,0.5);">\n                </div>'
)
write_file(os.path.join(PPT_DIR, 'slide_06_variant.html'), s6)
print('Slide 6: fixed architecture image size and fit')

# ============================================================
# SLIDE 7: ML Engine — crystal ball image as right section bg
# ============================================================
s7 = read_file(os.path.join(PPT_DIR, 'slide_07_variant.html'))
# Remove old technical diagram references
s7 = re.sub(r'background-image: url\(\'\.\./images/[^\']+\'\);', '', s7)
s7 = re.sub(r'<div class="slide-bg-image"></div>', '', s7)
# Fix crystal ball image
s7 = s7.replace(
    '<img src="slide_07_crystal_ball.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; opacity:0.15; border-radius:18px;">',
    '<img src="slide_07_crystal_ball.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; object-position:40% center; opacity:0.30; border-radius:18px;">'
)
write_file(os.path.join(PPT_DIR, 'slide_07_variant.html'), s7)
print('Slide 7: fixed crystal ball, removed old refs')

# ============================================================
# SLIDE 8: OED Playbook — pillars image as full background
# ============================================================
s8 = read_file(os.path.join(PPT_DIR, 'slide_08_variant.html'))
# Remove old technical diagram references
s8 = re.sub(r'background-image: url\(\'\.\./images/[^\']+\'\);', '', s8)
s8 = re.sub(r'<div class="slide-bg-image"></div>', '', s8)
# Fix slide-container
s8 = re.sub(
    r'<div class="slide-container" style="background-image: url\(\'slide_08_oed_pillars\.png\'\); background-size: cover; background-position: center;">',
    '<div class="slide-container">',
    s8
)
old_s8_container = re.search(r'\.slide-container \{[^}]*\}', s8).group(0)
new_s8_container = '''.slide-container {
            width: 1280px;
            height: 720px;
            background-image: url("slide_08_oed_pillars.png");
            background-size: cover;
            background-position: center;
            border-radius: 24px;
            box-shadow: 0 24px 80px -20px rgba(6, 95, 70, 0.15), 0 8px 24px -12px rgba(16, 24, 40, 0.08);
            position: relative;
            overflow: hidden;
            padding: 60px 80px;
            display: flex;
            flex-direction: column;
        }'''
s8 = s8.replace(old_s8_container, new_s8_container, 1)
if '<div style="position:absolute; top:0; left:0; right:0; bottom:0;' not in s8:
    s8 = s8.replace(
        '<div class="slide-container">',
        '<div class="slide-container">\n        <div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(236,253,245,0.88) 0%, rgba(254,252,232,0.86) 35%, rgba(240,253,244,0.88) 70%, rgba(220,252,231,0.90) 100%); z-index:0;"></div>'
    )
s8 = s8.replace('.header {', '.header { position: relative; z-index: 1;')
s8 = s8.replace('.philosophy {', '.philosophy { position: relative; z-index: 1;')
s8 = s8.replace('.pillars-container {', '.pillars-container { position: relative; z-index: 1;')
write_file(os.path.join(PPT_DIR, 'slide_08_variant.html'), s8)
print('Slide 8: fixed OED pillars background, removed old refs')

# ============================================================
# SLIDE 9: Atomic to Global — scale image as full background
# ============================================================
s9 = read_file(os.path.join(PPT_DIR, 'slide_09_variant.html'))
s9 = re.sub(
    r'<div class="slide-container" style="background-image: url\(\'slide_09_scale\.png\'\); background-size: cover; background-position: center;">',
    '<div class="slide-container">',
    s9
)
old_s9_container = re.search(r'\.slide-container \{[^}]*\}', s9).group(0)
new_s9_container = '''.slide-container {
            width: 1280px;
            height: 720px;
            background-image: url("slide_09_scale.png");
            background-size: cover;
            background-position: center;
            border-radius: 24px;
            box-shadow: 0 24px 80px -20px rgba(6, 95, 70, 0.15), 0 8px 24px -12px rgba(16, 24, 40, 0.08);
            position: relative;
            overflow: hidden;
            padding: 60px 80px;
            display: flex;
            flex-direction: column;
        }'''
s9 = s9.replace(old_s9_container, new_s9_container, 1)
if '<div style="position:absolute; top:0; left:0; right:0; bottom:0;' not in s9:
    s9 = s9.replace(
        '<div class="slide-container">',
        '<div class="slide-container">\n        <div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(236,253,245,0.90) 0%, rgba(254,252,232,0.88) 40%, rgba(240,253,244,0.90) 70%, rgba(220,252,231,0.92) 100%); z-index:0;"></div>'
    )
s9 = s9.replace('.header {', '.header { position: relative; z-index: 1;')
s9 = s9.replace('.content-area {', '.content-area { position: relative; z-index: 1;')
write_file(os.path.join(PPT_DIR, 'slide_09_variant.html'), s9)
print('Slide 9: fixed scale background')

# ============================================================
# SLIDE 10: Long Run Vision — roadmap image as full background
# ============================================================
s10 = read_file(os.path.join(PPT_DIR, 'slide_10_variant.html'))
s10 = re.sub(r'background-image: url\(\'\.\./images/[^\']+\'\);', '', s10)
s10 = re.sub(r'<div class="slide-bg-image"></div>', '', s10)
s10 = re.sub(
    r'<div class="slide-container" style="background-image: url\(\'slide_10_roadmap\.png\'\); background-size: cover; background-position: center;">',
    '<div class="slide-container">',
    s10
)
old_s10_container = re.search(r'\.slide-container \{[^}]*\}', s10).group(0)
new_s10_container = '''.slide-container {
            width: 1280px;
            height: 720px;
            background-image: url("slide_10_roadmap.png");
            background-size: cover;
            background-position: center;
            border-radius: 24px;
            box-shadow: 0 24px 80px -20px rgba(6, 95, 70, 0.15), 0 8px 24px -12px rgba(16, 24, 40, 0.08);
            position: relative;
            overflow: hidden;
            padding: 60px 80px;
            display: flex;
            flex-direction: column;
        }'''
s10 = s10.replace(old_s10_container, new_s10_container, 1)
if '<div style="position:absolute; top:0; left:0; right:0; bottom:0;' not in s10:
    s10 = s10.replace(
        '<div class="slide-container">',
        '<div class="slide-container">\n        <div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(236,253,245,0.88) 0%, rgba(254,252,232,0.86) 35%, rgba(240,253,244,0.88) 70%, rgba(220,252,231,0.90) 100%); z-index:0;"></div>'
    )
s10 = s10.replace('.header {', '.header { position: relative; z-index: 1;')
s10 = s10.replace('.content-area {', '.content-area { position: relative; z-index: 1;')
write_file(os.path.join(PPT_DIR, 'slide_10_variant.html'), s10)
print('Slide 10: fixed roadmap background, removed old refs')

# ============================================================
# SLIDE 11: Closing — closing image as full background
# ============================================================
s11 = read_file(os.path.join(PPT_DIR, 'slide_11_variant.html'))
# Fix slide-container CSS
old_s11_container = re.search(r'\.slide-container \{[^}]*\}', s11).group(0)
new_s11_container = '''.slide-container {
            width: 1280px;
            height: 720px;
            background-image: url("slide_11_closing.png");
            background-size: cover;
            background-position: center;
            border-radius: 24px;
            box-shadow: 0 24px 80px -20px rgba(6, 95, 70, 0.3), 0 8px 24px -12px rgba(16, 24, 40, 0.15);
            position: relative;
            overflow: hidden;
            padding: 60px 80px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }'''
s11 = s11.replace(old_s11_container, new_s11_container, 1)
# Remove old gradient background declarations
s11 = re.sub(r'background: linear-gradient\(160deg, #065f46 0%, #047857 30%, #059669 60%, #10b981 100%\);', '', s11)
# Fix overlay
s11 = s11.replace(
    '<div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(6,95,70,0.85) 0%, rgba(4,120,87,0.80) 30%, rgba(5,150,105,0.75) 60%, rgba(16,185,129,0.70) 100%); z-index:0;"></div>',
    '<div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(6,95,70,0.82) 0%, rgba(4,120,87,0.75) 30%, rgba(5,150,105,0.70) 60%, rgba(16,185,129,0.65) 100%); z-index:0;"></div>'
)
s11 = s11.replace('.content {', '.content { position: relative; z-index: 1;')
write_file(os.path.join(PPT_DIR, 'slide_11_variant.html'), s11)
print('Slide 11: fixed closing background')

# Final verification: ensure no ../images/ references remain
print('\n--- Checking for leftover old references ---')
for i in range(1, 12):
    fname = f'slide_{i:02d}_variant.html'
    content = read_file(os.path.join(PPT_DIR, fname))
    if '../images/' in content:
        print(f'WARNING: {fname} still has ../images/ references!')
    else:
        print(f'OK: {fname}')

print('\nAll fixes applied!')
