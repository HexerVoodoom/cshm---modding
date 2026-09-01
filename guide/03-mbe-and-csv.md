# 03 — `.mbe` tables and the CSV patch model

## What a `.mbe` is

A container of one or more **sheets**, each a table of fixed-schema records. Unpacked, it
becomes a **folder** named `something.mbe` containing one `.csv` per sheet.

Unlike Time Stranger, DSCS sheets come out **with a real header row of column names**
(DSCSTools carries a `structures/` definition per table). Names like `unk7` mean the field
type is known but its meaning is not — those are honest gaps, not placeholders you may
reorder.

```
data/digimon_common_para.mbe/
    digimon.csv          id,level,attribute,type,unk1,...,fieldGuideId,unk19,unk20,unk21
    no_generations.csv   id
```

Most tables have one sheet; the sheet is often called `Sheet1` or the entity name.
`reference/mbe-catalog.csv` lists all 3025 sheets with their row counts and column names.

## The patch model — the thing to get right

A mod does **not** ship a whole table. It ships a CSV containing **only the rows it
changes**, at the same path, and SDMM merges it into the vanilla data.

- The **first line of your mod CSV is ignored** — put the vanilla header there for your own
  sanity.
- The **first cell is the ID** (rarely two or more cells).
- Same ID as a vanilla row → edits that row. New ID → adds a record.
- **An empty cell is transparent**: it keeps the vanilla value. This is how you change one
  number without knowing the other 24.

So a mod that changes only Agumon's level is a two-line CSV with one number in it.

## The rules

The default rule is `mberecord_merge`. You only need to name another rule in a build script
(see [05-sdmm-mods.md](05-sdmm-mods.md#build-scripts)).

| Rule | Effect |
|---|---|
| `mberecord_merge` | **Default.** Replace/add the record; blank cells stay vanilla. |
| `mberecord_overwrite` | Replace/add the whole record; blank cells overwrite too. |
| `mberecord_append` | Strip padding, append your entries, re-pad. Padding char defaults to `0`. |
| `mberecord_remove` | Strip padding, remove your entries, re-pad. |
| `mbetable_overwrite` | Replace the entire CSV. Use this, **not** the generic `overwrite`, for a CSV. |

`mberecord_append` / `_remove` are for the list-shaped records — a row that is really a
fixed-width array of IDs padded with zeros (evolution lists, shop line-ups). Do not
hand-edit those with `merge` unless you have counted the padding.

## Where a file goes decides how it is read

- `modfiles/data/charname.mbe/Digimon Names.csv` → recognised as an **MBE table**.
- `modfiles/data/charname/Digimon Names.csv` → recognised as a plain **CSV**.

The `.mbe` in the folder name is the switch, and getting it wrong is a silent failure. It is
not that the merge rule changes — a loose CSV still defaults to `mberecord_merge`. It is that
the **target path no longer exists**: SDMM merges your file into `data/charname/Sheet1.csv`,
a path the game never reads. The file installs, the build succeeds, nothing changes.

## Rules for editing

1. Never open these in Excel.
2. Never insert or remove a column.
3. Include only rows you changed.
4. Re-read your CSV after writing it and confirm the ID column is what you think it is.
