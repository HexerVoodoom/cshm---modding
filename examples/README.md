# Examples

## `Kyoko` — the smallest real mod on this machine

Not in this repo (it is user content), but it lives at
`<game>/mods/Kyoko` and is the reference for a minimal mod folder:

```
Kyoko/
  METADATA.json          Name / Author / Version / Category / Description
  modfiles/
    images/              6 files: .img (DDS) character textures + .dds UI icons
```

No build script, no softcodes, no data tables — the files land on top of the vanilla ones
under the default `overwrite` rule. Install it through SDMM and Build once before writing
anything of your own, to prove the chain reaches the game.

## Wanted

- A hello-world **data** mod: one CSV, one changed number, visible in game. This proves the
  merge path, which the texture path does not.
