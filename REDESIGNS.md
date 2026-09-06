# Redesigns — Radar de Bolsas TT-FAPESP

Três redesigns completos do site, cada um em sua própria branch, construídos em
paralelo usando o skill **Impeccable** (`.claude/skills/impeccable`). Nenhum
altera dado, comportamento de filtro, contrato de dados
(`data/oportunidades.json`) ou o texto de rodapé — só a linguagem visual.

Ambiente sem geração de imagem disponível, então os três seguiram o caminho
**code-led** (sem comp/mockup prévio): a direção foi escrita como um contrato
textual (THESIS / OWN-WORLD / STORY / FIRST VIEWPORT / FORM / FINISH) e
construída diretamente em código, auditada no final contra esse contrato.

## Como as 3 direções foram escolhidas

Para fugir do "modo seguro" (a mesma estética neutra que qualquer modelo
tende a convergir), cada direção veio de `impeccable concept-seed --scope
direction --mode operate`, que sorteia qual candidato de uma lista própria
(ordenada por ressonância com o produto) deve ser construído — nunca o topo
óbvio da lista — e ainda apresenta "desafiantes" de um catálogo externo para
disputar a vaga em dois eixos: identificação com o público (físicos/
matemáticos computacionais/cientistas de dados) e clareza do produto (uma
lista curta de bolsas, ranqueada por urgência de prazo). Rodou-se uma vez por
versão (v2 e v3 via re-roll, que descarta tudo já sorteado antes), garantindo
três mundos genuinamente distintos.

---

## V1 — Caderno de Laboratório (`redesign/lab-notebook`)

**Tese:** uma ferramenta pessoal de pesquisa deveria parecer o caderno de
laboratório anotado do próprio pesquisador, não um dashboard de SaaS.

**Mundo visual:**
- Fundo papel-milimetrado creme (`#f4edd6`), tinta grafite (`#2b2a20`),
  estrutura em índigo (`#2f3184`/`#1f2160`), e **um único** laranja-marca-texto
  (`#d9600a`/`#eb8a1f`) reservado estritamente para prazos ≤5 dias.
- Tipografia: Caveat (título e legendas manuscritas), Permanent Marker (o
  numeral gigante de dias-restantes do card mais urgente), Space Mono
  (metadados: instituição, área, datas, código de modalidade) — todas
  auto-hospedadas em `fonts/`, sem CDN.
- Composição: uma coluna de espiral (furos + ganchos, CSS puro) corre na
  margem esquerda; oportunidades são cards de índice "colados" com fita
  washi e canto cortado, levemente rotacionados; o card de prazo mais
  próximo é trazido para frente, desrotacionado, ampliado, com o numeral
  gigante de dias dentro de um anel desenhado à mão; hover/foco levanta o
  card ativo e esmaece os vizinhos.

**Preservado:** filtro de modalidade (checkboxes desenhados à mão em vez de
chips), lógica de urgência (≤5 dias), atribuição de rodapé, contrato de
dados.

**Ver localmente:**
```bash
git checkout redesign/lab-notebook
python -m http.server 8000
# http://localhost:8000
```

---

## V2 — Tabela Periódica de Bolsas (`redesign/periodic-table`)

**Tese:** rejeita o feed de cards; oportunidades viram entradas de uma carta
de referência científica — classificadas, comparáveis, factuais à primeira
vista, do jeito que um físico já lê uma tabela periódica.

**Mundo visual:**
- Fundo pôster clínico em tom sálvia frio (`#edf0e4`), tinta `#1b1912`,
  painéis elevados `#e2e6d5`. Cada oportunidade é um "elemento": código de
  modalidade no canto superior esquerdo (como símbolo químico), número de
  sequência no canto superior direito (como número atômico), tingimento
  suave por grupo de modalidade (TT-IV/TT-IV-A/TT-V, cada um com sua
  própria dupla de cor/tinta).
- Tipografia: IBM Plex Sans (variável, para títulos e corpo) + IBM Plex Mono
  (datas, contadores, legendas) — auto-hospedadas em `fonts/`.
- **Um único** vermelho-sinal reservado (`#cf2c0e`/`#a3220a`) para o link de
  inscrição e para blocos de prazo fechando em ≤5 dias — em nenhum outro
  lugar da página.
- Composição: moldura de pôster com legenda (kicker de gráfico + contagem +
  timestamp), uma chave de legenda compacta explicando a anatomia do bloco,
  grade responsiva de blocos com réguas de 1px estilo tabela real. Blocos
  se re-ranqueiam (urgente primeiro dentro do grupo) e guardam um destaque
  persistente (não um flash) na primeira vez que cruzam para "urgente"
  entre visitas (memória via `localStorage`). Tocar um bloco expande em
  linha o detalhe completo, sem modal.

**Preservado:** filtro de modalidade (chips-tingidos), lógica de urgência
(≤5 dias), atribuição de rodapé, contrato de dados.

**Ver localmente:**
```bash
git checkout redesign/periodic-table
python -m http.server 8000
# http://localhost:8000
```

---

## V3 — Trilho de Linhas de Emissão (`redesign/emission-rail`) — a mais ousada

**Tese:** abandona chips coloridos de status e a própria grade de cards em
favor de um único eixo ranqueado, porque a única pergunta que importa é o
que fecha primeiro. Esta direção venceu um "desafiante" do catálogo
(inspirado em espectroscopia de emissão) contra a própria lista de
candidatos do modelo, por vencer nos dois eixos de julgamento: identificação
com o público (linhas de emissão são cultura central de física/óptica) e
clareza de produto (estado por forma de linha, não por cor, e o trilho
espelha a estrutura real do dado: uma lista ranqueada por urgência).

**Mundo visual:**
- Fundo carvão procedural (`#0d0d0e`, com grão via SVG turbulence), texto
  osso (`#f4f1ea`/`#c9c5ba`/`#8f8b80`, tudo tingido do próprio matiz, nunca
  cinza puro). Cor só existe como linhas hairline de "emissão": cada
  oportunidade é um traço vertical fino, posicionado no eixo horizontal de
  tempo pela data real do prazo.
- Estado por **forma da linha**, nunca por cor: traço sólido inteiro =
  aberta; tracejado = fecha em ≤5 dias; meia-altura = interdisciplinar/
  prioridade menor; riscada = expirada. Um único traço dobrado e
  brilhante em amarelo-sódio (`#ffcc33`) marca a oportunidade mais urgente.
- Tipografia: JetBrains Mono (eixo do trilho, ficha de dados) + IBM Plex
  Sans (prosa do resumo) — auto-hospedadas em `fonts/`.
- Composição: um único trilho horizontal full-bleed; a ficha da
  oportunidade líder já vem "florescida" acima do trilho por padrão;
  clicar/focar qualquer traço floresce seu detalhe completo (título,
  instituição, área, prazo, resumo, link) enquanto os demais recuam a
  hairlines esmaecidos. Filtros de modalidade viram toggles de densidade de
  traços, não chips. Inclui algoritmo de desvio de colisão para prazos
  coincidentes, e o layout não assume um número fixo de itens.

**Preservado:** filtro de modalidade (reimaginado como toggles), lógica de
urgência (≤5 dias, mapeada para tracejado/dobrado), atribuição de rodapé,
contrato de dados.

**Ver localmente:**
```bash
git checkout redesign/emission-rail
python -m http.server 8000
# http://localhost:8000
```

---

## Comparando as três

| | V1 · Caderno de Laboratório | V2 · Tabela Periódica | V3 · Trilho de Emissão |
|---|---|---|---|
| Registro | pessoal, analógico, quente | clínico, referência, poster | técnico, instrumento, escuro |
| Estrutura | cards de índice colados | grade de blocos tipo elemento | um único eixo/trilho ranqueado |
| Sinal de urgência | laranja-marca-texto + numeral gigante | vermelho-sinal reservado | forma da linha (tracejado/dobrado) |
| Risco | mais ilustrativo, menos denso | mais neutro, menos memorável | mais não-convencional; exige 1 clique a mais para ver detalhe de item não-líder |
| Boa escolha se... | você quer abrir o site e sentir "meu caderno" | você quer o padrão mais rápido de escanear/comparar | você só liga pra "o que fecha primeiro" e curte algo mais autoral |

## Próximos passos sugeridos

1. Abra as três branches localmente (comandos acima) e escolha uma — ou peça
   ajustes pontuais em qualquer uma antes de decidir.
2. A branch escolhida pode virar `main` via merge/rebase; as outras duas
   ficam como referência ou são descartadas.
3. Nenhuma das três tem `DESIGN.md` formal ainda — depois de escolher,
   `/impeccable document` na branch vencedora grava o sistema visual
   definitivo para orientar edições futuras.
