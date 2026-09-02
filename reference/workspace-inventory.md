# What is already on this machine

Surveyed 2026-09-01. Author handle: **Mojoceramon AKA HexerVoodoom**.

## Game and database

- `E:/SteamLibrary/steamapps/common/Digimon Story Cyber Sleuth Complete Edition`
- `DSDB/` — the full unpacked database (42 551 files; 214 data / 61 text / 1451 message
  tables). This is the "whole game extracted" folder. There is no second one.
- `resources/` — vanilla `.mvgl` plus ~12 third-party archives loaded by `DSCSModLoader.dll`.

## Tools

| Tool | Where |
|---|---|
| SimpleDSCSModManager | `<game>/SimpleDSCSModManager/` (+ `Documentation/*.pdf`) |
| DSCSModLoader | `<game>/app_digister/DSCSModLoader.dll` |
| **MVLibraryNET.GUI** | `E:/DIGIMON MODS/EXTRACT/MVLibraryNET.GUI.exe` — SydMontague's GUI archive tool |
| Blender **2.83** | `C:/Program Files/Blender Foundation/Blender 2.83`, addons include **Blender-Tools-for-DSCS**, plus XNALaraMesh, NifTools, SourceIO, XXMITools, retargeting |
| Blender **2.92** | addons: **Blender-Tools-for-DSCS** *and* `Blender-Tools-for-DSCS-develop` |
| Blender 4.1 / 4.2 / 4.5 / 5.1 | Time Stranger and general work — **no DSCS addon** |

The addon supports **2.80–2.91**, so **use 2.83**. The 2.92 install has the addon but sits
outside the supported range — the Discord's own advice is that the tools "work with 2.80-2.91
inclusive". No modern Blender here has the DSCS addon.

## The user's own mods

| Where | What |
|---|---|
| `C:/Users/spera/Documents/` (loose `METADATA.json` + `modfiles/`) | **WIP: two new Digimon** — Samudramon_FB (Gaioumon: Itto Mode) and duramon_sword_form (Durandamon Sword Form). 130 files: full model + animation + camera + effect sets, 15 data tables, 4 text tables, all softcoded. The source of [guide/10-new-digimon.md](../guide/10-new-digimon.md). |
| `C:/Users/spera/Documents/METADATA.json` | *"DW2 Challenge Battle ost"* — a Voice-category mod. |
| `E:/DIGIMON MODS/SAMUDRAMON/` | Source assets: `chr_samudramon.fbx`, two `.blend` files, six `.dds`. |
| `<game>/SimpleDSCSModManager/mods/` | `Kyoko`, `Kyoko - Copy`, `nokia`, `nokia - breasts`, `nokia - pc`, `nokia backup`, `rie - breasts`, and `mods cshm/` holding three built zips. Plus loose `nokia*.blend` working files. |
| `<game>/mods/Kyoko/` | The installed texture mod. |
| `C:/Users/spera/Downloads/digimon/` | ~40 community reference mods (zips) + `ReadMe.txt`. |

## The reference corpus

The ~40 zips in `Downloads/digimon` are **texture-only** mods — `METADATA.json` +
`modfiles/images/chrNNNa01.img`, `chrNNNa02.img`, `ui_chara_icon_1NNN.img`. Three unpacked
under `chaos lords/`. They are the reference for the *appearance* path, not the
*new-record* path.

For the new-record path the community reference named in the ReadMe is **Big Digimon Pack
by Dantles1992** ([gamebanana 379118](https://gamebanana.com/mods/379118)).

Credits from that ReadMe: SydMontague, Pherakki and LoudKuyuki for the tools; Dantles1992
for the new-Digimon research. Community Discord: `https://discord.gg/hb6qXc3U`.

## SimpleDSCSModManager was broken, and why

**Fixed 2026-09-01.** Both SDMM installs crashed on startup with

```
File "CoreOperations\PathManager.py", line 179, in game_executable_loc
AttributeError: 'PathManager' object has no attribute 'self'
```

The crashlogs in `SimpleDSCSModManager-develop/SimpleDSCSModManager/logs/` go back to
**11 July 2026**, so nothing could be built for two months.

Cause: `config/config.json` had

```json
"game_loc": "D:\SteamLibrary\steamapps\common\Digimon Story Cyber Sleuth Complete Edition"
```

but that folder is an **empty stub** — it contains only `resources/backup`. The real install
is on **E:** (Steam's `appmanifest_1042550.acf` lives in `E:/SteamLibrary/steamapps`,
`StateFlags 4`, 5.9 GB). SDMM could not find the executable, and its own error path has a
typo (`self.self`) that turns "game not found" into a fatal crash instead of a message.

Pointing `game_loc` at the E: install makes it start normally. The original file is kept as
`config/config.json.bak-before-claude`.

Worth knowing while you are in there: this game keeps **no executable in its root**. Everything
lives in `app_digister/` — `Digimon Story CS.exe`, `DSCSModLoader.dll`, `steam_api64.dll`,
`cg.dll`, `opengl32.dll`. An empty-looking game root is normal here.

The profiles in `SimpleDSCSModManager-develop/SimpleDSCSModManager/profiles/*.profile` still
reference `C:\SteamLibrary\...`, a path that does not exist on this machine, so the saved
mod selections are stale too.

## The mod set the save depends on

**Installing a mod set replaces the whole set.** SDMM rebuilds `DSDBP` from exactly what is
ticked, so anything previously installed and not ticked is *removed* — and a save that
contains a Digimon or item from a removed mod will crash on load.

The `New Profile` in the **develop** install (`SimpleDSCSModManager-develop/.../profiles/`)
has these **12 mods enabled**, and this is the set to restore before loading an older save:

```
ARESTERDRAMON
DSCS-Mod-UnlockHackingSkills-master
DigiDestined
Playable Rina
UI
atlur kabuterimon blue
battle_cam
chaosmon_ulforce_veedramon_and_jesmon_c7b72xxx
easy_hacking_skills_8f96d
exp_item
gmtyrano_mod
no_red_outline
```

Four of them add new Digimon — `ARESTERDRAMON`, `chaosmon_ulforce_veedramon_and_jesmon`,
`gmtyrano_mod`, `Playable Rina` — which is what a save is most likely to depend on.

Caveat: those profile entries store paths beginning `C:\SteamLibrary\...`, a drive that does
not exist here, so SDMM may not map the saved ticks onto the mods folder. The names above are
the reliable part; tick them by hand.

## Known problems in the WIP mod

1. **`text/charname.mbe/Sheet1.csv`** — vanilla's sheet is **`Digimon Names.csv`**. Very
   likely a silent no-op, leaving both Digimon nameless in game.
2. **Duplicated tables at `modfiles/` top level**: `battle_command.mbe`,
   `battle_command_effect.mbe`, `battle_effect.mbe` exist both at the root *and* under
   `data/`. Outside `data/` they are not table sheets. Two of the three **differ** from the
   `data/` copies, so this is not a harmless duplicate — one version is stale.
3. `images/eff_lig_04f.img.img` — double extension.
4. `duramon_sword_form_[Action Stash].anim` and `.001.anim` — Blender action-stash leftovers
   shipped as animations.
5. Vanilla effect textures (`eff_fir_*`, `eff_lig_*`, `eff_par_*` …) are redistributed
   rather than requested with `.request`.
6. The mod lives loose in `Documents/`, not in a named folder — SDMM expects
   `<ModName>/METADATA.json` + `<ModName>/modfiles/`.
