# 04 — The data tables

214 tables in `data/`, 61 in `text/`, 1451 in `message/`. The full machine-readable index —
every sheet, its row count and its column names — is
[../reference/mbe-catalog.csv](../reference/mbe-catalog.csv).

Find things with the tool rather than by guessing:

```bash
python tools/cshm.py sheets digimon_common_para     # what sheets does it have
python tools/cshm.py head mon_para -n 3             # column names + sample rows
python tools/cshm.py grep-cols 'skill'              # which tables mention skills
python tools/cshm.py row item_para table 1          # one record, field by field
```

## The ID systems — the most common silent failure

Three ID forms coexist, and nothing warns you when you mix them:

| Form | Looks like | Used by |
|---|---|---|
| **bare** | `9` | `data/` tables: `digimon_common_para`, `evolution_next_para`, `mon_para.type` |
| **4ID** | `1009` (`1` + the bare ID padded to 3) | `text/charname` and other text tables |
| **filename** | `chr009` (`chr` + padded to 3) | model and texture filenames |

`tools/cshm.py name 9` accepts either numeric form and resolves through `text/charname`.
SDMM's softcodes expose exactly these as the `3ID`, `4ID` and `filename` methods on the
`Digimon` category — use those instead of writing the padding yourself.

**Composite IDs exist.** `mon_para.mbe/Monster.csv` is keyed by `(type, variation)` — the
same Digimon appears several times, one row per enemy statline variant. A merge rule that
matches on the first cell alone will hit the wrong row. Check the header before you patch.

## Cyber Sleuth vs Hacker's Memory

Both games share this database. Hacker's Memory content is largely carried in tables with an
**`_add` suffix**, alongside dedicated `hackers_*` tables:

- `quest_para_add`, `quest_text_add`, `field_area_para_add`, `map_select_add`,
  `keyword_para_add`, `digiline_para_add`, `tutorial_para_add`, …
- `hackers_memory_para`, `hackers_battle_battle`, `hackers_battle_result`,
  `text/hackers_battle_mission`, `text/hacker_rank`

Evidence: `text/quest_text_add` is entirely BBS/hacker-team quest copy, which is HM
mechanics; `text/quest_text` is CS content. Sampled, not exhaustively proven — treat
"`_add` = Hacker's Memory" as a strong working rule, not a law. If you change a shared
table you change **both** games.

## The tables you will actually reach for

### Digimon

| Table | Sheet | What it holds |
|---|---|---|
| `digimon_common_para` | `digimon` | The core record: `level` (stage), `attribute`, `type`, `fieldGuideId`, + 20 unknown fields. 375 rows. |
| `mon_para` | `Monster` | Stats per `(type, variation)`: `baseHP/ATK/DEF/INT/SPD`, `levelHP/…` growth, per-status resistances, `EXP`, `YEN`, drops. |
| `mon_para_hard` | | The hard-mode statline. |
| `digimon_list` | `digimon` | A bare list of live IDs (351 rows). Presence here matters. |
| `lvup_para` | `table` | Growth-rate profiles: `HP,SP,ATK,DEF,INT,SPD` percentages. |
| `personality_para` | | Personality stat modifiers. |
| `mon_design_para` | | Appearance data. Keyed on the **first 2 cells**. |
| `mon_cpl` | `Coupling` | Enemy groups for encounters and scripted battles — see above. |
| `text/charname` | `Digimon Names` | Names in JP/EN/ZH/EN-censored/KR/DE, keyed by **4ID**. |
| `text/digimon_book_explanation` | | Field Guide text. |

### Evolution

| Table | What it holds |
|---|---|
| `evolution_next_para` | Per Digimon, up to 6 evolution targets (`digi1..digi6`, `0` = none). |
| `evolution_condition_para` | Up to 10 `(condType, condValue, condUnk)` triples gating those evolutions. |
| `evolution_direction_para` | Evolution presentation/direction. |
| `degeneration_para` | De-digivolution. |
| `text/evolution` | Evolution-screen text. |

Adding an evolution means editing **both** `evolution_next_para` (the target) and
`evolution_condition_para` (the gate). Changing one alone is a classic half-mod.

### Items, equipment, shops

`item_para` (`table`: prices, `effectType/effectValue`, farm effects, medal fields, skin
flags, `descriptionId`, `iconId`; plus a `medal_price` sheet), `equip_para`,
`shop_para` (`lineup`, `limit_lineup` — wide padded arrays, use the append/remove rules),
`digimon_market_para`, `medal_collection_para`, `medal_gasha_para`.
Text lives in `text/item_name`, `text/item_explanation`, `text/equip_name`,
`text/equip_explanation`, `text/shop_text`, `text/medal_name`.

### Battle

`battle_ai` (983 AI rows, 69 columns), `battle_command`, `battle_command_effect`,
`battle_effect`, `battle_support_skill`, `battle_field`, `battle_camera`, `battle_bgm`,
`battle_se`, `battle_voice`, `experience_table`, `tp_table`.
Skill text: `text/skill_name`, `text/skill_content_name`, `text/skill_target_name`,
`text/support_skill_name`, `text/element`.

### Field, encounters, quests

`map_encount_param` (+`_add`), `field_area_para` (+`_add`), `field_npc_para` (+`_add`),
`field_tr_para` (triggers), `field_ap_para`, `field_cp_para`, `field_gk_para`,
`map_select` (+`_add`), `selectmapparam`, `quest_para` (333 rows, +`_add` 140),
`join_digimon_para` (`party` / `guest` — who joins you, with level and skills).

### DigiFarm

`farm_constant`, `farm_development`, `farm_investigation` (+`_add`), `farm_training`,
`farm_talk`, `farm_give_food`, `farm_goods`, `digimon_farm_para`.

### Hacking skills, keywords, Digiline

`hacking_skill_para`, `hacking_skill_conditions`, `learn_hacking_skill`,
`keyword_para` (+`_add`), `keyword_npc_para` (+`_add`), `keyword_message_para` (+`_add`),
`digiline_para` (+`_add`), `digiline_constant`.

### Text and dialogue

`text/` is one sheet per table, 7 columns: `ID, Japanese, English, Chinese,
EnglishCensored, Korean, German`. **Fill every language you care about** — an empty
English cell under `mberecord_merge` keeps the vanilla string, which is usually what you
want, but under `mberecord_overwrite` it blanks the line in game.

`message/` holds 1451 per-scene conversation tables (`d0101`, `battle_1020`, …), plus
`data/subtitle_*` for the pre-rendered movies.

## Decoded `unk` columns

The community decoded a good number of these. They are collected, with attribution, in
[../reference/discord-research.md](../reference/discord-research.md#decoded-columns) — the
highlights:

- `digimon_common_para`: `unk1` / `fieldGuideId` / `unk19` / `unk20` are the **per-region
  Field Guide numbers** (JP / US / EU / ASIA); `unk3` is generation sorting.
- `mon_para/Monster` `unk16` = `battle_ai`.
- `map_encount_param(_add)/Field` (16 columns, already named): `map_id`, `battlefield_id`,
  then ten `coupling_unk_pctchance_N` slots. **Each slot packs three values into one cell,
  space-separated** — `61 0 5` is coupling 61, flag 0, 5% — and the empty padding is `-1 0 0`,
  not `0`. Pass `-1` as the padding argument if you use `mberecord_append` here.
- A **coupling** is an enemy group, and the table is **`mon_cpl/Coupling`** (1947 rows, 25
  columns) — *not* `mon_coupling_para`, which does not exist. Its columns are `id`,
  `digi1`–`digi6`, **`level1`–`level6`**, `variation1`–`variation6`, `unk13`–`unk16`,
  `NPC_id`, `NPC_Variation`. The per-enemy **levels live here**, so a custom battle whose
  enemies come out at the wrong level is a `mon_cpl` problem, not a stat-table one.
- `join_digimon_para/party` is already named — `id, digimon_id, level, unk2, Skill1..Skill4,
  ABI`. (`guest` has 8 columns and a different shape.) The Discord-era `unk1..unk7` numbering
  refers to an older dump; use your own header.
- `battle_effect/effect.csv`: the last column is named `skillSFX` and points into `battle_se`.

**The upstream source of truth for column names is DSCSTools' `structures/` folder.** Update
it and re-extract and your CSV headers change — which is why two people can disagree about a
column: one has a stale dump.

## Before you edit anything

Run `python tools/cshm.py head <table>` and read the real header. Column meanings in this
file are a map, not a contract — the catalog and the game data are the contract.
