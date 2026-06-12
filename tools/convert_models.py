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
    """First matching rule wins — RULES order puts the specific words
    (crawl, mutant) before the generic ones (zombie, walk)."""
    low = name.lower()
    for kind, pat in RULES:
        if re.search(pat, low):
            return [kind]
    return []


def find_blender():
    for cand in ('/Applications/Blender.app/Contents/MacOS/Blender',
                 shutil.which('blender')):
        if cand and os.path.exists(cand):
            return cand
    return None


def convert_npx(src, dst):
    """The fbx2gltf npm package has NO bin entry — it's a Node API wrapping
    platform binaries. Install it once into tools/_fbxconv and call the API."""
    prefix = os.path.join(os.path.dirname(__file__), '_fbxconv')
    pkg = os.path.join(prefix, 'node_modules', 'fbx2gltf')
    if not os.path.isdir(pkg):
        print('  (one-time: installing fbx2gltf into tools/_fbxconv ...)')
        r = subprocess.run(['npm', 'install', 'fbx2gltf', '--prefix', prefix,
                            '--no-fund', '--no-audit', '--loglevel=error'],
                           capture_output=True, text=True, timeout=600)
        if not os.path.isdir(pkg):
            return False, 'npm install failed: ' + (r.stderr or r.stdout)[-300:]
    script = ('const c=require("fbx2gltf");'
              'c(process.argv[1],process.argv[2],["--binary"])'
              '.then(d=>{console.log("OK",d);process.exit(0);})'
              '.catch(e=>{console.error(String(e));process.exit(1);});')
    r = subprocess.run(['node', '-e', script, src, dst],
                       cwd=prefix, capture_output=True, text=True, timeout=600,
                       env={**os.environ, 'NODE_PATH': os.path.join(prefix, 'node_modules')})
    return os.path.exists(dst) and os.path.getsize(dst) > 10000, (r.stderr or r.stdout)[-400:]


def convert_blender(src, dst, blender):
    expr = ("import bpy; bpy.ops.wm.read_factory_settings(use_empty=True); "
            f"bpy.ops.import_scene.fbx(filepath={src!r}); "
            f"bpy.ops.export_scene.gltf(filepath={dst!r}, export_format='GLB')")
    r = subprocess.run([blender, '-b', '--python-expr', expr],
                       capture_output=True, text=True, timeout=600)
    return os.path.exists(dst) and os.path.getsize(dst) > 10000, r.stderr[-400:]


def optimize(dst, mb_before):
    """Mixamo embeds multi-MB textures. Shrink them to 1024px WebP and prune
    unused data — decoder-free (no Draco/meshopt), so the game needs nothing.
    Falls back to the unoptimized file if gltf-transform is unavailable."""
    tmp = dst + '.opt.glb'
    try:
        r = subprocess.run(['npx', '-y', '@gltf-transform/cli', 'optimize', dst, tmp,
                            '--compress', 'false', '--texture-compress', 'webp',
                            '--texture-size', '1024', '--simplify', 'false'],
                           capture_output=True, text=True, timeout=600)
        if os.path.exists(tmp) and os.path.getsize(tmp) > 10000:
            os.replace(tmp, dst)
            mb = os.path.getsize(dst) / 1e6
            print(f'      optimized {mb_before:.1f} MB -> {mb:.1f} MB '
                  '(1024px webp textures, pruned)')
            return mb
        print('      optimize skipped: ' + (r.stderr or r.stdout)[-200:].strip())
    except Exception as e:
        print(f'      optimize skipped: {e}')
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return mb_before


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
            print(f'  ok  {os.path.basename(src)} -> models/{kind}.glb ({mb:.1f} MB)')
            mb = optimize(dst, mb)
            flag = '  ** still larger than 4MB — consider a lighter character' if mb > BIG_MB else ''
            if flag:
                print(flag)
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
