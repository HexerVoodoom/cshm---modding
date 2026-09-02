# Dissected mod patterns

Five working mods on this machine, taken apart file by file. These are the recipes; the
mods are the proof they work. Paths are given so you can reread the original.

---

## 0. `BUILD.json` is the rename map — the thing that makes everything else possible

This was the missing piece behind "custom models have arbitrary names". They do **in your
mod folder**. `BUILD.json` maps each authored filename onto the softcoded name the game
demands, at build time. **A custom model with no rename rule will never be found by the
game.**

The direct form, one file at a time:

```json
{
  "images/ui_chara_icon_[Digimon::cg::4ID()].img": "images/ui_chara_icon_cg.img",
  "images/dot[Digimon::cg::3ID()].img":            "images/dot007.img",
  "[Digimon::cg::filename()].name":                "cg.name",
  "[Digimon::cg::filename()].skel":                "cg.skel",
  "[Digimon::cg::filename()].geom":                "cg.geom",
  "[Digimon::cg::filename()].anim":                "cg.anim",
  "eff_bts_[Digimon::cs::filename()]_bs01.name":   "eff_bts_chaosforce.name"
}
```

Read it as **target ← source**: "build the file the game will call
`chr###.name` from my file `cg.name`".

The **build-pattern** form does the whole set in one rule, which is what you want for a
Digimon with 15 animations, 5 cameras and 2 effect models:

```json
{
  "{0}[Digimon::Samudramon_FB::filename()]{1}": {
    "BuildSteps": "{0}Samudramon_FB{1}",
    "Variables": [{ "Regex": "(.*)Samudramon_FB(.*)" }]
  }
}
```

Every mod file matching `(.*)Samudramon_FB(.*)` — `Samudramon_FB.name`,
`Samudramon_FB_ba01.anim`, `cam_Samudramon_FB_bs01_pc.geom`, `eff_bts_Samudramon_FB_bs02.skel`
— is installed under the same name with `Samudramon_FB` replaced by the resolved `chr###`.

`BUILD.json` is also where the compatibility rules go, e.g. the evolution-append line:

```json
"data/evolution_next_para.mbe/digimon.csv": ["data/evolution_next_para.mbe/digimon.csv", "mberecord_append"]
```

`SDMM` writes an `INDEX.json` next to it after a build. That file shows **exactly which
softcodes resolved where**, and is the fastest way to debug a rename that did not happen.

---

## 1. Custom interactive NPC — *Digimon Partner (HM)*

`.../SimpleDSCSModManager/mods/Hackers Memory` — 11 files. The cleanest example in the corpus.

```
ALIASES.json                        { "ModNPCsCS": "Town_CS::t30|SubArea::t3001|NPC" }
METADATA.json
modfiles/
  t3001p_add.mdledit                <- places the NPC in the map
  t3001p_add.phys                   <- the map's collider, shipped raw
  data/field_npc_para_add.mbe/t3001.csv       <- what the NPC IS
  data/join_digimon_para_add.mbe/party.csv    <- the partner it can summon
  data/multi_select_para.mbe/para.csv         <- the dialogue menu structure
  text/multi_select_text.mbe/para.csv         <- the menu's words
  text/charname.mbe/Sheet1.csv                <- the speaker's name (always Sheet1 in a mod)
  message/mod_<yourname>npc.mbe/Sheet1.csv    <- its lines
  script64/t3001_add.txt                      <- what it DOES
```

**Placement** — `.mdledit`, which SDMM expands into `mdledit_name/skel/geom/anim` edits of
the map's `p` (position) model:

```json
{ "editNPC": {
    "id": [Town_CS::t30|SubArea::t3001|NPC::digidestine],
    "position": [3, -0.3, 5], "rotation": [1, 0, 0, 0], "scale": [1, 1, 1] } }
```

**Definition** — `field_npc_para_<add>.mbe/<mapId>.csv`, **one sheet per map**:

| Column | Meaning |
|---|---|
| `id` | the NPC softcode |
| `name1` | the **bone name** — `[...::bone_name()]`, i.e. `npc_0008` |
| `model` | which model to wear (`chr112`, a `mob`, a `pc`…) |
| `variation`, `pose`, `rotation` | appearance |
| `actionIcon`, `interactable`, `interactionRange` | whether and how you can talk to it |

**Behaviour** — the game calls a Squirrel function named **`<mapId>_<bone_name>`**. That
naming is the entire hook; there is no table pointing at the script.

```squirrel
function t3001_[ModNPCsCS::digidestine::bone_name()]()
{
    this.Talk.Load("mod_digidestinenpc");   // your message table, by name
    this.Talk.SetMode(1);
    this.Message(this.Math.Rand(1000, 1004)); // random greeting from your rows
    this.MessageClose();
    this.TalkExit();

    this.Window.OpenMultiSelect(3564);        // entryID in multi_select_para
    while (!this.Window.IsNextMultiSelect()) { this.WaitFrame(this.Util.SecondFromFrame(1)); }
    local pick = this.Window.GetResultMultiSelect();
    this.Window.CloseMultiSelect();
    while (!this.Window.IsEndCloseMultiSelect()) { this.WaitFrame(this.Util.SecondFromFrame(1)); }

    switch (pick) {
        case 2: this.Common.SetFieldGuest(112); break;  // materialise the partner
        case 1: this.Common.SetFieldGuest(0);   break;  // dismiss
    }
}
```

The **menu** is two tables: `multi_select_para/para.csv` gives
`entryID, questionID, initialOption, unknown, ansN, ansNEnabled` (six answer slots, `-1`/`0`
for unused), and `text/multi_select_text` supplies the strings for the question ID and each
answer ID. `pick` is 1-based over the enabled answers.

The **message table** is a brand-new `message/<name>.mbe` with columns
`ID, Speaker, Unknown1, English, Chinese, …`. `Speaker` takes a `[Speakers::Key]` softcode,
and that same key gets a row in `text/charname` to give the speaker a display name.

*Mojoceramon NPC* (`D:/Mateus/Modding Digimon/MOJOCERAMON/funcionando`) is the same shape
plus a conditional reward:

```squirrel
this.Message(1001);
if (this.Item.GetNum(1061) == 1) this.Item.Add(12301, 1);
```

### The 12,286-line lesson

`Digimon Partner (HM)` also ships `script64/t5001_add.txt` — a **complete copy of the vanilla
base script, 257 functions**. Diffed against vanilla, it changes **two lines**: it deletes
`this.Common.SetFieldGuest(0);` from `HM_emblem_guest_protect()` and `HM_emblem_geust_leave()`,
so the story does not despawn your partner.

That should have been a `.sqmod`:

```json
[{ "replace_call_in_funcs": "this.Common.SetFieldGuest(0)", "with": "",
   "funcs": ["HM_emblem_guest_protect", "HM_emblem_geust_leave"] }]
```

As shipped, the mod redefines 257 global functions and will silently beat every other mod
that touches any of them. **Always diff a concat script against vanilla before shipping it;
if the diff is small, it is a `.sqmod`.**

---

## 2. NPC as a playable character — *Playable Rina 3.0*

`.../mods/Playable Rina`. Not a new Digimon at all — it rides the **costume system**.

- **The costumes are `item_para` rows 801–845.** There is no row 800, and `itemType` 3 alone
  does not identify a costume — rows 901–905 are also type 3 with empty skin columns. The
  Discord's "player costumes must have an ID between 800 and 900" is the ID *range* the game
  enforces, not the set of rows that exist. The three columns
  `keisukeSkin` / `takumiSkin` / `amiSkin` name the **model prefix** each protagonist wears
  when that costume is equipped. `skinFlag` is the unlock flag; `iconId` is 101 for all of them.
- Rina goes playable by pointing one of those columns at her NPC model:
  row `803` becomes `keisukeSkin=pc002, takumiSkin=npc014, amiSkin=pc020`.
- **`same_animation_data.mbe/pc.csv` is `ID → model`: "this pc uses that model's animation
  set".** Vanilla maps pc003/005/007/009 → `pc001` and pc004/006/008/010 → `pc002`. The mod
  adds `2 → pc014`, so the swapped-in model animates off the shipped `pc014` set.
- Ships the model (`pc002.*`, `pc014.*`), 87 `.anim` files, and the UI: `ui_chara_icon_*`,
  `ui_save_load_*`, `cutin_photo_*`, `ui_main_hacker_*`.

So: **to make any NPC playable, give it a `pc` slot, aim a costume row's skin column at it,
and add a `same_animation_data` row so you do not have to author animations.**

Note the mod ships all 45 vanilla costume rows and only 15 of them differ. Under
`mberecord_merge` that is harmless, but it is noise — ship the changed rows only.

---

## 3. A recoloured skill with its own voice — *Chaos Generals*

`.../mods/Chaos Generals Digidestined Edition` and `.../mods/voice` (*Chaos Powers VO*).
This is the "greyscale WarGreymon skill" pattern.

**The visual half.** A skill's animation is a model, and its look comes from the textures
that model names.

1. Clone the donor's attack effect model — all four files — into your mod under a readable
   stem: `eff_bts_chaosforce.name/.skel/.geom/.anim`.
2. Copy every `eff_*` texture it uses and repaint them (greyscale, in this case). Ship them
   under a distinguishing name: the mod uses a **`c` prefix** — `ceff_aur_05.img`,
   `ceff_lig_01.img`, `ceff_par_05.img`, `ceff_etc_33.img` — and the same for the character
   textures, `cchr009a01.img` from `chr009a01.img`.
3. Point the cloned model at the recoloured textures.
4. Rename the effect model to what the game expects, in `BUILD.json`:
   `"eff_bts_[Digimon::cs::filename()]_bs01.name": "eff_bts_chaosforce.name"`.

**The data half**, three tables in a chain:

```
battle_command/Command.csv          the skill itself
  skillID -> skillTextId, Icon, Animation, Power, DamageType, Damage Delay, Type,
  TargetType, NumAttacksMin/Max, Chain Delay, XrosType, SP Cost, SpeedUse, damageRange,
  alwaysHits, Accuracy, canCrit, critChance, sacrificeHP, knockbackChance, HPabsorb,
  SPabsorb, comboRate, StatusType/Effect/Chance, SelfStatus*, UndoStatus*, PrevAttack
battle_command_effect/effect.csv    skillID -> casterSkillEffectIDs, targetSkillEffectIDs
battle_effect/effect.csv            effect id -> skillEffModel, ..., skillSFX -> battle_se
```

Text: `text/skill_name` and `text/skill_content_name`, both via a `[SkillText::Key]` softcode.

**The voice half** — *Chaos Powers VO*, a `FormatVersion: 2` mod of four files:

```
modfiles/chaos.steam.mvgl                    your AFS2, built with DSCSToolsCLI --afs2pack
modfiles/DSDBP/data/voice.csv                name,volume,loop_start,loop_end,cri_contents_id,cri_dbname
modfiles/DSDBP/data/battle_voice.mbe/voice.csv       (Cyber Sleuth)
modfiles/DSDBP/data/battle_voice_add.mbe/voice.csv   (Hacker's Memory)
```

```csv
# voice.csv - cri_contents_id is the DECIMAL index into your AFS2, whose members are named in hex
force,100,0,0,0,chaos
river,100,0,0,1,chaos

# battle_voice*/voice.csv
voice_id,voice_name,unk2,unk3,unk4,unk5,unk6,unk7,unk8,unk9,unk10
[SkillVFX_CS::chaosforce],force,0,0,0,[Digimon::cg::4ID()],0,0,-1,[Skill::chaosforce],0
#                          ^name in voice.csv        ^unk5 = Digimon 4ID   ^unk9 = skill ID
```

Ship the **same rows to both `battle_voice` and `battle_voice_add`** so the line plays in
both games. Note the `SkillVFX_CS` softcode category — wider than the v0.1 documentation.

**Support (passive) skills** live in `battle_support_skill/support_skill.csv`, which has a
fully named 58-column schema: `condition`, `cond Value`, then per-stat and per-element
modifiers, every status chance and resistance, `Combo Rate`, `EXP Boost`, `YEN Boost`,
`Drop Rate`, `Scan Rate`, `Heal HP %`, `Damage to HP`, `moveFirst`, `min HP`, `HP to ATK`.

---

## 4. A custom battle ladder — *DigimonWorld 2 Challenge*

`D:/Mateus/Modding Digimon/neocrimson/finalizando/ALL VERSION/DigimonWorld 2 Challenge`.

**A new battle is a cloned battle script.** `battle_603535.txt` … `battle_603545.txt` are
each a copy of the vanilla base `battle_0000.txt`, 895 lines and 87 functions, differing in
**one line**:

```squirrel
this.Battle.SetBGM("M802", "M804");   // vanilla: this.Battle.SetBGM("M24", "M26");
```

The battle *number* is the identity. `this.Battle.Encount(603535, 600)` starts it; `600` is
the battle map. The enemy line-up comes from the coupling tables, not the script.

**Progress is tracked with items, not flags.** The gatekeeper NPC walks a ladder of
possessions, each unlocking a harder fight, with a randomised final tier:

```squirrel
function t0511_npc_0005()
{
    if (this.Item.GetNum(847) == 1)                     { ...; this.Battle.Encount(this.Math.Rand(603542, 603545), 600); }
    else if (this.Item.GetNum(846) == 1)                { ...; this.Battle.Encount(603541, 600); }
    else if (this.Item.GetNum([Item::ChaosRingB]) == 1) { ...; this.Battle.Encount(603540, 600); }
    /* ... */
    else                                                { ...; this.Battle.Encount(603535, 600); }
}
```

That is a deliberate choice worth copying: the game's flags are a **finite shared resource
(0–20031)** that every mod draws from, while a softcoded item is yours alone and shows up in
the player's inventory as visible progress.

---

## 5. Big mods use `FormatVersion: 2` even when they do not have to

*Loud's custom Quests/Challenges* puts **everything** under `modfiles/DSDBP/` — `data/`,
`text/`, `message/`, `images/`, `script64/` — rather than at the `modfiles/` root. Both work;
the explicit form makes the target archive obvious and is required the moment you add an
AFS2. Its 37 scripts are the same clone-a-battle-script pattern (`battle_5700`…`battle_5715`)
plus map scripts (`d1303.txt`).
