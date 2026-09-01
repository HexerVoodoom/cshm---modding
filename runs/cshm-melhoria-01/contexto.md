# Bloco de contexto — cshm-melhoria-01

**Alvo.** O projeto `cshm-modding`: um guia + toolchain + squad de agentes para modding de
Digimon Story Cyber Sleuth: Complete Edition (Cyber Sleuth + Hacker's Memory).

1. **Quem usa.** Um modder único e experiente — "Mojoceramon AKA HexerVoodoom", autor de ~200
   mods publicados —, e agentes de IA lendo o repo como fonte de verdade. Não é software de
   consumo; é conhecimento operacional.
2. **Problema.** O conhecimento do domínio está espalhado por um Discord de 5 anos, PDFs, 253
   pastas de mod e o próprio jogo. Já foi parcialmente destilado. O risco agora é **afirmação
   errada**: o guia já teve uma alegação central errada (stems de modelo "arbitrários"), que
   só apareceu ao dissecar um mod real.
3. **Métrica-norte.** Um agente que lê só o repo consegue produzir um mod que funciona no jogo
   sem tentativa e erro — e não afirma nada que não possa provar com um comando.
4. **Restrições.** Nunca escrever dentro do install do jogo. Blender 2.83 é o único com o addon
   DSCS. O jogo não pôde ser executado nesta sessão — nada é verificável in-game por mim.
5. **Stack.** Markdown + Python 3 sem dependências. Repo git → github.com/HexerVoodoom/cshm---modding.
6. **Dados.** `DSDB/` extraído (3025 sheets), 2623 scripts vanilla, corpus de 253 mods.
7. **Marca/DS.** N/A.
8. **Rastreador.** git + `guide/09-open-questions.md`.
9. **Regulatório.** Nenhum. Regra da comunidade: nada de pirataria, nada de redistribuir
   asset vanilla.
10. **Dono das decisões.** O usuário. Suposição declarada: ele quer autonomia nestes 5 loops e
    um único gate no fim.

## Modo
`validar-o-que-existe` — o material existente passa pelo mesmo loop adversarial, nunca é
carimbado como pronto.
