# 11 — Scripted content: NPCs, dialogue, battles

Tables decide what exists. **Scripts decide what happens.** Everything in this file is
reconstructed from working mods on this machine — the file-by-file dissections are in
[../reference/mod-patterns.md](../reference/mod-patterns.md).

Read [06-scripts.md](06-scripts.md) first for the `.txt` vs `.sqmod` decision and the
root-table scoping trap.

## The one naming rule

The game calls a Squirrel function named **`<mapId>_<npcBoneName>`** when the player
interacts with that NPC. `t3001_npc_0008`. No table points at the script; the *name* is the
hook. Get it wrong and the NPC is mute with no error.

The bone name comes from the NPC softcode's `bone_name()` method, which pads the ID to four
digits and prefixes `npc_`.

## Adding an NPC — the four things it needs

1. **A place to stand.** A `.mdledit` file editing the map's `p` (position) model:

   ```json
   { "editNPC": { "id": [Town_CS::t30|SubArea::t3001|NPC::mynpc],
                  "position": [3, -0.3, 5], "rotation": [1, 0, 0, 0], "scale": [1, 1, 1] } }
   ```

   Rotation is a quaternion in **WXYZ** order — **not Euler degrees**. SDMM asserts only
   that it is a 4-element list, so `[90, 0, 0, 0]` is accepted, written into the skeleton,
   and is a quaternion of magnitude 90; a conversion that does not normalise scales by
   |q|². Use the identity `[1, 0, 0, 0]` and set the facing with `field_npc_para`'s own
   `rotation` column. Of the 43 `.mdledit` rotations on this machine, 32 are the identity
   and every outlier was one mod writing degrees. `tools/validate_mod.py` now fails on a
   non-unit quaternion.

   **The `model` cell is not renamed by `BUILD.json`.** If your NPC uses a model your mod
   adds, the cell must carry the softcode — `[Digimon::MyMon::filename()]`, not the stem
   you named the file. `BUILD.json` renames files; cell contents are yours to get right,
   and `model` is a string column so a wrong stem is legal and silent.

   SDMM expands one `.mdledit` into four edits (`mdledit_name/skel/geom/anim`) and appends
   the `npc_NNNN` bone if the skeleton lacks it, so you do not have to add it yourself. If
   the map has a `.phys`, `.request` it rather than shipping a copy.

   **Do not guess the coordinates.** The map's `p` model already tells you every valid spot:
   `<map>p.name` lists the locators (`start_NN` player spawns, `npc_NNNN` NPC slots,
   `obj_gk_NNNN` objects, `ragdoll_evt_NNNN`) and `<map>p.skel` holds their rest positions —
   records of 12 floats with the position at offset +9. Read them, then place your NPC at, or
   mirrored from, a vanilla `npc_` locator and check its clearance from every `obj_gk_`. Rooms
   are typically symmetric, so a reflected NPC position is proven ground.

2. **A definition.** A row in `data/field_npc_para<_add>.mbe/<mapId>.csv` — **one sheet per
   map**. The columns that matter: `id` (the softcode), `name1` (the **bone name**), `model`
   (any `chr`/`mob`/`npc`/`pc` stem), `variation`, `pose`, `rotation`, `actionIcon`,
   `interactable`, `interactionRange`.

3. **Words.** A new `message/<yourmod>npc.mbe/Sheet1.csv` with columns
   `ID, Speaker, Unknown1, English, Chinese, …`. `Speaker` is a `[Speakers::Key]` softcode,
   and the same key needs a row in `text/charname` to get a display name.

4. **Behaviour.** A `script64/<mapId>.txt` defining `<mapId>_<boneName>()`.

## The dialogue vocabulary

```squirrel
this.Talk.Load("mod_mynpc");                 // your message table, by name
this.Talk.SetMode(1);
this.Message(1000);                          // a row ID in that table
this.Message(this.Math.Rand(1000, 1004));    // a random greeting
this.MessageClose();
this.TalkExit();
```

Every message that declares a variable **must** have it filled or the game hard-crashes.

### A choice menu

Two tables plus a polling loop. `data/multi_select_para.mbe/para.csv` gives the structure —
`entryID, questionID, initialOption, unknown, ans1, ans1Enabled, … ans6, ans6Enabled`, with
`-1`/`0` for unused slots — and `text/multi_select_text` supplies the strings for the
question ID and every answer ID.

```squirrel
this.Window.OpenMultiSelect(3564);           // the entryID
while (!this.Window.IsNextMultiSelect()) { this.WaitFrame(this.Util.SecondFromFrame(1)); }
local pick = this.Window.GetResultMultiSelect();
this.Window.CloseMultiSelect();
while (!this.Window.IsEndCloseMultiSelect()) { this.WaitFrame(this.Util.SecondFromFrame(1)); }

switch (pick) {
    case 1: /* first enabled answer  */ break;
    case 2: /* second enabled answer */ break;
}
```

`pick` is **1-based over the enabled answers**, not over the six slots.

### Reacting to the player

```squirrel
if (this.Item.GetNum(1061) == 1) this.Item.Add(12301, 1);   // conditional reward
this.Common.SetFieldGuest(112);   // summon a partner; 0 dismisses it
this.Common.AddMoney(5000);
this.Quest.GetProgress(id);  this.Quest.AdvanceProgress(id);
this.Flag.Check(id);  this.Flag.Set(id);  this.Flag.Clear(id);
```

## Custom battles

**The number you pass to `Encount` is the `mon_cpl` coupling id, and the battle script must
be named `battle_<that same id>.txt`** — the script name is zero-padded, so coupling `48` is
`battle_0048.txt`. Pick an id that is free in vanilla `mon_cpl` **and inside the 0–9999
range**: that is what Loud Kuyuki's quest mod does, and nothing proves the game accepts the
600000+ ids one other mod uses. That is the whole binding — there is no third table.
So a custom fight is two files plus a row:

| Piece | Holds |
|---|---|
| `mon_cpl/Coupling` row, id = N | `digi1`–`digi6`, `level1`–`level6`, `variation1`–`variation6`. Unused slots are `-1`. |
| `mon_para` / `mon_para_hard`, matching `(type, variation)` | That variation's stats, and `unk16` = its `battle_ai` id. |
| `battle_ai` row | **Use an id inside the vanilla range (0–9122).** No mod on this machine adds a `battle_ai` row at all — every one patches an existing vanilla id — so there is no precedent for a large one, and an out-of-range id risks an enemy with no AI. The enemy's moveset. **Slots are 7 columns wide starting at column index 8** (`Unk5`), with the **skill at +0 and its weight at +3**; empty slots are `-1`. Verified against 982 of 983 vanilla rows. The first slot (index 8) is empty in 906/983 rows — start at index 15. Weights are percentages and the used ones sum to 100. |
| `script64/battle_N.txt` | Cloned from vanilla `battle_0000.txt`. |

`multi_select` is the exception to the stay-in-range rule: vanilla tops out at entryID 500,
but working mods use `3564`, `113564` and `113567`, so a large id there is proven. Match
that magnitude rather than inventing a bigger one.

Because the variation is part of the key, a sparring or scripted version of a Digimon can
have its own stats and AI **without touching the normal one**.

### Rules a script can attach to a combatant

`Battle_Boot()` is where vanilla puts these. `charId` 6 is the first enemy; the party is
0–2.

```squirrel
this.Battle.AttachFixDamage(6, 1, 1);   // every hit lands for exactly 1  (-1,-1 disables)
this.Battle.AttachUndead(6, true);      // cannot be killed
this.Battle.AttachNoDamage(6, true);    // takes nothing at all
this.Battle.AttachAlwaysHit(6, true);   // never misses
this.Battle.AttachAlwaysAvoid(6, true); // never gets hit
this.Battle.SetTurnStartActionCommand(skillId, 6, -1);  // force a move each turn
```

`AttachFixDamage`'s three arguments are `(charId, min, max)` — vanilla uses `(6, 0, 1)` and
`(6, 100, 100)`. This is how a boss gets special rules without a single table edit.

**Copy the base script.** Take vanilla `battle_0000.txt` to
`battle_<yourNumber>.txt` and change what you want — often just one line:

```squirrel
this.Battle.SetBGM("M802", "M804");
```

Then start it from anywhere:

```squirrel
this.Battle.Encount(603535, 600);   // battle number, battle map
```

The enemy line-up is **not** in the script — it comes from **`mon_cpl/Coupling`** (the enemy
group, including each enemy's **level**) and `map_encount_param`. See
[04-data-tables.md](04-data-tables.md#decoded-unk-columns).

The battle script's own lifecycle is `Battle_Init()` (BGM starts here) → `Battle_Boot()` →
`Battle_Start()` → `Battle_Command()` → `Battle_Turn_End()` → `Battle_Victory()` /
`Battle_Defeat()`. Nothing fires when the action menu opens.

## Items as progress flags

The game's flags are a **finite shared resource, 0–20031**, and every mod draws from the same
pool. A softcoded item is yours alone, cannot collide, and shows the player their own
progress in the inventory. The *DigimonWorld 2 Challenge* ladder is built entirely this way:

```squirrel
if      (this.Item.GetNum([Item::ChaosRingG]) == 1) this.Battle.Encount(603536, 600);
else if (this.Item.GetNum([Item::ChaosRingS]) == 1) this.Battle.Encount(603537, 600);
else                                                this.Battle.Encount(603535, 600);
```

Prefer this over `Flag.Set` for anything that is your mod's own state.

## Before you ship a `.txt` script

**Diff it against vanilla.** The *Digimon Partner (HM)* mod ships a 12,286-line copy of the
base script to delete **two lines**. As shipped it redefines 257 global functions and beats
every other mod that touches any of them. If your diff is small, it is a `.sqmod`:

```json
[{ "replace_call_in_funcs": "this.Common.SetFieldGuest(0)", "with": "",
   "funcs": ["HM_emblem_guest_protect", "HM_emblem_geust_leave"] }]
```

Vanilla scripts are in `<game>/DSDB/script64/` — 2,623 of them. Diffing is one command.
