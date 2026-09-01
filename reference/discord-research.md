# What the archived `#dscs-research` channel established

Scraped 2026-09-01 from the read-only archive channel (`825038465871118337`), 1128 messages
covering **2021-04-01 → 2023-02-01** — effectively the whole channel. Attributions are to
the person who stated the finding. Nothing here has been re-verified against this install
unless the guide says so; treat it as strong community evidence, not proof.

## Where the column documentation actually lives

DSCSTools carries the machine-readable column definitions **and** human docs:

- `github.com/SydMontague/DSCSTools/tree/master/structures` — the `structure.json` files
  SDMM uses to name columns. Improving these is how research gets shared: open a PR, or ask
  Pherakki to file one for you.
- `github.com/SydMontague/DSCSTools/tree/master/docs/structures` — per-table `.txt` notes
  (e.g. `battle_command.txt`, `item_para.txt`).
- `github.com/SydMontague/DSCSTools/tree/master/docs/squirrel/builtin` — the **Squirrel API
  reference**, one file per namespace (e.g. `Work.txt`, `Debug.txt`).

If you re-extract after updating the structures, the CSV headers change. That is why two
people can disagree about a column name — one of them has a stale dump.

## Decoded columns

### `digimon_common_para` — the sort fields (SydMontague, Dec 2022)

The four "unknown" numbers next to `fieldGuideId` are **per-region Field Guide numbers**:

| Column | Region |
|---|---|
| `unk1` | JP |
| `fieldGuideId` | US (ENGLISH_CENSORED) |
| `unk19` | EU (ENGLISH, GERMAN) |
| `unk20` | ASIA (CHINESE, KOREAN) |

`unk3` is generation sorting. `unk5` is another sort value. `unk6, 8, 10, 12, 14` are
name-sort values stored per selected language, and appear to be fallbacks. The vanilla
Field Guide order is *gojuon* per class using the Japanese sub-names (Biyomon sorts as
Piyomon, Myotismon as Vamdemon).

### Encounters

- **Coupling** = an enemy group for one battle: up to 6 enemy IDs plus variant IDs. Defined
  in `mon_coupling_para`, referring to chr IDs + variant IDs in `mon_para` / `mon_para_hard`.
- `map_encount_param(_add)/Field`: `unk1` is the **map ID** (`101` → `d0101`, `1101` →
  `d1101`); `unk6`–`unk15` are ten slots of **(coupling ID, flag, percentage trigger
  chance)**. The flag looks like a quest flag — a battle whose flag is unset falls back to
  coupling 0.
- `mirror_dungeon_para_add/para`: `id` 1–14, `unk2` unlock condition, `unk9`–`unk27`
  coupling IDs.
- `digital_space_para/para`: `unk2` map ID, `unk13`–`unk32` the spawn list.

### `join_digimon_para` (Cyberpro123, Zeak6464)

`party.csv` / `guest.csv`: `unk1` = the level the Digimon joins at, `unk2` = join
conditions, `unk3`–`unk6` = up to four known moves, `unk7` = starting ABI.

### `map_select` (g1g2, Cloud)

`unk1` = map ID before the Digimon attack (prefix a `0` to match the DSDB filename — `101` →
`t0101`, Shinjuku), `unk2` = map ID after, `unk4` = thumbnail texture (**only takes effect
when `unk6` is 0**), `unk5` = which piece of `ui_mapsel_select` / `ui_mapsel_cursor_sel`.

### Other

- `battle_effect/effect.csv` `unk15` = **Sound Effect ID** → `battle_se.mbe` (Pherakki).
- `mon_para/Monster` `unk16` = `battle_ai` (Zeak6464).
- Farm food is in `farm_give_food.mbe`; farm item meshes in `farm_goods`; Farm/Bank
  Expansion kits are hardcoded and have no `item_para` effect.
- Equipment (the USBs) lives in **`equip_para.mbe`**, not `item_para`.
- `shop_para.mbe`: `lineup.csv` holds the line-ups, `shop.csv` maps shops to line-ups by
  trigger. The game walks all line-ups for a shop and **picks the last one whose trigger is
  set** — that is how shops unlock stock over time. There are two shops sharing the DigiLab's
  ID and dialogue but with different line-ups (the other is the EDEN entrance Terminal).

## Formulas

- **EXP**: `((level - 1) * exp2 + exp1) * itemFactor * supportFactor`. Both factors are
  `1.0 + something` and never drop below 1. (SydMontague, Jan 2023.)
- **Farm development**: two rolls. Roll 1 picks one of 7 loot tables from a weighted sum of
  the natures of the Digimon on the farm. Roll 2 draws `0.0–0.5`, multiplies by the Dev
  Knowhow boost `(1 + 0.55 * boosts)`, adds 1, multiplies by the search level
  (100 / 1000 / 10000), then takes the highest-weighted item the result exceeds.
- There are **11 condition types** for battle support skills (`battle_support_skill`).

## Voicelines — the ID blocks are load-bearing

The game categorises a battle voiceline by the **thousands digit** of its ID, and the IDs
**must sit in the right block, in order**. Appending 8766 to the end of the file does not work.

| Block | Meaning |
|---|---|
| 1000 | Battle start |
| 2000 | Battle win |
| 3000 | Battle loss |
| 4000 | XROS attack |
| 5000 | Battle escape |
| 6000 | Battle item use |
| 7000 / 8000 | Special attacks |
| 9000 | Knockout |

The IDs in `data/battle_voices.mbe/voices.csv` point at nothing; they only number the lines.
Similar range rules exist elsewhere — **player costumes must have an item ID in [800, 900)**.

### Adding a voiceline (Loud Kuyuki)

`voice.csv`: column A `name` (your key, e.g. `1001_004` or `Stingmon`), column E
`cri_contents_id` (the file index, **decimal**, while the files are named in **hex**), column
F `cri_dbname` (your archive's name). `this.MessageTalk(id)` *always* tries to fetch audio,
so supplying one is all that is needed — no script change.

`battle_voice.mbe` (CS) / `battle_voice_add.mbe` (HM): `unk5` = Digimon ID, `unk9` = skill
ID, `voice_name` = your key from `voice.csv`. The knockout line is the row with the Digimon
ID and `-1`s, at ID + 9000.

### Building the audio

```bash
VGAudioCli.exe -i input.wav -o 00000001.hca --out-format hca --keycode 2897314143465725881
# rename .hca -> .dat, put them in a folder named after your DB
DSCSToolsCLI.exe --afs2pack name_folder yourDB_name.steam.mvgl
```

Ship the `.mvgl` with `"FormatVersion": 2` and point `bgm.csv` / `voice.csv` at
`yourDB_name`. **The game loads any AFS2 archive you name in those CSVs** — confirmed by
Pherakki. SDMM now has a GUI for the WAV→HCA step. The game's audio mixing is very quiet;
Loud Kuyuki adds +10 dB to everything.

## Squirrel scripting

### Scope — the thing that bites

Loading a script **dumps its contents into the root table with no cleanup** until you return
to the main menu or load a save (SydMontague). Redefining a function replaces it globally and
permanently for that session. Walk into a room whose script redefines a base function and you
are stuck with that definition. This is why vanilla scripts redefine every function they use.
`m00_e00_common.nut` is loaded by rooms; `include.nut` and `function_common.nut` are not.

### Battle script lifecycle (Uncle Jon)

`Battle_Init()` (the BGM starts here) → `Battle_Boot()` → `Battle_Start()` (after enemies are
scanned) → `Battle_Command()` (after the player's input menu closes) → `Battle_Turn_End()`
(after any Digimon's turn) → `Battle_Victory()` / `Battle_Defeat()`. `Battle_Direction_End()`
was never triggered. **No hook fires when the action menu opens** — that was an open problem.
Every battle script runs off a base script; editing `battle_0000` only changes that one battle.

### Debug printing

`this.INFO_WINDOW(id)` prints a message from `text/info_message.mbe/Sheet1.csv`.

For exceptions (Pherakki): add a message row that is just `[d0]` (a blank string slot), then

```squirrel
try { /* ... */ }
catch (ex) { this.Talk.SetString(ex); this.MessageTalk(<id of the [d0] message>); }
```

**Any message that declares a variable must have it filled or the game hard-crashes.**
`this.seterrorhandler(func)` exists for a global handler but was never made to work.

### Useful API (Zeak6464's dump; full reference in DSCSTools `docs/squirrel/`)

```squirrel
this.Item.Add(itemId, amount);          this.Common.AddMoney(amount);
this.Flag.Set(id);  this.Flag.Clear(id);        // flags run 0..20031
this.Quest.AdvanceProgress(id);  this.Quest.GetProgress(id);
this.Quest.DebugComplete(id);    this.Common.AdvanceStoryProgress();
this.Field.ChangeField(map, area, locator, angle);
this.HM_ChangeField("t05", 3, "start_01", 0);
this.Battle.Encount(battleNo, battleMap);
this.Common.SetFieldGuest(couplingId);
this.Field.AddGuestFormal(slotFrom0, id);   // id from join_digimon_para/guest.csv
this.Field.AddPartyFormal(id);              // id from join_digimon_para/party.csv
this.Field.RemoveGuest(slot);    this.Field.SetNpcVisible(npcId, bool);
this.Field.LoadNpc(index, "mobFile", x*0.1, y*0.1, z*0.1, loc);
this.Common.LearnHackingSkill(id);   this.DEBUG_ALLSKILL();
this.Sound.StopBGM(fadeOut);  this.Sound.PlayBGM(trackName);  this.Sound.PlaySE(name, type);
this.Work.IsPushKey("DECIDE"|"CANCEL"|"UP"|"DOWN"|"LEFT"|"RIGHT"|"TAP"|"ANY");
this.Battle.SetParameter(mon, paramId, value);   // 0 HP, 1 SP, 4 ATK, 5 DEF, 6 INT, 7 SPD
this.Battle.GetStatus(mon, statusId);            // returns REMAINING DURATION of a buff
```

`SetParameter`'s indices for max HP/SP and its Digimon indexing are **disputed**: Loud Kuyuki
reports party = 1,2,3 and enemies 6+, with max HP/SP at 0/1; GrowaSowa reports party = 0,1,2
with 2 = max HP and 3 = max SP. Test before relying on it.

BGM is per-battle: `battle_bgm` only names tracks; the script has to stop and start them.
The X Antibody mod's `d9002.txt` is the worked example.

## Skills

- A Digimon's learnset is `digimon_farm_para` → `moveN` / `moveNLevel` for N = 1–6, plus
  `sMove1` / `sMove2` for the Special Skills. Skill IDs are in `data/battle_command`; its
  second column is the name ID in `text/skill_name`. Support skills are in
  `battle_support_skill`.
- Six learned moves fit the table, but the Field Guide only shows **seven moves total**
  (learned + special), so a Digimon with two specials realistically gets five.
- Guard (`battle_command` ID 3) is hardcoded: changing its power, damage type and target type
  does nothing; only `SpeedUse` had an effect.

## Mod compatibility — the BUILD.json line every evolution mod needs

Pherakki's standing recommendation. Without it, your mod **replaces** the target's whole evo
list; with it, entries are appended until the game's max of 6 is reached, so two mods that
both add an evolution to the same Digimon coexist:

```json
"data/evolution_next_para.mbe/digimon.csv": ["data/evolution_next_para.mbe/digimon.csv", "mberecord_append"],
```

To deliberately take priority instead, use `mberecord_overwrite` on
`data/degeneration_para.mbe/digimon.csv` and tell users to install your mod last.

A BUILD.json entry reads *"take this file from my mod, merge it into that vanilla file with
this rule"*, and one target can appear more than once with different sources and rules:

```json
"data/degeneration_para.mbe/digimon.csv": ["data/edits_that_overwrite_stuff.csv", "mberecord_overwrite"],
"data/degeneration_para.mbe/digimon.csv": ["data/edits_that_dont_overwrite_stuff.csv", "mberecord_append"],
```

## Engine and save

- The engine has an **unused switch to load loose files from the filesystem instead of the
  `.mvgl` archives**, and it also supports mixed archive/folder loading. `DSCSModLoader`
  enables it. The AFS2 sound archives are the exception — always packed. This also lifts the
  4 GiB `.mvgl` concern for texture mods.
- Save limits are savegame-format limits, not engine limits (internally `std::map`):
  Digimon bank 300, ScanData 400 entries, three inventories (a 2000-slot bag and two
  100-slot unknowns). SydMontague reimplemented save load/save in the mod loader.
- You cannot convert a Digimon you have not seen, however high the scan rate.
- Movement is computed per frame with a **fixed 1/120 delta**, so it is FPS-dependent;
  `Vista.SetFPS` resets the framerate.
- The game has **3 empty font slots**; fonts are a standard format and can be replaced
  directly, but using the empty slots needs mod-loader support.

## Fixed bugs and their causes

- **Custom keyboard layouts crash the game.** The game calls `GetKeyboardLayoutNameA` and
  passes the hex string to `stoi`, which overflows for e.g. `A0000409`. The fix is `stoul`;
  the mod loader patch is `0x2d0233=B9`.
- **`[` or `]` in a username crashes.** The username goes through the message string parser,
  so an invalid code in brackets breaks it — and valid codes let you colour your username.

## Language

The Steam build can select only **English, Chinese, Korean, German**. The Japanese column
exists in every text table but there is no known way to select it without editing the EXE.
The Spanish translation therefore overwrites English and EnglishCensored. Part of the UI is
built from 3D models, so a full translation has to touch those too. The **Switch and PC model
formats are identical**, so Switch assets can be swapped in directly.

Protagonist IDs: `2000` boy, `2001` girl, `2020` Hacker's Memory. There is an unused Female
Protagonist ID and an internal gender value the game never uses; misgendered lines can be
fixed either by rewriting them or by branching on that value in script.
