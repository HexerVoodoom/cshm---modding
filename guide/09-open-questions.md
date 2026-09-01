# 09 — Open questions

> **2026-09-01: several entries below were answered** by the archived Discord channels. See
> [../reference/discord-research.md](../reference/discord-research.md) and
> [../reference/model-porting.md](../reference/model-porting.md). What remains open is marked
> in the "still open" section at the bottom.

Everything here is unproven. Do not build on it without checking first, and update this
file when something moves from claim to fact.

## Format and data

- **DDS formats per texture role.** Which DXT/BC format, mip count and flags each `.img`
  role expects in DSCS. The Time Stranger table does not apply. Blocks any confident
  texture work. Next step: dump headers across a sample of vanilla `.img` files.
- **`.detr`, `.note`, `.sprk`, `.navi`.** Described upstream as "seems to" — walk paths,
  text rendering, particles, autoran paths. None confirmed.
- **`unk*` columns.** `digimon_common_para` alone has 21. No decoding attempted yet. The
  method that worked for Time Stranger — correlate a column against known in-game values
  across all rows — should transfer.
- **`hackers_memory_para`** has seven columns, all `unk`. Values look like scene IDs
  (`s602_e00_0101`) paired with chapter-ish numbers.
- **"`_add` = Hacker's Memory"** is inferred from sampling `quest_text` vs `quest_text_add`,
  not proven across all `_add` tables.
- **Does `../dsts-modding/tools/mbe.py` read DSCS `.mbe`?** Untested, and assumed **no**.
  Not urgent while SDMM ships CSVs.

## Pipeline

- **The missing executable.** The game root on this install has no `.exe`. Either the
  install is incomplete or it lives somewhere unexpected. Must be settled before anything
  can be tested in game.
- **Save location and backup procedure** for the Steam release — not yet confirmed on this
  machine.
- **CYMIS** installer scripts: unsummarised, untested.
- **New AFS2 archives** for custom BGM: the mechanism is documented upstream (register the
  archive name in `bgm.csv`), never exercised here.
- **The 12 third-party `.mvgl` mods** already in `resources/`: what each one changes is
  unknown. They can invalidate any "vanilla" observation made on this machine.

## Added 2026-09-01, from surveying the existing work

- **Does SDMM match a text sheet by name?** Vanilla `text/charname.mbe` has one sheet,
  `Digimon Names.csv`; the WIP mod on this machine writes `Sheet1.csv`. If SDMM matches by
  filename this is a silent no-op. Testable: build and check whether the new Digimon has a
  name in game.
- **The installed SDMM's softcode set is wider than the v0.1 PDF.** `DigimonText`,
  `SkillText` and `SkillEffect` are in real use. The full current list has not been read out
  of the installed binary's config.
- ~~`model_default_scale` columns `Uk4`/`Uk5`~~ — **answered**: a mod built from a newer
  `structures/` names them `talkScale` and `FollowDistanceScale`.
- **`mon_design_para`'s 9 columns** are all `unk`; the last is a float (1.2 in both known
  custom entries).
- **Which Blender-Tools-for-DSCS build is authoritative** — 2.92 has both `Blender-Tools-for-DSCS`
  and `-develop` installed.


## Still open after the Discord sweep (2026-09-01)

- **`this.Battle.SetParameter` indexing is disputed.** Loud Kuyuki: party = 1,2,3, enemies
  6+, max HP/SP at 0/1. GrowaSowa: party = 0,1,2, with 2 = max HP and 3 = max SP. Test.
- **Attachment/weapon animations** (weapons, sabres, accessories) misbehave through
  Blender-Tools while working in Pherakki's C++ model editor. Unresolved as of Jul 2022;
  reproducers were Beelzemon and chr680.
- **No script hook for the battle action menu opening.** Uncle Jon never found one.
- **What `shader_hex` selects**, and what the two integers in each sampler triple mean.
- **`#dscs-3d-modelling` from Jul 2022 to Mar 2023** was not scraped, nor `#dscs-tools`,
  `#dscs-beta_tests`, `#dscs-mod_*`, nor the live `#modding` / `#projects` scrollback.
- **The `join () takes exactly one argument (2 given)` build error** — still open upstream.


## Raised by the squad-alpha audit (2026-09-01)

- **Does SDMM match an MBE sheet by filename?** 124 corpus mods write
  `text/charname.mbe/Sheet1.csv` instead of `Digimon Names.csv` and appear to work, which
  suggests the name is ignored for a **single-sheet** table. Unproven, and it says nothing
  about multi-sheet tables. Testable: build one mod each way and look at the name in game.
- **`text/skill_name.mbe` has two sheets** — `Sheet1.csv` and `skill name.csv`, both 935 rows.
  Which one the game reads is unknown. Patch both until someone checks.
- **`digimon_common_para` `unk6, 8, 10, 12, 14`** are described upstream as per-language name
  sort values, but they are stored on the Digimon instance, which does not fit. Unresolved.
- **`model_attach_para/npc.csv` has a 5-cell composite key** (per SDMM's
  `config/mberecord_idsizes.json`). What the five cells are has not been decoded.
- **Blender 2.92** has the DSCS addon installed on this machine but sits outside the addon's
  stated 2.80–2.91 range. Whether it actually works is untested; the guide now says use 2.83.
