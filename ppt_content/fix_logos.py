"""
White-background removal for logos using PIL threshold — not rembg.
rembg confuses coloured logo elements with the background on flat logos.
"""
from pathlib import Path
from PIL import Image
import numpy as np

DIR = Path(__file__).parent

def remove_white_bg(src: str, dst: str, threshold: int = 240):
    """Turn near-white pixels transparent, keeping coloured logo pixels."""
    img = Image.open(DIR / src).convert("RGBA")
    data = np.array(img, dtype=np.uint8)
    r, g, b, a = data[..., 0], data[..., 1], data[..., 2], data[..., 3]
    # Pixel is "white-ish" when all channels are above threshold
    white_mask = (r > threshold) & (g > threshold) & (b > threshold)
    data[white_mask, 3] = 0          # set alpha to 0 (transparent)
    Image.fromarray(data).save(DIR / dst)
    print(f"  {src} -> {dst}  ({white_mask.sum()} px made transparent)")

print("Fixing logos with PIL threshold removal...")
remove_white_bg("J2W logo.png",         "j2w_nobg.png",     threshold=235)
remove_white_bg("Netflix_Logo_RGB.png", "netflix_nobg.png", threshold=240)
print("Done.")
