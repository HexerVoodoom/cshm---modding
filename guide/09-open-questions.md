# 09 — Open questions

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
- **`model_default_scale` columns `Uk4`/`Uk5`** — the reference mod uses `511`/`0.8` for one
  Digimon and `1`/`1` for the other. Meaning unknown.
- **`mon_design_para`'s 9 columns** are all `unk`; the last is a float (1.2 in both known
  custom entries).
- **Which Blender-Tools-for-DSCS build is authoritative** — 2.92 has both `Blender-Tools-for-DSCS`
  and `-develop` installed.
