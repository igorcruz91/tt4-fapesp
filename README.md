# Radar de Bolsas TT — FAPESP

MVP estático (V1) que coleta oportunidades de bolsas FAPESP nas modalidades
**Treinamento Técnico IV (TT-IV)**, **IV-A (TT-IV-A)** e **V (TT-V)**, e
publica um site simples com a lista sempre atualizada.

Fonte: https://fapesp.br/oportunidades/mais-recentes/

## Como funciona

1. `scraper/fetch_fapesp.py` baixa a página de oportunidades (HTML renderizado
   no servidor, sem necessidade de navegador/JS), filtra os itens das três
   modalidades de interesse e depois aplica um **filtro de relevância por
   perfil** (veja abaixo), gerando `data/oportunidades.json` só com o que
   passou nos dois filtros.
2. `index.html` é um site estático (sem build) que lê esse JSON e mostra os
   cards com filtro por modalidade.
3. `.github/workflows/scrape.yml` roda o scraper 1x/dia via GitHub Actions,
   comita o JSON se houver mudança, e publica o site no GitHub Pages.

## Filtro de relevância por perfil

O perfil considerado é: física, matemática (com mestrado em física
computacional), ciência de dados, inteligência artificial e modelagem.
Áreas interdisciplinares entram desde que o texto da oportunidade mostre
alguma interseção real com essas especialidades.

Isso é implementado em `scraper/fetch_fapesp.py` com duas regras (ver
`CORE_AREAS` e `RELEVANCE_KEYWORDS`):

- **Área núcleo**: se a FAPESP já classifica a oportunidade em Física,
  Matemática, Ciência da Computação, Biofísica ou Astronomia, ela entra
  direto, sem precisar de palavra-chave.
- **Palavra-chave**: para qualquer outra área (ex.: Engenharia, Agronomia,
  Medicina, Química...), a oportunidade só entra se o título/resumo mencionar
  termos como "computacional", "inteligência artificial", "aprendizado de
  máquina", "simulação", "modelagem", "bioinformática", "estatística", etc.
  Itens incluídos por essa via vêm marcados como `"interdisciplinary": true`
  no JSON e aparecem com a tag "(interdisciplinar)" no site.

Esse é um filtro simples por palavra-chave (compatível com o escopo do V1,
sem LLM). Se o radar passar a errar por falta ou excesso de resultados,
ajuste as listas `CORE_AREAS`/`RELEVANCE_KEYWORDS` no topo do script.

## Rodar localmente

```bash
pip install -r requirements.txt
python scraper/fetch_fapesp.py
```

Depois abra `index.html` num servidor local (por exemplo `python -m http.server`)
— não abra o arquivo direto (`file://`), pois o `fetch` do JSON é bloqueado
por CORS nesse esquema.

## Publicar no GitHub Pages

Após dar push para um repositório no GitHub:

1. Em **Settings → Pages**, defina a fonte como **GitHub Actions**.
2. O workflow `scrape.yml` cuida do resto (roda diariamente às 09:00 BRT e
   também a cada push em `main`).
