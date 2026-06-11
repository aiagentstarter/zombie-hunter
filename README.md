# 🍉 Fruit Party!

A Fruit Ninja–style browser game for little kids. Fruit floats up slowly, you slice it by
**waving your hand at the camera** (or just touching the screen). No bombs, no lives, no
game over — a 2-year-old waves and fruit explodes. Big celebration every 10 fruits.

Everything is one file: [index.html](index.html). No build step, no install, no server code.

---

## Put it online (GitHub Pages — free, ~5 minutes)

The camera **requires HTTPS**, which GitHub Pages gives you automatically.

1. Go to <https://github.com/new>. Repository name: `fruit-party`. Keep it **Public**. Click **Create repository**.
2. On the new repo page, click **uploading an existing file**, drag `index.html` in, click **Commit changes**.
   *(Or from this folder: `git remote add origin https://github.com/YOURNAME/fruit-party.git && git push -u origin main`)*
3. In the repo: **Settings → Pages** (left sidebar). Under **Branch** pick `main`, folder `/ (root)`, click **Save**.
4. Wait 1–2 minutes. Your game is at:
   **`https://YOURNAME.github.io/fruit-party/`**

Any other static host (Netlify Drop, Cloudflare Pages, Vercel) works the same — drop the
file in, get an HTTPS URL.

## Open it on the iPad

1. Open **Safari** and go to your `https://...github.io/fruit-party/` URL.
2. Tap **📷 Start (with camera)** → tap **Allow** when Safari asks for the camera.
3. Wave! (Optional: Share button → **Add to Home Screen** makes a full-screen app icon.)

First load needs internet (the hand-tracking model, ~8 MB, comes from a CDN — it's cached
after that). Sound starts after the first tap — that's an iOS rule, the Start button counts.

### The colored pill (bottom-left) tells you what the camera sees

| Pill | Meaning |
|---|---|
| 🟢 **✋ I see your hand!** | Tracking is working — a glowing dot follows your fingertip. |
| 🟡 **👋 Show me your hand** | Tracking is fine, but your hand isn't in the picture. Usually it's resting on the mouse/table, below the camera's view. Step back or lift your hand. |
| ⚪ **👆 Touch mode** | Hand tracking is off (couldn't load, or this device is too slow) — touching the screen always works. |

If no hand is seen for a while, the game says it outright: *"Step back so the
camera can see your hand!"*

### If something is off

| Symptom | Fix |
|---|---|
| Pill stays yellow | Your hand is out of frame — camera probably sees only your head and shoulders. Step back, or angle the camera down, then wave at chest height. |
| Camera prompt never appears / always denied | iPad **Settings → Apps → Safari → Camera → Ask/Allow**, then reload. Or in Safari tap **aA → Website Settings → Camera → Allow**. |
| "Camera needs a secure (https) page" | You opened it via `http://` or a file. Use the GitHub Pages `https://` URL. |
| No sound | Tap the screen once (any tap restarts the audio engine) and check the volume. The ringer/silent switch does **not** mute the game after the first tap — like a real game, it claims the speaker (which may pause background music). ⚙️ shows a live "Audio engine: …" line so you can see what it's doing. |
| Hands feel laggy | The game lowers its own tracking rate first, then rebuilds the tracker in a compatible mode, and only then switches to touch — the pill always shows where it landed. |

## Desktop

Chrome, Safari, or Edge — same URL. Mouse slices just by moving (no clicking needed).
For local development: `python3 -m http.server 8000` in this folder, then
<http://localhost:8000> (`localhost` is allowed to use the camera without HTTPS).

## Playing together on a video call (optional)

Tap **⚙️ → Play together**: both devices enter a nickname and the **same room code**, tap
**Join room**. Each player's name and live score appears top-left on both screens.

How it works, honestly: scores travel through a **free public MQTT relay**
(broker.emqx.io, with two fallbacks) over secure WebSockets — no account and no server,
but it's shared public infrastructure:

- Only the room code, nickname, and score are ever sent. Use first names or nicknames.
- Pick a **unique silly code** (`BANANA-MOON-42`), since anyone using the same code lands
  in the same room.
- If the relay is down, the game says so and plays on solo — multiplayer can never break
  the game. If the relay quietly drops the connection mid-game, the room rebuilds it by
  itself within a few seconds.
- To remove the feature entirely, set `ROOM_ENABLED = false` near the bottom of
  [index.html](index.html).

## Seeing each other (live video)

Join the same room on both devices and video simply appears — the other player shows up
in a small rounded picture-in-picture in the corner, with their name. You can talk too
(each device asks for the microphone; the 🎤 button on the picture mutes you).

- **Tap** the little picture to swap who's big. **Drag** it to any corner.
- **In Versus mode it gets good**: while it's the other player's turn, their live video
  fills your screen behind their name and climbing score — you're watching your kid
  play. On your turn they shrink back to the corner.
- A "🔴 you're on camera" badge shows whenever your video is being sent. Leaving the
  room closes the connection immediately and releases the microphone.

**Privacy, plainly:** the video and voice travel **directly between your two devices**,
encrypted end-to-end by WebRTC — they are never sent through any server. The public
relay only carries the small "let's connect" notes (a few KB of connection setup). New
room codes are now generated as random word combos like `banana-rocket-42` (tap ↻ for a
new one) because guessable codes matter more with video; a room only ever video-connects
its **first two** members — anyone else gets a polite "video is full" and just shares
scores. If video can't connect within 20 seconds (some strict networks need a TURN
server, which this setup deliberately doesn't require), you get a friendly note and
everything else — game, Versus, scores — works exactly as before.

## Playing Versus mode (take turns, best of 3)

Made for a parent on one device and a kid (with a helper) on the other:

1. Both devices join the **same room code** (see above).
2. On **one** device, open ⚙️ and tap **⚔️ Versus — take turns!**. That's the last
   button anyone needs to press.
3. From here it runs itself: the device that tapped goes first — big **"YOUR TURN!"**,
   a 3-2-1 countdown, then 30 seconds of slicing while a time bar shrinks across the top.
   The other device watches that player's name and score climb in giant letters.
4. Turns flip automatically. A round = one turn each; whoever slices more gets a ⭐
   (a tie gives one to each). Three rounds, most stars wins, and **both** screens get a
   confetti party — the other player sees a "Great game!" message, never a "you lost."
5. If someone's device drops out mid-round, the other screen shows
   *"💤 Waiting for …"* — the round restarts when they return, and after a minute the
   game gives up gracefully and goes back to free play.

Notes: kids never need to tap anything once the room is joined. If a third device is in
the room, the match pairs the tapper with the first other player; everyone else watches.

## Settings

⚙️ gear → one slider: **fruit speed** (🐢…🐇), saved on the device. Default is toddler-slow.

## How the code works (quick tour)

All in [index.html](index.html), top to bottom:

- **Sounds** — synthesized with WebAudio (no audio files): pop = pitch-drop square wave +
  filtered noise burst; quick combos pitch up; cheer = little arpeggio.
- **Fruit** — emoji drawn on a canvas (≥120 px). Each fruit picks where its arc should
  peak and how long it should take, and launch speed/gravity are derived from that, so
  the speed slider scales everything consistently.
- **Slicing / collision** — every input (each finger, mouse, each tracked hand) keeps a
  ~0.3 s trail of points. A fruit pops when the **segment between the last two points**
  passes within its radius (so fast swipes can't tunnel through), *or* when the newest
  point rests inside it (so a toddler holding a finger still pops fruit drifting by).
- **Hand tracking** — MediaPipe HandLandmarker (tasks-vision, pinned CDN version) watches
  the 640×480 selfie video and reports 21 landmarks per hand; we use #8, the index
  fingertip. Detection runs at ~15 Hz, and the blade glides toward the newest fingertip
  every frame, so the trail stays smooth between detections. Coordinates are mapped
  through the same object-fit:cover math the video uses, with X flipped for mirroring.
  A glowing dot marks every detected fingertip, and the status pill reports live whether
  a hand is currently seen.
- **Fallback ladder** — camera denied → gradient background + touch; load fails → one
  retry after 5 s; a detection exception retries 3× then rebuilds the tracker on the CPU
  delegate before giving up; detection averaging too slow → halves its rate, then
  rebuilds on CPU, then touch. Every step is visible in the pill — nothing fails
  silently, and touch/mouse slicing is always on.
- **Versus mode** — one retained ~200-byte JSON state on the room's `_versus` topic.
  Each device is authoritative only while it acts (its own countdown and turn), so no
  clock sync is needed and a second of relay lag is harmless; sequence numbers drop
  stale states, and presence staleness drives the "waiting for…" recovery.
- **Live video** — WebRTC peer-to-peer with "perfect negotiation" (the greater client id
  is the polite peer), signaled over the room's `_rtc` subtopic. The call reuses the same
  camera stream the hand tracker reads (the camera is never opened twice) plus a mic
  requested with echo cancellation. Outgoing video is capped at ~480×360 / 15 fps /
  400 kbps so gameplay stays smooth; hand detection pauses while you're just watching.
  Recovery ladder: ICE restart on drops, full renegotiation when the partner's page
  reloads (fresh session id), and a 10s stuck-detector. STUN only (Google); a TURN slot
  sits at the top of the file (`RTC_CFG`) — the old free Open Relay TURN was probed dead
  on 2026-06-11 and deliberately left out.
- **Auto quality** — if fps sags, the canvas renders at a lower resolution and the fruit
  cap drops before anything else suffers.

## Milestone test log

Tested in a desktop browser preview (Chromium). **Not yet run on a physical iPad — do the
2-minute checklist below before game time.**

- **M1 touch game**: synthetic swipe slices fruit (score increments); resting-point slice
  works; celebration banner at every 10; speed slider updates + persists; portrait resize
  correct; no console errors.
- **M2 hand tracking**: permission-denial path shows friendly message and keeps playing;
  with a fake camera stream MediaPipe loads from CDN, reaches "wave your hand" state, and
  stays healthy; coordinate mapping verified (camera center → screen center, mirror
  correct); under artificially slow software-GL the perf guard correctly self-disabled to
  touch. Real-hand-in-real-camera verified only by the math + pipeline, not a human hand.
- **M3 polish**: praise banner text, spawn boop, particle cap under rapid slicing.
- **M4 room**: joined a real public relay from the preview; second client appeared on the
  board with name + score; peer received local score updates; leave cleared everything;
  failure path falls back to a friendly message by construction.

### Update 2 (hand feedback + Versus) test log

- **Hand-motion slicing**: a synthetic fingertip sweep was fed through the *real*
  detection pipeline (camera-coordinate mapping → smoothing → trail → collision) at the
  real 15 Hz cadence and sliced a fruit parked mid-screen. Marker and green/yellow pill
  transitions observed live; the 10-second "step back" hint fired.
- **Recoverable failures**: two transient detection exceptions were absorbed (tracking
  survived); a permanent failure disabled tracking *with* the pill flipping to Touch
  mode while the game played on; the slow-GPU path live-rebuilt the tracker on the CPU
  delegate and came back green.
- **Versus, against the real public relay** with a protocol-correct simulated second
  player: full best-of-3 (16/13/14 vs 20/2/20 → 1:2), giant live watcher score,
  zero-click auto-advancing turns, mid-round disconnect → "Waiting for Emma…" →
  reconnect → round restarted → match completed; the one-minute friendly cancel; kind
  loser banner; both sides exited cleanly with the retained match state cleared.
- Found and fixed in the process: a public relay can kick a client with a *clean*
  disconnect, which silently stops mqtt.js auto-reconnect — the room heartbeat now
  detects a dead client and rebuilds the connection.

### Update 3 (live video) test log

Tested in a desktop preview against the real public relay, with a second simulated
player running a full WebRTC peer:

- **Signaling + media**: hi → offer → answer → ICE candidates exchanged as small JSON on
  the room's `_rtc` subtopic; both peers reached `signalingState: stable`,
  `connectionState: connected`, and the remote video **decoded real frames** both ways.
  Quality caps verified live on the sender (400 kbps / 15 fps / downscale to 480×360).
- **UI**: partner PiP with name in free play; tap-swap both directions; drag to any
  corner; Versus choreography confirmed by screenshot — their video fullscreen under
  their giant name + live score during their turn, back to the corner on yours; mute
  flips the shared mic track and the badge says "mic off".
- **Resilience**: mid-call crash noticed (`ice: disconnected`), partner rejoined with a
  fresh session id, full renegotiation reconnected with frames flowing; the
  third-joiner gate blocked video (zero signaling sent) with the polite chip while all
  three scores kept syncing; the kind 20s failure message appeared with the game,
  Versus, and scoreboard fully working throughout.
- **Not verifiable here**: real NAT traversal between two homes (preview is one
  machine). Most home-wifi↔home-wifi pairs connect over plain STUN; if yours doesn't,
  the failure path above is what you'll see, and a TURN server can be added in one
  place at the top of the file.

### Known issues / honest caveats

- **Physical-iPad smoke test pending** (needs a real device): camera permission flow,
  actual hand-tracking fps, audio after first tap. Checklist: load URL → Start with
  camera → Allow → wave → green pill + glowing dot → fruit pops → tap ⚙️ → slider moves.
- Hand identity can swap when two hands cross — a trail may briefly jump. Cosmetic.
- Very old iPads (pre-2017, no decent WebGL) will land in touch mode by design.
- Public MQTT relays carry no uptime promise; the room may occasionally be unavailable.
- Versus turn timing is driven by each device while it plays; if a device sleeps
  mid-turn (auto-lock), the other side sees "waiting" until it wakes. Keep auto-lock off
  or screens awake during a match.
- The score resets on reload — by design, it just counts up forever within a session.
