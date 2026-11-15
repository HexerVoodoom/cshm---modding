# 12 — Thicc bodies: the end-to-end recipe

How the Amy / Ami / NPC / mob / Digimon "thicc" mods were made, what each gate measures, and
what is still unproven. Skirts have their own chapter:
[../reference/pleated-skirts-and-garment-lumps.md](../reference/pleated-skirts-and-garment-lumps.md).
Digimon: [../reference/digimon-thicc.md](../reference/digimon-thicc.md). Costume slots:
[../reference/wardrobe-and-costumes.md](../reference/wardrobe-and-costumes.md).
The shorter proportions summary is `reference/model-edit-patterns.md` (sections 1-5); this
chapter is the procedure and does not repeat its tables.

**In-game status (read first).** Nothing here is verified in game except: the user called
*Amy Thicc* "otimo", and the user hand-corrected *Amy Even Thicker v1.1* in Blender (the
corrections are measured in `AMY_THICC/notes/learned_from_user_fix.md`). Every other number
is a measurement of a file, not of how it looks in game. Rows marked UNVERIFIED stay so until
the user reports.

Workspaces: `E:/DIGIMON MODS/AMY_THICC/` (frozen; Amy tools) and
`E:/DIGIMON MODS/NPC_THICC/` (everything else; index in its `README.md`).

## 1. Model families

| Family | Stems | Skeleton / layers | Source |
|---|---|---|---|
| Amy (player, Ami in code) | `pc002` | 81 bones, 9 meshes, no breast bones | `AMY_THICC/notes/inspection.md` |
| Ami costumes | `pc006 pc008 pc010 pc201-pc242` (pc236 held back) | 81 bones, shared body | `NPC_THICC/notes/female_all.md`, `tools/pack_mid.py` |
| Adult female NPCs | `npc002 003 006 008 012 013 014 015 019` (+`037` in Mid) | 68-80 bones; only `npc006`, `npc008` have `l_/r_breast` | `notes/female_npcs.md` |
| Female mobs | `mob004 018 028 029 030 032 033 038 041 042 043 056 063 066 067 069 070 115` | 31-33 bones (generic), no breast bones, materials `mobNNNface/body_01/skin_01/spec_01` + `MTR_line` | `notes/female_all.md` |
| Female Digimon | 18 shipped `chr` | 7 rig dialects | [digimon-thicc.md](../reference/digimon-thicc.md) |

Name correction (2026-10-05, `NPC_THICC/notes/erika_identification.md`): **npc019 is not
Erika.** Identification by speaker/model join: `npc012` Fei Wong (3012), `npc013` Mirei
Mikagura (3013), `npc015` Makiko Date (3015) are CONFIRMED; `npc019` is probably Reiko Tawa
(4060, MEDIUM confidence); Erika Mishima (3045) is `npc025` (HIGH; alternates `npc032`,
`npc031` pajamas, `npc029`). `npc018` is probably a young Mirei/Sayo flashback model (MEDIUM).
`notes/female_npcs.md/csv`, `female_all.*` and the pack METADATA still carry the old guesses;
they are not edited here. **Erika's stems `npc025`, `npc031`, `npc032` are in `NPC Mid Pack`
(files and METADATA, QA round 1); `npc029` is not built** (seated model, 122-bone rig, the
Mid chain is unusable on it).

### Identifying an NPC stem (method)

No data table maps a model stem to a name (`field_npc_para` gives `npc_NNNN -> model` only).
The method that worked: in `script64`, join every `Talk.Load("<message>")` -> the speaker-id
column of `message/<message>.mbe` against the `Talk.LoadModel(slot,"<stem>",..)` calls in the
same script, over the whole corpus; the stem's top speaker is its character. Names:
`text/charname.mbe`, ids 3xxx/4xxx. Speaker 2000/2001/2020 is the player; ignore. A stem with
no speaker of its own (npc032) can only be identified by its render. Worked example and
counts: `NPC_THICC/notes/erika_identification.md`. Never name a stem from a render alone.

## 2. Tiers and calibrated targets

Four tiers exist in code. Targets are millimetres **per metre of hip-joint height** (`/H`),
measured with the same metric definitions on the Time Stranger reference
(`NPC_THICC/notes/ts_reference/calibration.md`, `table.md`, `metrics.json`, `measure.py`).

| Tier | Meaning | Pack |
|---|---|---|
| Thicker | gentle lift, about TS Thicker on hip width and bust | `Amy Thicc`, `NPC Thicker Pack` |
| Mid | midpoint of the two measured tiers of the same model | `Amy Mid Thicker`, `NPC Mid Pack`, `Ami Costumes Mid`, `Digimon Mid Pack` |
| Even Thicker | TS **EvenThicker** level (retune of 2026-10) | `Amy Even Thicker` v1.2, `NPC Even Thicker Pack` |
| Extra | the OLD Even = TS **Extra Thicc** level, kept as tier `extra` | not shipped (`params/*_extra.json`, `work/extra_keep/`) |

What "Even Thicker" really is. `calibration.md` measured Amy Even v1.2 and Kyoko Even against
the TS ladder: hip half-width +73-75 mm vs TS Extra +70, bust forward 74-99 vs 96; that is
2.5-3x TS EvenThicker on hip width and 2-3x on bust. The first CSHM "Even Thicker" was
therefore TS Extra Thicc. It was kept as tier `extra` and Even was retuned (`notes/pipeline.md`).
Two EvenThicker Inori sources differ a lot (TS Even zip hip rear +107 mm vs the family file
+38.5 mm, because the zip's skirt flares back); the **family file** (the Even Thicker the
user's family ships, 12 meshes) was chosen as the target, `calibration.md`.

Even targets (mm per metre of hip height; `notes/pipeline.md`): hip half-width 28.4, hip rear 48
(TS fam 42.8, peak 56), thigh t.55 half-width 30.6 and rear 28.7, calf half-width 3.0 and rear
16.8, bust forward 42 (35-48), cleavage forward 18 (15-23), thigh gap at t.55 about 3.6 mm,
narrowest waist -6 %. Thicker targets (TS Thicker /H): hip hw 21.9, hip rear 61.1, thigh hw
30.2, calf hw 4.9, bust forward 23.7, cleavage 11.0 (`table.md`). Mid starts at the midpoint and
for a straight skirt uses the skirt preset (see the skirt chapter).

Known limits recorded with the targets: calf half-width cannot go below about 3.8/H (calf rear
gain leaks sideways); where a garment hangs over skin the garment >= skin floor sets the hip
width (Kyoko 37/H at floor 1.0, 29/H at floor 0.78).

## 3. The displacement-field method

One function of the ORIGINAL position, summed from terms; no per-vertex edits. Files:
Amy `AMY_THICC/tools/field.py` (frozen), generalised `NPC_THICC/tools/npcfield.py`; Mid
variants `skirt_field.py` (= `mid2_field.py`; they differ only in CRLF line endings, `diff --strip-trailing-cr` is empty), `dgm_field.py` for Digimon.

1. **Landmarks from the bind pose**: hip, knee, foot, root, spine02, neck, arm, leg x, breast
   bones; stature scale = hip_y / 0.888; mesh roles (face/hair/skin/outline/garment) from material
   tokens (`npc_params.py`). Amy's numbers: hip 0.9233, knee 0.5247, root 1.1052
   (`inspection.md`).
2. **Terms**: pelvis (hip/glute, DSTS `PELVIS_BASE`/`PELVIS_REAR` profiles, rear lobe peaks above
   the hip joint), thigh out/front/back/in, calf, bust, waist cinch.
3. **Inner thigh**: pull the inner faces toward the midline, peak ~11 mm at t 0.5-0.6, 0 at the
   knee side; near-touch (3-6 mm per leg, never < ~2 mm) at t ~0.55; a clamp stops any vertex
   moving toward x=0 past the vanilla inner-face |x|. Source: user fix, `learned_from_user_fix.md` s1.
4. **Rounded dome bust**: spread the dome sideways (x' ~ 1.57 x, ramped), lower the centre 25-40
   mm, do not push further forward; horizontal radius of curvature >= ~100 mm (v1.1 cone 43 mm,
   user 107, vanilla 98). `learned_from_user_fix.md` s3. Without breast bones the bust centre is
   spine02 + 0.29 x (neck - spine02), x = 0.9 x leg_x.
5. **Front of the pelvis stays near vanilla** (the user removed ~85 % of a +28 mm front growth):
   grow rear and sides. `learned_from_user_fix.md` s2.
6. **Slight waist cinch** from Even up (memory `dsts-waist-cinch-preference`). The bust spread in
   Amy v1.2 removed the cinch (narrowest point +7 mm over vanilla); the user's own edit does the
   same, so it was left. TS tiers cinch about -10.5 %; ours -2..-6 %. Do not chase TS: a tuner
   cinch of 2.72 pinched `npc012`'s jacket to -14.9 % (wasp waist); hand-lowered to 1.3
   (`notes/npc012_judgement.md`).
7. **Garment >= skin floor**: where cloth hangs over skin, garment growth is at least the skin's
   (exact radius grid, 24 sectors, 3x3 dilation). Only if the model has skin in the hip zone;
   `npc003`, `npc012`, `npc013` have none (floor off, holds by construction via `r_eff`).
8. **Freezes**: ceiling = min(neck - 0.035 s, face min y); face/spec/hair/lens meshes move 0.0 mm;
   Amy: every vertex above y 1.376 within 0.07 mm of vanilla. Hair/hood/cap/wings: Amy hair min y
   1.424 is above the ceiling; on Digimon, rigid/cloth weight rules
   ([digimon-thicc.md](../reference/digimon-thicc.md)). A ceiling too close to the bust leaks: `npc013`
   face ceiling 1.331 is 5.2 cm above the bust centre 1.279, the dome leaked 0.9-4 mm until
   `bust_centre y` and `bust_ax y` were lowered (`notes/grpq_npc013_014_015_019.md`).
9. **Tuning**: `npc_params.py STEM even` runs `tune_even` (6-10 min): per-metric gains, up to 8
   iterations to within 8 %, one cinch-only secant; history in `params/STEM_even.json`
   ("tuning"). Hand edits go in `params/STEM_override.json` or a `skipparams` marker file so
   `run_model.sh` does not retune (used on npc002, npc012, npc013, npc015 Even).

## 4. Subdivision, weights, normals

- Coarse vanilla lower bodies (median edge 47-52 mm at thigh/hip/waist, `model-edit-patterns.md` s2)
  facet when deformed: subdivide first. Amy Thicker `SUB_LEN 0.050 m, 2 passes`; Even `0.036 m, 3
  passes`; Mid npc `0.036`; skirts `0.028-0.044` (see skirt chapter: finer is not smoother).
  Identical rule on the outline meshes.
- New-vertex weights = mean of the endpoints, capped to the mesh's vanilla influence count,
  normalised. Gate: sums 0.9997-1.0003, max influences and group counts unchanged.
- Budget: ~10k verts per mesh, ~15k per model. Amy Even v1.2 is 16,964 (shipped geom, `qa/geomqa.json`; the user's hand-fix v1.1 is 16,755; 16,724 is the older
  report figure; over budget, chosen over finer subdivision which gave 18.0k).
- **Normals are the dominant visible defect**; see the skirt chapter, section "Normals". Short
  form: build with `NORMALS_FIX=1`; count with `tools/normals_loopcount.py`.

## 5. The gates, and what each really measures

`npc_verify.py STEM TIER BUILT` (Mid: `mid2_verify.py`, Digimon: `dgm_verify.py`) prints
`FAILS: none` when clean. Each gate:

| Gate | Measures | Caveat found |
|---|---|---|
| budget | verts per mesh | a plain re-export already merges duplicate verts (Amy 15,194 -> 11,159 with no edit) |
| displacement per role | built verts vs vanilla *surface*; face/hair > 0.6 mm fails; above ceiling | surface sampler reads midpoints of big hair triangles as "moved" (mob038 note) |
| weights | sum, influences, group count | exporter merges coincident verts: mob038 loses group 5 with no field at all (`work/mob038_ctrl`) |
| flips, texel stretch | 3D area post/pre (UVs unchanged = texel stretch), symmetry of the field | texture stretched median +26 % in grown bands |
| silhouette | half-width/rear/front at landmark heights | hip rows are dominated by the skirt on skirted models |
| thigh gap | min |x| of leg layers | unmeasurable when a skirt/apron/robe covers the legs: measure on skin meshes only |
| garment-over-skin clearance | per 24 sectors, only sectors covered in vanilla | fails when built min < vanilla min; Digimon/free-garment variant fails only if < vanilla **and** < 20 mm (`dgm_verify.py`) |
| calibration metrics | the /H table above | field-only measure and built geom disagree up to 7 mm at the hip when the floor is active (`mid_needs_shared_fix.md` s4) |

Metrics that lied or mislead:
- Face-level normal counter (`normals_facecount.py`) is blind to single flipped corners; the loop
  counter (`normals_loopcount.py`) is the one that separates field-flipped normals from export noise.
- Vertex-raw NN mirror metric (Amy mesh1 max 33.6 mm vs vanilla 26.1) reflects vanilla's
  asymmetric triangulation, not the field; use displacement asymmetry between mirrored ORIGINAL
  positions (0.62 mm).
- Front-strap metric -55 -> -171 mm compares straps under the dress with the front-most dress
  vertex; the dress moved forward. The user's own edit gives -175.
- Outline-inside-body counts are not a defect marker (the shell sits on the surface by design).
- "Before/after diff" of a global transform: diff against the intended transform instead.

## 6. Packaging rules (all measured on this machine)

- **Real vanilla `.name/.skel/.anim` next to the new `.geom`, no `.request` files**:
  `Amy Even Thicker v1.2 (generated)` ships vanilla copies byte-identical (`cmp`); the installed
  hand-fix `Amy Even Thicker` (v1.1) does not: its `.skel`/`.anim` are regenerated by the user's
  Blender export (QA round 1). The first Amy report shipped
  empty `.request` stubs and no vanilla files; the later packs and `AMY_THICC/notes/report_even_thicker.md`
  switched. `pack_mid.py` copies and `cmp`-checks them. (Why not `.request`: `packaging.md` (a).)
- Plain overwrite of the stem: flat in `modfiles/`, no `BUILD.json` (`packaging.md` (a), (c)).
- Exporter non-determinism: re-importing and re-exporting gives `.skel` differing by float noise
  and `.anim` by 1 byte (`report.md`), so a mod's `.geom` is reproducible only to the vertex
  distance: rebuild and compare with the gate "moved only in the intended bands"
  (`geom_diff.py`). Byte identity was achieved only for Amy Thicker re-run with `TIER` unset
  (`report_even_thicker.md`).
- **Mutually exclusive mods**: any two mods writing the same stem conflict; the order in SDMM
  decides. Amy Thicc / Mid / Even all write `pc002.*`; NPC Thicker / Even / Mid packs share npc
  stems; NPC Mid also writes the mob stems and `Digimon Mid Pack` the `chr` stems. Enable one per stem.
  `Kyoko`, `nokia ... pc`, `Playable Rina` also write `pc002`.
- **SDMM rereads its mods folder only on restart** (memory `cshm-amy-thicc-mod`): copy, restart
  SDMM, tick, Save/Build.
- **Item id collisions** (wardrobe mods): see the wardrobe reference.
- `python tools/validate_mod.py "<mod>"` before telling anyone it is done.
- `pc002` is **Amy** (Ami protagonist column), pc020 is Keisuke; see
  [wardrobe-and-costumes.md](../reference/wardrobe-and-costumes.md).

## 7. QA flow per stem

`bash tools/run_model.sh STEM TIER` (params+tune, build, verify, render ~25-30 min) ->
`b_reimport_npc.py` (bones identical, same frame, materials/name_hash identical) ->
`b_pose_npc.py` (arms down 65 deg; `stride` = leg forward) -> render montage -> `npc_package.py`
or `pack_mid.py` (ships a stem only if its verify file reads `FAILS: none` or every item is in
the `ALLOW` list with a reason; `HOLD` list: `pc236` material table 11->13 after export, `chr773`
29.4k verts). Then `cshm-qa`. Blender 2.83 headless only.

## 8. The mod set and where everything is

| Mod (folder) | Contents | Installed in SDMM mods |
|---|---|---|
| `AMY_THICC/mod/Amy Thicc` | pc002 Thicker; frozen; the user's "otimo" | yes |
| `AMY_THICC/mod/Amy Mid Thicker` v1.0 | pc002 Mid (no report file read; metadata only) | yes |
| `AMY_THICC/mod/Amy Even Thicker` v1.2 | pc002 Even, generated, 16,964 verts | installed as `Amy Even Thicker v1.2 (generated)` |
| (no E: source) `Amy Even Thicker` v1.1 | the user's hand-fixed geom, 713,084 B, `.skel`/`.anim` regenerated by his Blender export, plus an `images/` folder | yes, this is the folder named `Amy Even Thicker` in `<game>/SimpleDSCSModManager/mods` |
| `NPC_THICC/mod/NPC Thicker Pack` | 9 npc stems | yes |
| `NPC_THICC/mod/NPC Even Thicker Pack` | same 9 stems | yes |
| `NPC_THICC/mod/NPC Mid Pack` | 13 npc stems (npc025 031 032 002 003 006 008 012 013 014 015 019 037) + 18 mobs = 31 | yes |
| `NPC_THICC/mod/Ami Costumes Mid` | 44 pc stems (pc201-235, 237-242, 006, 008, 010) | yes |
| `NPC_THICC/mod/Digimon Mid Pack` | 18 `chr` stems (no chr773) | yes |
| `NPC_THICC/mod/NPC Wardrobe`, `TEST-A`, `TEST-B` | 9 test costume rows | yes (did not work, see wardrobe) |

All are UNVERIFIED in game except Amy Thicc. Source of lists: each folder's `METADATA.json`.

### Installing and the SDMM state (QA round 1, 2026-10-05, `NPC_THICC/qa/qa_round1.md`)

- Enabled mods live in `SimpleDSCSModManager/profiles/*.profile` (0 off, 2 on), **not** in
  `config/config.json` (game path and language only). A mod absent from the profile is not
  built even if its folder is installed.
- A mod is in no archive until **Save/Build**; copying the folder is not installing it.
- `INDEX.json` appears inside a mod folder only after SDMM has read it; no `INDEX.json` = SDMM never saw it.
- `E:` free space must be >= 1 GB before building. QA found E: at 0 bytes: a build or copy there fails or truncates.
- On 2026-10-05 `resources/DSDBP.steam.mvgl` (built 2026-10-04 13:24) held only the 9 old NPC
  stems (npc002 003 006 008 012 013 014 015 019); `pc002`, `mob004`, `chr148` were absent. The
  NPC pack files were rewritten 17:46 after that build, so even those may be older bytes.
  Rebuild after any file change.

## 9. What is NOT done

Bust changes on approved models: read [../reference/bust-iterations-postmortem.md](../reference/bust-iterations-postmortem.md) first; approvals live in `NPC_THICC/qa/approved_registry.md`.

| Gap | Consequence |
|---|---|
| `npc029` (Erika alternate) not built: seated model, unusable chain | stays vanilla; `npc025/031/032` are in NPC Mid Pack |
| `mob014`, `mob113` not shipped (listed "ready" in `female_all.md`). Reason: maxi skirts to the ankle; the field is not designed for a hem that low and the barrel would be worse. This was the pilot agent's judgment from survey images, never tried: **judgement, untried** | they stay vanilla |
| `mob031` stopped: its material is named `mob029face` but is the exposed-skin mesh, so the role heuristic fails; the field moved nothing in round 1; after overriding the role the calves came out +168 % and the clearance gate failed | stays vanilla |
| Amy Even hand-fix (the user's own geom) still has flipped normals: mesh 1 0 -> 22, mesh 8 0 -> 35 corners (`qa/geomqa.json`) | possible dark patches; the repair is an optional step, see the skirt chapter section 1 |
| `pc236`, `chr773` held back by `pack_mid.py` | vanilla in game |
| Thicker/Even tiers for mobs, Ami costumes, Digimon | only Mid exists |
| In-game look of Mid and Even | unknown; Even was reached from the TS ladder, not from the user's eye |
| Amy Even v1.2 (generated) not seen by the user; waist cinch removed by bust spread | may conflict with the cinch preference |
| Shaders, outline shell, animation playback, shared `pc002` anims for pc004/006/008/010 | unverified |
| npc stems as wardrobe skins | not proven to work |

## 10. Tool inventory (`NPC_THICC/tools`)

Standard path now: `npc_params.py`, `npcfield.py`, `b_build_npc.py` (+`NORMALS_FIX`),
`npc_verify.py`, `npc_measure.py`, `run_model.sh` (Thicker/Even); Mid: `mid2_*`, `skirt_*`,
`grpq_*`, `g5_*`, `capsh2_*`, `mobgrp_*`, `skgrp_*`, `ami2_*`, `pack_mid.py`; Digimon: `dgm_*`,
`b_build_dgm.py`, `sis_*`, per-stem `g773_*`, `g779_*`. Which skirt builder for which group:
skirt chapter. Superseded: `ami_build*.py`, `ami_v2/v3.sh`, `capsh_*` (before `capsh2`),
`b_build_mid_npc.py` + `npcfield_mid.py` (npc008 only), per-stem `npc015_*`/`npc019_*` (kept for
their normals fix, now folded into `grpq_build.py`).

**Prefix-collision incident.** Parallel agents reused the `g3_*` prefix and overwrote each
other's scripts: `tools/g3_batch.sh` still calls `tools/g3_run.sh`, which no longer exists.
Rule: one unique prefix per agent/run, never reuse another's; a batch script that calls
another script must be checked with `ls` before it is trusted. Shared files must not be edited
while models run (`notes/pipeline.md`).
