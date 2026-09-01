#!/usr/bin/env python3
"""scan_mods.py - catalogue every SDMM mod folder on this machine.

An SDMM mod is any folder holding a METADATA.json. This walks a set of roots, reads each
one, and reports what the mod actually contains: which tables it patches, how many model
and image files it ships, and whether it uses softcodes.

    python tools/scan_mods.py --roots D:/Mateus "E:/DIGIMON MODS" -o reference/mod-corpus.csv
    python tools/scan_mods.py --summary            # counts by author/category, no file

The result is a *corpus*: the working examples to copy from when a question is
"how did this get done before?".
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

DEFAULT_ROOTS = [
    r"D:/Mateus",
    r"D:/SteamLibrary/steamapps/common/SimpleDSCSModManager-develop",
    r"E:/DIGIMON MODS",
    r"E:/SteamLibrary/steamapps/common/Digimon Story Cyber Sleuth Complete Edition/mods",
    r"E:/SteamLibrary/steamapps/common/Digimon Story Cyber Sleuth Complete Edition/SimpleDSCSModManager/mods",
    r"C:/Users/spera/Documents",
    r"C:/Users/spera/Downloads/digimon",
]

MODEL_EXT = {".name", ".skel", ".geom", ".anim", ".phys", ".detr", ".note", ".sprk", ".navi"}
SOFTCODE = re.compile(r"\[[A-Za-z_]+::")

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def find_mods(roots: list[str]):
    """Yield every directory containing a METADATA.json, skipping the game's own DSDB."""
    for root in roots:
        r = Path(root)
        if not r.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(r, onerror=lambda e: None):
            if "DSDB" in Path(dirpath).parts:
                dirnames[:] = []
                continue
            if "METADATA.json" in filenames:
                yield Path(dirpath)


def describe(mod: Path) -> dict:
    """Read one mod folder. Never raises - a broken mod is a row, not a crash."""
    meta_path = mod / "METADATA.json"
    meta, meta_error = {}, ""
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
        if not isinstance(meta, dict):
            meta, meta_error = {}, "not a JSON object"
    except Exception as exc:
        meta_error = f"{type(exc).__name__}: {exc}"

    files = mod / "modfiles"
    tables, models, images, scripts, others, softcoded = set(), 0, 0, 0, 0, False
    if files.is_dir():
        for dirpath, _dirnames, filenames in os.walk(files, onerror=lambda e: None):
            rel = Path(dirpath).relative_to(files)
            for fn in filenames:
                ext = Path(fn).suffix.lower()
                if ext == ".csv":
                    # The .mbe folder name is what makes a CSV a table sheet.
                    part = next((p for p in rel.parts if p.endswith(".mbe")), None)
                    tables.add(f"{part[:-4]}/{Path(fn).stem}" if part else f"(loose){Path(fn).stem}")
                    if not softcoded:
                        try:
                            softcoded = bool(SOFTCODE.search(
                                (Path(dirpath) / fn).read_text(encoding="utf-8", errors="replace")))
                        except OSError:
                            pass
                elif ext in MODEL_EXT:
                    models += 1
                elif ext in (".img", ".dds", ".png"):
                    images += 1
                elif ext in (".txt", ".sqmod"):
                    scripts += 1
                else:
                    others += 1

    return {
        "name": meta.get("Name", ""),
        "author": meta.get("Author", ""),
        "version": meta.get("Version", ""),
        "category": meta.get("Category", ""),
        "format_version": meta.get("FormatVersion", 1),
        "n_tables": len(tables),
        "n_models": models,
        "n_images": images,
        "n_scripts": scripts,
        "n_other": others,
        "softcodes": "yes" if softcoded else "no",
        "has_modfiles": "yes" if files.is_dir() else "NO",
        "meta_error": meta_error,
        "tables": "|".join(sorted(tables)),
        "path": str(mod),
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--roots", nargs="*", default=DEFAULT_ROOTS)
    p.add_argument("-o", "--output", default=str(REPO / "reference" / "mod-corpus.csv"))
    p.add_argument("--summary", action="store_true", help="print counts instead of writing the file")
    args = p.parse_args(argv)

    rows = [describe(m) for m in find_mods(args.roots)]
    rows.sort(key=lambda r: (r["author"].lower(), r["name"].lower(), r["path"]))

    if args.summary:
        print(f"{len(rows)} mods\n")
        for field in ("author", "category"):
            print(f"-- by {field}")
            for k, n in Counter(r[field] or "(blank)" for r in rows).most_common(15):
                print(f"  {n:>4}  {k}")
            print()
        data = [r for r in rows if r["n_tables"]]
        print(f"{len(data)} mods patch at least one table; {sum(r['softcodes']=='yes' for r in rows)} use softcodes")
        broken = [r for r in rows if r["meta_error"] or r["has_modfiles"] == "NO"]
        print(f"{len(broken)} mods are malformed (bad METADATA.json or no modfiles/)")
        return

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["path"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} mods -> {out}")


if __name__ == "__main__":
    main()
