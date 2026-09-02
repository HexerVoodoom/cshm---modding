# 08 — Troubleshooting

Ordered by how often the cause is the real one. The dangerous entries are the ones where
**nothing errors**.

## The mod installs and nothing changes

| Cause | Check |
|---|---|
| Folder named `charname` instead of `charname.mbe` — read as a loose CSV, not a table sheet. | `ls modfiles/data` |
| A sheet is not named what SDMM's own `resources/base_resources/` extraction calls it. Two different failures: a wrong `charname` name (the DSDB dump says `Digimon Names.csv`, SDMM says `Sheet1.csv`) **drops the rows silently**; a wrong `multi_select_text` name (SDMM says `para.csv`) **fails the build** with `something went wrong while writing <table>.mbe`. There is no per-folder rule. | `diff <(ls <mod>/text/*.mbe/) <(ls <SDMM>/resources/base_resources/text/*.mbe/)` |
| Wrong ID form: bare vs 4ID vs `chrNNN`. | [04-data-tables.md](04-data-tables.md#the-id-systems--the-most-common-silent-failure) |
| Composite key (e.g. `mon_para` is `(type, variation)`) — you patched the wrong row. | `python tools/cshm.py head mon_para` |
| A third-party `.mvgl` in `resources/` overrides you via DSCSModLoader. | [../reference/archives.md](../reference/archives.md) |
| You edited `DSDB/` (the read-only extraction) instead of your mod folder. | — |


## Driving the game without the mod manager's permission layer

The computer-use resolver on this machine does not recognise the game or SDMM and never
shows the user a permission dialog, but the game can still be observed and driven from
PowerShell:

```powershell
# see the screen
$b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp=New-Object System.Drawing.Bitmap($b.Width,$b.Height)
[System.Drawing.Graphics]::FromImage($bmp).CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size)

# send a key -- SCAN CODES (0x0008), not virtual keys, which the game ignores
[W]::keybd_event(0,0x1C,0x0008,[UIntPtr]::Zero)   # Enter down
[W]::keybd_event(0,0x1C,0x000A,[UIntPtr]::Zero)   # Enter up
```

Always re-assert `SetForegroundWindow` and verify `GetForegroundWindow()` before each key --
otherwise the keystroke lands in whatever window stole focus.

**What the keyboard can and cannot do**, measured across ~60 keys:

**The arrow keys are EXTENDED keys.** `keybd_event` needs `KEYEVENTF_EXTENDEDKEY` (0x0001)
as well as the scancode flag -- `0x0009` down, `0x000B` up. Send `0x0008` alone and you have
pressed the *numpad* equivalent, not the arrow. This single mistake cost this session a wrong
published conclusion ("the character cannot be moved"), because numpad-8 happens to open the
Digivice menu, so the "movement" tests were driving a menu.

| Works | Notes |
|---|---|
| Title screen and save select | Enter, Down |
| **Walking the character** | the four arrows, **extended flag required**; hold ~2 s per step |
| Opening the Digivice menu | long press (~1.5 s) of scancode `0x48` **without** the extended flag (numpad 8); short taps do nothing, so a tap-based sweep misses it |
| Closing it | **Escape** -- Backspace does not. Verify with a screenshot: a test run against a menu you think you closed measures nothing |
| Camera | G, T |

The Digivice menu has no travel option -- travel in this game is done at in-world terminals --
The Digivice ring's selection could not be rotated from the keyboard, so menu entries such as
the Field Guide stayed out of reach; the world itself, however, is fully walkable once the
arrows are sent correctly, and travel in this game happens at in-world terminals rather than
through a menu.

## The title screen can crash on its own

Idling at the title produced an access violation at a constant offset (`0x250ffb`) five times
in one hour, while leaving the title promptly did not. The same offset appears in a crash
from before any of this work, so it is not new. A save that loads fine can sit behind a title
screen that dies first -- when a user reports "my save crashes", check whether the game
survives the title before concluding anything about the save.


## Verify the built archive, not just the mod folder

Every gate in `tools/validate_mod.py` runs on the mod **before** the build. That is not the
same as checking what shipped. The archive is encrypted and each file inside it is
doboz-compressed, so grepping `DSDBP.steam.mvgl` proves nothing -- a control probe for a
stem that is definitely there comes back absent too.

`tools/inspect_archive.py` opens it properly. DSCSTools does the work, and although it is a
Python 3.8 extension, **LibreOffice bundles a complete Python 3.8.10** that loads it, so
nothing needs installing:

```bash
python tools/inspect_archive.py --find chr007 t3001p
python tools/inspect_archive.py --table field_npc_para/t3001 --grep chr007
python tools/inspect_archive.py --strings text/item_name "Powerful Mojo"
```

This is the only way to answer "is my model actually in there under the name the table
says?". It is how the `chr992` NPC bug was confirmed: `chr007` returned 16 files and
`chr992` returned zero, from the same archive.

Text tables have no DSCSTools structure file, so use `--strings` for those; game text is
readable once decompressed.


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

## SDMM crashes on startup with `'PathManager' object has no attribute 'self'`

It cannot find the game. Check `config/config.json` → `game_loc` actually points at the
install that has `resources/` full of `.mvgl` files — a second, empty Steam library folder for
the same appid is easy to point at by mistake. SDMM's own error path has a typo, so "game not
found" surfaces as a fatal crash rather than a message. See
[../reference/workspace-inventory.md](../reference/workspace-inventory.md).

## An existing save crashes after installing mods

Installing replaces the **entire** mod set — SDMM rebuilds `DSDBP` from exactly what is
ticked, so anything previously installed and now unticked is gone. A save holding a Digimon,
item or skill from a removed mod crashes on load. Re-tick the mods that save was made with
and install again. Back the save up before changing the set.

## The game will not launch at all

1. Disable all mods in SDMM and build — does vanilla launch?
2. Verify files through Steam. (On this install the executable was not found in the game
   root during setup — see [01-setup.md](01-setup.md).)
3. Only then suspect a specific mod.


## SDMM says "some file is malformatted"

**ModernCSV.** It writes a trailing comma after the last column. Use LibreOffice, or write
the CSV programmatically.

## SDMM build fails with `join () takes exactly one argument (2 given)`

Unsolved as of 2026-09-01. Reported against `item_para.mbe/table.csv`; SydMontague's first
suspicion is a syntax error in a mod JSON. Bisect by removing table folders one at a time.

## Blender-Tools will not import or export

It supports **Blender 2.80-2.91 only**. Above 3.0 it does not work. Then, in order: did you
select the collection before exporting; is a mesh empty or unrigged; are there zero-weight
vertex groups; is every mesh parented to the same armature. Full table in
[../reference/model-porting.md](../reference/model-porting.md#exporting--the-errors-and-what-they-mean).

## The model explodes in game

The mesh's shader was never configured ("explosive model syndrome"), or — on metallic meshes
— tangent vectors were not exported. Blender also silently attaches colour maps to meshes
that should not have them, which breaks models in game.

## Geometry disappears when a mod loads

Two meshes share a `name_hash`. A loading mesh removes every loaded mesh with the same hash;
that is the costume system, and it deletes whatever you did not intend to replace.

## An imported model renders black or untextured

Three known causes: a `.001` suffix on a texture name in Blender; file extensions left inside
the texture names in the model file (check with a hex editor); the material's diffuse colour
node set to `0 0 0`. See [07-models-and-textures.md](07-models-and-textures.md).
