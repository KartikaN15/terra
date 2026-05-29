"""Rename and integrate Gemini-generated clay-render images into Terra HTML slides."""
import os
import re
import shutil

PPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Mapping: original filename -> renamed filename + target slide
IMAGE_MAP = {
    'Gemini_Generated_Image_6q07xy6q07xy6q07.png':  'slide_01_hero.png',         # Title: Earth + character
    'Gemini_Generated_Image_cbp9u7cbp9u7cbp9.png':  'slide_02_scopes.png',       # Scopes: 3 stacked planets
    'Gemini_Generated_Image_swalpjswalpjswal.png':  'slide_03_companion.png',    # What is Terra: character on hill
    'Gemini_Generated_Image_whx21mwhx21mwhx2.png':  'slide_04_timeline.png',     # Diary: vertical timeline (portrait)
    'Gemini_Generated_Image_7stvtb7stvtb7stv.png':  'slide_05_steps.png',        # How it works: 4 connected cards
    'Gemini_Generated_Image_mlwgusmlwgusmlwg.png':  'slide_06_architecture.png', # Architecture: 4 modules
    'Gemini_Generated_Image_gcqawegcqawegcqa.png':  'slide_07_crystal_ball.png', # ML: crystal ball
    'Gemini_Generated_Image_zhx80zzhx80zzhx8.png':  'slide_08_oed_pillars.png',  # OED: 3 pillars
    'Gemini_Generated_Image_k5ouzlk5ouzlk5ou.png':  'slide_09_scale.png',        # Scale: zoom out
    'Gemini_Generated_Image_gz24f3gz24f3gz24.png':  'slide_10_roadmap.png',      # Vision: winding road
    'Gemini_Generated_Image_xbyattxbyattxbya.png':  'slide_11_closing.png',      # Closing: transformed Earth
}

# Rename files
for old_name, new_name in IMAGE_MAP.items():
    old_path = os.path.join(PPT_DIR, old_name)
    new_path = os.path.join(PPT_DIR, new_name)
    if os.path.exists(old_path):
        shutil.move(old_path, new_path)
        print(f'Renamed: {old_name} -> {new_name}')
    else:
        print(f'Warning: {old_name} not found')

# Helper to read/write files
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
# Remove old technical diagram reference if any
s1 = re.sub(r'background-image: url\(\'\.\./images/[^\']+\'\);', '', s1)
s1 = re.sub(r'<div class="right-bg-image"></div>', '', s1)

# Replace slide-container background with image
s1 = s1.replace(
    'background: linear-gradient(160deg, #ecfdf5 0%, #fefce8 35%, #f0fdf4 70%, #dcfce7 100%);',
    "background-image: url('slide_01_hero.png'); background-size: cover; background-position: center;"
)
# Add semi-transparent overlay for text readability
s1 = s1.replace(
    '<div class="slide-container">',
    '<div class="slide-container">\n        <div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(90deg, rgba(236,253,245,0.92) 0%, rgba(236,253,245,0.75) 45%, rgba(236,253,245,0.3) 100%); z-index:0;"></div>'
)
# Make content and illustration area relative
s1 = s1.replace('.content {', '.content { position: relative; z-index: 1;')
s1 = s1.replace('.illustration-area {', '.illustration-area { display: none; /* using real image background */')
write_file(os.path.join(PPT_DIR, 'slide_01_variant.html'), s1)
print('Slide 1: hero image as full background')

# ============================================================
# SLIDE 2: Sustainability Crisis — scopes image in right column
# ============================================================
s2 = read_file(os.path.join(PPT_DIR, 'slide_02_variant.html'))
# Remove old planets CSS and replace with image
old_planets = '''                <div class="planets-container">
                    <div class="connector-ribbon"></div>
                    <div class="carbon-particle" style="left:20%;bottom:30%;animation-delay:0s;"></div>
                    <div class="carbon-particle" style="left:45%;bottom:20%;animation-delay:1s;"></div>
                    <div class="carbon-particle" style="left:70%;bottom:40%;animation-delay:2s;"></div>
                    <div class="carbon-particle" style="left:35%;bottom:50%;animation-delay:0.5s;"></div>

                    <div class="planet-row">
                        <span class="planet-label">Scope 1</span>
                        <div class="planet scope1">
                            <div class="planet-items">⛽🚛</div>
                        </div>
                        <span style="font-size:13px;color:#6b7280;">Direct emissions</span>
                    </div>
                    <div class="planet-row">
                        <span class="planet-label">Scope 2</span>
                        <div class="planet scope2">
                            <div class="planet-items">⚡🔌</div>
                        </div>
                        <span style="font-size:13px;color:#6b7280;">Purchased energy</span>
                    </div>
                    <div class="planet-row">
                        <span class="planet-label">Scope 3</span>
                        <div class="planet scope3">
                            <div class="planet-items">✈️🛍️</div>
                        </div>
                        <span style="font-size:13px;color:#6b7280;">Value chain</span>
                    </div>

                    <div class="analogy-box">
                        "Trying to reduce your carbon footprint without data is like trying to save money without looking at your bank statement."
                    </div>
                </div>'''
new_planets = '''                <div class="planets-container" style="position:relative;">
                    <img src="slide_02_scopes.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:contain; opacity:0.95; z-index:0;">
                    <div style="position:relative; z-index:1; margin-top:auto;">
                        <div class="analogy-box">
                            "Trying to reduce your carbon footprint without data is like trying to save money without looking at your bank statement."
                        </div>
                    </div>
                </div>'''
s2 = s2.replace(old_planets, new_planets)
write_file(os.path.join(PPT_DIR, 'slide_02_variant.html'), s2)
print('Slide 2: scopes image in right column')

# ============================================================
# SLIDE 3: What is Terra — companion image as right section background
# ============================================================
s3 = read_file(os.path.join(PPT_DIR, 'slide_03_variant.html'))
# Remove old bg reference
s3 = re.sub(r'background-image: url\(\'\.\./images/[^\']+\'\);', '', s3)
s3 = s3.replace(
    '<div class="right-section" style="position:relative;">\n                <div class="right-bg-image"></div>',
    '<div class="right-section" style="position:relative;">\n                <img src="slide_03_companion.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; opacity:0.2; border-radius:24px;">'
)
write_file(os.path.join(PPT_DIR, 'slide_03_variant.html'), s3)
print('Slide 3: companion image as right section background')

# ============================================================
# SLIDE 4: Atomic Diary — timeline image in left column
# ============================================================
s4 = read_file(os.path.join(PPT_DIR, 'slide_04_variant.html'))
# Replace timeline CSS with image
old_timeline = '''            <div class="timeline-col">
                <div class="timeline-line"></div>

                <div class="timeline-item">'''
new_timeline = '''            <div class="timeline-col" style="position:relative;">
                <img src="slide_04_timeline.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; object-position:center; opacity:0.18; border-radius:16px; z-index:0;">
                <div class="timeline-line" style="z-index:1;"></div>

                <div class="timeline-item" style="position:relative; z-index:1;">'''
s4 = s4.replace(old_timeline, new_timeline)
# Add z-index to all timeline items and daily total
s4 = s4.replace('<div class="timeline-item">', '<div class="timeline-item" style="position:relative; z-index:1;">')
s4 = s4.replace('<div class="daily-total">', '<div class="daily-total" style="position:relative; z-index:1;">')
write_file(os.path.join(PPT_DIR, 'slide_04_variant.html'), s4)
print('Slide 4: timeline image as left column background')

# ============================================================
# SLIDE 5: How Terra Works — steps image as full background
# ============================================================
s5 = read_file(os.path.join(PPT_DIR, 'slide_05_variant.html'))
# Remove old diagram references
s5 = re.sub(r'background-image: url\(\'\.\./images/[^\']+\'\);\s*opacity: [\d.]+;', '', s5)
s5 = re.sub(r'<div class="slide-bg-image"></div>', '', s5)
s5 = re.sub(r'<img src="\.\./images/07-audit-confidence-story\.png"[^>]+>', '', s5)
# Add new background
s5 = s5.replace(
    '<div class="slide-container">',
    '<div class="slide-container" style="background-image: url(\'slide_05_steps.png\'); background-size: cover; background-position: center;">\n        <div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(236,253,245,0.90) 0%, rgba(254,252,232,0.88) 35%, rgba(240,253,244,0.90) 70%, rgba(220,252,231,0.92) 100%); z-index:0;"></div>'
)
# Make header and content relative
s5 = s5.replace('.header {', '.header { position: relative; z-index: 1;')
s5 = s5.replace('.formula-bar {', '.formula-bar { position: relative; z-index: 1;')
s5 = s5.replace('.steps-container {', '.steps-container { position: relative; z-index: 1;')
write_file(os.path.join(PPT_DIR, 'slide_05_variant.html'), s5)
print('Slide 5: steps image as full background')

# ============================================================
# SLIDE 6: Architecture — architecture image replacing ER diagram
# ============================================================
s6 = read_file(os.path.join(PPT_DIR, 'slide_06_variant.html'))
# Remove old diagram
s6 = re.sub(r'<img src="\.\./images/04-domain-model-er\.png"[^>]+>', '', s6)
old_er = '''                <div class="er-diagram-container" style="background:rgba(255,255,255,0.85); backdrop-filter:blur(12px); border:1px solid rgba(16,185,129,0.15); border-radius:20px; padding:16px; overflow:hidden;">
                    
                </div>'''
new_er = '''                <div class="er-diagram-container" style="border-radius:20px; overflow:hidden; height:180px;">
                    <img src="slide_06_architecture.png" style="width:100%; height:100%; object-fit:cover; object-position:center; display:block;">
                </div>'''
s6 = s6.replace(old_er, new_er)
write_file(os.path.join(PPT_DIR, 'slide_06_variant.html'), s6)
print('Slide 6: architecture image replacing ER diagram')

# ============================================================
# SLIDE 7: ML Engine — crystal ball image as right section background
# ============================================================
s7 = read_file(os.path.join(PPT_DIR, 'slide_07_variant.html'))
# Remove old references
s7 = re.sub(r'background-image: url\(\'\.\./images/[^\']+\'\);\s*opacity: [\d.]+;', '', s7)
s7 = re.sub(r'<div class="slide-bg-image"></div>', '', s7)
s7 = re.sub(r'<img src="\.\./images/08-story-greenlight-to-report\.png"[^>]+>', '', s7)
# Add crystal ball image to the data-col (right side)
s7 = s7.replace(
    '<div class="data-col">',
    '<div class="data-col" style="position:relative;">\n                <img src="slide_07_crystal_ball.png" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; opacity:0.15; border-radius:18px;">'
)
write_file(os.path.join(PPT_DIR, 'slide_07_variant.html'), s7)
print('Slide 7: crystal ball image as right section background')

# ============================================================
# SLIDE 8: OED Playbook — pillars image as full background
# ============================================================
s8 = read_file(os.path.join(PPT_DIR, 'slide_08_variant.html'))
# Remove old references
s8 = re.sub(r'background-image: url\(\'\.\./images/[^\']+\'\);\s*opacity: [\d.]+;', '', s8)
s8 = re.sub(r'<div class="slide-bg-image"></div>', '', s8)
# Add new background
s8 = s8.replace(
    '<div class="slide-container">',
    '<div class="slide-container" style="background-image: url(\'slide_08_oed_pillars.png\'); background-size: cover; background-position: center;">\n        <div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(236,253,245,0.88) 0%, rgba(254,252,232,0.86) 35%, rgba(240,253,244,0.88) 70%, rgba(220,252,231,0.90) 100%); z-index:0;"></div>'
)
s8 = s8.replace('.header {', '.header { position: relative; z-index: 1;')
s8 = s8.replace('.philosophy {', '.philosophy { position: relative; z-index: 1;')
s8 = s8.replace('.pillars-container {', '.pillars-container { position: relative; z-index: 1;')
write_file(os.path.join(PPT_DIR, 'slide_08_variant.html'), s8)
print('Slide 8: OED pillars image as full background')

# ============================================================
# SLIDE 9: Atomic to Global — scale image as full background
# ============================================================
s9 = read_file(os.path.join(PPT_DIR, 'slide_09_variant.html'))
s9 = s9.replace(
    '<div class="slide-container">',
    '<div class="slide-container" style="background-image: url(\'slide_09_scale.png\'); background-size: cover; background-position: center;">\n        <div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(236,253,245,0.90) 0%, rgba(254,252,232,0.88) 40%, rgba(240,253,244,0.90) 70%, rgba(220,252,231,0.92) 100%); z-index:0;"></div>'
)
s9 = s9.replace('.header {', '.header { position: relative; z-index: 1;')
s9 = s9.replace('.content-area {', '.content-area { position: relative; z-index: 1;')
write_file(os.path.join(PPT_DIR, 'slide_09_variant.html'), s9)
print('Slide 9: scale image as full background')

# ============================================================
# SLIDE 10: Long Run Vision — roadmap image as full background
# ============================================================
s10 = read_file(os.path.join(PPT_DIR, 'slide_10_variant.html'))
# Remove old references
s10 = re.sub(r'background-image: url\(\'\.\./images/[^\']+\'\);\s*opacity: [\d.]+;', '', s10)
s10 = re.sub(r'<div class="slide-bg-image"></div>', '', s10)
s10 = s10.replace(
    '<div class="slide-container">',
    '<div class="slide-container" style="background-image: url(\'slide_10_roadmap.png\'); background-size: cover; background-position: center;">\n        <div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(236,253,245,0.88) 0%, rgba(254,252,232,0.86) 35%, rgba(240,253,244,0.88) 70%, rgba(220,252,231,0.90) 100%); z-index:0;"></div>'
)
s10 = s10.replace('.header {', '.header { position: relative; z-index: 1;')
s10 = s10.replace('.content-area {', '.content-area { position: relative; z-index: 1;')
write_file(os.path.join(PPT_DIR, 'slide_10_variant.html'), s10)
print('Slide 10: roadmap image as full background')

# ============================================================
# SLIDE 11: Closing — closing image as full background
# ============================================================
s11 = read_file(os.path.join(PPT_DIR, 'slide_11_variant.html'))
# The closing slide already has a dark emerald gradient. Replace with image.
s11 = s11.replace(
    'background: linear-gradient(160deg, #065f46 0%, #047857 30%, #059669 60%, #10b981 100%);',
    "background-image: url('slide_11_closing.png'); background-size: cover; background-position: center;"
)
# Darken overlay more since this image is lighter
s11 = s11.replace(
    '<div class="slide-container">',
    '<div class="slide-container">\n        <div style="position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(160deg, rgba(6,95,70,0.85) 0%, rgba(4,120,87,0.80) 30%, rgba(5,150,105,0.75) 60%, rgba(16,185,129,0.70) 100%); z-index:0;"></div>'
)
s11 = s11.replace('.content {', '.content { position: relative; z-index: 1;')
write_file(os.path.join(PPT_DIR, 'slide_11_variant.html'), s11)
print('Slide 11: closing image as full background')

print('\nAll Gemini images renamed and integrated!')
