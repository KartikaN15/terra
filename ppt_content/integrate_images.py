"""Integrate project images into Terra HTML slides."""
import os
import re

PPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(os.path.dirname(PPT_DIR), 'images')


def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


# ============================================================
# SLIDE 3: What is Terra — add system-overview as background
# ============================================================
slide3 = read_file(os.path.join(PPT_DIR, 'slide_03_variant.html'))

# Add a background image style and div before closing right-section
slide3_bg_style = """        .right-bg-image {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url('../images/01-system-overview.png');
            background-size: cover;
            background-position: center;
            opacity: 0.12;
            border-radius: 24px;
            z-index: 0;
        }
        .vertical-card { position: relative; z-index: 1; }"""

# Insert bg style before the page-number rule
slide3 = slide3.replace(
    '        .page-number {',
    slide3_bg_style + '\n        .page-number {'
)

# Add the bg div inside right-section
slide3 = slide3.replace(
    '            <div class="right-section">',
    '            <div class="right-section" style="position:relative;">\n                <div class="right-bg-image"></div>'
)

write_file(os.path.join(PPT_DIR, 'slide_03_variant.html'), slide3)
print("Slide 3: Added 01-system-overview.png as right-section background")


# ============================================================
# SLIDE 5: How Terra Works — backend lifecycle background + confidence card
# ============================================================
slide5 = read_file(os.path.join(PPT_DIR, 'slide_05_variant.html'))

# Add background image to the slide container
slide5_bg_style = """        .slide-bg-image {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url('../images/02-backend-request-lifecycle.png');
            background-size: cover;
            background-position: center;
            opacity: 0.08;
            z-index: 0;
            pointer-events: none;
        }"""

slide5 = slide5.replace(
    '        .page-number {',
    slide5_bg_style + '\n        .page-number {'
)

# Add bg div right after slide-container opening
slide5 = slide5.replace(
    '    <div class="slide-container">',
    '    <div class="slide-container">\n        <div class="slide-bg-image"></div>'
)

# Add confidence story image to Step 3 card
slide5_confidence_img = """                    <div style="margin-top:10px; border-radius:10px; overflow:hidden; border:1px solid rgba(16,185,129,0.2);">
                        <img src="../images/07-audit-confidence-story.png" style="width:100%; height:90px; object-fit:cover; object-position:top; display:block; opacity:0.85;">
                    </div>"""

slide5 = slide5.replace(
    '                </div>\n            </div>\n\n            <div class="step-card">\n                <div class="step-number">4',
    slide5_confidence_img + '\n                </div>\n            </div>\n\n            <div class="step-card">\n                <div class="step-number">4'
)

write_file(os.path.join(PPT_DIR, 'slide_05_variant.html'), slide5)
print("Slide 5: Added 02-backend-request-lifecycle.png as slide background + 07-audit-confidence-story.png in Step 3")


# ============================================================
# SLIDE 6: Architecture — replace CSS entity flow with ER diagram
# ============================================================
slide6 = read_file(os.path.join(PPT_DIR, 'slide_06_variant.html'))

# Replace the entity-flow div with an image
old_entity_flow = '''                <div class="entity-flow">
                    <div class="entity-card project">
                        <div class="entity-icon">📁</div>
                        <div class="entity-name">Project</div>
                        <div class="entity-desc">The container — production, site, route</div>
                    </div>
                    <div class="entity-arrow">→</div>
                    <div class="entity-card event">
                        <div class="entity-icon">⚡</div>
                        <div class="entity-name">Activity Event</div>
                        <div class="entity-desc">The atom — every litre, kWh, km</div>
                    </div>
                    <div class="entity-arrow">→</div>
                    <div class="entity-card factor">
                        <div class="entity-icon">📊</div>
                        <div class="entity-name">Emission Factor</div>
                        <div class="entity-desc">The science — kgCO₂e per unit</div>
                    </div>
                    <div class="entity-arrow">→</div>
                    <div class="entity-card calc">
                        <div class="entity-icon">🧮</div>
                        <div class="entity-name">Calculation</div>
                        <div class="entity-desc">The result — auditable, immutable</div>
                    </div>
                </div>'''

new_entity_img = '''                <div class="er-diagram-container" style="background:rgba(255,255,255,0.85); backdrop-filter:blur(12px); border:1px solid rgba(16,185,129,0.15); border-radius:20px; padding:16px; overflow:hidden;">
                    <img src="../images/04-domain-model-er.png" style="width:100%; height:160px; object-fit:contain; object-position:center; display:block;">
                </div>'''

slide6 = slide6.replace(old_entity_flow, new_entity_img)

write_file(os.path.join(PPT_DIR, 'slide_06_variant.html'), slide6)
print("Slide 6: Replaced CSS entity flow with 04-domain-model-er.png")


# ============================================================
# SLIDE 7: ML Engine — ML pipeline background + greenlight story card
# ============================================================
slide7 = read_file(os.path.join(PPT_DIR, 'slide_07_variant.html'))

# Add background image style
slide7_bg_style = """        .slide-bg-image {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url('../images/05-ml-pipeline-training-serving.png');
            background-size: cover;
            background-position: center;
            opacity: 0.07;
            z-index: 0;
            pointer-events: none;
        }"""

slide7 = slide7.replace(
    '        .page-number {',
    slide7_bg_style + '\n        .page-number {'
)

# Add bg div
slide7 = slide7.replace(
    '    <div class="slide-container">',
    '    <div class="slide-container">\n        <div class="slide-bg-image"></div>'
)

# Add greenlight-to-report image as a visual card after the prediction box
old_loop = '''                <div class="loop-box">'''
new_loop = '''                <div style="background:rgba(255,255,255,0.85); backdrop-filter:blur(8px); border:1px solid rgba(16,185,129,0.15); border-radius:16px; padding:12px; overflow:hidden; margin-top:8px;">
                    <img src="../images/08-story-greenlight-to-report.png" style="width:100%; height:100px; object-fit:cover; object-position:center; display:block; border-radius:10px;">
                </div>
                <div class="loop-box">'''

slide7 = slide7.replace(old_loop, new_loop)

write_file(os.path.join(PPT_DIR, 'slide_07_variant.html'), slide7)
print("Slide 7: Added 05-ml-pipeline-training-serving.png as background + 08-story-greenlight-to-report.png as card")


# ============================================================
# SLIDE 10: Long Run Vision — deployment topology background
# ============================================================
slide10 = read_file(os.path.join(PPT_DIR, 'slide_10_variant.html'))

# Add background image style
slide10_bg_style = """        .slide-bg-image {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url('../images/06-deployment-topology.png');
            background-size: cover;
            background-position: center;
            opacity: 0.08;
            z-index: 0;
            pointer-events: none;
        }"""

slide10 = slide10.replace(
    '        .page-number {',
    slide10_bg_style + '\n        .page-number {'
)

# Add bg div
slide10 = slide10.replace(
    '    <div class="slide-container">',
    '    <div class="slide-container">\n        <div class="slide-bg-image"></div>'
)

write_file(os.path.join(PPT_DIR, 'slide_10_variant.html'), slide10)
print("Slide 10: Added 06-deployment-topology.png as slide background")


# ============================================================
# SLIDE 8: OED Playbook — add 03-end-to-end-user-flow if not used
# ============================================================
# 03-end-to-end-user-flow.png is still unused. Let's add it to Slide 8 as a decorative element
slide8 = read_file(os.path.join(PPT_DIR, 'slide_08_variant.html'))

# Add a subtle background with the end-to-end flow
slide8_bg_style = """        .slide-bg-image {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url('../images/03-end-to-end-user-flow.png');
            background-size: cover;
            background-position: center;
            opacity: 0.06;
            z-index: 0;
            pointer-events: none;
        }"""

slide8 = slide8.replace(
    '        .page-number {',
    slide8_bg_style + '\n        .page-number {'
)

slide8 = slide8.replace(
    '    <div class="slide-container">',
    '    <div class="slide-container">\n        <div class="slide-bg-image"></div>'
)

write_file(os.path.join(PPT_DIR, 'slide_08_variant.html'), slide8)
print("Slide 8: Added 03-end-to-end-user-flow.png as subtle background")


print("\nAll images integrated successfully!")
