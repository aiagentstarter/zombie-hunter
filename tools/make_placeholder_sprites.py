#!/usr/bin/env python3
"""PLACEHOLDER sprite generator (tooling only).

Alex's real photorealistic renders weren't on disk yet, so this paints
moody, textured stand-ins for sprites/zombie|crawler|ghoul|bat|brute.png
in the poster palette — dark decayed green-grays, pale moonlit rim from
the upper right, glowing toxic-green eyes. They exercise the exact same
pipeline (transparent PNG, trim, eye detection) as the real art will.

Drop the real renders over these files (same names) and re-run
tools/prep_sprites.py — nothing in the game changes.
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

random.seed(31)
OUT = os.path.join(os.path.dirname(__file__), '..', 'sprites')
os.makedirs(OUT, exist_ok=True)

# poster palette
BASE   = (24, 36, 26)     # body green-gray
DARK   = (12, 20, 14)
LIGHT  = (46, 68, 48)
BONE   = (132, 148, 122)
RIM    = (170, 240, 180)
EYE    = (150, 255, 105)
HALO   = (110, 255, 80)


def mask_canvas(w, h):
    m = Image.new('L', (w, h), 0)
    return m, ImageDraw.Draw(m)


def jagged_poly(d, pts, n=3, amp=10, fill=255):
    """polygon whose every edge is broken into jittered segments — torn cloth"""
    out = []
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        for k in range(n):
            t = k / n
            out.append((x0 + (x1 - x0) * t + random.uniform(-amp, amp),
                        y0 + (y1 - y0) * t + random.uniform(-amp, amp)))
    d.polygon(out, fill=fill)


def textured_body(mask, seed_sigma=44):
    """noise-mottled decayed flesh inside the mask + vertical shading"""
    w, h = mask.size
    noise = Image.effect_noise((w, h), seed_sigma).filter(ImageFilter.GaussianBlur(2))
    body = Image.new('RGB', (w, h), BASE)
    body = ImageChops.multiply(body, Image.merge('RGB', (noise, noise, noise)).point(
        lambda v: int(110 + v * 0.75)))
    shade = Image.new('L', (w, h), 0)
    sd = ImageDraw.Draw(shade)
    for y in range(h):  # darker toward the bottom — moonlight comes from above
        sd.line([(0, y), (w, y)], fill=int(255 * (1 - 0.45 * y / h)))
    body = ImageChops.multiply(body, Image.merge('RGB', (shade, shade, shade)).point(
        lambda v: int(90 + v * 0.65)))
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.paste(body, (0, 0), mask)
    return out


def add_blotches(img, mask, n, r0, r1, dark=True):
    """rot patches / mold — random soft ellipses clipped to the body"""
    w, h = img.size
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    mp = mask.load()
    placed = 0
    while placed < n:
        x, y = random.randint(0, w - 1), random.randint(0, h - 1)
        if mp[x, y] < 200:
            continue
        r = random.uniform(r0, r1)
        col = (*DARK, random.randint(90, 150)) if dark else (*LIGHT, random.randint(60, 110))
        d.ellipse([x - r, y - r * .7, x + r, y + r * .7], fill=col)
        placed += 1
    lay = lay.filter(ImageFilter.GaussianBlur(3))
    lay.putalpha(ImageChops.multiply(lay.getchannel('A'), mask))
    return Image.alpha_composite(img, lay)


def add_rim(img, mask, dx=-5, dy=6, blur=2, alpha=180):
    """pale moonlit edge: the mask minus itself shifted toward lower-left"""
    shifted = ImageChops.offset(mask, dx, dy)
    edge = ImageChops.subtract(mask, shifted)
    edge = edge.filter(ImageFilter.GaussianBlur(blur))
    lay = Image.new('RGBA', img.size, (*RIM, 0))
    lay.putalpha(edge.point(lambda v: min(alpha, v)))
    return Image.alpha_composite(img, lay)


def add_eye(img, x, y, r):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for rr in range(int(r * 3.2), 0, -2):  # halo
        a = int(120 * (1 - rr / (r * 3.2)) ** 2)
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(*HALO, a))
    img = Image.alpha_composite(img, lay.filter(ImageFilter.GaussianBlur(2)))
    d2 = ImageDraw.Draw(img)
    d2.ellipse([x - r, y - r, x + r, y + r], fill=EYE)
    d2.ellipse([x - r * .4, y - r * .3, x + r * .4, y + r * .5], fill=(20, 40, 20))
    return img


def limb(d, pts, width):
    d.line(pts, fill=255, width=width, joint='curve')
    for (x, y) in (pts[0], pts[-1]):
        d.ellipse([x - width / 2, y - width / 2, x + width / 2, y + width / 2], fill=255)


def fingers(d, x, y, n, length, width, up=True):
    for i in range(n):
        a = math.radians(-130 + i * 26) if up else math.radians(130 - i * 26)
        x2 = x + math.cos(a) * length
        y2 = y + math.sin(a) * length * (1 if up else -1)
        d.line([(x, y), (x2, y2)], fill=255, width=width)


def finish(img, name):
    img = img.filter(ImageFilter.GaussianBlur(0.5))
    img.save(os.path.join(OUT, name), optimize=True)
    print('wrote', name, img.size)


# ---------------------------------------------------------------- zombie
def make_zombie():
    w, h = 820, 1000
    m, d = mask_canvas(w, h)
    limb(d, [(300, 560), (200, 330), (170, 160)], 64)            # left arm up
    limb(d, [(530, 560), (640, 350), (680, 190)], 64)            # right arm up
    fingers(d, 170, 130, 4, 70, 22)
    fingers(d, 684, 160, 4, 70, 22)
    jagged_poly(d, [(255, 470), (270, 950), (560, 950), (575, 470)], n=4, amp=16)  # torso, torn hem
    d.ellipse([300, 250, 530, 490], fill=255)                    # head
    d.ellipse([330, 430, 500, 520], fill=255)                    # jaw/neck
    img = textured_body(m)
    img = add_blotches(img, m, 26, 12, 42)
    img = add_blotches(img, m, 10, 6, 18, dark=False)
    img = add_rim(img, m)
    # torn shirt shadow band + exposed ribs hint
    rib = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rib)
    for i in range(4):
        rd.arc([330, 560 + i * 42, 500, 660 + i * 42], 200, 340, fill=(*BONE, 120), width=7)
    rib.putalpha(ImageChops.multiply(rib.getchannel('A'), m))
    img = Image.alpha_composite(img, rib)
    img = add_eye(img, 365, 360, 17)
    img = add_eye(img, 462, 352, 17)
    md = ImageDraw.Draw(img)                                     # hanging mouth
    md.ellipse([385, 430, 448, 470], fill=(8, 14, 9, 235))
    finish(img, 'zombie.png')


# --------------------------------------------------------------- crawler
def make_crawler():
    w, h = 1150, 620
    m, d = mask_canvas(w, h)
    d.ellipse([330, 230, 760, 430], fill=255)                    # low torso
    jagged_poly(d, [(700, 280), (1090, 350), (1080, 430), (690, 420)], n=4, amp=12)  # trailing legs/rags
    limb(d, [(380, 380), (210, 430), (90, 510)], 52)             # dragging arm
    fingers(d, 80, 520, 4, 60, 18, up=False)
    limb(d, [(520, 400), (470, 500)], 46)                        # planted arm
    d.ellipse([200, 170, 420, 380], fill=255)                    # head, low and forward
    for i in range(5):                                           # spine bumps
        d.ellipse([430 + i * 64, 208 - (i % 2) * 8, 492 + i * 64, 268], fill=255)
    img = textured_body(m)
    img = add_blotches(img, m, 24, 12, 38)
    img = add_rim(img, m, dx=-4, dy=7)
    img = add_eye(img, 268, 258, 15)
    img = add_eye(img, 342, 252, 15)
    md = ImageDraw.Draw(img)                                     # hanging jaw
    md.polygon([(226, 330), (330, 352), (322, 300)], fill=(8, 14, 9, 235))
    for tx in (252, 286):
        md.polygon([(tx, 330), (tx + 16, 334), (tx + 8, 350)], fill=(*BONE, 230))
    finish(img, 'crawler.png')


# ----------------------------------------------------------------- ghoul
def make_ghoul():
    w, h = 800, 1080
    m, d = mask_canvas(w, h)
    d.ellipse([255, 120, 545, 420])                              # hood dome
    d.ellipse([255, 120, 545, 420], fill=255)
    jagged_poly(d, [(265, 280), (205, 700), (270, 880), (530, 880), (595, 700), (535, 280)],
                n=4, amp=14)                                      # cloak
    limb(d, [(280, 430), (170, 560), (140, 660)], 48)            # drooping arms
    limb(d, [(520, 430), (630, 560), (660, 660)], 48)
    # wispy tendrils below
    for tx, tl in [(300, 1020), (390, 1060), (470, 1000), (540, 960)]:
        d.line([(tx, 840), (tx + random.randint(-40, 40), tl)], fill=255,
               width=random.randint(14, 26))
    img = textured_body(m, seed_sigma=36)
    img = add_blotches(img, m, 18, 14, 40)
    img = add_rim(img, m, dx=-5, dy=5, alpha=200)
    hood = Image.new('RGBA', (w, h), (0, 0, 0, 0))               # hollow face pit
    hd = ImageDraw.Draw(hood)
    hd.ellipse([320, 200, 480, 400], fill=(6, 10, 7, 245))
    img = Image.alpha_composite(img, hood)
    img = add_eye(img, 365, 290, 15)
    img = add_eye(img, 437, 290, 15)
    md = ImageDraw.Draw(img)
    md.ellipse([380, 340, 424, 396], fill=(2, 5, 3, 255))        # wailing mouth
    # dissolve the bottom into mist: linear alpha fade + blur on the tail
    a = img.getchannel('A').load()
    for y in range(820, h):
        f = max(0.0, 1 - (y - 820) / (h - 820))
        for x in range(w):
            a2 = a[x, y]
            if a2:
                img.putpixel((x, y), (*img.getpixel((x, y))[:3], int(a2 * f * (0.75 + 0.25 * math.sin(x / 26 + y / 18)))))
    finish(img, 'ghoul.png')


# ------------------------------------------------------------------- bat
def make_bat():
    w, h = 1250, 760
    m, d = mask_canvas(w, h)
    for sgn in (-1, 1):                                          # webbed wings
        cx = 625
        pts = [(cx + sgn * 70, 360)]
        pts += [(cx + sgn * 580, 150), (cx + sgn * 520, 320), (cx + sgn * 430, 280),
                (cx + sgn * 380, 430), (cx + sgn * 250, 360), (cx + sgn * 200, 500),
                (cx + sgn * 90, 430)]
        d.polygon(pts, fill=255)
    d.ellipse([540, 300, 710, 560], fill=255)                    # body
    d.ellipse([550, 190, 700, 350], fill=255)                    # head
    d.polygon([(560, 230), (530, 90), (620, 200)], fill=255)     # ears
    d.polygon([(690, 230), (720, 90), (630, 200)], fill=255)
    img = textured_body(m, seed_sigma=50)
    img = add_blotches(img, m, 16, 10, 30)
    img = add_rim(img, m, dx=-6, dy=6)
    bones = Image.new('RGBA', (w, h), (0, 0, 0, 0))              # wing fingers
    bd = ImageDraw.Draw(bones)
    for sgn in (-1, 1):
        for tip in [(580, 150), (520, 320), (380, 430)]:
            bd.line([(625 + sgn * 70, 360), (625 + sgn * tip[0], tip[1])],
                    fill=(*DARK, 200), width=9)
    bones.putalpha(ImageChops.multiply(bones.getchannel('A'), m))
    img = Image.alpha_composite(img, bones)
    img = add_eye(img, 593, 268, 16)
    img = add_eye(img, 657, 268, 16)
    md = ImageDraw.Draw(img)                                     # bared fangs
    md.ellipse([585, 308, 665, 342], fill=(8, 14, 9, 235))
    for tx in (602, 634):
        md.polygon([(tx, 312), (tx + 14, 312), (tx + 7, 344)], fill=(*BONE, 240))
    finish(img, 'bat.png')


# ----------------------------------------------------------------- brute
def make_brute():
    w, h = 1000, 1060
    m, d = mask_canvas(w, h)
    for sx, sy, tx, ty in [(500, 330, 430, 60), (350, 400, 180, 150), (650, 400, 830, 140),
                           (260, 520, 90, 360), (740, 520, 910, 350)]:
        d.polygon([(sx - 56, sy), (tx, ty), (sx + 56, sy)], fill=255)   # bone spikes
    d.ellipse([180, 330, 820, 850], fill=255)                    # massive torso
    d.ellipse([150, 320, 420, 580], fill=255)                    # shoulders
    d.ellipse([580, 320, 850, 580], fill=255)
    limb(d, [(255, 520), (180, 760), (200, 920)], 110)           # huge arms
    limb(d, [(745, 520), (820, 760), (800, 920)], 110)
    d.ellipse([400, 250, 600, 440], fill=255)                    # sunken head
    d.rectangle([330, 840, 480, 1010], fill=255)                 # legs
    d.rectangle([530, 840, 680, 1010], fill=255)
    img = textured_body(m, seed_sigma=48)
    img = add_blotches(img, m, 34, 16, 52)
    img = add_blotches(img, m, 12, 8, 22, dark=False)
    img = add_rim(img, m, dx=-6, dy=7)
    spikes = Image.new('RGBA', (w, h), (0, 0, 0, 0))             # pale bone tips
    sd = ImageDraw.Draw(spikes)
    for tx, ty in [(430, 60), (180, 150), (830, 140), (90, 360), (910, 350)]:
        sd.ellipse([tx - 26, ty - 26, tx + 26, ty + 26], fill=(*BONE, 90))
    spikes = spikes.filter(ImageFilter.GaussianBlur(8))
    spikes.putalpha(ImageChops.multiply(spikes.getchannel('A'), m))
    img = Image.alpha_composite(img, spikes)
    img = add_eye(img, 462, 330, 16)
    img = add_eye(img, 540, 330, 16)
    md = ImageDraw.Draw(img)                                     # glowing mouth
    for rr in range(40, 0, -3):
        md.ellipse([500 - rr * 1.6, 398 - rr * .5, 500 + rr * 1.6, 398 + rr * .5],
                   fill=(*HALO, int(7 * (40 - rr))))
    md.ellipse([445, 386, 555, 412], fill=EYE)
    for tx in range(452, 548, 19):
        md.polygon([(tx, 388), (tx + 12, 388), (tx + 6, 412)], fill=(10, 18, 11, 255))
    finish(img, 'brute.png')


if __name__ == '__main__':
    make_zombie(); make_crawler(); make_ghoul(); make_bat(); make_brute()
    print('placeholder sprites written to', os.path.abspath(OUT))
