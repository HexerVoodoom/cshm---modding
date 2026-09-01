# 05 — Building an SDMM mod

Source: `<game>/SimpleDSCSModManager/Documentation/modders_guide.pdf` (Pherakki, SDMM v0.1).
That PDF is upstream truth; this file is the operational summary.

## Minimum viable mod

```
MyMod/
  METADATA.json
  modfiles/
    data/mon_para.mbe/Monster.csv     <- only the rows you changed
```

`METADATA.json` — all values are strings:

```json
{
  "Name": "Example Mod",
  "Author": "You",
  "Version": "1.0",
  "Category": "Utilities",
  "Description": "Short description"
}
```

`Description` must be one line. For anything richer, add a `DESCRIPTION.html` next to
`METADATA.json` — it takes priority.

`modfiles/` mirrors an unpacked archive: it holds `data/`, `text/`, `message/`,
`script64/`, `images/` and loose model files, exactly as they appear in `DSDB/`.

The real example on this machine is `<game>/mods/Kyoko`: `METADATA.json` +
`modfiles/images/` with six texture files. Read it before writing your first one.

## How SDMM decides what to do with a file

Every file is matched to a **filetype**, and each filetype has a **default rule**. Put the
file in the right place with the right extension and you usually need nothing else.

| File | Recognised as | Default rule |
|---|---|---|
| `*.csv` inside a `*.mbe/` folder | MBE table sheet | `mberecord_merge` |
| `*.csv` not inside a `*.mbe/` folder | loose CSV | `mberecord_merge` |
| `*.txt` inside `script64/` | Squirrel source | `squirrel_concat` |
| `*.sqmod` | Squirrel patch | `squirrel_modify` |
| `*.name` `*.skel` `*.geom` `*.anim` | model part | `overwrite` |
| `*.mdledit` | model edit script | `mdledit_*` |
| `*.request` | vanilla file request | `request_file` |
| anything else | raw asset | `overwrite` |

**Anything unrecognised is copied over the vanilla file wholesale.** That is the failure
mode behind most "my mod deleted half the game" reports.

### `.request` — don't redistribute vanilla assets

To include a vanilla file in your mod without shipping it, drop an empty
`chr003.name.request` where the file should be. Write an archive name inside the file
(e.g. `DSDB`) to pin which version you want.

## Where the data lands

By default everything goes into **`DSDBP`**, the highest-priority archive. That is correct
for nearly every mod.

To target other archives, add `"FormatVersion": 2` to `METADATA.json` and put your files in
folders named after the archive:

```
modfiles/
  DSDBP/data/...        -> into DSDBP
  DSDBbgm/...           -> into the BGM AFS2
  someFolder/...        -> installed as a loose folder (not an archive)
```

Use this only for audio or loose files. **Never install into `DSDB`** — huge, slow, and no
spare room.

## Softcodes — mandatory for anything new

IDs are hardcoded throughout the database, in model filenames and in scripts. Two mods that
both invent "item 900" conflict. Softcodes let SDMM assign the number.

```
[Category::Key]
[Category::Key|SubCategory::Key2]
[Category::Key::function()]
```

Write `[Item::MyNewPotion]` anywhere; if the key is new, SDMM allocates an ID for it, and
**other mods can refer to the same key** and build on yours.

Functions format the number for the context. On the `Digimon` category:

| Function | `1` becomes |
|---|---|
| `3ID` | `001` |
| `4ID` | `1001` |
| `filename` | `chr001` |

Categories in v0.1: `BattleBGM`, `Digimon` (child `DigimonEnemyVariant`), `Dungeon_CS` /
`Dungeon_HM` (→ `…SubArea` → `…SubAreaNPC`), `Town_CS` / `Town_HM` (same tree, `t` instead
of `d`), `Field_CS`, `Field_HM`, `Item`, `Shop`, `ShopLineup`, `ShopLimitLineup`,
`ShopText`, `Skill`, `SupportSkill`, `Speakers`.

Area softcodes carry the map-file functions: `fieldFile`, `collisionFile`, `surfaceFile`,
`positionFile`, `battleFile`, `cameraFile`, `hideablesFile` — the `f/c/s/p/b/_cam/_hide`
suffixes from [07-models-and-textures.md](07-models-and-textures.md).

The v0.1 softcode set does **not** cover the whole database. Where no category exists,
hardcode and leave a comment; migrate later.

### Aliases

Long softcodes get shortened in `ALIASES.json`, next to `METADATA.json`:

```json
{ "ShibuyaNPCs": "Dungeon_CS::d90|SubArea::d9002|NPC" }
```

Aliases are private to your mod.

## Mod manager variables

`Variables.txt`, next to `METADATA.json`, defines lists that **other mods can extend** —
e.g. a shop inventory that grows as more mods are installed.

```
MyListOfItems
::0,0,0        # default (only applies if nothing edits it)
++10           # add
--5            # remove
```

Reference it as `[VarList::MyListOfItems]`, with `splat`, `splat_strings`, `as_list`,
`as_list_strings`, `as_braced_list`, `as_braced_list_strings` to control how it is
rendered. `splat` is what you want to expand a list across CSV cells.

## Build scripts

A JSON dict mapping **file target** (the path SDMM should treat the file as) to build
instructions. Use it to rename, to pick a non-default rule, to order multiple files onto
one target, or to put a softcode in a filename.

```json
{
  "script64/t0101.txt": "myscript.txt",
  "data/shop_para.mbe/lineup.csv": ["my_lineup.csv", "mberecord_append", "-1"]
}
```

The third element is a rule argument — here, the padding character for `mberecord_append`.
Paths are always relative to `modfiles/`, even under `"FormatVersion": 2`.

## Distribution

Ship a zip, in one of two shapes:

- the zip's top level contains `modfiles/` and `METADATA.json`; or
- the zip contains a **single folder with the same name as the zip**, which contains them.

## CYMIS

For installers with user-facing options (flags, `ChooseOne` choices, conditional copies),
SDMM supports CYMIS wizard scripts. See section 5 of the upstream PDF; not summarised here
until we ship a mod that needs one.

## Checklist before building

1. Every CSV contains **only** changed rows, with the vanilla header on line 1.
2. `.mbe` folders are named `something.mbe`, not `something`.
3. New IDs use softcodes, not invented numbers.
4. No vanilla assets redistributed — `.request` instead.
5. `METADATA.json` parses, and `Description` is one line.
6. Nothing targets `DSDB`.
