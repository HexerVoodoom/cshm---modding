# What transfers from the Time Stranger guide, and what does not

Both games are Media.Vision engine titles. SydMontague's MVGLTools handles both
(`--game dscs` vs `--game dsts`). That similarity is a trap as often as it is a shortcut.

## Transfers

- **Concept of the `.mbe` table** — a container of sheets of fixed-schema records.
- **The model split** — `.name` / `.skel` / `.geom` / `.anim` as four files sharing a stem.
- **Column indices are the API** mindset: inserting a column shifts everything after it.
- **Never open a game CSV in Excel.**
- **ID cross-references are hardcoded** and a dangling reference fails silently.

## Does NOT transfer

| Thing | Time Stranger | Cyber Sleuth |
|---|---|---|
| Mod loader | Reloaded II + DSTS Mod Loader | SimpleDSCSModManager (+ `DSCSModLoader.dll` for `.mvgl` mods) |
| Mod format | Reloaded mod folder + `ModConfig.json` | `modfiles/` + `METADATA.json` |
| How a mod ships data | Loose files the loader overlays | SDMM re-packs `DSDBP.steam.mvgl` |
| Table columns | **Unnamed** — index only; `tools/columns.py` maps them | **Named** — DSCSTools `structure.json` gives a real header row |
| Merging | Manual | SDMM record rules (`mberecord_merge` etc.) |
| New IDs | Pick one | **Softcodes** — let SDMM assign it |
| Scripting | Lua | Squirrel 2.2.4 (compiled; NutCracker decompiles) |
| Textures | `.img` | `.img` (DDS) — but the DSTS swizzle/format table is unverified here |

**`../dsts-modding/tools/mbe.py` is not known to read DSCS `.mbe` files** and you should not
assume it does. On this workspace the DSCS tables are already unpacked to CSV by SDMM, so
you rarely need a binary reader at all. If you do, use MVGLTools or DSCSTools, which carry
the `structures/` folder that defines each table's field types.
