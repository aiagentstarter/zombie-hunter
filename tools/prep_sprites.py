#!/usr/bin/env python3
"""One-time sprite preprocessing for Zombie Hunter (tooling only — the
deployed game stays static files, no build step).

For every PNG in ../sprites/ this script:
  1. removes a plain (near-uniform) background if the image has no real
     transparency — corner-sampled chroma distance, soft threshold
  2. cleans edge fringe: kills faint halo alpha and erodes the matte 1px
  3. trims empty margins to the visible creature (+ small padding)
  4. downscales anything above 1024px on its longest side (LANCZOS)
  5. saves an optimized transparent PNG in place

Run:  python3 tools/prep_sprites.py
Safe to re-run any time; already-clean sprites just get trimmed/optimized.
"""
import os, sys, glob
from PIL import Image, ImageFilter

SPRITES = os.path.join(os.path.dirname(__file__), '..', 'sprites')
MAX_DIM = 1024
PAD = 10


def has_real_alpha(img):
    if img.mode != 'RGBA':
        return False
    lo, hi = img.getchannel('A').getextrema()
    return lo < 250  # something is actually transparent


def remove_plain_background(img):
    """Distance-from-corner-color keying with a soft edge."""
    img = img.convert('RGBA')
    px = img.load()
    w, h = img.size
    # average the four corner patches = the background color
    samples = []
    for cx, cy in [(0, 0), (w - 8, 0), (0, h - 8), (w - 8, h - 8)]:
        for dx in range(8):
            for dy in range(8):
                samples.append(px[min(w - 1, cx + dx), min(h - 1, cy + dy)][:3])
    br = sum(s[0] for s in samples) / len(samples)
    bg = sum(s[1] for s in samples) / len(samples)
    bb = sum(s[2] for s in samples) / len(samples)
    NEAR, FAR = 28, 70  # chroma distance: fully gone .. fully kept
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            d = ((r - br) ** 2 + (g - bg) ** 2 + (b - bb) ** 2) ** 0.5
            if d <= NEAR:
                px[x, y] = (r, g, b, 0)
            elif d < FAR:
                px[x, y] = (r, g, b, min(a, int(255 * (d - NEAR) / (FAR - NEAR))))
    return img


def defringe(img):
    """Drop halo alpha, erode the matte edge by one pixel."""
    img = img.convert('RGBA')
    a = img.getchannel('A')
    a = a.point(lambda v: 0 if v < 40 else v)          # faint halo -> gone
    a = a.filter(ImageFilter.MinFilter(3))             # 1px erosion
    img.putalpha(a)
    return img


def process(path):
    img = Image.open(path)
    keyed = False
    if not has_real_alpha(img):
        img = remove_plain_background(img)
        keyed = True
    img = defringe(img)
    box = img.getchannel('A').getbbox()
    if not box:
        print(f'  !! {os.path.basename(path)}: nothing visible after keying — left untouched')
        return
    box = (max(0, box[0] - PAD), max(0, box[1] - PAD),
           min(img.width, box[2] + PAD), min(img.height, box[3] + PAD))
    img = img.crop(box)
    if max(img.size) > MAX_DIM:
        k = MAX_DIM / max(img.size)
        img = img.resize((max(1, round(img.width * k)), max(1, round(img.height * k))),
                         Image.LANCZOS)
    img.save(path, optimize=True)
    print(f'  ok {os.path.basename(path)}: {img.width}x{img.height}'
          f'{" (background removed)" if keyed else ""}')


if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(SPRITES, '*.png')))
    if not files:
        sys.exit(f'no PNGs found in {os.path.abspath(SPRITES)}')
    print(f'processing {len(files)} sprite(s)…')
    for f in files:
        process(f)
    print('done.')
