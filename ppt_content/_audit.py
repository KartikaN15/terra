from playwright.sync_api import sync_playwright
import pathlib, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

slides = sorted(pathlib.Path('.').glob('slide_*_variant.html'))

JS = r"""
() => {
    const sc = document.querySelector('.slide-container');
    const scr = sc.getBoundingClientRect();
    const results = [];
    function walk(el) {
        for (const c of el.children) {
            const cr = c.getBoundingClientRect();
            const oR = cr.right - scr.right;
            const oB = cr.bottom - scr.bottom;
            if (oR > 2 || oB > 2) {
                const cs = getComputedStyle(c);
                if (cs.position === 'fixed') continue;
                results.push({
                    tag: c.tagName.toLowerCase(),
                    cls: (c.className && c.className.toString ? c.className.toString() : '').slice(0,60),
                    oR: Math.round(oR),
                    oB: Math.round(oB),
                    pos: cs.position,
                    text: (c.innerText||'').slice(0,50).replace(/\s+/g,' ')
                });
            }
            walk(c);
        }
    }
    walk(sc);
    return {
        clientW: sc.clientWidth, clientH: sc.clientHeight,
        scrollW: sc.scrollWidth, scrollH: sc.scrollHeight,
        overflows: results.slice(0, 10)
    };
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={'width': 1400, 'height': 900}, device_scale_factor=1)
    page = ctx.new_page()
    for f in slides:
        page.goto(f.absolute().as_uri())
        page.wait_for_load_state('networkidle')
        info = page.evaluate(JS)
        print(f"\n=== {f.name} (client {info['clientW']}x{info['clientH']}, scroll {info['scrollW']}x{info['scrollH']}) ===")
        if not info['overflows']:
            print("  no overflow")
        for o in info['overflows']:
            print(f"  {o['tag']}.{o['cls'][:40]} oR={o['oR']} oB={o['oB']} pos={o['pos']} | {o['text']}")
    browser.close()
