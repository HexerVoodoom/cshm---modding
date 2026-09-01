# 02 — Extracting

## The short version

On this machine the extraction is **already done** — `<game>/DSDB/` holds the unpacked
database. Query it with `tools/cshm.py`; do not re-extract unless it is stale.

## Doing it again

**With SDMM (recommended):** Extract tab → pick an archive in the left column → extract.
SDMM unpacks the MDB1 *and* converts each `.mbe` into a **folder of CSV files** and each
`script64` entry into decompiled Squirrel text. That conversion is what makes the data
readable, and it is why every path in this guide looks like
`data/digimon_common_para.mbe/digimon.csv` — `.mbe` is a **directory** in the extraction.

**With MVGLTools (CLI):**

```bash
mvgltools --game dscs unpack DSDB.steam.mvgl out/
```

Asset encryption for DSCS is handled transparently. MBE↔CSV needs the `structures/` folder
in the working directory.

## What comes out

| Path | Contents |
|---|---|
| `data/` | 214 `.mbe` table folders (the database) + loose CSVs. |
| `text/` | 61 `.mbe` folders: names, descriptions, one column per language. |
| `message/` | 1451 `.mbe` folders: conversation text, one per scene. |
| `script64/` | Squirrel 2.2.4, decompiled to `.txt` by SDMM. |
| `images/` | DDS files with an `.img` extension. `images_as/_de/_kr` are language variants. |
| `shaders/` | Plaintext Cg. |
| top level | Model files (`.name .skel .geom .anim` + optional `.phys .detr .note .sprk .navi`). |

## Encodings — this bites

- CSVs **inside** a `.mbe` folder are **UTF-8**.
- The **loose** CSVs directly in `data/` are **SHIFT-JIS**: `bgm.csv`, `se.csv`,
  `voice.csv`, `voice_us.csv`, `soundtest_bgm.csv`, `soundtest_se.csv`,
  `soundtest_voice.csv`, `debug_call_script.csv`, `debug_call_script_hm.csv`.

Reading a loose CSV as UTF-8 will either throw or silently mangle Japanese text.

## Naming conventions are load-bearing

The game finds assets **by filename**. `chr009.name` is Digimon ID 9's model because of its
name, not because a table points at it. You do not get to rename things. See
[07-models-and-textures.md](07-models-and-textures.md).
