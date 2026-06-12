# 🧟 Zombie Hunter — *Survive the night*

A dark, stylized horde-slashing game built on the Fruit Party engine. Zombies climb out of
the ground, crawl, float, and swoop through a ruined moonlit city — you slash them by
**waving your hand at the camera** (or just swiping the screen). Glowing **green ichor**,
never gore. No lives, no game over: the score climbs forever, lightning storms roll
through, and every 25 kills the night celebrates you with a wolf howl.

Everything is static files: [index.html](index.html), `poster.png` (the title-screen
art), and the `sprites/` folder (the five photoreal enemy PNGs). No build step, no
install, no server code.

**🎉 Silly mode** flips the whole game into a bright purple-and-orange Halloween party
for little kids — same enemies, goofy smiles, confetti goo, giggles instead of groans.

---

## Put it online (GitHub Pages — free, ~5 minutes)

The camera **requires HTTPS**, which GitHub Pages gives you automatically.

1. Go to <https://github.com/new>. Repository name: `zombie-hunter`. Keep it **Public**.
   Click **Create repository**.
2. On the new repo page, click **uploading an existing file**, drag in `index.html`,
   `poster.png`, **and the whole `sprites/` folder**, click **Commit changes**.
   ⚠️ The poster must sit **next to index.html** and the five enemy PNGs must stay in
   `sprites/` — that's where the game looks for them. Missing art never breaks the
   game: no poster = plain dark gradient; a missing sprite = that enemy uses its
   built-in drawn fallback.
   *(Or from this folder: `git remote add origin https://github.com/YOURNAME/zombie-hunter.git && git push -u origin main` — the sprites are already committed)*
3. In the repo: **Settings → Pages** (left sidebar). Under **Branch** pick `main`,
   folder `/ (root)`, click **Save**.
4. Wait 1–2 minutes. Your game is at:
   **`https://YOURNAME.github.io/zombie-hunter/`**

Any other static host (Netlify Drop, Cloudflare Pages, Vercel) works the same — drop
**both files** in, get an HTTPS URL.

## Open it on the iPad

1. Open **Safari** and go to your `https://...github.io/zombie-hunter/` URL.
2. Tap **🌙 Start** → tap **Allow** when Safari asks for the camera.
3. Wave! (Optional: Share button → **Add to Home Screen** makes a full-screen app icon.)

First load needs internet (the hand-tracking model, ~8 MB, comes from a CDN — it's cached
after that; the Creepster title font is also a CDN fetch). Sound starts after the first
tap — that's an iOS rule; touching the title screen starts the heartbeat, the Start
button counts too.

### The colored pill (bottom-left) tells you what the camera sees

| Pill | Meaning |
|---|---|
| 🟢 **✋ I see your hand!** | Tracking is working — a glowing dot follows your fingertip. |
| 🟡 **👋 Show me your hand** | Tracking is fine, but your hand isn't in the picture. Usually it's resting below the camera's view. Step back or lift your hand. |
| ⚪ **👆 Touch mode** | Hand tracking is off (couldn't load, or this device is too slow) — touching the screen always works. |

If no hand is seen for a while, the game says it outright: *"Step back so the
camera can see your hand!"*

### If something is off

| Symptom | Fix |
|---|---|
| Pill stays yellow | Your hand is out of frame — the camera probably sees only your head. Step back, or angle the camera down, then wave at chest height. |
| Camera prompt never appears / always denied | iPad **Settings → Apps → Safari → Camera → Ask/Allow**, then reload. Or in Safari tap **aA → Website Settings → Camera → Allow**. |
| "Camera needs a secure (https) page" | You opened it via `http://` or a file. Use the GitHub Pages `https://` URL. |
| No sound | Tap the screen once (any tap restarts the audio engine) and check the volume. The ringer/silent switch does **not** mute the game after the first tap. ⚙️ shows a live "Audio engine: …" line so you can see what it's doing. |
| Hands feel laggy | The game lowers its own tracking rate first, then rebuilds the tracker in a compatible mode, and only then switches to touch — the pill always shows where it landed. |
| Title screen has no poster | `poster.png` isn't next to `index.html` on your host — upload it (any portrait-ish dark art works; the UI is layered on top). |

## Desktop

Chrome, Safari, or Edge — same URL. The mouse slashes just by moving (no clicking).
For local development: `python3 -m http.server 8000` in this folder, then
<http://localhost:8000> (`localhost` may use the camera without HTTPS).

## 🎉 Silly mode (for the 2- and 4-year-old)

Toggle it on the title screen (**👻 Silly mode**) or in ⚙️ settings. Everything flips
to a bright purple/orange Halloween party:

- the same five enemies redraw as goofy cartoons with big googly eyes and derpy grins
- ichor becomes **confetti goo**, groans become **giggles and boings**
- thunder goes soft and the scary lightning silhouettes stay hidden
- the title screen swaps the poster for a friendly cartoon scene (smiling moon included)

The choice is remembered on the device. **In a room it syncs**: whoever toggles last
wins, on every device — so both Versus players always see the same version.

## Hunting together (live scoreboard)

Tap **⚙️ → Hunt together**: both devices enter a nickname and the **same room code**
(spooky word combos like `GRAVEYARD-BAT-13` — tap ↻ for a fresh one), tap **Join room**.
Each player's name and live score appears top-left on both screens.

How it works, honestly: scores travel through a **free public MQTT relay**
(broker.emqx.io, with two fallbacks) over secure WebSockets — no account and no server,
but it's shared public infrastructure:

- Only the room code, nickname, score, and the Silly-mode flag are ever sent. Use
  nicknames.
- Pick a **unique code**, since anyone using the same code lands in the same room.
- If the relay is down, the game says so and plays on solo — multiplayer can never break
  the game. If the relay quietly drops the connection mid-game, the room rebuilds it by
  itself within a few seconds.
- To remove the feature entirely, set `ROOM_ENABLED = false` in
  [index.html](index.html).

## Seeing each other (live video)

Join the same room on both devices and video simply appears — the other hunter shows up
in a small rounded picture-in-picture in the corner, with their name. You can talk too
(each device asks for the microphone; the 🎤 button on the picture mutes you).

- **Tap** the little picture to swap who's big. **Drag** it to any corner.
- **In Versus mode it gets good**: while it's the other player's turn, their live video
  fills your screen behind their name and climbing score — you're watching your kid
  hunt. On your turn they shrink back to the corner.
- A "🔴 you're on camera" badge shows whenever your video is being sent. Leaving the
  room closes the connection immediately and releases the microphone.

**Privacy, plainly:** the video and voice travel **directly between your two devices**,
encrypted end-to-end by WebRTC — they are never sent through any server. The public
relay only carries the small "let's connect" notes (a few KB of connection setup).
A room only ever video-connects its **first two** members — anyone else gets a polite
"video is full" and just shares scores. If video can't connect within 20 seconds (some
strict networks need a TURN server, which this setup deliberately doesn't require), you
get a friendly note and everything else — game, Versus, scores — works exactly as
before. A TURN slot sits at the top of the file (`RTC_CFG`) if you ever need one.

## Playing Versus mode (take turns, best of 3)

Made for a parent on one device and a kid (with a helper) on the other:

1. Both devices join the **same room code** (see above).
2. On **one** device, open ⚙️ and tap **⚔️ Versus — take turns!**. That's the last
   button anyone needs to press.
3. From here it runs itself: the device that tapped goes first — big **"YOUR TURN!"**,
   a 3-2-1 countdown, **"HUNT! 🧟"**, then 30 seconds of slashing while a glowing time
   bar shrinks across the top. The other device watches that player's name and score
   climb in giant letters.
4. Turns flip automatically. A round = one turn each; whoever scores more gets a ⭐
   (a tie gives one to each — and brutes count their full +5). Three rounds, most stars
   wins, and **both** screens celebrate — the other player sees a "Great game!"
   message, never a "you lost."
5. If someone's device drops out mid-round, the other screen shows
   *"💤 Waiting for …"* — the round restarts when they return, and after a minute the
   game gives up gracefully and goes back to free play.

Notes: kids never need to tap anything once the room is joined. If a third device is in
the room, the match pairs the tapper with the first other player; everyone else watches.

## Settings

⚙️ gear → **zombie speed** slider (🐢…🐇, saved on the device, default toddler-slow) and
the **Silly mode** checkbox.

## How the code works (quick tour)

All in [index.html](index.html), top to bottom:

- **Sounds** — synthesized with WebAudio, no audio files. One shared `noiseBurst()`
  (decaying noise through a filter) powers the wet slash-splat, the brute's rasp, and
  the rolling thunder; oscillator ramps make the groans, bat screech, brute roar, wolf
  howl, title heartbeat — and the giggles/boings of Silly mode. Quick combos pitch the
  splat up. The iOS audio plumbing (playback session, interrupted-state recovery,
  silent-loop ringer bypass, resume-on-any-tap) is inherited from Fruit Party untouched.
- **Enemies** — five kinds. In spooky mode each is a **photoreal PNG from `sprites/`**:
  all five preload + decode behind the title screen, then get analyzed once on a
  scratch canvas — the alpha bounding box sizes the **hit circle to the visible
  creature** (not the file rectangle) and clusters of bright green pixels locate the
  eyes for a pulsing glow overlay. Render time is one plain `drawImage` from the
  pre-decoded image (no filters, nothing computed per frame), plus a slow 2–3 px
  breathing bob so the stills feel alive. A sprite that fails to load leaves that
  enemy on its drawn fallback. Silly mode always uses the drawn cartoon bodies.
  Movement: the shambler and the 3-hit brute rise from below on a derived arc
  (vy = -2h/T, g = 2h/T²); the crawler drags across the ground (flipped to face its
  travel); the ghoul floats up on a sine wobble; the bat swoops through. The brute
  flashes and staggers on each hit behind a 420 ms shield (so one fast swipe can't
  chain all three hits), then bursts for +5.
- **Sprite tooling** (not part of the deployed game) — `tools/prep_sprites.py` cleans
  whatever you drop into `sprites/`: removes a plain background if the PNG isn't
  transparent, defringes the matte, trims empty margins, downscales above 1024 px, and
  saves optimized files. `tools/make_placeholder_sprites.py` is what painted the
  current stand-in art.
- **Slashing / collision** — every input (each finger, mouse, each tracked hand) keeps
  a ~0.3 s trail. An enemy dies when the **segment between the last two points** passes
  within its radius (fast swipes can't tunnel), *or* when the newest point rests inside
  it (a toddler holding a finger still kills zombies drifting by). Kills within 1 s
  chain a combo (x2, x3 … callout + rising pitch).
- **The night** — scenery is cached in offscreen layers rebuilt on resize: a deep
  green tint + heavy vignette (also drawn over the camera feed), the moon and its
  halo, two dimmed ruined skylines, slow fog puffs, cloud streaks, and **faint film
  grain** (one pre-rendered tile stamped as a single repeating pattern fill per frame,
  cycling four offsets so it shimmers like film stock). Per frame only the cheap
  animated bits run: flickering windows, drifting fog, rising embers. Lightning is a
  double-blink envelope with thunder behind it; for one second per strike a
  pre-painted horde stands revealed in the skyline (hidden in Silly mode). A storm
  rolls through every 30–60 s, and every 25 kills triggers a triple-strike celebration
  with a wolf howl. Kills burst into glowing green ichor plus dark gobbets that tumble
  and dissolve into green-gray smoke — never red.
- **Hand tracking** — MediaPipe HandLandmarker (tasks-vision, pinned CDN version)
  watches the 640×480 selfie video and reports 21 landmarks per hand; we use #8, the
  index fingertip. Detection runs at ~15 Hz, the blade glides toward the newest
  fingertip every frame. Coordinates map through the same object-fit:cover math the
  video uses, X flipped for mirroring. The status pill reports live whether a hand is
  seen.
- **Fallback ladder** — camera denied → dark gradient + touch; load fails → one retry;
  a detection exception retries 3× then rebuilds the tracker on the CPU delegate before
  giving up; detection averaging too slow → halves its rate, then rebuilds on CPU, then
  touch. Nothing fails silently, and touch/mouse slashing is always on.
- **Silly mode** — one flag swaps: a `body.silly` CSS palette, per-kind purple/orange
  sprite repaints (`cute` branch in each painter: googly eyes + grins), party-colored
  scenery, confetti-goo ichor, giggle/boing voices, soft thunder, no horde, and a
  cartoon canvas title. Synced through the room as a tiny retained `_mode` message —
  newest change wins everywhere.
- **Versus mode** — one retained ~200-byte JSON state on the room's `_versus` topic.
  Each device is authoritative only while it acts (its own countdown and turn), so no
  clock sync is needed; sequence numbers drop stale states, presence staleness drives
  the "waiting for…" recovery. Turn scores count points (a brute is +5), not just
  slashes.
- **Live video** — WebRTC peer-to-peer with "perfect negotiation," signaled over the
  room's `_rtc` subtopic; the call reuses the same camera stream the hand tracker
  reads. Outgoing video is capped (~480×360 / 15 fps / 400 kbps) so gameplay stays
  smooth; recovery ladder: ICE restart, full renegotiation on partner reload, 10 s
  stuck-detector.
- **Auto quality** — if fps sags, the canvas renders at a lower resolution and the
  enemy cap drops before anything else suffers.

## Milestone test log

Tested in a desktop browser preview (Chromium). **Not yet run on a physical iPad — do
the 2-minute checklist below before game time.**

- **M1 theme + enemies + touch**: poster title screen with glowing Start; all five
  enemies parked on screen and verified visually (glowing eyes, palette); synthetic
  touch swipes through the real pointer-event path killed each kind; the brute took
  exactly 3 separate swipes (hp 3→2→1, no score until the kill, then +5 and the
  "BRUTE DOWN!" banner) — an early bug where one swipe could land the killing blow
  immediately after the second hit was found and fixed by moving the 420 ms post-hit
  shield in front of the kill branch; one swipe through three parked enemies popped
  the 🔥 x3 combo; kill VFX (green ichor, skull poof, flying +1, shake) captured in a
  screenshot; the 25-kill celebration fired; portrait (375×812) rebuilt the scenery
  correctly; zero console errors.
- **M2 hand tracking**: a synthetic fingertip sweep fed through the **real** detection
  pipeline (camera-coordinate mapping → smoothing → trail → collision) at the real
  ~15 Hz cadence killed shambler, crawler, ghoul, and bat parked mid-screen; the brute
  needed exactly 3 sweeps; `videoToScreen` verified (center→center, mirror correct);
  green pill during sweeps, yellow "Show me your hand" within ~1 s after the hand
  left. The degrade-but-never-disable ladder is byte-identical to Fruit Party (its
  recovery behavior was torture-tested there) and was not re-run here.
- **M3 sounds + lightning**: all nine spooky voices schedule cleanly (AudioContext
  `running`); the lightning envelope was sampled mid-strike (bright pop, the between-
  blink dip at ~80 ms, fade to 0); the natural storm armed itself inside the 30–60 s
  window and fired on its own; the horde silhouettes were caught on screenshot during
  a flash; heartbeat arms on the first title-screen touch and stops at Start.
- **M4 Silly mode**: toggled on the title screen and via the settings checkbox, both
  directions, persisted across reload; cartoon sprites + party scenery + smiling moon
  verified on screenshot; confetti goo on kills; giggle/boing scheduling clean;
  lightning in Silly mode showed no silhouettes; zero console errors.
- **M5 Versus against the real public relay** (broker.emqx.io) with a protocol-correct
  simulated second player: room joined with a spooky code (`CRYPT-OWL-9955`), the
  second player appeared on the board, Versus started with one tap and ran a full
  best-of-3 with **zero further clicks**: my turns scored through the real slicing
  path **including a brute +5** (7 / 0 / 2), the watcher overlay showed the opponent's
  giant climbing live score each turn, round banners ("Alex wins round 1!", stars)
  advanced automatically, the 2:2 tie ended in "🏆 You BOTH win! 🏆", and the retained
  match state was verified **cleared** afterward (a fresh subscriber received
  nothing). Silly-mode sync was exercised live in both directions over the relay
  (my toggle reached the peer; the peer's newer toggle flipped me back, with the
  friendly chip). Leave-room released everything.

- **M6 photoreal sprite reskin**: all five `sprites/` PNGs loaded, decoded, and
  analyzed (every kind reported two detected eyes; hit circles shrank to the visible
  creature — e.g. the narrow zombie's radius dropped from 60 to 41 px). The synthetic
  hand sweep killed each photo-sprite enemy through the real pipeline and the photo
  brute took exactly 3 sweeps with stagger flashes. A triple kill spawned 26
  chunk particles (12 from the brute) that were sampled again 800 ms later mid
  smoke-phase. Silly toggle re-dressed live enemies drawn↔photo both directions.
  Canvas stayed at full retina resolution (no perf-guard degradation) with sprites +
  grain active; zero console errors throughout.

### Known issues / honest caveats

- **All art is currently generated placeholder art.** `poster.png` and the five
  `sprites/*.png` are painted stand-ins in the right palette and poses — moody dark
  silhouettes with glowing eyes, not the photoreal renders. Save your real renders
  over the same filenames (any size; backgrounds OK), run
  `python3 tools/prep_sprites.py` once, and re-upload — zero code changes. The
  in-game eye-glow finds glowing green eyes in whatever art it gets.
- **Physical-iPad smoke test pending** (needs a real device): camera permission flow,
  actual hand-tracking fps, audio after first tap, Creepster font load on cellular.
  Checklist: load URL → 🌙 Start → Allow → wave → green pill + glowing dot → zombie
  splats green → ⚙️ slider moves → Silly toggle flips the world.
- The dropped-player "💤 Waiting…" recovery and the video call paths are engine-code
  inherited unchanged from Fruit Party (tested there); they were not re-run end-to-end
  in this reskin.
- Hand identity can swap when two hands cross — a trail may briefly jump. Cosmetic.
- Very old iPads (pre-2017, no decent WebGL) land in touch mode by design.
- Public MQTT relays carry no uptime promise; the room may occasionally be unavailable.
- Versus turn timing is driven by each device while it plays; if a device sleeps
  mid-turn (auto-lock), the other side sees "waiting" until it wakes. Keep auto-lock
  off or screens awake during a match.
- The score resets on reload — by design, the night just keeps counting up.
