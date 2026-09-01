# 10 — Adding a new Digimon

Reconstructed from a real work-in-progress mod on this machine
(`C:/Users/spera/Documents/`, author "Mojoceramon AKA HexerVoodoom"), which adds two
Digimon: **Samudramon_FB** (Gaioumon: Itto Mode) and **duramon_sword_form** (Durandamon
Sword Form). That mod is the ground truth for this file; the SDMM PDF documents the
mechanism but not the recipe.

## The correction that matters

**Model file stems are arbitrary.** A new Digimon's model is *not* `chrNNN`. The reference
mod ships `Samudramon_FB.name/.skel/.geom/.anim` and the game finds it because the tables
point at that stem. `[Digimon::Key::filename()]` exists for the cases where the game
*derives* a filename from the ID (effect and camera lookups), not to force your model to be
called `chr700`.

Textures, however, are still ID-named where they replace a vanilla slot
(`images/chr700a01.img`), alongside freely-named custom ones (`images/samudra_a01.img`).

## The table set

Every one of these is a patch CSV under `modfiles/data/` or `modfiles/text/`, with the new
ID written as a softcode. Missing any of them produces a partial Digimon that does not
error.

### `data/`

| Table / sheet | Role in the reference mod |
|---|---|
| `digimon_list.mbe/digimon.csv` | One cell — the ID exists. |
| `digimon_common_para.mbe/digimon.csv` | Stage (`level`), `attribute`, `type`, `fieldGuideId` → a `[DigimonText::…]` softcode. |
| `mon_para.mbe/Monster.csv` | The statline, keyed `(type, variation)` — note the `1` in cell 2. |
| `mon_para_hard.mbe/Monster.csv` | The hard-mode statline. Ship both. |
| `mon_design_para.mbe/Monster.csv` | 9 columns, last one a float (1.2 in both entries). |
| `model_default_scale.mbe/digimon.csv` | `fieldGuideScale, battleScale, fieldScale, Uk4, Uk5`. Samudramon is 9/9/6.2; Durandamon 0.7/0.7/0.7. **This is where a new model comes out giant or microscopic.** |
| `model_attach_para.mbe/digimon01..03.csv` | Three sheets, each a bone attachment: `J_head` plus offset, rotation and scale. |
| `digimon_farm_para.mbe/digimon.csv` | DigiFarm entry, and the skill-learn table (`level, skillId` pairs). |
| `degeneration_para.mbe/digimon.csv` | De-digivolution target (`744` = the donor). |
| `evolution_next_para.mbe/digimon.csv` | **Two rows**: the donor gains the new ID as a target, *and* the new ID gets its own (empty) row. |
| `evolution_condition_para.mbe/digimon.csv` | The `(condType, condValue, condUnk)` gate — Samudramon uses 5 of the 10 slots. |
| `skill_use_group_set.mbe/digimon.csv` | 30 flags controlling which skill groups it may use. |
| `battle_command.mbe/Command.csv` | The custom skill, `[Skill::…]` → `[SkillText::…]`. |
| `battle_command_effect.mbe/effect.csv` | Links the skill to `[SkillEffect::…]`. |
| `battle_effect.mbe/effect.csv` | Points the effect at the model `eff_bts_[Digimon::Key::filename()]_bs01`. |

### `text/`

`charname`, `digimon_book_explanation`, `skill_name`, `skill_content_name` — every language
column filled with the same string in the reference mod.

> **Watch the sheet name.** Vanilla `text/charname.mbe` has a single sheet called
> **`Digimon Names.csv`**, not `Sheet1.csv`. The other three text tables *do* use `Sheet1`.
> A mod that writes `charname.mbe/Sheet1.csv` is very likely a silent no-op — the Digimon
> ends up nameless. Verify with `python tools/cshm.py sheets <table>` before writing.

## The model set

Per Digimon, at the top level of `modfiles/` (no folder):

- Base: `<Stem>.name/.skel/.geom/.anim`
- Battle overlays: `_ba01 _ba02 _bd01 _bd02 _bd03 _bg01 _bn01 _br01 _bs01 _bs02 _bv01`
- Field: `_fa01 _fe01` (the rest fall back to the battle animations)
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

## Order of work

1. Model in Blender (Blender-Tools-for-DSCS, 2.83 or 2.92 on this machine) → export the
   four base files and every overlay animation.
2. Textures → `images/`.
3. `digimon_list` + `digimon_common_para` + `mon_para` + `mon_para_hard` — it exists and has stats.
4. `model_default_scale` — it is the right size. Get this wrong and nothing else is visible.
5. `text/*` — it has a name and a Field Guide entry.
6. Evolution pair (`next` + `condition`) and `degeneration` — it is reachable.
7. Skill chain (`battle_command` → `battle_command_effect` → `battle_effect`) + cameras and
   effect models.
8. `cshm-qa`, then build in SDMM, then test in game.
