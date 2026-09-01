# Upstream contracts — the docs the community actually maintains

Read 2026-09-01 from the two upstream repositories. These supersede anything reconstructed
from Discord chat, and they are the places to check first when something in this guide looks
stale.

- **Squirrel API**: `github.com/SydMontague/DSCSTools/tree/master/docs/squirrel/builtin` —
  one file per namespace, with **typed signatures**.
- **Table columns**: `github.com/SydMontague/DSCSTools/tree/master/structures` (machine
  readable, what SDMM uses) and `.../docs/structures` (human notes per table).
- **Model export**: `github.com/Pherakki/Blender-Tools-for-DSCS/wiki` — the
  `Exporting-Custom-Models`, `Exporting-Custom-Materials` and `Exporting-Custom-Animations`
  pages.

## The Squirrel namespaces

`Battle`, `Colosseum`, `Common`, `Costume`, `DLC`, `Debug`, `Digilab`, `Digiline`, `Digimon`,
`Domination`, `Effect`, `Fade`, `Field`, `Flag`, `Item`, `Keyword`, `Math`, `Medal`, `Movie`,
`PostEffect`, `Quake`, `Quest`, `Shop`, `Sound`, `Talk`, `Util`, `Vista`, `Window`, `Work`,
plus `this` and `test`.

`Costume`, `Digilab`, `Domination`, `Medal`, `Movie`, `PostEffect` and `Quake` were not
visible anywhere in this guide before — if a mod needs one of those systems, the reference
exists.

## Model export — the hard requirements

The wiki gives numbers the Discord only gestured at.

**Scene hierarchy is a contract**, not a convention:

```
Plain Axes empty          <- top-level parent
  └── Armature            <- parented under the empty
        └── Meshes        <- parented under the armature (Ctrl+P > Armature Deform)
```

**Limits that produce the "too many vertex groups" export error:**

| Limit | Value |
|---|---|
| Non-empty vertex groups per mesh | **fewer than 56** |
| Vertex groups influencing one vertex | **4 or fewer** |
| UV maps per mesh | **at most 3**, assigned in outliner order |
| Colour maps exported | **only the first** in outliner order |

Empty groups and zero-weight assignments are ignored automatically, and the exporter can
filter groups below a threshold and renormalise the remaining weights. **Be in Object Mode
before exporting.**

## Material contract — the authoritative version

A material is a **shader file plus its arguments**. This replaces the ad-hoc property list in
[community.md](community.md), which came from one person's helper script.

**`shader_hex` is the shader's *filename*** in the game's `shaders/` folder, e.g.
`088100c1_00880111_00000000_00058000`. Both the fragment (`_fp`) and vertex (`_vp`) files
must be **installed in a `shaders/` folder alongside your exported model** — a shipping step
that is easy to miss.

**Texture nodes must be named exactly**, and only the ones the chosen shader declares:

`ColorSampler`, `NormalSampler`, `EnvSampler`, `OverlayColorSampler`, `OverlayNormalSampler`,
`CLUTSampler`, `EnvsSampler`

> **"Do not add textures that are not referenced by the shader."** This is the documented
> form of the bug Pherakki chased for weeks — Blender attaching data the shader never asked
> for, and the model breaking in game with no error.

**Shader uniforms** are custom properties, each a float vector of size 1–4 matching the
shader header: `DiffuseColor`, `Bumpiness`, `SpecularStrength`, `SpecularPower`,
`ReflectionStrength`, `FresnelExp`, `FresnelMin`, `FuzzySpecColor`, `SubColor`,
`SurfaceColor`, `Rolloff`, `VelvetStrength`, `OverlayBumpiness`, `OverlayStrength`,
`Curvature`, `GlassStrength`, `UpsideDown`, `ParallaxBiasX/Y`, `Time`, `ScrollSpeedSet1-3`,
`OffsetSet1-3`, `DistortionStrength`, `LightMapStrength`, `LightMapPower`, **`Fat`**,
`RotationSet1-2`, `ScaleSet1`, `ZBias`.

`Fat` is the outline thickness — the parameter Pherakki multiplied to prove the game runs
custom shader code.

**Vertex data flags** are mesh custom properties and must match what the shader consumes:
`export_normals`, `export_tangents`, `export_binormals` (1 enables). **Misaligned vertex data
inputs make the model fail to render** — which is the documented cause of the Magnamon X
"explosive model" bug (missing tangents on metallic meshes).

## `this.Battle` — typed signatures

```
Encount(int encounterId, int battleMapId)      SetBGM(string battle, string victory)
GetParameter(int charId, int paramId) -> int   SetParameter(int charId, int paramId, int value)
GetStatus(int charId, int) -> int              GetTurn(int) -> int
GetDifficulty() -> int                         GetTurnCharacter()
SetCommand(int commandId)                      SetCommandTarget(int charId)
SetSkill(int, int)                             SetCombo(int, bool)
SetStatus(int, int, bool)                      SetTurnStartActionCommand(int, int, int)
SetTurnStartActionBuff(int, int, int)          AddAnimation(int charId, int)
PlayAnimation(int charId, string anim, bool)   SetAnimationFix(int charId, bool)
SetFirstAttack()                               SetBackAttack()
SetPlayerInvisible(int, bool)                  SetPlayerPosition(float, float, float)
SetPlayerModelID / GetPlayerModelID(int)       SetDispUI(bool)
SetItemDisable(bool)                           SetReserveDisable(bool)
SetRefuseScan(bool)                            SetBackgroundMovie(string movieName)
LoadObject(string, string, float, float, float, float, int)
ChangeGuest(int, int, int)                     IsChangeGuest()
EventParty(int, int, int)                      ForceEnd()
AttachNoDamage(int, bool)                      AttachUndead(int, bool)
AttachAlwaysHit(int, bool)                     AttachAlwaysAvoid(int, bool)
AttachFixDamage(int, int, int)                 AttachReducePenetrate(int, int)
```

The `Attach*` family is how a scripted boss fight gets special rules — invulnerability
phases, guaranteed hits, fixed damage — without touching any table. None of that was known
to this guide before.

## `this.Window` — beyond the multi-select

The choice menu is not the only dialog. `OpenYesNoInfo()` / `IsNextYesNoInfo()` /
`GetResultYesNoInfo()` / `CloseYesNoInfo()` is a far cheaper two-option prompt that needs no
`multi_select_para` row at all. There are also `OpenInfo`, `OpenInfoGetItem`,
`OpenInfoReleaseItem`, `OpenMoneyWindow` and `OpenTutorial`, each with the same
`Open` → `IsNext…` → `Get…` → `Close…` → `IsEndClose…` polling shape.

**`SetReplaceString` and `SetReplaceNumber`** (both an Info and a YesNo variant) substitute
values into a message's variable slots. That is the supported way to fill the `[d0]`-style
placeholders — and the reason an unfilled slot hard-crashes the game.

## `this.Field`

120+ methods covering map changes and transitions, NPC loading and animation
(`LoadNpc`, `MoveNpcPosition`, `SetNpcAnime`), background movies, BGM and SE, player movement
and visibility, map icons and markers, the save UI, hacking and stealth mechanics, warping
and chapter progression. Several are annotated **"Does nothing"** upstream — check the file
before building on one.

## How to use this file

When you need an exact signature, **fetch the namespace file** rather than guessing. When a
column name here disagrees with your CSV header, your extraction is stale: update
`structures/` and re-extract.
