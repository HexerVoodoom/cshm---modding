# The community: Digimon Modding Community Discord

Server ID `824985120817414155`. Read 2026-09-01 as HexerVoodoom. The 2022 invite in the
downloaded ReadMe (`discord.gg/hb6qXc3U`) has **expired** — reach it from the account's
server list, not that link.

## Channel layout

Live, per game — Cyber Sleuth has `#general`, `#modding`, `#projects` (forum, with a *Mod
Requests* thread) and a `#resources` **forum**. Time Stranger has its own `#general`,
`#modding`, `#research`, `#projects`.

In March 2023 Pherakki **archived** the old flat channels into an `archive` category. They
are read-only but fully readable:
`dscs-resources`, `dscs-3d-modelling`, `dscs-research`, `dscs-tools`, `dscs-mod_requests`,
`dscs-mod_releases`, `dscs-beta_tests`. `dscs-3d-modelling` ("for discussions of the DSCS
model format, and how to import new models into the game") and `dscs-research` are the two
with unextracted format knowledge — **neither has pinned messages**, so that knowledge only
exists as raw scrollback.

## Who to believe

| Person | What they own |
|---|---|
| **SydMontague** | DSCSTools, MVGLTools, archive and save formats. Answers format questions in `#modding`. |
| **Pherakki** | SimpleDSCSModManager, Blender-Tools-for-DSCS, the modders' guide, the server's structure. |
| **dantles1992** | New-Digimon research; the Big Digimon Pack; the model-porting video tutorials. |
| **Zeak6464** | Blender helper scripts (below). |
| **LoudKuyuki** | Tools and research; "Loud's custom Quests/Challenges" is the reference quest mod. |

## The curated resources (the `#resources` forum, 5 threads)

| Thread | What |
|---|---|
| `[Tool] SimpleDSCSModManager` | Pherakki. v0.1 binaries; docs in the repo's `Documentation/`. |
| `[Tool] DSCSTools` | SydMontague. Pack/unpack plus save encryption. Take the **static** build. |
| `[Tool] Blender-Tools-For-DSCS` | Pherakki. Import/export via the `.name` file. **Has a wiki**: `github.com/Pherakki/Blender-Tools-for-DSCS/wiki`. |
| `[Tool] YAML-MBE Tool` | logicallyanime, Jun 2025. MBE to/from **YAML**, ~3x faster than the CSV route, readable for localisation. **Text and message MBEs only — data MBEs unsupported.** Untested on Time Stranger. `github.com/logicallyanime/YAML_MBE_Tool` |
| `[Resource] Model name mapping list` | SydMontague. **The chr ID map** (below). |

## The chr ID map — use this before porting anything

<https://docs.google.com/spreadsheets/d/11zy6lzOl_4WR679IB9OflsXjRHZh8JvRFx8M6-nrWAI/edit>

Maps every `chrXXX` number to its Digimon **across games**: Another Mission, Adventure,
Re:Digitize, Decode, Cyber Sleuth, Linkz, Encounters, ReArise **and Time Stranger**. Columns
are `Chr ID`, `Last Known Mapping`, then one per game; `NO DATA` where the Digimon is absent.
This is the bridge between the two projects in this workspace.

Also pinned in `#general`: a Google Doc of textual errors in the Complete Edition, and
SydMontague's Switch-to-PC save conversion procedure (HxD plus
`DSCSToolsCLI.exe --saveencrypt`, removing eight 4-byte values at listed offsets in
`000X.bin` and padding 64 bytes into `slot_000X.bin` around `0x00000040`).

## Zeak6464's Blender scripts (pinned in `#modding`)

Three helpers, all Blender Python. The third is the important one.

**Split by loose parts** — separate a mesh into its disconnected pieces, which is how a
foreign model gets divided into the donor's mesh slots:

```python
import bpy
obj = bpy.context.active_object
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_loose()
bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.mode_set(mode='OBJECT')
```

**All actions to NLA strips** — the exporter reads animations from NLA tracks, so every
action in the Action Editor has to be pushed down:

```python
import bpy
for action in bpy.data.actions:
    nla_track = bpy.context.object.animation_data.nla_tracks.new()
    nla_strip = nla_track.strips.new(name=action.name, start=1, action=action)
```

**The exporter's custom-property contract** — Blender-Tools-for-DSCS reads these custom
properties off materials and objects. Without them the export is wrong or refused.
Known-good values from the pin:

```python
# on every material
material["CLUTSampler"]    = "[2, 1179, 0]"
material["ColorSampler"]   = "[0, 1417, 0]"
material["DiffuseColor"]   = "[1.0, 1.0, 1.0, 1.0]"
material["enable_shadows"] = "3"
material["shader_hex"]     = "088100c1_00880111_00000000_00050000"

# on every selected object
obj["export_binormals"] = "0"
obj["export_normals"]   = "1"
obj["export_tangents"]  = "0"
obj["name_hash"]        = "d0f5d39b"
```

`name_hash` is per-model and must not be copied blindly; the sampler and shader values are a
working baseline for a standard character material. `UNVERIFIED` what `shader_hex` selects,
and what the two integers in each sampler mean.

## Live troubleshooting worth keeping

- **Do not use ModernCSV.** It appends a comma after the last column, which SDMM rejects as
  "some file is malformatted". Use LibreOffice. (DanKings and SydMontague, Aug 2026.)
- `join () takes exactly one argument (2 given)` on build — SydMontague's first guess is a
  syntax error in a mod JSON; the reporter traced it to `item_para.mbe/table.csv`. **Still
  open as of 2026-09-01.**
- Black or missing textures on an imported model (Hyotan, Aug 2026): a `.001` suffix on a
  texture name in Blender; file extensions accidentally included in texture names inside the
  model (check with a hex editor — they should not be there); or the material's diffuse
  colour node set to `0 0 0`.

## Tutorials

dantles1992, linked from the `#modding` pins:

- *Digimon Story Cyber Sleuth — How to Port Models Tutorial* — <https://youtu.be/uI3nfbu-Cv8>
- *HOW TO PORT New Century MODELS TUTORIAL* — <https://youtu.be/o56T5TWEBrM>

## What has NOT been read

The curated layer is covered: every pin in the Cyber Sleuth `#general` and `#modding`, the
whole `#resources` forum, and the archived `#dscs-resources`. **The raw scrollback has not
been read** — `#modding` (2021 to now), `#general`, the `#projects` forum threads, and the
archived `#dscs-3d-modelling`, `#dscs-research`, `#dscs-tools`, `#dscs-beta_tests`. That is
five years of messages across a dozen channels and cannot be swept in one pass. The two
worth doing next, in order, are **`dscs-3d-modelling`** and **`dscs-research`** — they hold
format knowledge that was never pinned or written up anywhere else.
