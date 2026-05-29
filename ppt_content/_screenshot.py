from playwright.sync_api import sync_playwright
import pathlib

slides = sorted(pathlib.Path('.').glob('slide_*_variant.html'))
outdir = pathlib.Path('_shots'); outdir.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={'width': 1400, 'height': 800}, device_scale_factor=1)
    page = ctx.new_page()
    for f in slides:
        page.goto(f.absolute().as_uri())
        page.wait_for_load_state('networkidle')
        # screenshot just the slide-container element
        el = page.query_selector('.slide-container')
        el.screenshot(path=str(outdir / f'{f.stem}.png'))
        print(f'shot {f.name}')
    browser.close()
