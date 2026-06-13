# ZOMBIE HUNTER — *Survive the night*

A real-time **3D first-person** horde game in a single static page. You stand at the end
of a ruined city street at night. Heavy fog. A cold moon. Distant fires. Things come out
of the dark — eyes first — and you slash them by **waving your hand at the camera** (or
swiping the screen). Glowing **green ichor**, never gore. No lives, no game over: an
enemy that reaches you gets one claw-swipe scare and the night keeps coming. Lightning
storms roll through every 30–60 seconds and briefly reveal everything in the fog.

Built on Three.js (pinned CDN version, no build step, no bundler). The complete original
2D game lives on, untouched and fully playable, as **[classic.html](classic.html)** —
including Silly mode for little kids. There's a small CLASSIC 2D MODE link on the 3D
title screen, and devices that can't run the 3D build (iOS before 16.4, or no WebGL)
are redirected there automatically.

## Real 3D monsters from Mixamo (free, ~15 minutes — do this anytime)

The 3D game renders any enemy that has a rigged model in `models/`, and uses a fog-lit
sprite billboard for any enemy that doesn't. You never edit code — models are drop-in.

1. Go to <https://www.mixamo.com> and sign in (free Adobe account).
2. **Characters** tab → search **zombie** — pick the most realistic ones. Also search
   **mutant**: a hulking one makes a great brute.
3. With a character selected, open **Animations** → search **zombie walk** (for the
   crawler use a **crawl** animation; check **In Place** if shown).
4. **Download** with Format **FBX Binary (.fbx)** and Skin **With Skin**.
5. Repeat for 3–4 creatures and drop every file into **`models/raw/`** — no renaming,
   no conversion needed on your side.
6. Run `python3 tools/convert_models.py`. It maps each file by its name
   (crawl→crawler, mutant→brute, ghoul/ghost→ghoul, zombie/walk→zombie), converts
   FBX→GLB (via `npx fbx2gltf`, or Blender if installed), writes `models/zombie.glb`
   etc., and prints which enemies now have real models. Ambiguous names are skipped
   with instructions (`--map "My File.fbx=brute"` overrides).
7. Reload the game. When deploying, upload the `models/*.glb` files alongside
   `index.html` (skip `models/raw/` — that's just your downloads).

Notes: the **bat** is fine as a billboard (no model needed). Keep characters modest —
the converter flags any GLB over 4 MB. A clip whose name contains *walk/run/crawl/fly*
is used for movement (death animations: the engine currently uses its own crumple
dissolve for all kills). The loader measures and rescales every model to its enemy's
height, so Mixamo's units don't matter.

**Current status: four real Mixamo creatures are in.** `models/` ships zombie.glb
(1.1 MB), crawler.glb (0.9 MB), ghoul.glb (1.0 MB) and brute.glb (2.5 MB) — converted
and texture-optimized (1024px WebP) by the tool above. Only the **bat** still uses a
billboard, and its sprite is a generated dark silhouette; replace `sprites/bat.png`
with a real render any time (then `python3 tools/prep_sprites.py`).

---

## Put it online (GitHub Pages — free, ~5 minutes)

The camera **requires HTTPS**, which GitHub Pages gives you automatically.

1. Go to <https://github.com/new>. Repository name: `zombie-hunter`. Keep it
   **Public**. Click **Create repository**.
2. Upload (or `git push`) **everything in this folder**: `index.html`,
   `classic.html`, `poster.png`, the `sprites/` and `textures/` folders, and any
   `models/*.glb` you've made. (`tools/` and `models/raw/` are optional — they're
   not used by the game at runtime.)
3. In the repo: **Settings → Pages** → Branch `main`, folder `/ (root)` → **Save**.
4. Wait 1–2 minutes. Your game is at **`https://YOURNAME.github.io/zombie-hunter/`**

## Open it on the iPad / iPhone

1. Open **Safari** and go to your URL. (iOS 16.4+ runs the 3D night; older devices
   land on Classic automatically.)
2. Tap **START — CAMERA ON** → **Allow**.
3. Wave. Your hand draws a glowing blade through the street.

First load fetches Three.js (~1 MB) and, in camera mode, the hand-tracking model
(~8 MB, cached after that). Sound starts after the first tap — an iOS rule; touching
the title screen starts the heartbeat, the START button counts.

A small mirrored **self-view** sits in the corner so you can frame yourself — tap it
to tuck it away (tracking keeps running either way).

### The status pill (bottom-left) tells you what the camera sees

| Pill | Meaning |
|---|---|
| 🟩 **TRACKING ACTIVE** | A hand is in view — a glowing dot follows your fingertip. |
| 🟨 **SHOW YOUR HAND** | Tracking is fine, but no hand is in the picture. Step back or lift your hand. |
| ⬜ **TOUCH MODE** | Hand tracking is off (couldn't load, or this device is too slow) — touch always works. |

If no hand is seen for a while the game says it outright: *STEP BACK SO THE CAMERA
SEES YOUR HAND*.

### If something is off

| Symptom | Fix |
|---|---|
| Black screen then "THE 3D NIGHT COULD NOT LOAD" | A CDN/network failure — RETRY, or PLAY CLASSIC MODE. |
| Pill stays yellow | Your hand is out of frame. Step back, angle the camera down, wave at chest height. |
| Camera prompt never appears | iPad **Settings → Apps → Safari → Camera → Ask/Allow**, reload. |
| No sound | Tap once (any tap restarts the audio engine). The ringer switch does **not** mute the game after the first tap. MENU shows a live AUDIO line. |
| Hands feel laggy | The game lowers its tracking rate, rebuilds the tracker in a compatible mode, and only then switches to touch — the pill always shows where it landed. |
| Choppy on an old phone | The game sheds quality on its own: bloom → grain → particles → resolution → enemy cap. Tracking is never reduced. |

## Play with your kid (rooms, Versus, live video)

Two devices, two hunters, both faces on screen — here's the whole flow:

1. On your device: tap **MENU → PLAY WITH SOMEONE**. A big spooky code appears
   (like `MOON-TOAD-72`) with a link under it. Tap **COPY LINK** and text it.
2. On the other device: **just open the link.** It joins automatically — no
   typing, no menus. The title screen says *WAITING FOR PLAYER 2…* until you're
   both in, then *CONNECTED TO &lt;NAME&gt;!*
3. Both tap START. You'll see each other's faces in the corners — small rounded
   windows labeled **YOU** and their name — while each of you hunts your own
   street. Live scores for both players sit top-left. A red-dot **ON CAMERA**
   badge shows whenever you transmit; the **MIC** button mutes you.
4. Only have a code, not a link? MENU → **HAVE A CODE? PASTE IT HERE** → JOIN
   WITH CODE.

Good to know, in plain terms:

- **Video is peer-to-peer and end-to-end encrypted — it never passes through a
  server.** Only the room code, nicknames and scores touch the (free, public)
  relay that introduces the two devices.
- **Two on video max.** A third player who joins still sees and shares scores —
  they just get "ROOM IS FULL FOR VIDEO".
- **If video can't connect within ~20 seconds** you'll see *VIDEO COULD NOT
  CONNECT — YOU CAN STILL PLAY AND SEE SCORES*, and that's exactly true: the
  game and the score race keep working, and it quietly keeps retrying. Most
  home-to-home connections work on the free setup; a small share of strict
  networks need a paid TURN relay — there's a labeled slot at the top of
  index.html if yours ever turns out to be one.
- Leaving the room stops your camera/mic transmission immediately.

- Scores travel through a **free public MQTT relay** (broker.emqx.io + two fallbacks)
  over secure WebSockets — no account, no server. Only the room code, nickname and
  score are ever sent. If the relay drops, the room heals itself; solo play is never
  affected. `ROOM_ENABLED = false` in the file removes the feature entirely.
- **A 3D device and a Classic device can share a room** — same codes, same scores,
  same Versus. (Classic's Silly-mode toggle is ignored by the 3D game.)
- **VERSUS — TAKE TURNS (BEST OF 3)**: one tap on one device, zero taps after that.
  30-second turns (a glowing time bar shrinks across the top), the watcher sees the
  active player's name and climbing score in giant stencil text, round tallies (●),
  and both screens end under a lightning storm. Brutes count their full +5. If a
  device drops mid-round, the other waits kindly and the round restarts on return.
- **Live video** rides the same room, peer-to-peer WebRTC. During free play BOTH
  faces show at once: the partner in one corner, your own mirrored self-view in
  the opposite corner, each with a name tag (drag to re-corner, tap the partner
  to go fullscreen, tap the small selfie to shrink them back). In Versus, THEIR
  turn puts their video fullscreen behind their score — you're watching your kid
  hunt — and the 3D renderer politely pauses so the video gets the GPU. If a
  player reloads or drops, the call rebuilds itself when they come back through
  the same link.

## How the 3D night works (quick tour)

All in [index.html](index.html) (~3,500 lines, one module script):

- **Boot gate** — import-map + WebGL detection in a tiny classic script: unsupported
  devices redirect to classic.html before anything loads; a watchdog shows a friendly
  escape hatch if the CDN fails. Three.js r0.184.0 pinned via import map.
- **The street** — merged-geometry building slabs (each wall remembers its face so
  emissive windows sit flush), far silhouette skyline, debris, a flipped car. Damp
  asphalt under one cold directional moonlight (kept rough on purpose: a glossy
  floor mirrors the flashlight's specular lobe straight back into the camera as a
  giant clipped pool). Heavy `FogExp2`: enemies spawn deeply fogged, eyes first.
- **Light** — every lighting level lives in one set of constants (`AMB_BASE`,
  `DIR_BASE`, `RIM_BASE`, `FL_BASE`) consumed by BOTH the world setup and the
  per-frame lightning envelope — values set only at init are dead code one frame
  later. Your flashlight rakes hot down the center of the street; a cool rim light
  from behind the horde separates silhouettes from the dark. The gear menu's
  BRIGHTNESS slider (0.5–2, saved) scales the light rig itself, never the
  exposure — exposure lifts the flat fog color and washes the night gray. The
  moon disc is deliberately kept *below* the bloom threshold (its halo sprite
  provides the aura); bloom thresholds at clip-only so it's reserved for true
  emitters: flickering windows, enemy eyes, the slash. Readability never depends
  on bloom or lightning — acceptance screenshots are taken with bloom OFF.
- **Post** — half-res UnrealBloom, then one custom grade pass doing vignette +
  animated film grain + lightning whitewash + the claw-scare tint, then OutputPass
  (ACES). Lightning re-uses the 2D double-blink envelope to spike the lights, burn
  the fog back, and reveal 8 horde silhouettes for one second per strike.
- **Enemies** — data + movement in world units: shambler lurches stop-start with a
  hitch tremor, crawler drags in pulses, ghoul drifts dead-quiet at head height, bat
  swoops serpentine, brute stomps on a 0.9s cycle that shakes the camera by distance.
  Tier 1 looks: camera-facing boards (yaw-only, Lambert + alphaTest — lit by the
  scene) cut from `sprites/` via an in-browser analyzer that finds the visible
  bounding box and the glowing eyes; additive >1-green eye planes pierce the fog.
  Tier 2: `models/<kind>.glb`, height-normalized, walk clip auto-selected.
  At ~3.4m (brutes 3.8m) an enemy **lunges**: a 150ms ramp to a per-kind burst
  speed, pounce dip, hard steer onto you, eyes flaring 1.5x, animation at double
  speed — announced by a roar (brute) or a panned stinger (everything else). A
  global 600ms limiter keeps a pack from pouncing in unison.
- **The wave director** (solo only) — horror pacing instead of a metronome:
  LULL (no spawns, but panned groans and shuffles talk from the dark; shrinks
  from 9s toward 3.5s as kills mount) → CLUSTER (2–4 enemies pushing in down a
  shared lane) → CLEARING → a few seconds of QUIET opened by a tritone stinger →
  LULL again. Score climbs forever. Versus rooms keep the legacy fixed cadence
  verbatim, so both ends of a match see the same economy even across versions.
- **Slashing** — every input (finger, mouse, each tracked hand at ~15 Hz with
  between-frame interpolation) keeps a ~0.3s screen-space trail. Enemies project to
  screen circles each frame (26px minimum so deep targets stay fair) and the trail's
  segment+point collision — the proven 2D engine math, unchanged — does the rest.
  The visible slash is a tapered additive ribbon unprojected 2.2m in front of the
  camera, tail green, head hotter than 1.0 so the bloom ignites it, spitting embers.
- **Kills** — a kill LANDS: 60ms hitstop (only the world freezes — every
  contractual clock is wall-time), a hot slash flash along the cut, an ichor fan
  arcing toward the camera (never red) with droplets that splat and spread on the
  street, and the corpse is SHOVED along the cut as it crumples into smoke; a
  stencil +1/+5 floats up. Brutes take 3 hits behind a 420ms shield (one fast
  swipe can't chain them), stagger with a white-hot flash, and die into a 400ms
  quarter-speed finisher with a sub-boom. Kills within 1s chain combos: a
  pentatonic ladder climbs with each link, a thin ember bar under the callout
  drains the 1s window (glows at x3, pulses at x6), and a soft thud marks a
  broken chain. Every 25th kill: triple lightning + wolf howl.
- **The scare** — an enemy that reaches you despawns into smoke with a camera jolt,
  claw streaks (near-black + toxic rim), a roar and fabric-rip rasps. 1.5s cooldown,
  score untouched. Tension, no game over.
- **Sound** — 100% synthesized WebAudio (no files), all routed through one bus:
  master → compressor, with a synthesized-impulse convolver reverb send (every
  sound sits in a SPACE) and a waveshaper grit path for roars and impacts. A
  looped drone bed (lowpassed noise + a detuned 55/55.7Hz pair beating at 0.7Hz)
  hums under the night; a dynamic heartbeat tracks the nearest enemy from 1400ms
  calm down to ~450ms at 3m. Voices: chunky kill impact, dark pannable groans,
  wet shuffles, guttural grit roars, lunge stinger, finisher sub-boom, combo
  ladder + break thud, tritone lull stinger, thunder, wolf howl, claw rasps. The
  iOS audio plumbing (playback session, interrupted-state recovery, silent-loop
  ringer bypass, resume-on-any-tap) is the proven engine from classic,
  byte-identical.
- **Perf** — pixel ratio capped at 1.5, max 4 enemies (3–4 readable threats beat
  8 wallpaper ones), no shadow maps, no AA, merged draw calls. If fps sags: bloom
  off → grain off → fewer particles → lower resolution → max 3 enemies, one-way,
  never touching tracking. A pause-gap guard keeps a slept tab from faking "slow".
- **Multiplayer** — MQTT rooms, the Versus protocol (retained ~200-byte JSON,
  device-authoritative turns, sequence numbers) and WebRTC perfect negotiation are
  the classic engine, ported verbatim.

## Payload (why it loads fast)

| Asset | When | Size (approx) |
|---|---|---|
| three.module.min.js + addons (CDN) | always | ~0.9 MB (~0.25 MB gzipped) |
| textures/ (3 × CC0 JPGs) | always | 0.7 MB |
| sprites/ (5 billboards) | always | 0.75 MB |
| poster.png + fonts | always | ~0.2 MB |
| mqtt.min.js (CDN) | only on JOIN ROOM | 0.18 MB |
| MediaPipe wasm + hand model (CDN) | only in camera mode | ~8 MB, cached |
| models/*.glb (4 committed creatures) | always | 5.5 MB total |

## Texture sources (CC0 — Poly Haven)

Committed under `textures/`; the game falls back to dark procedural materials if
they're missing.

| File | Asset | Source |
|---|---|---|
| textures/asphalt_diff_1k.jpg | asphalt_02 | https://polyhaven.com/a/asphalt_02 |
| textures/brick_diff_1k.jpg | red_brick_03 | https://polyhaven.com/a/red_brick_03 |
| textures/concrete_diff_1k.jpg | concrete_wall_004 | https://polyhaven.com/a/concrete_wall_004 |

All CC0 (no attribution required — credited anyway). Downloaded via
`https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/<asset>/<asset>_diff_1k.jpg`.

## 3D rebuild test log

Tested in a desktop Chromium preview; each milestone's screenshot was compared
side-by-side against poster.png per the locked art direction (palette, shape
language, no kid-friendly elements). **Physical iPad/iPhone smoke test pending.**

- **M1 (a–d)**: classic.html frozen + verified; the 2D game ran as a strict-mode
  module with zero behavior change (full hook suite re-run) before any 3D code;
  night street verified — moon-over-tower with halo, flickering windows flush on
  real walls, fire reflections on wet asphalt, film grain; lightning strobe whites
  the street and reveals the horde; portrait 375×812 retuned (moon kept under the
  bloom threshold); degrade ladder steps forced; classic smoke test green.
- **M2**: all five kinds park exactly where asked (screen-ray spawn) and project to
  correct hit circles; touch swipes kill every kind at depths −6/−12/−20m (radii
  85/42/26px); brute exactly 3 swipes with stagger flashes → BRUTE DOWN +5; scare
  fires once (overlay + jolt, score untouched); spawner advanced 3 kinds at correct
  speeds; ichor/smoke/corpse pools live. Found + fixed: a splice had silently
  deleted the trail declarations (all input collision dead); fallback billboards no
  longer cache over late-loading art. Eye-pairs-in-fog screenshot is the signature.
- **M3**: synthetic 15Hz hand sweeps through the REAL pipeline killed every kind;
  brute exactly 3 sweeps; blooming ribbon + ember scatter + mid-sweep ichor burst +
  TRACKING ACTIVE pill captured on screenshot.
- **M4**: all ten synth voices attested live (AudioContext running); x3 combo; the
  25th kill fired FEARLESS! 25 with triple strike + howl; storm scheduler re-armed
  inside its 30–60s window.
- **M5**: full best-of-3 Versus against the real public relay (broker.emqx.io) with
  a protocol-correct simulated second player — zero clicks after the first, my
  turns scored through real slicing **including brute +5s**, watcher overlay with
  giant climbing score and ● tallies, Alex WINS finale, retained match state
  verified cleared, LEAVE ROOM clean. Found + fixed: a dangling `_mode` handler
  call (classic devices publish it) — now explicitly ignored; verified live with a
  fake classic peer in the room (board showed them, no errors).
- **Video co-op**: full two-context E2E against the real public relay — a second
  complete game instance in a same-origin iframe (own identity via a test-only
  URL override), synthetic canvas cameras, real MQTT signaling, real
  RTCPeerConnections CONNECTED with video flowing both ways. Verified: link
  auto-join with zero typing (and zero camera prompts before START), both-faces
  PiP with labels, mute, fullscreen swap, third-joiner "room is full" while the
  pair stays connected, leave-room stripping the mic instantly, and the graceful
  20s failure chip with kills still scoring through it. Found + fixed a latent
  engine deadlock: the partner-reload recovery path ('hi' session rebuild) was
  receive-only — nothing ever sent 'hi' — and the obvious fix raced the
  drop-triggered ICE restart; the call now also rebuilds deterministically from
  the room layer when the partner's roster join stamp changes. Verified live:
  drop mid-call → rejoin via the same link → reconnected with video both ways.
- **Tuning pass 1+2** (after the first real-hardware play): found the root cause
  of "still too dark" — the per-frame lightning envelope overwrote the light
  intensities with stale constants, so every init-time boost was dead code one
  frame later; all levels now live in shared constants used by both sites.
  Flashlight rake + rim light + brightness slider (drives the light rig, not
  exposure). Kill feel: hitstop frozen across `tick(50)` while an observer enemy
  held still, corpse knocked +0.6m along the cut / −0.5m away over 240ms, 34
  blood particles per kill, combo bar draining `scaleX(.999→.694)` across 220ms.
  Lunge: unpinned ghoul at 3.6m lunged at −3.33m and covered 1.5m in 300ms
  (exactly its 5.0 m/s burst); pack limiter held a trailing shambler. Director
  cycled quiet→lull(9s)→cluster(2 spawns, shared lane)→clearing→quiet→lull on a
  live 14s page recording. Bloom soup root-caused to the glossy floor mirroring
  the flashlight's specular lobe back into the camera — roughened, re-shot clean
  at slider 0.5/1/2. Acceptance gates (all bloom OFF, default brightness):
  mid-lunge ghoul at 2.85m fully readable; five-kind lineup at 10–12m readable
  (crawler smallest by design, lit in-beam). Full suite re-run green: touch 4/4,
  hand 4/4 through the real detection pipeline, brute 3-hit on BOTH paths with
  the same-instant double-swipe blocked by the shield, scare fired + despawned,
  16/16 voices attested (AudioContext running), 59–60fps, degrade step 0.

### Known issues / honest caveats

- **Four of five creatures are real rigged models** (Mixamo: zombie walk, zombie
  crawl, floating ghoul, mutant brute — moonlit, animated, fog-piercing eyes). The
  bat is still a generated-silhouette billboard; the other four `sprites/*.png`
  remain only as automatic fallbacks if a GLB fails to load.
- Physical-device smoke test pending: camera permission flow, real hand-tracking
  fps, audio after first tap, real GPU thermals. Checklist: load → START — CAMERA
  ON → Allow → wave → green pill + glowing dot → slash kills → MENU works.
- The Versus watcher's renderer pause is logic ported verbatim from classic (where
  live video was E2E-tested); it was not re-tested with a real camera call in this
  rebuild.
- GLB death animations aren't used yet — all kills use the crumple dissolve.
- Public MQTT relays carry no uptime promise; the room may occasionally be
  unavailable. The game says so and plays on solo.
- Score resets on reload — by design, the night just keeps counting.
