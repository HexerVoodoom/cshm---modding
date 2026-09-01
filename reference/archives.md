# The archives

Game data lives in `<game>/resources/`. `.mvgl` is not a filetype — it is a container that
is either **MDB1** (generic compressed data) or **AFS2** (HCA audio).

## Main game data (MDB1), in increasing load priority

| Archive | Size (this install) | Contents |
|---|---|---|
| `DSDB` | 2.68 GB | The bulk of the game. |
| `DSDBA` | 62 MB | Overwrite data, mostly censorship (e.g. the Sistermon Ciel model). |
| `DSDBS` | 146 MB | Overwrite data for PC with an Xbox controller. |
| `DSDBSP` | 136 MB | Overwrite data for PC with a DualShock controller. |
| `DSDBP` | 42 MB | Overwrite data, mostly the Vita/PS4 DLC. **Highest priority — SDMM builds into this one.** |

Later archives win. That is why a mod only has to ship the records it changes: SDMM merges
them into `DSDBP` and `DSDBP` overrides `DSDB`.

Do **not** install into `DSDB`. It is huge, slow to rebuild and has little spare room.

## Sound

| Archive | Kind | Contents |
|---|---|---|
| `DSDBse`, `DSDBPse` | MDB1 | SFX, as HCA inside a `sound/` folder (extension `.snds`). |
| `DSDBbgm` | AFS2 | The soundtrack. |
| `DSDBPDSEbgm` | AFS2 | Short Digimon anime OST snippets. |
| `DSDBvo` | AFS2 | Most voicelines. |
| `DSDBPvo` | AFS2 | Additional voicelines. |
| `DSDBvous` | AFS2 | Censorship voicelines. |

AFS2 members extract as `NNNNNN.hca`, named by their **hexadecimal** entry number. The game
maps them to names through `data/bgm.csv` (`cri_contents_id` is that index, in **decimal**)
and `data/voice.csv` / `data/voice_us.csv`. Those CSVs also name the archive, and the game
loads whatever archive name is written there — which is how a mod adds a brand new AFS2.

`.usm` files in `resources/` are videos.

## Third-party archives already present on this install

`resources/` on this machine also holds community `.mvgl` files that are not vanilla:
`chaos`, `chaosgenerals`, `bravehearttri`, `desafio2mucho`, `gachaeng`, `gachaesp`,
`newmusicdb`, `newtestdb`, `quest1*`, `tiamatvoice`, `dw2sound`, `7d6db`. These are loaded
by `DSCSModLoader.dll` (in `app_digister/`), not by SDMM. Treat them as pre-existing mods:
they can be the reason a vanilla assumption does not hold on this machine.
