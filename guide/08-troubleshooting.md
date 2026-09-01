# 08 — Troubleshooting

Ordered by how often the cause is the real one. The dangerous entries are the ones where
**nothing errors**.

## The mod installs and nothing changes

| Cause | Check |
|---|---|
| Folder named `charname` instead of `charname.mbe` — read as a loose CSV, not a table sheet. | `ls modfiles/data` |
| Sheet filename does not match the vanilla sheet. `text/charname.mbe`'s sheet is
**`Digimon Names.csv`**, not `Sheet1.csv` — a very common miss. | `python tools/cshm.py sheets <table>` |
| Wrong ID form: bare vs 4ID vs `chrNNN`. | [04-data-tables.md](04-data-tables.md#the-id-systems--the-most-common-silent-failure) |
| Composite key (e.g. `mon_para` is `(type, variation)`) — you patched the wrong row. | `python tools/cshm.py head mon_para` |
| A third-party `.mvgl` in `resources/` overrides you via DSCSModLoader. | [../reference/archives.md](../reference/archives.md) |
| You edited `DSDB/` (the read-only extraction) instead of your mod folder. | — |

## Half the game's content vanished

You shipped a whole table instead of a patch, or an unrecognised file got the blanket
`overwrite` rule. A mod CSV must contain only the rows it changes. See
[03-mbe-and-csv.md](03-mbe-and-csv.md#the-patch-model--the-thing-to-get-right).

## Text is blank in game

Under `mberecord_overwrite`, an empty language cell **writes an empty string**. Under
`mberecord_merge` it is transparent. If you only meant to change English, use `merge` and
leave the other five columns empty.

## Japanese text is mojibake

You read or wrote a **loose** `data/*.csv` (`bgm.csv`, `voice.csv`, `se.csv`,
`debug_call_script*.csv`, `soundtest_*.csv`) as UTF-8. Those are SHIFT-JIS. Sheets inside a
`.mbe` folder are UTF-8.

## A row got corrupted and the columns shifted

Something opened the CSV in Excel, or you inserted/removed a column. Column count is fixed;
`reference/mbe-catalog.csv` records the expected count per sheet.

## Evolution does not appear

You edited `evolution_next_para` but not `evolution_condition_para` (or the reverse). Both
are required.

## A shop line-up or evolution list ignored the addition

Those are fixed-width padded arrays. Use `mberecord_append` / `mberecord_remove` with the
correct padding character (default `0`; pass `-1` as a rule argument where the table pads
with `-1`), not `merge`.

## Two mods conflict over a new ID

Neither used softcodes. Convert both to `[Category::Key]`. See
[05-sdmm-mods.md](05-sdmm-mods.md#softcodes--mandatory-for-anything-new).

## A script change affected more than intended

`replace` has no syntactic awareness. Scope it with `replace_call_in_funcs`, or match the
call form instead of raw text.

## A model plays the wrong animation

Missing overlay animation — the game falls back (no `fr01` → uses `br01`). Add the file,
don't chase the table.

## The build takes forever

You targeted `DSDB` (2.7 GB). Target `DSDBP`.

## The game will not launch at all

1. Disable all mods in SDMM and build — does vanilla launch?
2. Verify files through Steam. (On this install the executable was not found in the game
   root during setup — see [01-setup.md](01-setup.md).)
3. Only then suspect a specific mod.
