# Gate — cshm-melhoria-01 (5 loops)

**Modo:** validar-o-que-existe. **Checkpoints agrupados em um só**, a pedido ("faça 5 loops").
Suposição declarada no contexto §10.

| Loop | Agente / método | Resultado |
|---|---|---|
| 1 Governança do roster | `alpha-governanca` | 3 fatais, 4 fixáveis, 2 lacunas de disciplina |
| 2 Ataque ao conhecimento | `alpha-skeptic` | **5 fatais**, 7 fixáveis, 14 alegações provadas corretas |
| 3 Verificação empírica | validador × 253 mods | conflito guia↔corpus achado e resolvido |
| 4 Fontes upstream | leitura direta | contrato de material e API tipada, novos |
| 5 Ferramenta | `tools/validate_mod.py` | gates viraram comando executável |

## Corrigido

**Fatais (conhecimento errado que produziria mod quebrado):**
1. `mon_coupling_para` **não existe** — é `mon_cpl/Coupling`, e é lá que ficam os **níveis**
   dos inimigos. Estava errado em 3 arquivos.
2. `digimon_farm_para` — os pares de learnset são **(skill, level)**, não (level, skill).
   Invertido, o Digimon nunca aprende nada e não há erro.
3. `model_default_scale` — a primeira coluna é `digimonID`; o guia listava só as 5 seguintes,
   deslocando tudo uma casa exatamente na tabela que ele marca como crítica.
4. `guide/07` afirmava que nenhuma tabela mapeia ID→modelo. `same_animation_data` faz isso,
   e é a 2ª tabela mais editada do corpus.
5. Versão do Blender contraditória entre 4 arquivos. Resolvida para **2.83**.

**Fixáveis:** contagens erradas (375/351/20, não 347/352/21), numeração `unk` obsoleta
marcada como histórico, `skill_use_group_set` (20 flags), `battle_support_skill` (59 col),
faixa de fantasias (801–845), overlays `_bs02`/`_fa01` marcados opcionais, contradição
`guide/03`×`05` resolvida, `mod-builder` renumerado, `cshm-art` deixou de contradizer o
gate 16 do QA, caminho do `cshm.py` corrigido em 8 arquivos.

**Novo conhecimento:** `reference/upstream-contracts.md` — hierarquia de cena obrigatória,
limites reais (<56 grupos/mesh, ≤4 por vértice, ≤3 UV), os 7 samplers nomeados, ~30 uniforms
incluindo `Fat`, a exigência de embarcar `shaders/` `_fp`+`_vp`, a família `Battle.Attach*`,
`OpenYesNoInfo` e `SetReplaceString`. **Lista autoritativa de 10 chaves compostas** tirada do
`mberecord_idsizes.json` do próprio SDMM — o guia conhecia 1.

## Objeção que sobreviveu

O cético apontou a **causa-raiz**: cabeçalhos e contagens foram digitados à mão em vez de
derivados do `mbe-catalog.csv`. Corrigi as instâncias; **não corrigi o processo**. Enquanto
o guia for escrito à mão, a mesma classe de erro volta.

## Pendências para o humano

1. **Fusões de roster** (`table-surgeon`→`mod-builder`, `art`→`porter`) — não executadas.
   Mudam o elenco e o próprio auditor exigiu eval de regressão antes.
2. **Agente de BGM/mapas** — lacuna real, mas o auditor recomenda não criar sem demanda.
3. Nada foi verificado **no jogo**. Restrição do contexto §4.
