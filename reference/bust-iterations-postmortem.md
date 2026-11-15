# Bust iterations, 2026-10-13/14: post-mortem and rules

Who reads this: anyone about to change a body part the user has already approved. Read section 3 before
touching a geom. Sources: user verdicts as relayed in the session; scripts `NPC_THICC/tools/bust{2..6}_*`;
renders and metrics `NPC_THICC/qa/bust*`; memory note `cshm-thicc-packs` (bust SHAPE rule). The user's
verdicts are quotes from chat, not from a file; nothing in the repo records them except the registry
created with this document (`NPC_THICC/qa/approved_registry.md`).

## 1. What happened

Start state: the FIRST Mid tier (single version halfway between Thicker and Even Thicker; bust forward
about 32 mm per metre of hip height) was tested in game: "quase tudo perfeito". Only asked change: the bust
"levemente maior e mais arredondado" on most NPCs. Frozen copies of that state:
`NPC_THICC/work/<stem>_mid_prebust/*.geom` (10 stems, md5 in the registry). Superseded as the base for
Kyoko and Rina: the approved files are `qa/approved_frozen/npc006|npc014.first_mid_ofix.approved.geom`
(with the outline fix); the prebust copies lack it.

| Version | What changed | Numbers | User verdict | Why it failed |
|---|---|---|---|---|
| bust2 (`tools/bust2_*`) | `bust_ax` x1.3, one size step up, dx/dz ratio 3.0 | targets 38 mm fwd / 17.5 cleavage | "horrible", flat seen from the side, "bolachas deitadas" | Ratio 3.0 spread the bust sideways 3x the forward gain: a disc. Its own V/P metric said "not flatter than vanilla", so the metric passed a rejected shape. |
| bust3 (`tools/bust3_*`, `qa/bust3_side_montage.png`) | uniform 3D scaling about each breast centre, with gates for groove / armpit / underbust / top | front-view W/H only 0.61-0.84 | "most almost good, but flattened on the other axis, bolachas em pe" | The gates clipped the lateral extent, so the growth was forward and vertical only: a standing disc. |
| bust4 (`tools/bust4_*`, `qa/bust4_metrics.json`) | isotropic circular spherical-cap lift | W/H 0.90-1.06 | "nao esta ficando bom; a anterior estava quase boa" | Metric target met, look rejected. Replaced the shape instead of growing the approved one. |
| bust5 (`tools/bust5_*`, `qa/bust5_metrics.json`) | bust3 + lateral widening, 3 variants w090/w100/w110 on Kyoko (npc006) and Rina (npc014); vertical squeeze `ky` to reach W/H 1.0 | W/H 1.0 | Rina w110 "muito bom"; Kyoko w110 "reto por baixo" | Found the geometry limit: the torso edge at bust height is about 120 mm, so front W can only reach 120-136 mm. Good on a body that already fits, bad on one that does not. |
| bust6 (`tools/bust6_*`, `qa/bust6_metrics.json`) | Kyoko lower round arc m1/m2/m3 | per `qa/bust6_*` | "ficou bem ruim" | A fix for one model's underside, invented without a target example. |

**Final decision:** go back to the FIRST Mid bust ("apesar de ter engrossado pouco, tinha ficado
excelente"); later try +10% size increments from it. Open item in `guide/09-open-questions.md`.

Bust episodes that went well, and why (use as the pattern): Erika bigger bust v2 (approved), Valkyrimon
chr773 (apex located by a RULER RENDER on the vanilla surface, two domes plus groove; approved), Mastemon
chr748 wider front-view bust (approved), Rina w110 (approved as a shape example). Each was one model, one
named change, judged by looking.

## 2. Root causes (process, not geometry)

a. **Many changes at once, drifting from the baseline.** "Levemente" (slightly) was asked; +20-40% size and
   a new shape were delivered, each version built on the last rejected one instead of on the approved one.
b. **Metrics did not measure what the user saw.** Forward projection, front half-width, silhouette V/P and
   circle fits Rx/Ry are single-axis numbers. The user judges side AND front together. "Targets met" was
   reported next to a rejected render, three times. See also `port-metrics-that-lie` in the memory index:
   a metric must be checked against a case the user has already judged.
c. **No frozen reference of the approved look next to each candidate.** The comparison was candidate vs
   vanilla, so a drift away from the approved bust was invisible.
d. **The user's words were mapped to one axis at a time.** "deitada" then "em pe" produced an oscillation
   between two flat shapes. Both words describe the same missing thing: a round 3D cap. The constraint that
   limits front width (torso edge about 120 mm) was found only in bust5.
e. **Unapproved variants were installed over the approved pack.** bust2, bust3 and bust4 builds reached the
   user's game. The packs in `NPC_THICC/mod/*` had files rewritten on 2026-10-14 14:36 and several stems no
   longer match the first-Mid md5 (registry: npc006 876fb675..., npc014 eb1e4445..., against 829126dd...,
   65eec179... in `work/*_prebust`). What finally worked: Kyoko + Rina as a two-character pilot.
f. **Wasted agent time.** About 9 agent runs (bust2 to bust6, plus their render/montage batches) ended in a
   rollback. Count taken from the caller; the repo has no run log for them.

## 3. Rules: before changing an approved body part

1. **Freeze.** Copy the approved geom, record md5, the user's verdict and the date in
   `NPC_THICC/qa/approved_registry.md`. Without a row there, a version is not approved.
2. **One parameter, one small step** (+10% size). Everything else bit-identical to the frozen file. Verify:
   vertices outside the bust region move by 0.0 mm.
3. **Render side by side with the frozen version**, same camera: front, side, 3/4 and horizontal slices.
   Show these before reporting any number.
4. **Ask for a target example** (a model he likes, e.g. Rina w110) and measure shape descriptors on THAT
   model; do not invent metrics. A metric is allowed only if it ranks the user's approved and rejected
   builds the way he did.
5. **Pilot on 1-2 characters**; show the pilot; fan out only after a yes.
6. **Install = approved only.** Never put an unapproved variant over an approved one. Variants go in a
   separate, toggled mod folder or to 1-2 characters.
7. **Record each verdict in the registry immediately**, with the quote.
8. When the user's word is ambiguous ("deitada"), write down both readings and render both before building.
9. After a rejected try, go back to the frozen file, not to the last candidate.

## 4. Process lessons of the whole thicc project

Only items verified in repo docs or memory notes; the source is named.

- **Prefix collision.** Parallel agents reused `g3_*` and overwrote each other's scripts
  (`guide/12-thicc-bodies.md` section 10). Rule: one unique prefix per agent/run; `ls` a called script first.
- **Gates that passed on broken output.** Black diamonds, lattice and barrel skirts passed every numeric
  gate for hours; only renders showed them (`reference/pleated-skirts-and-garment-lumps.md`). Rule: look
  at close-ups after every build.
- **Counter blind to the defect.** The face-level normals counter cannot see single flipped corners; the
  loop counter can (`guide/12-thicc-bodies.md` section 5). Rule: run a new gate on a known-bad control.
- **A fix that did nothing.** `skirt_build.py` ignores `GN_ALL`, so the early `GN_ALL=0` fix changed
  nothing. Rule: confirm a switch is read by the script before relying on it.
- **Stale builds.** QA round 1 found pack files newer than the SDMM build (mtime 17:46 vs INDEX 12:35 / 13:24)
  and stems NOT built (`qa/qa_round1.md`). Rule: Save/Build after any file change; compare mtimes.
- **QA on a different build than shipped.** QA round 1 compared shipped files against E: sources for this
  reason; the Amy Even hand-fix differs from its source by design. Rule: QA reads the file in the pack, not
  the work folder.
- **Disk full.** E: at 0 bytes truncated builds (`qa/qa_round1.md`); work and renders were moved to
  `D:/digimon-work/NPC_THICC` behind junctions. Rule: 1 GB free on E: before every build.
- **Hold decisions never tried.** `mob014`/`mob113` were held on a survey-image judgement and never built
  (`guide/12-thicc-bodies.md` section 9). Rule: label a hold "judgement, untried" or try it once.
- **Wrong identification from renders.** npc019 was taken for Erika from low-res renders; the script join
  proved otherwise (`cshm-npc-identification`). Rule: identify by data, then by render.
- **The user is the only gate for look.** Amy Thicc is the only mod he has approved in game as a whole;
  the rest are unverified (`guide/12-thicc-bodies.md` section 8).
- **NOT verified in any file I could read** (kept out of the rules): the `split()` bug on paths with spaces
  that packaged the wrong geoms, a QA montage rendered from a different build than shipped (beyond the
  round-1 comparison above), a vacuous UV audit, packaging gates that skipped, agent usage-limit
  interruptions. If they happened, the owner of those runs should add file and command.

## 5. What is NOT done

- ~~No +10% step has been tried~~ — done 2026-10-18: a +5/+10/+15 % pilot on Kyoko and Rina
  (`qa/bust7_kyoko_rina.png`, `work/<stem>_mid_s05|s10|s15_ofix`) was shown and the user kept the approved
  bust ("Mantém o approved"; `qa/approved_registry.md`, Decision 2026-10-18). Do not re-run it unasked.
- The packs in `NPC_THICC/mod/NPC Mid Pack` do not currently hold the first-Mid geoms for npc006 and npc014
  (md5 differs from `work/*_prebust`). Restoring them is not done by this document.
- The user's verdict quotes come from the session, not a log file.


## Process lessons witnessed in the session (added by the coordinator, 2026-10-14)

These are first-hand events of the 2026-10-05..14 session; they are not recorded in any other file.

1. **A `split()` on whitespace silently packaged the wrong geoms.** `ofix_final_sources.txt` lines start with a path that contains a space (`E:/DIGIMON MODS/...`). pack_mid.py parsed it with `split()`, found zero entries and packaged the plain `work/<stem>_mid` geoms (without the outline fix) while the printed summary said '35 shipped'. Only a verification pass (compare pack md5s against the list, got 0 equal) caught it. Rule: parse paths with a regex up to `.geom`, and ALWAYS cross-check what was packaged against its declared source (md5), not against the summary line.
2. **QA renders came from a different build than the shipped one.** The first visual QA used the default `<stem>_mid_montage.png`, which some agents had not regenerated after a later rebuild. Rule: render the montage directly from the packed geom and assert its md5 (qa/shipped_montages/INDEX.md).
3. **A vacuous check passed.** The UV audit of the first QA 'checked' UVs on a vertex dict with no UV key. Rule: every check needs a control that can fail (a deliberately broken input).
4. **A face-level normals counter was blind** to the flipped-normal defect that the corner counter found; the black diamonds survived every gate for hours.
5. **Judgement holds were never tried.** mob014/mob113 (maxi skirts) and chr359/chr703 were excluded by assumption; when finally tried, mob014/mob113 worked. Rule: try before excluding, and record 'untried' as untried.
6. **E: filled to 100% while agents were building** (Windows pagefile growth on E: + 13 concurrent Blenders). Rule: stage temp on D:, keep >= 1 GB free on E: before an SDMM build, do not run more than ~7 Blender agents at once.
7. **Usage limits and an org access error cut agents mid-run** (no completion record). Rule: on resume, inspect the disk for partial outputs before trusting a stopped agent's last state (the stale 'FAILS' list of npc029 was out of date).
8. **An agent overwrote another agent's prefixed scripts** (g3_*). Rule: one unique prefix per agent, never reuse another's.
