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

   Rotation is a quaternion in **WXYZ** order. SDMM expands one `.mdledit` into four edits
   (`mdledit_name/skel/geom/anim`). If the map has a `.phys`, ship it alongside.

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

**A new battle is a cloned battle script.** Copy the vanilla base `battle_0000.txt` to
`battle_<yourNumber>.txt` and change what you want — in practice that is one line:

```squirrel
this.Battle.SetBGM("M802", "M804");
```

Then start it from anywhere:

```squirrel
this.Battle.Encount(603535, 600);   // battle number, battle map
```

The enemy line-up is **not** in the script — it comes from the coupling tables
(`mon_coupling_para`, `map_encount_param`). See
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
