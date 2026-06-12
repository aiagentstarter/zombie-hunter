#!/usr/bin/env python3
"""Mixamo FBX -> game-ready GLB converter (tooling only, runs on your Mac;
the deployed game stays static files).

Drop raw Mixamo downloads (FBX Binary, "With Skin") into models/raw/ —
no renaming needed. This script:
  1. maps each FBX to an enemy by filename keywords
       crawl                       -> models/crawler.glb
       mutant | brute | hulk | heavy -> models/brute.glb
       ghoul | ghost | wraith | float | fly -> models/ghoul.glb
       bat                         -> models/bat.glb   (optional — billboard is fine)
       zombie | walk | shambl      -> models/zombie.glb
  2. converts FBX -> GLB with the first tool that works:
       a) npx fbx2gltf   (needs Node, which this machine has)
       b) Blender CLI    (if installed)
  3. reports which enemies got real models and the file sizes.

Ambiguous or colliding files are SKIPPED with a clear message — re-run with
an explicit override:   python3 tools/convert_models.py --map "My File.fbx=brute"

The game loads models/<kind>.glb automatically when present and falls back
to the billboard sprite for any enemy without a model. Re-run any time.
"""
import os, re, sys, glob, shutil, subprocess

ROOT = os.path.join(os.path.dirname(__file__), '..')
RAW = os.path.join(ROOT, 'models', 'raw')
OUT = os.path.join(ROOT, 'models')

# order matters: first matching rule wins, specific words before generic ones
RULES = [
    ('crawler', r'crawl'),
    ('brute',   r'mutant|brute|hulk|heavy'),
    ('ghoul',   r'ghoul|ghost|wraith|float|fly'),
    ('bat',     r'\bbat\b|bat[ _-]'),
    ('zombie',  r'zombie|walk|shambl'),
]
BIG_MB = 4.0


def classify(name):
    low = name.lower()
    hits = [kind for kind, pat in RULES if re.search(pat, low)]
    return hits


def find_blender():
    for cand in ('/Applications/Blender.app/Contents/MacOS/Blender',
                 shutil.which('blender')):
        if cand and os.path.exists(cand):
            return cand
    return None


def convert_npx(src, dst):
    """fbx2gltf ships platform binaries through npm — one command, no install."""
    r = subprocess.run(['npx', '-y', 'fbx2gltf', '-b', '-i', src, '-o', dst],
                       capture_output=True, text=True, timeout=300)
    return os.path.exists(dst) and os.path.getsize(dst) > 10000, r.stderr[-400:]


def convert_blender(src, dst, blender):
    expr = ("import bpy; bpy.ops.wm.read_factory_settings(use_empty=True); "
            f"bpy.ops.import_scene.fbx(filepath={src!r}); "
            f"bpy.ops.export_scene.gltf(filepath={dst!r}, export_format='GLB')")
    r = subprocess.run([blender, '-b', '--python-expr', expr],
                       capture_output=True, text=True, timeout=600)
    return os.path.exists(dst) and os.path.getsize(dst) > 10000, r.stderr[-400:]


def main():
    overrides = {}
    for a in sys.argv[1:]:
        if a.startswith('--map'):
            spec = a.split('=', 1)[1] if '=' in a else ''
            # --map "file.fbx=kind"  (the first '=' splits flag, second splits pair)
            if '=' in spec:
                f, k = spec.rsplit('=', 1)
                overrides[f.lower()] = k.strip().lower()
    files = sorted(glob.glob(os.path.join(RAW, '*.fbx')) +
                   glob.glob(os.path.join(RAW, '*.FBX')))
    if not files:
        sys.exit(f'nothing to do: no .fbx files in {os.path.abspath(RAW)}\n'
                 'Download characters from mixamo.com (FBX Binary, With Skin) '
                 'and drop them there.')

    plan, problems = {}, []
    for f in files:
        base = os.path.basename(f)
        kind = overrides.get(base.lower())
        if not kind:
            hits = classify(base)
            if len(hits) == 1:
                kind = hits[0]
            else:
                problems.append((base, hits))
                continue
        if kind in plan:
            problems.append((base, [f'{kind} already taken by {os.path.basename(plan[kind])}']))
            continue
        plan[kind] = f

    blender = find_blender()
    print(f'converting {len(plan)} file(s); tools: npx fbx2gltf'
          + (f' + blender' if blender else ' (blender not found)'))
    done = {}
    for kind, src in plan.items():
        dst = os.path.join(OUT, kind + '.glb')
        ok, err = False, ''
        try:
            ok, err = convert_npx(src, dst)
        except Exception as e:
            err = str(e)
        if not ok and blender:
            try:
                ok, err = convert_blender(src, dst, blender)
            except Exception as e:
                err = str(e)
        if ok:
            mb = os.path.getsize(dst) / 1e6
            flag = '  ** larger than 4MB — consider a lighter character' if mb > BIG_MB else ''
            print(f'  ok  {os.path.basename(src)} -> models/{kind}.glb ({mb:.1f} MB){flag}')
            done[kind] = mb
        else:
            print(f'  FAIL {os.path.basename(src)} -> {kind}: {err.strip() or "no converter available"}')

    for base, hits in problems:
        why = ('matches nothing' if not hits else
               'matches several kinds: ' + ', '.join(hits) if len(hits) > 1 else hits[0])
        print(f'  ?   {base}: {why} — re-run with --map "{base}=<kind>"')

    if not done and not blender:
        print('\nIf npx failed: install Blender (free) from blender.org or '
              '`brew install --cask blender`, then re-run.')
    have = ', '.join(sorted(done)) or 'none'
    print(f'\nenemies with real models now: {have} (everything else stays a billboard)')


if __name__ == '__main__':
    main()
