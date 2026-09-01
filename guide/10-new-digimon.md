# 10 — Adding a new Digimon

Reconstructed from a real work-in-progress mod on this machine
(`C:/Users/spera/Documents/`, author "Mojoceramon AKA HexerVoodoom"), which adds two
Digimon: **Samudramon_FB** (Gaioumon: Itto Mode) and **duramon_sword_form** (Durandamon
Sword Form). That mod is the ground truth for this file; the SDMM PDF documents the
mechanism but not the recipe.

## First: the mod does not work without a `BUILD.json`

The game finds models **by filename** and a custom Digimon's files must end up as
`chr<id>.*`. You cannot write that name yourself — the ID does not exist until SDMM assigns
it. So you author under a readable stem and **`BUILD.json` renames everything at build
time**. The reference mod's whole rename is three rules:

```json
{
  "images/ui_chara_icon_[Digimon::Samudramon_FB::4ID()].img": "images/ui_chara_icon_Samudramon_FB.img",
  "images/dot[Digimon::Samudramon_FB::3ID()].img":            "images/dot_Samudramon_FB.img",
  "{0}[Digimon::Samudramon_FB::filename()]{1}": {
      "BuildSteps": "{0}Samudramon_FB{1}",
      "Variables": [{ "Regex": "(.*)Samudramon_FB(.*)" }] }
}
```

The pattern rule catches the base model, every overlay animation, every attack camera and
every effect model in one line. The two icon rules exist because those paths do **not**
contain the stem — the party icon is keyed by 4ID and the Field Guide dot by 3ID.

Add the compatibility line for evolutions in the same file:

```json
"data/evolution_next_para.mbe/digimon.csv": ["data/evolution_next_para.mbe/digimon.csv", "mberecord_append"]
```

After a build, SDMM writes an `INDEX.json` showing exactly which softcodes resolved where.
That is the fastest way to debug a rename that did not happen.

Textures that replace a vanilla slot are still ID-named (`images/chr700a01.img`); freely
named custom ones (`images/samudra_a01.img`) are fine because the model references them by
name.

## The table set

Every one of these is a patch CSV under `modfiles/data/` or `modfiles/text/`, with the new
ID written as a softcode. Missing any of them produces a partial Digimon that does not
error.

### `data/`

| Table / sheet | Role in the reference mod |
|---|---|
| `digimon_list.mbe/digimon.csv` | One cell — the ID exists. |
| `digimon_common_para.mbe/digimon.csv` | Stage (`level`), `attribute`, `type`, `fieldGuideId` → a `[DigimonText::…]` softcode. |
| `mon_para.mbe/Monster.csv` | The statline, **keyed on the first 2 cells** `(type, variation)` — note the `1` in cell 2. `mon_design_para/Monster` is composite too. |
| `mon_para_hard.mbe/Monster.csv` | The hard-mode statline. Ship both. |
| `mon_design_para.mbe/Monster.csv` | 9 columns, last one a float (1.2 in both entries). |
| `model_default_scale.mbe/digimon.csv` | Six columns: **`digimonID`**, `fieldGuideScale`, `battleScale`, `fieldScale`, `Uk4`, `Uk5`. Samudramon is 9/9/6.2; Durandamon 0.7/0.7/0.7. **This is where a new model comes out giant or microscopic** — and where omitting the ID column shifts every value one cell left. |
| `model_attach_para.mbe/digimon01..03.csv` | Three sheets, each a bone attachment: `J_head` plus offset, rotation and scale. **Keyed on the first 2 cells** — a merge matching cell 1 alone hits the wrong row. |
| `digimon_farm_para.mbe/digimon.csv` | 34 columns: `memoryUse`, `growthType`, `baseHP/SP/ATK/DEF/INT/SPD`, `maxLevel`, `equipSlots`, `supportSkill`, then the learnset as **`(skill, level)`** pairs — `sMove1, sMove1Level, sMove2, sMove2Level` for the Special Skills and `move1, move1Level` … `move6, move6Level` for the rest. **Skill first, level second.** Reversed, the Digimon learns skill 1 at level 101 and never learns anything, with no error. |
| `degeneration_para.mbe/digimon.csv` | De-digivolution target (`744` = the donor). |
| `evolution_next_para.mbe/digimon.csv` | **Two rows**: the donor gains the new ID as a target, *and* the new ID gets its own (empty) row. |
| `evolution_condition_para.mbe/digimon.csv` | The `(condType, condValue, condUnk)` gate — Samudramon uses 5 of the 10 slots. |
| `skill_use_group_set.mbe/digimon.csv` | 31 columns: `digimonID`, **20 flags** (`Unk1`–`Unk20`) and 10 padding cells. |
| `battle_command.mbe/Command.csv` | The custom skill, `[Skill::…]` → `[SkillText::…]`. |
| `battle_command_effect.mbe/effect.csv` | Links the skill to `[SkillEffect::…]`. |
| `battle_effect.mbe/effect.csv` | Points the effect at the model `eff_bts_[Digimon::Key::filename()]_bs01`. |

### Tables the reference mod did NOT ship, but the 253-mod corpus does

Frequency across every mod on this machine (`tools/scan_mods.py`, see
[../reference/mod-corpus.csv](../reference/mod-corpus.csv)) shows the community's real
new-Digimon set is wider:

| Table | Mods using it | What it is for |
|---|---|---|
| `ui_mon_param_info` | 87 | The Field Guide / party stat panel entry. |
| `same_animation_data` | 83 | Declares which model an animation set is borrowed from. |
| `battle_support_skill` | 79 | The support skill. Paired with `text/support_skill_name` (61) and `text/support_skill_content_name` (61). |
| `battle_voice` + `battle_voice_add` | 42 each | Battle voice lines — `_add` is the Hacker's Memory half. |
| `battle_se` | 25 | Battle sound effects. |
| `model_position_offset` | 21 | Positional offset of the model. |
| `model_default_effect` | 18 | Default attached effect. |
| `mon_cpl` | 6 | Rare; unstudied. |

`model_attach_para` is the single most-patched table in the whole corpus (312 sheets), which
matches three sheets per Digimon.

### `text/`

`charname`, `digimon_book_explanation`, `skill_name`, `skill_content_name` — every language
column filled with the same string in the reference mod.

> **Watch the sheet name.** Vanilla `text/charname.mbe` has a single sheet, `Digimon
> Names.csv`. 124 mods in the corpus write `Sheet1.csv` there and appear to work, so SDMM
> probably tolerates a wrong name when the table has only one sheet — `UNVERIFIED`, and
> matching costs nothing.
>
> Where it genuinely bites is a table with **several** sheets, because then the merge cannot
> guess. `text/skill_name.mbe` has **two** — `Sheet1.csv` and `skill name.csv`, both 935 rows.
> Which one the game reads is unknown: patch both.
>
> Check first: `python "D:/digimon modding claude/cshm-modding/tools/cshm.py" sheets <table>`.

## The model set

Per Digimon, at the top level of `modfiles/` (no folder):

- Base: `<Stem>.name/.skel/.geom/.anim`
- Battle overlays: `_ba01 _ba02 _bd01 _bd02 _bd03 _bg01 _bn01 _br01 _bs01 _bv01` — that is
  what a vanilla `chr` actually ships. Add `_bs02` only for a **second** Special Skill.
- Field: `_fe01`. `_fa01` is not vanilla-standard; the rest fall back to the battle animations.
- Attack cameras: `cam_<Stem>_bs01_pc` / `_bs01_em` / `_bs02_pc` / `_bs02_em` / `_bv01`,
  each a full four-file model. `_pc` and `_em` are the player-side and enemy-side cameras.
- Attack effects: `eff_bts_<Stem>_bs01` / `_bs02`, each a full four-file model.

## The image set

`modfiles/images/`: the character textures (`<stem>_a01.img`, `_a01s`, `_a01env`, …),
the field-guide dot icon (`dot_<Stem>.img`), the party icon
(`ui_chara_icon_<Stem>.img`), plus every effect texture the attack uses
(`eff_fir_*`, `eff_lig_*`, `eff_par_*`, …) — those are vanilla and should be `.request`
files rather than redistributed copies.

## Softcode categories in real use

Beyond the v0.1 PDF list, the reference mod uses `DigimonText`, `SkillText` and
`SkillEffect`, and calls `::4ID()` and `::filename()`. So the installed SDMM's softcode set
is **wider than the v0.1 documentation**. Read the mod, not just the PDF.

## Giving it its own skill, effect and voice

A skill is four things: a data row, an effect model, its textures, and optionally a voice.

```
data/battle_command/Command.csv         the skill: Power, DamageType, TargetType,
                                        NumAttacksMin/Max, SP Cost, SpeedUse, Accuracy,
                                        critChance, HPabsorb, StatusType/Effect/Chance, ...
data/battle_command_effect/effect.csv   skillID -> casterSkillEffectIDs, targetSkillEffectIDs
data/battle_effect/effect.csv           effectID -> skillEffModel, skillSFX (-> battle_se)
text/skill_name, text/skill_content_name
```

The **effect model** is a normal four-file model named `eff_bts_<stem>_bs01`. The cheapest
way to an original-looking attack is to clone a vanilla one and repaint the textures it
references — that is exactly how the *Chaos* mods make greyscale versions of WarGreymon's
and MetalSeadramon's attacks. Copy every `eff_*.img` the model names, recolour, ship them
under a distinguishing prefix, and point the cloned model at the new names.

Passive skills are `battle_support_skill/support_skill.csv`, a fully named 59-column table
covering every stat, element, status chance and resistance, plus `EXP Boost`, `Drop Rate`,
`Scan Rate`, `moveFirst` and `HP to ATK`.

For a **voice line**, build an AFS2 with `DSCSToolsCLI --afs2pack`, ship it at the mod root
under `"FormatVersion": 2`, register it in `data/voice.csv`, and add the same row to **both**
`battle_voice` and `battle_voice_add`. Step-by-step in
[../reference/mod-patterns.md](../reference/mod-patterns.md#3-a-recoloured-skill-with-its-own-voice--chaos-generals).

## Order of work

1. Model in **Blender 2.83** — the addon supports 2.80–2.91 and 2.83 is the only install on
   this machine inside that range (2.92 has the addon but is out of range) → export the
   four base files and every overlay animation.
2. Textures → `images/`.
3. `digimon_list` + `digimon_common_para` + `mon_para` + `mon_para_hard` — it exists and has stats.
4. `model_default_scale` — it is the right size. Get this wrong and nothing else is visible.
5. `text/*` — it has a name and a Field Guide entry.
6. Evolution pair (`next` + `condition`) and `degeneration` — it is reachable.
7. Skill chain (`battle_command` → `battle_command_effect` → `battle_effect`) + cameras and
   effect models.
8. `cshm-qa`, then build in SDMM, then test in game.
