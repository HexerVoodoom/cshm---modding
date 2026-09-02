# Softcodes — the authoritative reference

Source: **SDMM's own `Documentation/modders_guide.pdf`, section 4.1.3**, cross-checked
against the 38 category files in `SimpleDSCSModManager/softcodes/` and against a
real build. Prefer this file over inference: this repo previously guessed at `filename()`
and shipped a bug because of it.

## The form

`[Category::Key]`, `[Category::Key|SubCategory::Key2]`, `[Category::Key::method()]`

A softcode asks SDMM to allocate an ID for a name you invent, so two mods that both add a
Digimon do not collide. **Methods** transform that allocated ID into the shape a particular
field wants.

## Where they are substituted

Anywhere the file type opts in (`enable_softcodes = True`). Confirmed for `.mbe` CSV cells,
`BUILD.json`, `.mdledit`, `.sqmod`, uncompiled scripts and `.request` files — so the same
softcode works in a table cell and in a filename.

**But `BUILD.json` renames files, not cell contents.** If your model ships as `mymon.geom`
and is renamed on the way in, every *cell* that names the model must carry the softcode
too. See the `renamed-stem` gate in `tools/validate_mod.py`.

## Methods that matter

| Category | Method | Transform | Example |
|---|---|---|---|
| `Digimon` | *(none)* | the ID as-is | `7` |
| `Digimon` | `3ID` | zero-pad to 3 | `7` -> `007` |
| `Digimon` | `4ID` | zero-pad to 3, prefix `1` | `7` -> `1007` |
| `Digimon` | `filename` | zero-pad to 3, prefix `chr` | `7` -> `chr007` |
| `…SubArea::NPC` | `bone_name` | zero-pad to 4, prefix `npc_` | `1` -> `npc_0001` |
| `…SubArea` | `battleFile` / `collisionFile` / `positionFile` / `surfaceFile` / `fieldFile` | the SubArea value with `b` / `c` / `p` / `s` / `f` appended | `d0101` -> `d0101p` |
| `…SubArea` | `cameraFile` / `hideablesFile` | `_cam` / `_hide` appended | `d0101` -> `d0101_cam` |
| `Dungeon_*` / `Town_*` | `ID` | zero-pad to 2 | `1` -> `01` |
| `…SubArea` | `MapID` | zero-pad to 2, prefix the parent ID | `1` -> `101` |

`Town_*` is identical to `Dungeon_*` with the `d` padding character replaced by `t`.
`Item`, `Skill`, `Speakers`, `Shop*`, `Field_*` and `BattleBGM` return the ID unmodified
and have **no methods** — `[Item::PowerfulMojo]` is the whole vocabulary there.

The `4ID` shape is why a Digimon at softcode `7` takes `charname` row **1007**.

## Aliases

`ALIASES.json` shortens a prefix, and SDMM pads the right-hand side up to two `:`
characters so the result is still a valid softcode:

```json
{ "ShibuyaNPCs::": "Dungeon_CS::d90|SubArea::d9002|NPC::" }
```

Aliases are **private to your mod**. You cannot read another mod's, and it cannot read yours.

## Documented vs shipped

The guide documents **25** categories; the install ships **38**. The
22 that are shipped but undocumented are effect, audio and text banks, and behave like
the plain no-method categories:

`BattleEscapeVFX_CS`, `BattleEscapeVFX_HM`, `BattleInitVFX_CS`, `BattleInitVFX_HM`, `BattleItemUseVFX_CS`, `BattleItemUseVFX_HM`, `BattleKOVFX_CS`, `BattleKOVFX_HM`, `BattleLoseVFX_CS`, `BattleLoseVFX_HM`, `BattleWinVFX_CS`, `BattleWinVFX_HM`, `BattleXROSAttackVFX_CS`, `BattleXROSAttackVFX_HM`, `DigimonText`, `SkillEffect`, `SkillSFX`, `SkillText`, `SkillVFX`, `SkillVFX_CS`, `SkillVFX_HM`, `SupportSkillText`
