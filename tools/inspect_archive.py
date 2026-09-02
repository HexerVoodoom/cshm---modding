#!/usr/bin/env python3
"""Open a BUILT .mvgl archive and read what the game will actually load.

Until this existed, a mod could only be checked before the build. The shipped archive is
encrypted and every file inside it is doboz-compressed, so searching its bytes proves
nothing in either direction -- a control probe for a stem that is definitely present comes
back "absent" too. That is how an NPC pointing at a model that was not in the archive got
all the way to "installed".

DSCSTools does the decrypt/extract/decompress, but it is a Python 3.8 extension and this
repo runs on 3.13+. Rather than install anything: LibreOffice bundles a complete Python
3.8.10, and it loads DSCSTools fine. This script drives that interpreter as a subprocess.

    python tools/inspect_archive.py --list
    python tools/inspect_archive.py --find chr007 t3001p
    python tools/inspect_archive.py --table field_npc_para/t3001 --grep chr007
    python tools/inspect_archive.py --strings text/item_name "Powerful Mojo"

Text tables have no DSCSTools structure file, so --strings byte-searches the decompressed
table instead of parsing rows; game text is readable once decompressed.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PY38_CANDIDATES = [
    r"C:/Program Files/LibreOffice/program/python-core-3.8.10/bin/python.exe",
    r"C:/Program Files (x86)/LibreOffice/program/python-core-3.8.10/bin/python.exe",
]
DSCSTOOLS_DIRS = [
    r"E:/SteamLibrary/steamapps/common/Digimon Story Cyber Sleuth Complete Edition/SimpleDSCSModManager/sdmmlib/dscstools",
    r"D:/SteamLibrary/steamapps/common/SimpleDSCSModManager-develop/SimpleDSCSModManager/sdmmlib/dscstools",
]
ARCHIVES = [
    r"E:/SteamLibrary/steamapps/common/Digimon Story Cyber Sleuth Complete Edition/resources/DSDBP.steam.mvgl",
]

WORKER = r'''
import DSCSTools, os, sys, json, csv
cfg = json.loads(sys.argv[1])
os.chdir(cfg["dscstools"])                    # extractMBE resolves structures/ from cwd
work = cfg["work"]
ex = os.path.join(work, "ex")
if not os.path.isdir(ex):
    dec = os.path.join(work, "a.decrypt")
    DSCSTools.crypt(cfg["archive"], dec)
    DSCSTools.extractMDB1(dec, ex, False)
    os.remove(dec)
out = []

def decompress(rel):
    src = os.path.join(ex, rel)
    if not os.path.isfile(src):
        return None
    d = os.path.join(work, os.path.basename(rel) + ".unc")
    DSCSTools.dobozDecompress(src, d)
    return d

if cfg["list"]:
    for root, _, fs in os.walk(ex):
        out.append({"kind": "dir", "path": os.path.relpath(root, ex), "files": len(fs)})

for stem in cfg["find"]:
    hits = []
    for root, _, fs in os.walk(ex):
        rel = os.path.relpath(root, ex).replace("\\", "/")
        pre = "" if rel == "." else rel + "/"
        hits += [pre + f for f in fs if f.startswith(stem)]
    out.append({"kind": "find", "stem": stem, "count": len(hits),
                "sample": sorted(hits)[:8]})

for spec in cfg["tables"]:
    table, _, sheet = spec.partition("/")
    rel = None
    for folder in ("data", "text", "message"):
        if os.path.isfile(os.path.join(ex, folder, table + ".mbe")):
            rel = folder + "/" + table + ".mbe"
            break
    if rel is None:
        out.append({"kind": "table", "table": table, "error": "not in archive"})
        continue
    d = decompress(rel)
    o = os.path.join(work, "csv", table)
    try:
        DSCSTools.extractMBE(d, o)
    except Exception as e:
        out.append({"kind": "table", "table": table, "error": str(e)})
        continue
    sheets = []
    for r0, _, fs in os.walk(o):
        for f in fs:
            if sheet and os.path.splitext(f)[0] != sheet:
                continue
            with open(os.path.join(r0, f), encoding="utf-8", errors="replace") as fh:
                data = list(csv.reader(fh))
            body = data[1:]
            pat = cfg["grep"]
            keep = [x for x in body if not pat or any(pat in c for c in x)]
            sheets.append({"sheet": os.path.splitext(f)[0], "total": len(body),
                           "matched": len(keep), "rows": keep[:cfg["limit"]]})
    out.append({"kind": "table", "table": table, "sheets": sheets})

for rel, needles in cfg["strings"]:
    if not rel.endswith(".mbe"):
        rel += ".mbe"
    d = decompress(rel)
    if d is None:
        out.append({"kind": "strings", "path": rel, "error": "not in archive"})
        continue
    b = open(d, "rb").read()
    out.append({"kind": "strings", "path": rel, "size": len(b),
                "counts": {n: b.count(n.encode("utf-8")) for n in needles}})

print("@@JSON@@" + json.dumps(out))
'''


def find_tools() -> tuple[Path, Path]:
    py = next((Path(p) for p in PY38_CANDIDATES if Path(p).is_file()), None)
    if py is None:
        sys.exit("No Python 3.8 found. LibreOffice ships one at "
                 "program/python-core-3.8.10/bin/python.exe - install LibreOffice or "
                 "edit PY38_CANDIDATES.")
    dt = next((Path(d) for d in DSCSTOOLS_DIRS if (Path(d) / "DSCSTools.pyd").is_file()), None)
    if dt is None:
        sys.exit("DSCSTools.pyd not found; edit DSCSTOOLS_DIRS.")
    return py, dt


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archive", help="a .steam.mvgl (default: the installed DSDBP)")
    ap.add_argument("--list", action="store_true", help="show the archive's folders")
    ap.add_argument("--find", nargs="*", default=[], metavar="STEM",
                    help="report whether files starting with STEM are present")
    ap.add_argument("--table", nargs="*", default=[], metavar="TABLE[/SHEET]",
                    help="unpack a table and print rows")
    ap.add_argument("--grep", help="with --table, keep only rows containing this text")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--strings", nargs="+", default=[], metavar="ARG",
                    help="PATH NEEDLE [NEEDLE...] - byte-search a decompressed table")
    ap.add_argument("--fresh", action="store_true", help="discard the cached extraction")
    args = ap.parse_args()

    archive = args.archive or next((a for a in ARCHIVES if Path(a).is_file()), None)
    if not archive or not Path(archive).is_file():
        print("No archive found; pass --archive")
        return 2
    py, dt = find_tools()

    work = Path(tempfile.gettempdir()) / "cshm-archive-inspect"
    if args.fresh and work.is_dir():
        import shutil
        shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True, exist_ok=True)

    cfg = {"archive": str(archive), "dscstools": str(dt), "work": str(work),
           "list": args.list, "find": args.find, "tables": args.table,
           "grep": args.grep, "limit": args.limit,
           "strings": [[args.strings[0], args.strings[1:]]] if args.strings else []}

    src = work / "_worker.py"
    src.write_text(WORKER, encoding="utf-8")
    env = {**os.environ,
           "PATH": str(py.parents[2]) + os.pathsep + os.environ.get("PATH", ""),
           "PYTHONPATH": str(dt)}
    p = subprocess.run([str(py), str(src), json.dumps(cfg)],
                       capture_output=True, text=True, env=env)
    if "@@JSON@@" not in p.stdout:
        print(p.stdout[-2000:])
        print(p.stderr[-2000:])
        return 1

    print(f"archive: {archive}")
    for r in json.loads(p.stdout.split("@@JSON@@", 1)[1]):
        if r["kind"] == "dir":
            print(f"  {r['path']:<12} {r['files']} file(s)")
        elif r["kind"] == "find":
            print(f"  {'OK    ' if r['count'] else 'ABSENT'} {r['stem']:<12} "
                  f"{r['count']} file(s) {r['sample'][:5]}")
        elif r["kind"] == "table":
            if r.get("error"):
                print(f"  {r['table']}: {r['error']}")
                continue
            for sh in r["sheets"]:
                print(f"  {r['table']}/{sh['sheet']}: "
                      f"{sh['matched']}/{sh['total']} row(s)")
                for row in sh["rows"]:
                    print("      " + ",".join(row)[:150])
        elif r["kind"] == "strings":
            if r.get("error"):
                print(f"  {r['path']}: {r['error']}")
                continue
            print(f"  {r['path']} ({r['size']} bytes)")
            for n, c in r["counts"].items():
                print(f"      {'OK    ' if c else 'ABSENT'} {n!r} x{c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
