#!/usr/bin/env python3
"""cshm.py - query layer over an extracted Cyber Sleuth / Hacker's Memory database.

The game ships its tables as .mbe archives. SimpleDSCSModManager (SDMM) / DSCSTools
unpack each .mbe into a *folder of CSV files* - one CSV per sheet, with a real header
row of column names. This tool reads that unpacked tree. It never writes to it.

Usage:
    python tools/cshm.py env
    python tools/cshm.py catalog [-o reference/mbe-catalog.csv]
    python tools/cshm.py sheets <table>            # e.g. digimon_common_para
    python tools/cshm.py head <table> [sheet] [-n 5]
    python tools/cshm.py grep-cols <regex>         # which tables have a column like this
    python tools/cshm.py name <digimon-id>         # 4ID or bare id, both accepted
    python tools/cshm.py row <table> <sheet> <id>

The game path is resolved from, in order:
    1. --game / -g argument
    2. the CSHM_GAME environment variable
    3. reference/game-path.txt in this repo
    4. the known Steam library locations
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The name tables carry Japanese, Chinese and Korean. A Windows console defaults to
# cp1252 and would raise UnicodeEncodeError on the first Digimon name printed.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # already redirected, or not a real stream
        pass

STEAM_GUESSES = [
    r"E:/SteamLibrary/steamapps/common/Digimon Story Cyber Sleuth Complete Edition",
    r"D:/SteamLibrary/steamapps/common/Digimon Story Cyber Sleuth Complete Edition",
    r"C:/Program Files (x86)/Steam/steamapps/common/Digimon Story Cyber Sleuth Complete Edition",
]

# Folders inside an unpacked archive that hold .mbe tables.
TABLE_DIRS = ("data", "text", "message")


def find_game(explicit: str | None = None) -> Path:
    """Return the game root. Raises SystemExit with an actionable message if absent."""
    candidates: list[str] = []
    if explicit:
        candidates.append(explicit)
    if os.environ.get("CSHM_GAME"):
        candidates.append(os.environ["CSHM_GAME"])
    pathfile = REPO / "reference" / "game-path.txt"
    if pathfile.is_file():
        candidates.append(pathfile.read_text(encoding="utf-8").strip())
    candidates.extend(STEAM_GUESSES)

    for c in candidates:
        p = Path(c)
        if (p / "resources").is_dir():
            return p
    sys.exit(
        "Could not find the game install. Pass --game, set CSHM_GAME, or write the\n"
        "path into reference/game-path.txt. Looked at:\n  " + "\n  ".join(candidates)
    )


def find_db(game: Path) -> Path:
    """Return the unpacked database root (the folder holding data/, text/, message/)."""
    for name in ("DSDB", "extracted", "unpacked"):
        p = game / name
        if any((p / d).is_dir() for d in TABLE_DIRS):
            return p
    sys.exit(
        f"No unpacked database under {game}. Use SDMM's Extract tab on DSDB first;\n"
        "it writes a DSDB/ folder containing data/, text/, message/, script64/ ..."
    )


def iter_tables(db: Path):
    """Yield (folder, table_name, table_path) for every unpacked .mbe in the tree."""
    for folder in TABLE_DIRS:
        d = db / folder
        if not d.is_dir():
            continue
        for t in sorted(d.iterdir()):
            if t.is_dir() and t.name.endswith(".mbe"):
                yield folder, t.name[: -len(".mbe")], t


def resolve_table(db: Path, table: str) -> Path:
    """Find a table by bare name, with or without the .mbe suffix, in any folder."""
    want = table[:-4] if table.endswith(".mbe") else table
    hits = [p for _f, n, p in iter_tables(db) if n == want]
    if not hits:
        sys.exit(f"No table named {want!r}. Try: python tools/cshm.py catalog")
    if len(hits) > 1:
        sys.exit("Ambiguous, exists in several folders:\n  " + "\n  ".join(str(h) for h in hits))
    return hits[0]


def read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    """MBE sheets are UTF-8 (the loose CSVs in data/ are SHIFT-JIS - not read here)."""
    with path.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return [], []
    return rows[0], rows[1:]


# --------------------------------------------------------------------------- commands

def cmd_env(args):
    game = find_game(args.game)
    db = find_db(game)
    tables = list(iter_tables(db))
    print(f"game     {game}")
    print(f"database {db}")
    print(f"archives {len(list((game / 'resources').glob('*.mvgl')))} .mvgl in resources/")
    for folder in TABLE_DIRS:
        n = sum(1 for f, _n, _p in tables if f == folder)
        print(f"{folder:<9}{n} tables")
    mods = game / "mods"
    if mods.is_dir():
        print(f"mods     {', '.join(sorted(p.name for p in mods.iterdir())) or '(none)'}")


def cmd_catalog(args):
    db = find_db(find_game(args.game))
    out = Path(args.output) if args.output else REPO / "reference" / "mbe-catalog.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["folder", "table", "sheet", "rows", "n_columns", "columns"])
        for folder, name, path in iter_tables(db):
            for sheet in sorted(path.glob("*.csv")):
                header, body = read_csv(sheet)
                w.writerow([folder, name, sheet.stem, len(body), len(header), "|".join(header)])
                n += 1
    print(f"{n} sheets -> {out}")


def cmd_sheets(args):
    path = resolve_table(find_db(find_game(args.game)), args.table)
    for sheet in sorted(path.glob("*.csv")):
        header, body = read_csv(sheet)
        print(f"{sheet.stem:<32}{len(body):>7} rows  {len(header):>3} cols")


def cmd_head(args):
    path = resolve_table(find_db(find_game(args.game)), args.table)
    sheets = sorted(path.glob("*.csv"))
    if args.sheet:
        sheets = [s for s in sheets if s.stem == args.sheet] or sys.exit(
            f"No sheet {args.sheet!r} in {path.name}"
        )
    for sheet in sheets:
        header, body = read_csv(sheet)
        print(f"--- {path.name}/{sheet.name}")
        print(",".join(header))
        for row in body[: args.n]:
            print(",".join(row))


def cmd_grep_cols(args):
    db = find_db(find_game(args.game))
    rx = re.compile(args.regex, re.I)
    for folder, name, path in iter_tables(db):
        for sheet in sorted(path.glob("*.csv")):
            header, _ = read_csv(sheet)
            hit = [c for c in header if rx.search(c)]
            if hit:
                print(f"{folder}/{name}.mbe/{sheet.name}: {', '.join(hit)}")


def cmd_name(args):
    db = find_db(find_game(args.game))
    path = resolve_table(db, "charname")
    ident = str(args.id)
    # digimon_common_para uses the bare id; charname uses the 4ID form (1 + 3 digits).
    wanted = {ident, f"1{int(ident):03d}"} if ident.isdigit() else {ident}
    for sheet in sorted(path.glob("*.csv")):
        header, body = read_csv(sheet)
        for row in body:
            if row and row[0] in wanted:
                print(", ".join(f"{h}={v}" for h, v in zip(header, row) if v))
                return
    sys.exit(f"No charname entry for {args.id}")


def cmd_row(args):
    path = resolve_table(find_db(find_game(args.game)), args.table)
    sheet = path / f"{args.sheet}.csv"
    if not sheet.is_file():
        sys.exit(f"No sheet {args.sheet!r} in {path.name}")
    header, body = read_csv(sheet)
    for row in body:
        if row and row[0] == str(args.id):
            for h, v in zip(header, row):
                print(f"{h:<24}{v}")
            return
    sys.exit(f"No row with id {args.id} in {path.name}/{args.sheet}.csv")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-g", "--game", help="path to the game install")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("env").set_defaults(func=cmd_env)

    c = sub.add_parser("catalog"); c.add_argument("-o", "--output"); c.set_defaults(func=cmd_catalog)
    c = sub.add_parser("sheets"); c.add_argument("table"); c.set_defaults(func=cmd_sheets)
    c = sub.add_parser("head")
    c.add_argument("table"); c.add_argument("sheet", nargs="?"); c.add_argument("-n", type=int, default=5)
    c.set_defaults(func=cmd_head)
    c = sub.add_parser("grep-cols"); c.add_argument("regex"); c.set_defaults(func=cmd_grep_cols)
    c = sub.add_parser("name"); c.add_argument("id"); c.set_defaults(func=cmd_name)
    c = sub.add_parser("row")
    c.add_argument("table"); c.add_argument("sheet"); c.add_argument("id")
    c.set_defaults(func=cmd_row)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
