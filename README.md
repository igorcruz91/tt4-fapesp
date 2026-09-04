# Radar de Bolsas TT — FAPESP

MVP estático (V1) que coleta oportunidades de bolsas FAPESP nas modalidades
**Treinamento Técnico IV (TT-IV)**, **IV-A (TT-IV-A)** e **V (TT-V)**, e
publica um site simples com a lista sempre atualizada.

Fonte: https://fapesp.br/oportunidades/mais-recentes/

## Como funciona

1. `scraper/fetch_fapesp.py` baixa a página de oportunidades (HTML renderizado
   no servidor, sem necessidade de navegador/JS) e filtra apenas os itens das
   três modalidades de interesse, gerando `data/oportunidades.json`.
2. `index.html` é um site estático (sem build) que lê esse JSON e mostra os
   cards com filtro por modalidade.
3. `.github/workflows/scrape.yml` roda o scraper 1x/dia via GitHub Actions,
   comita o JSON se houver mudança, e publica o site no GitHub Pages.

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
