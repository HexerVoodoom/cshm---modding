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
— point it at the `.name` file.

## Naming is the API — with one big exception

The game locates vanilla models by filename: `chr009` is Digimon 9 because ID 9 is 9.

**A *new* Digimon does not have to follow that.** Custom models ship under an arbitrary
stem (`Samudramon_FB.name`) and the tables point at it. `[Digimon::Key::filename()]` exists
for the lookups the game derives from the ID — effect and camera models — not to force your
model into a `chrNNN` name. See [10-new-digimon.md](10-new-digimon.md).

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
