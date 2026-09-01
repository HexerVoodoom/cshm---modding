# 06 — Squirrel scripts

`script64/` holds compiled **Squirrel 2.2.4**. SDMM decompiles it on extraction (via
SydMontague's 64-bit NutCracker fork) and recompiles on build. Scripts are attached to game
contexts — battles, maps, events.

## Two ways to patch a script

### `.txt` — append (`squirrel_concat`)

A `.txt` file inside `script64/` is **appended** to the existing source for that target.
Because Squirrel is dynamic, redefining a function with the same name **replaces** it. So:

- new global functions and variables → just write them;
- wholesale replacement of a function → redefine it.

Anything outside `script64/` is not treated as a script.

### `.sqmod` — surgical edits (`squirrel_modify`)

A JSON list of rule dicts, applied to the existing source. Use this when you must *extend*
vanilla code rather than replace it — it is what keeps two mods touching the same function
compatible.

| Rule keys | Effect |
|---|---|
| `add_preamble` | List of lines inserted immediately before the first function definition. |
| `extend_func` + `with` | Append lines to the named function. |
| `replace` + `with` | Straight text find-and-replace. Blunt; easy to break things. |
| `replace_call` + `with` | Replace a *function call*, with argument capture. |
| `replace_call_in_funcs` + `with` + `funcs` | Same, but only inside the listed functions. |

Arguments in call patterns are `{#0}`, `{#1}`, … and can be reordered or wrapped in the
replacement.

```json
[
  {
    "replace_call": "this.Talk.PlayAnimation({#0}, {#1}, {#2}, {#3})",
    "with": "this.Talk.PlayAnimation({#0}, {#1}, globalSkipTextMode ? ({#2}/globalSkipAnimMultiplier) : ({#2}), {#3})"
  }
]
```

(From the skip-dialogue mod; `globalSkipTextMode` and `globalSkipAnimMultiplier` are
globals added by a companion `.txt` script.)

## The scoping rule that bites

Loading a script **dumps its contents into the root table with no cleanup** until the player
returns to the main menu or loads a save. Redefining a function replaces it globally *and
permanently for that session* — walk into a room whose script redefines a base function and
every later caller gets that version. This is why vanilla scripts redefine every function
they use, and it is the strongest argument for `.sqmod` over appended `.txt`.

Battle scripts run off a base script and fire, in order: `Battle_Init()` (BGM starts here),
`Battle_Boot()`, `Battle_Start()`, `Battle_Command()`, `Battle_Turn_End()`, then
`Battle_Victory()` / `Battle_Defeat()`. Nothing fires when the action menu opens.

Print a debug message with `this.INFO_WINDOW(id)` against `text/info_message.mbe/Sheet1.csv`.
The API reference is DSCSTools' `docs/squirrel/builtin/`; the commonly used calls are
collected in [../reference/discord-research.md](../reference/discord-research.md#squirrel-scripting).

## Practice

- **Prefer `.sqmod` over `.txt` whenever you are modifying vanilla behaviour.** Appending a
  redefined function silently wins over every other mod that touched it.
- `replace` is a last resort. It has no syntactic awareness and will happily edit a string
  literal or a comment.
- Scope with `replace_call_in_funcs` when you can — a global call replacement hits every
  call site in the file, including ones you never looked at.
- Decompiled output is not the original source. Read the decompiled `.txt` for the target
  before writing a pattern against it; do not pattern-match from memory.
