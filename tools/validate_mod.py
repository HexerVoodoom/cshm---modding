#!/usr/bin/env python3
"""validate_mod.py - pre-flight an SDMM mod folder against the known silent failures.

Every check here exists because something shipped broken for that reason. The point is that
a mod fails *here*, with a message, instead of installing cleanly and doing nothing.

    python tools/validate_mod.py "<path to mod folder>"
    python tools/validate_mod.py "<path>" --quiet     # findings only
    python tools/validate_mod.py --all                # every mod in reference/mod-corpus.csv

Exit code is 1 if there is any FAIL, else 0. WARN never fails the run - it flags something a
human should look at.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cshm import find_game, find_db, iter_tables, read_csv  # noqa: E402

REPO = Path(__file__).resolve().parent.parent

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SOFTCODE = re.compile(r"\[[A-Za-z_]+::")
SOFTCODE_CAT = re.compile(r"\[([A-Za-z_][A-Za-z0-9_]*)::")

# SDMM keeps one JSON per softcode category. A category that is not there does not resolve,
# so the build either fails or writes a broken ID.
SOFTCODE_DIRS = [
    r"D:/SteamLibrary/steamapps/common/SimpleDSCSModManager-develop/SimpleDSCSModManager/softcodes",
    r"E:/SteamLibrary/steamapps/common/Digimon Story Cyber Sleuth Complete Edition/SimpleDSCSModManager/softcodes",
]


def softcode_categories() -> set:
    for d in SOFTCODE_DIRS:
        p = Path(d)
        if p.is_dir():
            return {f.stem for f in p.glob("*.json")}
    return set()
MODEL_EXT = {".name", ".skel", ".geom", ".anim", ".phys", ".detr", ".note", ".sprk", ".navi"}
TABLE_DIRS = ("data", "text", "message")

# Loose CSVs that sit directly in data/ and are SHIFT-JIS, not UTF-8.
LOOSE_SJIS = {
    "bgm.csv", "se.csv", "voice.csv", "voice_us.csv", "soundtest_bgm.csv",
    "soundtest_se.csv", "soundtest_voice.csv", "debug_call_script.csv",
    "debug_call_script_hm.csv",
}

# Composite keys, taken verbatim from SDMM's own config/mberecord_idsizes.json.
# Keyed by "<table>/<sheet>". A merge rule that matches on cell 1 alone patches the wrong row.
COMPOSITE_KEYS = {
    "field_common_param/movie_bg": 2,
    "field_common_param/ui_field_name": 3,
    "model_attach_para/digimon01": 2,
    "model_attach_para/digimon02": 2,
    "model_attach_para/digimon03": 2,
    "model_attach_para/event": 3,
    "model_attach_para/npc": 5,
    "mon_design_para/Monster": 2,
    "mon_para/Monster": 2,
    "mon_para_hard/Monster": 2,
}

# Edits that are only half a feature on their own.
PAIRS = [
    ("evolution_next_para", "evolution_condition_para",
     "an evolution target with no condition never fires"),
    ("battle_voice", "battle_voice_add",
     "a voice line in only one table is silent in the other game"),
]


class Report:
    def __init__(self, mod: Path):
        self.mod = mod
        self.rows: list[tuple[str, str, str]] = []

    def add(self, level: str, gate: str, msg: str):
        self.rows.append((level, gate, msg))

    fail = lambda self, g, m: self.add("FAIL", g, m)      # noqa: E731
    warn = lambda self, g, m: self.add("WARN", g, m)      # noqa: E731
    ok = lambda self, g, m: self.add("PASS", g, m)        # noqa: E731

    @property
    def failures(self):
        return [r for r in self.rows if r[0] == "FAIL"]

    def render(self, quiet: bool) -> str:
        out = [f"=== {self.mod}"]
        for level, gate, msg in self.rows:
            if quiet and level == "PASS":
                continue
            out.append(f"  {level:<4} {gate:<22} {msg}")
        n_f = len(self.failures)
        n_w = sum(1 for r in self.rows if r[0] == "WARN")
        out.append(f"  -> {n_f} FAIL, {n_w} WARN")
        return "\n".join(out)


def vanilla_index(db: Path) -> dict:
    """{table_name: {"folder":…, "sheets": {sheet: (header, n_rows, ids)}}} for every table."""
    idx = {}
    for folder, name, path in iter_tables(db):
        sheets = {}
        for sheet in path.glob("*.csv"):
            header, body = read_csv(sheet)
            sheets[sheet.stem] = (header, len(body), {r[0] for r in body if r})
        idx[name] = {"folder": folder, "sheets": sheets}
    return idx


def check_metadata(mod: Path, rep: Report):
    p = mod / "METADATA.json"
    if not p.is_file():
        rep.fail("metadata", "no METADATA.json - this is not an SDMM mod folder")
        return {}
    try:
        meta = json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        rep.fail("metadata", f"METADATA.json does not parse: {exc}")
        return {}
    if not isinstance(meta, dict):
        rep.fail("metadata", "METADATA.json is not a JSON object")
        return {}
    for key in ("Name", "Author", "Version", "Category"):
        if not meta.get(key):
            rep.warn("metadata", f"{key} is missing or empty")
        elif not isinstance(meta[key], str):
            rep.fail("metadata", f"{key} must be a string, got {type(meta[key]).__name__}")
    desc = meta.get("Description", "")
    if isinstance(desc, str) and "\n" in desc:
        rep.fail("metadata", "Description must be one line - use DESCRIPTION.html instead")
    if not rep.failures:
        rep.ok("metadata", f"{meta.get('Name','(unnamed)')} by {meta.get('Author','?')}")
    return meta


def archive_roots(mod: Path, meta: dict) -> list[Path]:
    """Under FormatVersion 2 the archive name is a folder level; otherwise modfiles/ is root."""
    files = mod / "modfiles"
    if not files.is_dir():
        return []
    if meta.get("FormatVersion") == 2:
        roots = [d for d in files.iterdir()
                 if d.is_dir() and (d.name.startswith("DSDB") or d.name.startswith("7d6db"))]
        return roots or [files]
    return [files]


def check_tables(roots: list[Path], van: dict, rep: Report):
    seen_tables = set()
    for root in roots:
        for folder in TABLE_DIRS:
            d = root / folder
            if not d.is_dir():
                continue
            for entry in sorted(d.iterdir()):
                if entry.is_file() and entry.suffix.lower() == ".csv":
                    if entry.name in LOOSE_SJIS:
                        rep.ok("encoding", f"{folder}/{entry.name} is a loose SHIFT-JIS CSV")
                    continue
                if not entry.is_dir():
                    continue
                if not entry.name.endswith(".mbe"):
                    rep.fail("mbe-suffix",
                             f"{folder}/{entry.name}/ has no .mbe suffix - SDMM will treat its "
                             "CSVs as loose files and the edit is a silent no-op")
                    continue
                name = entry.name[:-4]
                seen_tables.add(name)
                v = van.get(name)
                if v is None:
                    rep.warn("unknown-table", f"{name}.mbe is not a vanilla table")
                    continue
                for sheet in sorted(entry.glob("*.csv")):
                    check_sheet(sheet, name, v, rep)
    return seen_tables


def check_sheet(sheet: Path, table: str, v: dict, rep: Report):
    label = f"{table}/{sheet.stem}"
    if sheet.stem not in v["sheets"]:
        real = sorted(v["sheets"])
        if v["folder"] == "text":
            # PROVEN by a real build: the extraction may name a text sheet something else
            # (charname unpacks as "Digimon Names.csv"), but SDMM merges text tables under
            # "Sheet1". Naming it after the extraction makes the rows vanish silently.
            rep.fail("sheet-name",
                     f"{label}.csv: text tables must use Sheet1.csv in a mod. The extraction "
                     f"calls this sheet {real[0]!r}, but the build merges under 'Sheet1' and "
                     "your rows are dropped without a warning.")
        elif len(real) == 1:
            rep.warn("sheet-name",
                     f"{label}.csv is not the vanilla sheet name ({real[0]}.csv). "
                     "The table has one sheet so SDMM probably tolerates this, but match it.")
        else:
            rep.fail("sheet-name",
                     f"{label}.csv does not exist in vanilla and {table} has "
                     f"{len(real)} sheets - the merge cannot guess. Real: "
                     + ", ".join(real))
        return
    vheader, vrows, vids = v["sheets"][sheet.stem]
    try:
        header, body = read_csv(sheet)
    except UnicodeDecodeError:
        rep.fail("encoding", f"{label}.csv is not valid UTF-8 (.mbe sheets must be UTF-8)")
        return

    widths = {len(r) for r in body if r}
    for w in sorted(widths):
        if w != len(vheader):
            rep.fail("columns",
                     f"{label}.csv has a {w}-cell row; vanilla is {len(vheader)} columns")

    if vrows and len(body) >= max(5, vrows * 0.8):
        rep.warn("patch-not-copy",
                 f"{label}.csv carries {len(body)} of vanilla's {vrows} rows - a mod CSV "
                 "should contain only what it changes")

    n = COMPOSITE_KEYS.get(label)
    if n:
        rep.warn("composite-key",
                 f"{label} is keyed on the first {n} cells - a rule matching cell 1 alone "
                 "patches the wrong row")

    raw = sheet.read_text(encoding="utf-8-sig", errors="replace")
    softcoded = bool(SOFTCODE.search(raw))
    new_ids = [r[0] for r in body if r and r[0] and r[0] not in vids and not r[0].startswith("[")]
    if new_ids and not softcoded:
        rep.warn("softcodes",
                 f"{label}.csv adds hardcoded new IDs ({', '.join(new_ids[:4])}"
                 f"{'…' if len(new_ids) > 4 else ''}) - use softcodes or you will collide "
                 "with other mods")


def check_pairs(seen: set, rep: Report):
    for a, b, why in PAIRS:
        if (a in seen) != (b in seen):
            missing = b if a in seen else a
            rep.warn("paired-edit", f"{a if a in seen else b} edited but {missing} is not - {why}")


def check_softcodes(mod: Path, rep: Report):
    """Every [Category::...] must be a registered category or an alias onto one."""
    valid = softcode_categories()
    if not valid:
        rep.add("WARN", "softcodes", "SDMM softcode registry not found - category check skipped")
        return
    aliases = {}
    ap = mod / "ALIASES.json"
    if ap.is_file():
        try:
            aliases = json.loads(ap.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            rep.fail("aliases", f"ALIASES.json does not parse: {exc}")
    for name, target in aliases.items():
        root = str(target).split("::")[0].strip()
        if root not in valid:
            rep.fail("softcodes", f"alias [{name}::] maps onto '{root}', which is not a "
                                  "registered softcode category")
    known = valid | {k.rstrip(":") for k in aliases}
    seen = {}
    skip = {".img", ".geom", ".name", ".skel", ".anim", ".phys", ".psd", ".request",
            ".dds", ".png", ".mvgl", ".detr", ".note", ".sprk", ".navi"}
    scan_root = mod / "modfiles"
    if not scan_root.is_dir():
        return
    for f in scan_root.rglob("*"):
        if not f.is_file() or f.suffix.lower() in skip:
            continue
        try:
            body = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for cat in SOFTCODE_CAT.findall(body):
            seen.setdefault(cat, f.relative_to(mod).as_posix())
    for cat, where in sorted(seen.items()):
        if cat not in known:
            rep.fail("softcodes",
                     f"[{cat}::] is not a registered softcode category and not an alias "
                     f"(first seen in {where}) - it will not resolve")
    if seen and not any(r[0] == "FAIL" and r[1] == "softcodes" for r in rep.rows):
        rep.ok("softcodes", f"{len(seen)} softcode categor{'y' if len(seen)==1 else 'ies'} all resolve")


ENCOUNT = re.compile(r"this\.Battle\.Encount\(\s*(\d+)\s*,")
BATTLE_SCRIPT = re.compile(r"^battle_(\d+)\.txt$")


def check_battles(roots: list[Path], db: Path, van: dict, rep: Report):
    """A custom battle is a mon_cpl coupling id plus a battle_<that id>.txt. Both or neither.

    Script names are zero-padded (`battle_0048.txt` for coupling `48`), so everything here
    is compared as an integer.
    """
    def num(s):
        try:
            return int(s)
        except (TypeError, ValueError):
            return None

    couplings, scripts, called = set(), set(), {}
    vanilla_cpl = {num(x) for x in
                   van.get("mon_cpl", {}).get("sheets", {}).get("Coupling", (None, 0, set()))[2]}
    vanilla_cpl.discard(None)
    for root in roots:
        p = root / "data/mon_cpl.mbe/Coupling.csv"
        if p.is_file():
            couplings |= {n for r in read_csv(p)[1] if r and (n := num(r[0])) is not None}
        d = root / "script64"
        if d.is_dir():
            for s in d.glob("*.txt"):
                m = BATTLE_SCRIPT.match(s.name)
                if m:
                    scripts.add(int(m.group(1)))
                for e in ENCOUNT.findall(s.read_text(encoding="utf-8", errors="replace")):
                    called.setdefault(int(e), s.name)

    def vanilla_script(n):
        return any((db / f"script64/battle_{n:0{w}d}.txt").is_file() for w in (1, 4, 5, 6))

    for c in sorted(couplings):
        if c not in scripts and not vanilla_script(c):
            rep.fail("battle", f"mon_cpl adds coupling {c} but no battle script defines that "
                               "fight - Battle.Encount on it has nothing to run")
        if c in vanilla_cpl:
            rep.warn("battle", f"coupling {c} overwrites a vanilla encounter")
    for s in sorted(scripts):
        if s not in couplings and s not in vanilla_cpl:
            rep.fail("battle", f"battle_{s}.txt ships but nothing defines coupling {s} - "
                               "the fight has no enemies")
    for n, where in sorted(called.items()):
        if n not in couplings and n not in vanilla_cpl:
            rep.fail("battle", f"{where} calls Battle.Encount({n}) but no coupling {n} exists")
    if couplings or scripts:
        rep.ok("battle", f"{len(couplings)} coupling(s), {len(scripts)} battle script(s), wired")


def check_variations(roots: list[Path], rep: Report):
    """Every (type, variation) in mon_para wants a matching mon_design_para row."""
    for root in roots:
        mp = root / "data/mon_para.mbe/Monster.csv"
        dp = root / "data/mon_design_para.mbe/Monster.csv"
        if not mp.is_file():
            continue
        pairs = {(r[0], r[1]) for r in read_csv(mp)[1] if len(r) > 1}
        design = {(r[0], r[1]) for r in read_csv(dp)[1] if len(r) > 1} if dp.is_file() else set()
        missing = sorted(pairs - design)
        if missing and dp.is_file():
            rep.warn("variations",
                     "mon_para has (type, variation) "
                     + ", ".join(f"{a}/{b}" for a, b in missing[:4])
                     + " with no mon_design_para row - 836 of 837 vanilla pairs have one")
        elif pairs and design:
            rep.ok("variations", f"{len(pairs)} statline(s), each with a design row")


STRUCTURE_DIRS = [
    r"D:/SteamLibrary/steamapps/common/SimpleDSCSModManager-develop/SimpleDSCSModManager/sdmmlib/dscstools/structures",
    r"E:/SteamLibrary/steamapps/common/Digimon Story Cyber Sleuth Complete Edition/SimpleDSCSModManager/sdmmlib/dscstools/structures",
]
INT_LIMITS = {"byte": (-128, 127), "ubyte": (0, 255), "short": (-32768, 32767),
              "ushort": (0, 65535), "int": (-2**31, 2**31 - 1), "uint": (0, 2**32 - 1)}
SOFT_START = re.compile(r"^\[[A-Za-z_][A-Za-z0-9_]*::")
INT_RE = re.compile(r"-?\d+")
FLOAT_RE = re.compile(r"-?\d+(\.\d+)?([eE]-?\d+)?")


def check_types(roots: list[Path], rep: Report):
    """Check every cell against DSCSTools' declared column type and width.

    This is the closest thing to a dry-run pack: a value that is the wrong type, or an
    integer too wide for its field, is what makes the build fail or write garbage.
    """
    sdir = next((Path(d) for d in STRUCTURE_DIRS if Path(d).is_dir()), None)
    if sdir is None:
        rep.warn("types", "DSCSTools structures/ not found - type check skipped")
        return
    bad, cells, sheets = [], 0, 0
    for root in roots:
        for f in sorted(root.rglob("*.csv")):
            rel = f.relative_to(root).as_posix()
            m = re.match(r"(?:data|text|message)/([^/]+)\.mbe/(.+)\.csv$", rel)
            if not m:
                continue
            sfile = sdir / f"{m.group(1)}.json"
            if not sfile.is_file():
                continue
            try:
                spec = json.loads(sfile.read_text(encoding="utf-8")).get(m.group(2))
            except Exception:
                continue
            if spec is None:
                bad.append(f"{rel}: no sheet '{m.group(2)}' in {m.group(1)}.json")
                continue
            sheets += 1
            cols = list(spec.items())
            for ri, r in enumerate(read_csv(f)[1], 1):
                if not r:
                    continue
                if len(r) != len(cols):
                    bad.append(f"{rel} row {ri}: {len(r)} cells, structure declares {len(cols)}")
                    continue
                for (name, typ), raw in zip(cols, r):
                    cells += 1
                    v = raw.strip()
                    if not v or SOFT_START.match(v):
                        continue
                    if typ in INT_LIMITS:
                        if not INT_RE.fullmatch(v):
                            bad.append(f"{rel} row {ri} '{name}' ({typ}): {v!r} is not an integer")
                            continue
                        lo, hi = INT_LIMITS[typ]
                        if not lo <= int(v) <= hi:
                            bad.append(f"{rel} row {ri} '{name}' ({typ}): {v} outside [{lo}, {hi}]")
                    elif typ == "float" and not FLOAT_RE.fullmatch(v):
                        bad.append(f"{rel} row {ri} '{name}' (float): {v!r} is not numeric")
    for b in bad[:12]:
        rep.fail("types", b)
    if len(bad) > 12:
        rep.fail("types", f"...and {len(bad)-12} more type problems")
    if not bad and cells:
        rep.ok("types", f"{cells} cell(s) across {sheets} sheet(s) match their declared type and width")


def check_build_json(mod: Path, roots: list[Path], rep: Report):
    """Any custom-named asset must be renamed by BUILD.json or it installs dead."""
    bp = mod / "BUILD.json"
    build_src = ""
    if bp.is_file():
        try:
            build = json.loads(bp.read_text(encoding="utf-8-sig"))
            build_src = json.dumps(build)
        except Exception as exc:
            rep.fail("build-json", f"BUILD.json does not parse: {exc}")
            return
    orphans = []
    for root in roots:
        if not root.is_dir():
            continue
        for entry in root.iterdir():
            if not entry.is_file() or entry.suffix.lower() not in MODEL_EXT:
                continue
            stem = entry.stem
            # Vanilla-shaped names are addressed directly and need no rename.
            if re.match(r"^(chr|pc|npc|mob|acc|cam|eff|ui|[dt]\d{4})", stem):
                continue
            base = re.split(r"_(?:ba|bb|bd|bg|bn|br|bs|bv|fa|fe|fn|fr|fw|e|ev)\d*", stem)[0]
            base = base.replace("eff_bts_", "").replace("cam_", "")
            if base and base not in build_src:
                orphans.append(entry.name)
    if orphans:
        uniq = sorted({re.split(r"_", o)[0] for o in orphans})
        rep.fail("build-json",
                 f"{len(orphans)} custom-named asset(s) with no BUILD.json rename rule "
                 f"(stems: {', '.join(uniq[:5])}) - they install under their literal name and "
                 "the game never loads them")
    elif bp.is_file():
        rep.ok("build-json", "every custom-named asset is covered by a rename rule")


FUNC = re.compile(r"^\s*function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.M)


def check_scripts(roots: list[Path], db: Path, rep: Report):
    """A script64 .txt is APPENDED to the vanilla source, not diffed against it.

    So the risk is not "how many lines changed" - it is how many vanilla functions the mod
    redefines. Squirrel keeps the last definition, globally, for the rest of the session, so
    every redefined function is a function this mod takes from every other mod.
    """
    import difflib
    clobber_total = {}
    for root in roots:
        d = root / "script64"
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.txt")):
            body = f.read_text(encoding="utf-8", errors="replace")
            n = len(body.splitlines())
            mine = set(FUNC.findall(body))
            van = db / "script64" / f.name
            if not van.is_file():
                rep.ok("script", f"{f.name}: new script, {n} lines, {len(mine)} function(s)")
                continue
            vbody = van.read_text(encoding="utf-8", errors="replace")
            theirs = set(FUNC.findall(vbody))
            clobbered = sorted(mine & theirs)
            if not clobbered:
                rep.ok("script", f"{f.name}: {n} lines, adds {len(mine)} function(s), "
                                 "redefines none")
                continue
            # How much of what it redefines is actually different?
            changed = sum(1 for line in difflib.unified_diff(
                vbody.splitlines(), body.splitlines(), n=0)
                if line[:1] in "+-" and line[:3] not in ("+++", "---"))
            if len(clobbered) > 5 and changed <= 40:
                rep.fail("script-bloat",
                         f"{f.name}: redefines {len(clobbered)} vanilla functions to change "
                         f"~{changed} lines. Every other mod touching any of them loses. "
                         "Use a .sqmod.")
            else:
                clobber_total[f.name] = len(clobbered)
    _summarise_clobber(clobber_total, rep)


def _summarise_clobber(clobber_total, rep):
    if not clobber_total:
        return
    worst = sorted(clobber_total.items(), key=lambda kv: -kv[1])[:3]
    total = sum(clobber_total.values())
    rep.warn("script-clobber",
             f"{len(clobber_total)} script(s) redefine {total} vanilla function(s) in total "
             f"(worst: {', '.join(f'{n} in {k}' for k, n in worst)}) - each becomes global "
             "for the session")


def validate(mod: Path, db: Path, van: dict, quiet: bool) -> Report:
    rep = Report(mod)
    meta = check_metadata(mod, rep)
    roots = archive_roots(mod, meta)
    if not roots:
        rep.fail("layout", "no modfiles/ folder")
        return rep
    seen = check_tables(roots, van, rep)
    check_pairs(seen, rep)
    check_softcodes(mod, rep)
    check_battles(roots, db, van, rep)
    check_variations(roots, rep)
    check_types(roots, rep)
    check_build_json(mod, roots, rep)
    check_scripts(roots, db, rep)
    return rep


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mod", nargs="?", help="path to the mod folder")
    p.add_argument("-g", "--game")
    p.add_argument("--all", action="store_true", help="validate every mod in mod-corpus.csv")
    p.add_argument("--quiet", action="store_true", help="hide PASS lines")
    args = p.parse_args(argv)

    db = find_db(find_game(args.game))
    van = vanilla_index(db)

    if args.all:
        corpus = REPO / "reference" / "mod-corpus.csv"
        mods = [Path(r["path"]) for r in csv.DictReader(corpus.open(encoding="utf-8"))]
    elif args.mod:
        mods = [Path(args.mod)]
    else:
        p.error("give a mod folder, or --all")

    worst = 0
    for m in mods:
        rep = validate(m, db, van, args.quiet)
        noteworthy = any(r[0] != "PASS" for r in rep.rows)
        if noteworthy or not args.quiet:
            print(rep.render(args.quiet))
        worst = max(worst, 1 if rep.failures else 0)
    return worst


if __name__ == "__main__":
    sys.exit(main())
