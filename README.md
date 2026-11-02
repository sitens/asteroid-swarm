# The Near-Earth Swarm

**Live:** [asteroids.siten.ai](https://asteroids.siten.ai)

4,606 real near-Earth asteroids from NASA/JPL — positions computed in real time by solving Kepler's equation. Every potentially hazardous asteroid known to humanity, plus the largest of the remaining NEOs by absolute magnitude.

![Near-Earth Swarm screenshot](https://asteroids.siten.ai/screenshot.png)

---

## What it does

- **Live orbital propagation** — each frame solves Kepler's equation using real orbital elements (semi-major axis, eccentricity, inclination, argument of perihelion, mean anomaly, epoch) from the JPL Small-Body Database
- **4,606 asteroids** rendered simultaneously on a Canvas 2D at ~35 FPS
- **2,547 hazardous objects** (PHAs) highlighted in amber
- **119 confirmed close approaches** ≤ 5 lunar distances through 2033, from CNEOS CAD — each with live countdown and fly-to navigation
- **Orbit class color coding** — Apollo (amber), Aten (teal), Amor (purple), Atira (pink)
- **Interactive** — drag to rotate, scroll to zoom, click any asteroid or close-approach entry to fly to it, toggle orbit classes on/off
- **Time control** — scrub date, adjust simulation speed, pause/play
- **Zero runtime dependencies** — physics engine, NASA imagery, and Hubble galaxy backdrops all inlined; single HTML file, works offline

---

## Data sources

| Source | What |
|--------|------|
| [NASA/JPL SBDB Query API](https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html) | Orbital elements for all NEOs (Apollo, Aten, Amor, Atira classes) |
| [NASA CNEOS CAD API](https://ssd-api.jpl.nasa.gov/doc/cad.html) | Close approach data ≤ 5 LD through 2033 |
| NASA/ESA imagery | Sun, planet textures |
| Hubble via Wikimedia Commons | Galaxy backdrop |

Data snapshot: **2026-07-27**. Refresh by re-running `scripts/build_data.py` and `scripts/build_html.py`.

---

## Repository structure

```
asteroid-swarm/
├── site/
│   ├── index.html      # Self-contained deployable (808 KB) — inlines all data + code
│   └── data.js         # Compiled orbital data (window.NEO_DATA) used by build script
├── src/
│   └── template.html   # HTML source before data injection (~40 KB)
├── scripts/
│   ├── build_data.py   # Fetches JPL SBDB + CNEOS → site/data.js
│   └── build_html.py   # Inlines site/data.js into src/template.html → site/index.html
├── data/
│   └── raw/            # Raw API responses (gitignored — large)
└── wrangler.toml       # Cloudflare Workers static assets config
```

---

## Building from source

**Requirements:** Python 3.8+, internet access for API calls.

**1. Fetch fresh data from JPL:**
```bash
python scripts/build_data.py
```
Writes `site/data.js` (~335 KB).

**2. Build the self-contained HTML:**
```bash
python scripts/build_html.py
```
Inlines `data.js` into `src/template.html`, writes `site/index.html`.

**3. Open locally:**
```bash
open site/index.html
# or just drag into a browser — no server needed
```

---

## Deployment

Uses [Cloudflare Workers static assets](https://developers.cloudflare.com/workers/static-assets/).

```bash
npx wrangler deploy
```

Deploys `site/` directory. Custom domain configured as `asteroids.siten.ai` in the Cloudflare dashboard.

---

## Physics

Each asteroid's position is computed per frame:

1. **Mean motion** `n = 2π / period`
2. **Mean anomaly at current time** `M = M₀ + n·(t - epoch)`
3. **Eccentric anomaly** E solved from Kepler's equation `M = E − e·sin(E)` via Newton-Raphson
4. **True anomaly** from E and eccentricity
5. **Heliocentric position** in the orbital plane, then rotated by (ω, i, Ω) into the ecliptic frame

All math runs in-browser — no server, no WebAssembly, plain JavaScript.

---

## Credits

- Orbital data: NASA/JPL Small-Body Database & CNEOS
- Imagery: NASA, ESA, Hubble via Wikimedia Commons
- Built by [Siten Sanghvi](https://siten.ai)
