# Porting and editing models — what `#dscs-3d-modelling` established

Scraped 2026-09-01 from the read-only archive channel (`909543791256547328`), 1446 messages
covering **2021-11-17 → 2022-07-04**. That is the channel's productive period, not its full
span — it stayed open until the March 2023 archiving. It has **no pinned messages**, so this
file is the only distillation that exists.

The canonical written docs are the Blender-Tools wiki, which Pherakki points everyone at:

- <https://github.com/Pherakki/Blender-Tools-for-DSCS/wiki/Exporting-Custom-Models>
- <https://github.com/Pherakki/Blender-Tools-for-DSCS/wiki/Exporting-Custom-Materials>
- <https://github.com/Pherakki/Blender-Tools-for-DSCS/wiki/Exporting-Custom-Animations>

## `name_hash` is a mesh slot, not a label

The single most important discovery in the channel (Zeak6464 and Pherakki, 1 Jul 2022).

Every mesh carries a `name_hash`. **When a mesh loads, every already-loaded mesh with the
same hash is removed.** That is the engine's costume system: an alternative t-shirt model has
a different mesh count from the base model and still works, because the hashes decide which
base meshes get replaced.

Hashes identified in that session:

| Hash | Slot |
|---|---|
| `99636f43` | PC001 |
| `1aad80b8` | shared across all models |
| `8d315e06` | PC020 |
| `1b015971` | PC021 — school clothing |
| `0d5b7106` | NPC001 |

Consequences: in-game costume customisation needs far less hacking than assumed, and any
costume tooling has to set the right hash. It also means **copying a hash between meshes is
how you claim or free a slot** — and copying one by accident deletes geometry you wanted.
Zeak confirmed it by deleting a head mesh and watching the base model's head disappear too.

This is the same `name_hash` custom property in Zeak6464's exporter script in
[community.md](community.md) — do not copy that script's value blindly.

## Blender version — this is a hard constraint

**Blender-Tools-for-DSCS works with Blender 2.80–2.91 inclusive. It does not work above
3.0.** This machine has the addon on **2.83** (good) and **2.92** (outside the stated
range) — see [workspace-inventory.md](workspace-inventory.md).

## Importing

- Import points at the **`.name`** file. Tick the animation checkbox — importing an animation
  without its skeleton destroys data in this format, so there is deliberately no separate
  animation importer.
- **Use "QA" mode to import animations. The "Animation" option is bugged.** (Pherakki.)
- Import from the extraction folder itself; the tools need the textures beside the model and
  will usually crash outright when a texture is missing. In Blender's file dialog, turn the
  filter off to see `.img` files.
- "Emulate DSCS Materials" is the import option that wires the material nodes up.
- If the imported model looks solid-coloured or invisible, it is probably the **outline
  mesh** in front of it — hide the final mesh, or turn backface culling on.
- Animations land in the **NLA editor**. If it is empty, check
  Window → Toggle System Console for the error.

## Exporting — the errors and what they mean

| Error / symptom | Cause |
|---|---|
| Exporter errors immediately | You did not **select the collection** inside the project file. Reason #1, per IlDucci. |
| "mesh with zero vertices" | A mesh has no geometry, or a new mesh is not rigged to any vertex group. |
| "too many vertex groups" | Zero-weight groups. Weight Paint mode → Weights → Clear, set to all deform groups so only bone-assigned vertices are cleared. |
| "texture isn't set" | A material's texture sampler node has no image. Dig the three sampler nodes out from under the node stack on the mesh's material. |
| **Explosive model syndrome** | A mesh whose **shader has not been configured**. Follow the Exporting-Custom-Materials wiki page. |
| Model explodes only on metallic meshes | **Tangent vectors were not exported.** This was the Magnamon X bug. |
| Model breaks in game for no visible reason | Blender silently attached a **colour map to a mesh that should not have one**. Several suspected tool bugs turned out to be these spurious vertex attributes. |

All meshes must be **parented under the same armature**.

## Skeletons — the rule that decides whether a port works

**The game addresses bones by index, not by name.** A donor skeleton whose bones are in a
different order produces a model that deforms wrongly, and nothing warns you. Pherakki:
"you've got to be lucky with the skeleton for it to work."

If the skeleton asks for animation data that does not exist, the game appears to fall back to
the **bind pose from the skel file** — that is what happened when Pherakki cleared the
"this bone has data" flags.

**Shapekeys are not supported.** Facial animation has to be a facial rig.

Known unresolved bug (as of Jul 2022): animations for **"attachment" meshes — weapons,
sabres, accessories** — misbehave in Blender-Tools while working in Pherakki's separate
C++ model editor. Beelzemon and chr680 were the reproducers.

## Budgets and rendering

- Vanilla CS meshes sit **under about 10k vertices each**. Debiddo's working target for a
  custom character is **~15k vertices including the outline mesh**.
- The game does **geometry batching**: a mismatch between the true and expected vertex buffer
  size spills into misreads of *other* meshes and even other models. A wrong count does not
  fail locally; it corrupts a neighbour.
- **Outlines are inverted-normal geometry**, not post-processing, with a "Fat" parameter in
  the shader.
- The game **can execute custom shader code** (Pherakki confirmed by putting a multiplier on
  the outline's Fat parameter and shifting vertices). Compute shaders need EXE hacking.
- CS textures are **diffuse, not PBR albedo** — it is an NPR renderer.

## Where to get models to port

| Source | Notes |
|---|---|
| **Digimon ReArise** — <https://chortos.selfip.net/~astiob/digimon-rearise-digimon/model/> | Best fit. SydMontague: converts "rather painlessly" — the same structure in animations and names, and the **same internal chr numbering as CS**. |
| **Digimon New Century** — <https://www.models-resource.com/mobile/digimonnewcentury/> | Works, but needs heavy texture work (below). |
| Other Media.Vision games | `.name/.skel/.geom/.anim` is an engine format, so a direct model swap is plausible. Outside Media.Vision, do not expect it. |

Models from those games usually arrive already animated with run, win, special attack, damage,
knockdown and idle — you still have to do VFX, cameras, stats, evolutions and requirements.

Cross-reference every chr number against the [chr ID map](community.md#the-chr-id-map--use-this-before-porting-anything)
before claiming a slot, and keep the community's numbering.

### Making a New Century model look like Cyber Sleuth

New Century over-uses hard black outlines so models read on a phone screen. Ported straight
in, they look wrong. Explodion and Debiddo's fixes:

1. Remove the hard black bordering from the texture by hand.
2. Normalise the texture toward ~0.5 — an NPR diffuse that is too bright or too dark breaks
   the shading.
3. Add some noise.
4. Easiest path to a matching style: **copy texture regions from a vanilla Digimon with
   similar traits** rather than painting from scratch.

New Century also **overlaps UV islands** (both halves of a body stacked on one rectangle),
which is fine for reskinning but makes shading impossible to control — darkening the underside
of the body also darkens a stripe across the head.

## Base models for costumes

Pherakki's spec for a costume system, if anyone builds it: one SFW base model per customisable
character, on the **original skeleton**, at vanilla-ish poly density, with good topology and
edge flow because modellers will cut it up. The face texture atlas should be shared. Costume
parts then get modelled over the base and the unused base geometry deleted — and each part has
to carry the correct **`name_hash`** so the right base meshes are replaced.
