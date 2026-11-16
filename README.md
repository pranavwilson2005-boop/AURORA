# AURORA — Lunar Outpost Survival Game

A third-person lunar outpost survival game with a directly controlled commander, compact supply HUD, room modules, equipment interactions, a shared resource simulation, and a drone-style LOLA terrain map. The resource values are fictional game-balancing values, not official engineering specifications.

## Run

Requires Node.js 20+.

```powershell
npm install
npm run dev
```

Open `http://127.0.0.1:5173/` (or the next port Vite prints if 5173 is already occupied). Keep that terminal open while playing. Run `npm test` for the mission simulation checks. For a production build, run `npm run build`; use `npm run preview` to serve it locally.

## Playable scenario

The active first-person scene is the Life Support Centre, greenhouse and exterior EVA patch. The seven-day clock runs continuously while the scene is open. Water, oxygen, crops, crew condition and emergencies update in the HUD.

- Collect sealing tape from the storage cabinet, close the water valve, then drag across the hose three times to stop the leak.
- Collect seeds and plant them in the greenhouse tray. The crop advances as game time passes; interact with the mature tray to harvest food.
- Collect a first-aid kit and use it at Noah's medical bed to improve his health.
- Collect the replacement oxygen filter and install it at the scrubber to restore oxygen output.
- Walk through the south airlock, enter the rover, drive to the sample marker, and collect a lunar sample.
- A random emergency affects multiple systems. Use the emergency response console to resolve it.

## Controls

- **WASD** move; **Shift** run.
- **Mouse** rotate the third-person camera after clicking the 3D world; click again if mouse look has not engaged.
- **E** interact with nearby equipment, collect items, enter/exit the rover, or take a rover sample.
- **WASD** walk; while driving, **WASD** steers the rover.
- **Shift** run on foot.
- In the repair overlay, drag across the hose graphic three times to apply visible tape wraps.
- **Esc** releases mouse look or closes the repair overlay.

Approach equipment until its contextual prompt appears, then press E. Tools must be physically collected before use. Emergency events currently occur within the first minute and then at randomized intervals. The terrain tile is an exterior survey area, and the rover currently collects a single sample.

## NASA LOLA terrain processing

The original 189,158,392-byte raster is expected at `Dataset/LDEM_80S_80MPP_ADJ.tiff`. `Dataset/` is ignored by Git. The reproducible processor is `scripts/process_terrain.py` and requires Python, rasterio, NumPy and Pillow:

```powershell
python -m pip install rasterio numpy Pillow
python scripts/process_terrain.py
```

Outputs are in `public/assets/nasa/terrain/`: `terrain_preview.png`, normalized 16-bit `heightmap.png`, little-endian Float32 `elevation.f32` and runtime `game_elevation.f32`, `metadata.json`, and `DATASET_INFO.txt`. Runtime Three.js geometry loads the Float32 grid and samples it for terrain vertices and astronaut ground height. The M map uses the visualization made from the same crop. Fictional buildings and equipment are generated separately and placed over the measured surface.

The local source file reports a 7,600 × 7,600 Float32 raster, Moon 2015 ocentric south-polar stereographic CRS (IAU:30135), 80 m pixels, projected bounds ±304,000 m, and NaN NoData. The selected crop spans about 20.48 km and transforms to roughly 87.85–88.80°S. A coarse search selected the lowest-mean-slope fully valid ~960 m patch within 61 km of the pole (mean 0.593°, maximum 1.481° in that screening patch). This is a game-site convenience metric, not a landing safety assessment. Detailed transform, elevation range and rendering scale are in `metadata.json`.

Source credit: NASA/GSFC/Arizona State University, Lunar Reconnaissance Orbiter Lunar Orbiter Laser Altimeter (LOLA), south-polar LDEM product. Product description and data listing: [NASA GSFC PGDA — A New View of the Lunar South Pole from LOLA](https://pgda.gsfc.nasa.gov/products/90).

## Verification and limitations

`npm run build` runs TypeScript checks and creates the production bundle. `npm test` covers the mission clock, incident timing, continuous resource and crop updates, and seven-day completion. The playable room and props use procedural low-poly geometry; the astronaut is a simple suit model. Rover driving uses direct movement controls and is not a physics simulation. The terrain display uses a visual height scale; original metre values are retained in processed Float32 output and rendering scale is documented. Automated browser tests are not included.
