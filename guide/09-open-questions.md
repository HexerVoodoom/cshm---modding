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
