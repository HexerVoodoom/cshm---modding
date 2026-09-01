# 00 — Orientation

## What you are modding

**Digimon Story Cyber Sleuth: Complete Edition** is one executable containing **both**
games: *Cyber Sleuth* (CS) and *Hacker's Memory* (HM). They share one asset database, one
Digimon roster and one set of tables. There is no separate HM install to mod.

The engine is Media.Vision's, the same family as *Digimon Story: Time Stranger* and
*The Hundred Line*. Read [../reference/vs-time-stranger.md](../reference/vs-time-stranger.md)
before you carry any assumption across.

## The shape of the game data

```
<game>/
  resources/            the shipped archives — 5 main MDB1 + sound + video. NEVER hand-edit.
    DSDB.steam.mvgl     2.7 GB, most of the game
    DSDBP.steam.mvgl    highest priority; SDMM rebuilds THIS one
  DSDB/                 the UNPACKED reference extraction (read-only for us)
    data/     214 .mbe tables  — the game database (stats, evolution, shops, quests...)
    text/      61 .mbe tables  — names and descriptions, one column per language
    message/ 1451 .mbe tables  — conversation text, one table per scene
    script64/                  — Squirrel 2.2.4 bytecode (decompilable)
    images/                    — DDS textures with an .img extension
    shaders/                   — plaintext Cg
    *.name/.skel/.geom/.anim   — models, loose at the top level
  mods/                 SDMM's mod library (source mods, not built output)
  SimpleDSCSModManager/ the mod manager, its config and its documentation PDFs
  app_digister/         DSCSModLoader.dll — a *separate* loader for whole .mvgl mods
```

## What "modding" actually means here

Cyber Sleuth has a static asset database and **no merge capability**. If a mod ships a
file, that file replaces the vanilla one wholesale. Adding one Digimon by shipping
`digimon_common_para.mbe` would delete every other Digimon.

SDMM exists to solve exactly that. You write a mod containing **only the records you
touch**, and SDMM merges them into the vanilla data and re-packs `DSDBP`. That merge is
the single most important idea in this guide; everything in
[05-sdmm-mods.md](05-sdmm-mods.md) follows from it.

## The two roads into the game

| Road | Loader | Use it for |
|---|---|---|
| **SDMM** | `SimpleDSCSModManager.exe` rebuilds `DSDBP.steam.mvgl` | Everything in this guide: data, text, scripts, models, textures. |
| **DSCSModLoader** | `app_digister/DSCSModLoader.dll` loads extra `.mvgl` files | Pre-built third-party archives. This install already has ~12 of them. |

They coexist. When a vanilla assumption does not hold on this machine, suspect the
`.mvgl` files listed in [../reference/archives.md](../reference/archives.md).

## The squad

Agents live in `../../.claude/agents/`. They share this guide as their ground truth.

| Agent | Owns |
|---|---|
| `cshm-researcher` | "What controls X?" — read-only sweeps over 3025 sheets. Answers, not dumps. |
| `cshm-table-surgeon` | Edits `.csv` records inside a mod folder. Never touches the install. |
| `cshm-mod-builder` | End-to-end: request → validated SDMM mod folder. |
| `cshm-script-modder` | Squirrel: interactive NPCs, custom battles, `.sqmod` surgical edits. |
| `cshm-porter` | Bringing a model in from another game and making it load and deform. |
| `cshm-vfx-voice` | Custom skills: the data chain, effect models, cameras, sound and voice. |
| `cshm-art` | Models and `.img` textures in general. |
| `cshm-qa` | The verdict before a mod is built or shown to the user. Read-only. |

Skills: `cshm-modding` (orientation), `cshm-new-digimon` (the full add-a-Digimon procedure),
`cshm-scripted-npc` (NPCs, dialogue, battles, playable-character swaps).

The rule that holds them together: **no agent reports success on a claim it has not run a
command to prove.**
