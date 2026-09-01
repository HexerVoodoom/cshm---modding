# 01 — Setup

## What this machine already has

Verified on 2026-09-01 (`python tools/cshm.py env`):

- Game at `E:/SteamLibrary/steamapps/common/Digimon Story Cyber Sleuth Complete Edition`
  (recorded in [../reference/game-path.txt](../reference/game-path.txt); two other Steam
  libraries hold empty stub folders for the same appid — ignore them).
- `DSDB/` already unpacked: 214 `data` tables, 61 `text`, 1451 `message`, 42 551 files total.
- `SimpleDSCSModManager/` installed, with `Documentation/modders_guide.pdf` and
  `user_guide.pdf` — the upstream reference this guide is built on.
- `app_digister/DSCSModLoader.dll` present, plus ~12 third-party `.mvgl` mods in `resources/`.
- One existing mod in `mods/`: `Kyoko` (a texture/model swap; `METADATA.json` +
  `modfiles/images/`). Useful as the smallest real example of a mod folder.

> The game executable was **not** found in the install root during setup. If the game will
> not launch, verify files through Steam before blaming a mod. `UNVERIFIED` whether this is
> a broken install or the exe simply lives elsewhere on this setup.

## Tools

| Tool | What for | Where |
|---|---|---|
| **SimpleDSCSModManager** | Install, merge and build mods. Also extracts archives. | [GameBanana 8918](https://gamebanana.com/tools/8918) · [GitHub](https://github.com/Pherakki/SimpleDSCSModManager) |
| **DSCSTools** | The pack/unpack/MBE↔CSV engine SDMM drives. | Pherakki/SydMontague |
| **MVGLTools** | Newer, multi-game (`--game dscs`), CLI. Handles MDB1, MBE↔CSV, AFS2, encryption, saves. | [GitHub](https://github.com/SydMontague/MVGLTools) |
| **Blender Tools for DSCS** | Import/export `.name` models in Blender. | [GitHub](https://github.com/Pherakki/Blender-Tools-for-DSCS) |
| **vgmstream** | Play the `.hca` audio that comes out of AFS2. | vgmstream.org |
| `tools/cshm.py` (this repo) | Query the unpacked database. Python 3, no dependencies. | here |

MBE conversion in DSCSTools/MVGLTools needs the `structures/` folder **relative to your
working directory** — `cd` into the folder holding the binary before calling it.

## First thing, every session

```bash
python tools/cshm.py env
```

If that does not print a game path and table counts, stop and fix it. Everything else
depends on it.

## Before your first mod

1. **Back up the save**: `<game>/gamedata/` equivalents for DSCS live in the Steam userdata
   folder — copy it. Mods that add records can corrupt a save if removed later.
2. Install `mods/Kyoko` through SDMM and build once, so you know the chain reaches the game
   before you build something of your own.
