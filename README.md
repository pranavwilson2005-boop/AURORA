# AURORA — Lunar Outpost Survival Simulator

AURORA is a fictional 30-day lunar base survival strategy game. Manage four astronauts, balance supplies, inspect eight outpost locations, repair equipment, assign work and respond to changing conditions. All resource values are illustrative game-balancing values, not NASA engineering specifications.

## Run locally

Requirements: Node.js 20 or newer.

```sh
npm install
npm run dev
```

Open the local URL printed by Vite. The app autosaves the current mission in browser local storage; choose **Continue Mission** from Home to resume.

## Production build

```sh
npm run build
npm run preview
```

## Gameplay

Choose a commander name, start a mission, and use the Drone/First Person controls to switch between an outpost map and room inspections. Select locations on the map, assign crew from Crew, repair with spare parts, and upgrade facilities with materials. **End Day** runs the resource and crew simulation. Survive through day 30 with all four astronauts alive.

The first-person view is an illustrated room inspection mode with contextual facility condition and equipment indicators. Crew assignments, repairs, facility condition and resources share one saved simulation state between views.

## Checks

`npm run build` performs TypeScript checking and creates the production bundle. No automated browser or unit test suite is currently included.

## Known limitations

- Event timing uses runtime randomness rather than a seeded generator.
- The first-person view uses supplied environment art rather than free movement through a 3D environment.
- Lunar ice prospecting and emergency resupply are not implemented as decision systems; research is tracked as a progress resource.
- Some requested event types and equipment subsystems are represented by a simplified condition/resource model.
- The visual package provides concept art, which is used as supplied and may include backgrounds or framing.

## Assets

Supplied individual visual assets are integrated from `public/assets/` including room backgrounds, building illustrations, crew portraits and resource icons. Maya's exact display name is **Maya Quinn White**.
