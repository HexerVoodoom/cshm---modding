# 07 — Models and textures

## The file split

A model is a set of files sharing one stem. Four are required:

| Ext | Required | Contents |
|---|---|---|
| `.name` | yes | Bone names and material names. |
| `.skel` | yes | The rest pose (equivalent to frame 1 of the base animation). |
| `.geom` | yes | Bind pose, materials, texture names, lights, cameras. |
| `.anim` | yes | Animation data — the **base animation**, constantly playing, often empty. |
| `.phys` | no | Colliders (maps). |
| `.detr` | no | Appears to be NPC walk paths. `UNVERIFIED` |
| `.note` | no | Appears to affect text rendering. `UNVERIFIED` |
| `.sprk` | no | Appears to be particle effects. `UNVERIFIED` |
| `.navi` | no | Used in "autoran" models; possibly another walk path. `UNVERIFIED` |

Import/export with [Blender-Tools-for-DSCS](https://github.com/Pherakki/Blender-Tools-for-DSCS)
— point it at the `.name` file. **It works on Blender 2.80-2.91 only, not 3.x or later.**

Two rules that decide whether a model works at all:

- **`name_hash` is a mesh slot.** When a mesh loads, every loaded mesh sharing its hash is
  removed. That is the costume system, and it is how a replacement mesh claims a slot.
- **Bones are addressed by index, not name.** A donor skeleton with its bones in a different
  order deforms wrongly and nothing warns you.

Both, plus every export error and its cause, are in
[../reference/model-porting.md](../reference/model-porting.md).

## Naming is the API — and `BUILD.json` is how you satisfy it

The game locates models **by filename**: `chr009` is Digimon 9 because ID 9 is 9. There is no
table that says "Digimon 9 uses this model". A custom Digimon's files must end up named
`chr<its id>.*` or the game will never load them.

You do **not** name your files that way in the mod folder, because the ID is not known until
SDMM assigns it. You author them under any readable stem and let **`BUILD.json` rename them
at build time**:

```json
{ "{0}[Digimon::MyMon::filename()]{1}": {
    "BuildSteps": "{0}MyMon{1}",
    "Variables": [{ "Regex": "(.*)MyMon(.*)" }] } }
```

That one rule installs `MyMon.name`, `MyMon_ba01.anim`, `cam_MyMon_bs01_pc.geom`,
`eff_bts_MyMon_bs02.skel` and every other match under the resolved `chr###` name.

**A custom model with no rename rule installs under its literal name and is dead weight.**
Full mechanics, including the one-file-at-a-time form and the icon paths, in
[../reference/mod-patterns.md](../reference/mod-patterns.md#0-buildjson-is-the-rename-map--the-thing-that-makes-everything-else-possible).

| Prefix | What |
|---|---|
| `chr` | Digimon / enemies |
| `pc` | Player characters, including outfits |
| `npc` | Named supporting cast |
| `mob` | Generic NPCs |
| `acc` | Accessories |
| `cam` | Cameras, including attack cameras |
| `eff` | Effects, including attack effects |
| `ui` | UI elements — all implemented as 3D models |
| `dXXXX` | Dungeon maps |
| `tXXXX` | Town maps |

Map models split by suffix: `f` field mesh, `c` collision, `s` surface (floor copy),
`p` position (triggers, NPC spawns), `_cam` camera, `_hide` meshes that fade when the
camera would be blocked. These are exactly the softcode functions in
[05-sdmm-mods.md](05-sdmm-mods.md).

## Animations

`chr003.anim` is the base animation for `chr003`. Overlays add a suffix:

| Suffix | Animation |
|---|---|
| `ba01` / `ba02` | Battle attack — basic attack / skill |
| `bb01` | Battle move backwards |
| `bd01` / `bd02` / `bd03` | Damage taken / knocked down / getting up |
| `bg01` | Damage while guarding |
| `bn01` | Battle idle |
| `br01` | Battle run |
| `bs01` / `bs02` | Special Skill 1 / 2 |
| `bv01` | Victory |
| `fn01` / `fw01` / `fw02` / `fr01` | Field idle / walk / slow walk / run |
| `fe01` | Eating in the DigiFarm |
| `e…` | Emotes in conversation |
| `ev…` | In-engine cutscene events, suffixed by chapter |
| `fXX_mXX` | Face and mouth (facial expression) |

The game **falls back**: with no `fr01`, it uses `br01`. That is why most `chr` models ship
few field animations — and why a missing animation often looks like a wrong animation
rather than a crash.

## Textures

`images/` holds DDS files with an **`.img`** extension. `images_as`, `images_de`,
`images_kr` are the Traditional Chinese, German and Korean variants.

The `Kyoko` mod on this install is the reference example: it ships six files into
`modfiles/images/` — a mix of `.img` and `.dds`, replacing character textures and UI icons.

`UNVERIFIED`: the exact DDS formats/mip requirements per texture role in DSCS. The Time
Stranger texture-format table does **not** transfer — do not apply it here. Check an
existing vanilla `.img` header before encoding a replacement.

## The exporter's custom-property contract

Blender-Tools-for-DSCS does not infer material settings - it reads **custom properties** off
each material and object. A model exported without them is wrong or refused. The known-good
baseline, the NLA-strip requirement and the loose-parts split script are all in
[../reference/community.md](../reference/community.md).

Two traps reported in the community for a model that imports black or untextured: a `.001`
suffix on a texture name, and file extensions left inside the texture names in the model
(check with a hex editor - they should not be there).

## Shaders

`shaders/` is plaintext **Cg** — a deprecated language predating HLSL. The game runs the Cg
runtime on OpenGL. Editable, but nothing here has been tested.

## `.mdledit`

A JSON model-edit script. In SDMM v0.1 it is a proof-of-concept that can only **add NPCs to
maps**:

```json
{ "editNPC": { "id": 8, "position": [0,0,0], "rotation": [1,0,0,0], "scale": [1,1,1] } }
```

Rotation is a quaternion in **WXYZ** order. Rules: `mdledit_name`, `mdledit_skel`,
`mdledit_geom`, `mdledit_anim`.
