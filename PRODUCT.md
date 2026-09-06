# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Uso pessoal: o único usuário é o próprio dono do projeto, um pesquisador/estudante com perfil em física, matemática (com mestrado em física computacional), ciência de dados, inteligência artificial e modelagem. Ele acessa o site periodicamente para verificar quais bolsas FAPESP das modalidades Treinamento Técnico IV (TT-IV), IV-A (TT-IV-A) e V (TT-V) estão abertas e são relevantes ao seu perfil, e quais prazos estão próximos do vencimento.

## Product Purpose

Poupar o trabalho manual de checar a página de oportunidades da FAPESP todos os dias: um scraper roda 1x/dia, filtra por modalidade e por relevância de área/perfil, e publica um site simples e sempre atualizado com as oportunidades abertas. Sucesso é o usuário conseguir, em segundos, ver se há alguma bolsa nova relevante e quanto tempo falta para o prazo, sem precisar visitar o site da FAPESP nem ler editais irrelevantes.

## Positioning

Um agregador pessoal de nicho: ao contrário de checar manualmente fapesp.br/oportunidades (que lista todas as modalidades e áreas), este site já entrega só o subconjunto (TT-IV/IV-A/V + relevância de perfil) que importa para este usuário específico, com zero infraestrutura e atualização automática diária.

## Operating Context

- Fonte de dados: https://fapesp.br/oportunidades/mais-recentes/ (HTML renderizado no servidor).
- `scraper/fetch_fapesp.py` baixa a página, filtra por modalidade e por perfil (`CORE_AREAS` / `RELEVANCE_KEYWORDS`), e gera `data/oportunidades.json`.
- `.github/workflows/scrape.yml` roda o scraper 1x/dia (09:00 BRT) e a cada push em `main`, comita o JSON se mudar, e publica via GitHub Pages.
- `index.html` é estático (sem build, sem framework) e lê `data/oportunidades.json` via `fetch`; precisa ser servido por HTTP (não funciona em `file://` por causa de CORS).
- Desenvolvimento local usa um `.venv` Python para o scraper; o site é servido com `python -m http.server` durante o desenvolvimento.

## Capabilities and Constraints

- Site 100% estático: sem backend, sem banco de dados, sem autenticação (uso individual, sem necessidade de login).
- Filtro de relevância é por palavra-chave (não semântico/LLM) e é **fixo por enquanto**: mudanças de perfil exigem editar `CORE_AREAS`/`RELEVANCE_KEYWORDS` diretamente no scraper, sem UI de configuração.
- Sem notificações proativas (e-mail, push): o usuário precisa abrir o site para ver novidades.
- Escopo atual corresponde à "Versão 1 — MVP Estático" de `propostas-projeto.md`. As versões V2 (backend, notificações, multi-fonte) e V3 (curadoria com LLM) descritas nesse documento são exploratórias e **não** representam direção confirmada; não devem influenciar decisões de design agora.
- Fonte de dados é só FAPESP nesta versão (LinkedIn/CNPq/Euraxess mencionados em `propostas-projeto.md` não estão implementados).

## Evidence on Hand

- Dados reais de oportunidades já existem em `data/oportunidades.json`, atualizados diariamente pelo scraper — não é necessário inventar dados de exemplo.
- Nenhum depoimento, case study ou material de marca além do nome já usado no site ("Radar de Bolsas TT — FAPESP").

## Product Principles

- Zero atrito: o usuário deve entender em segundos se há algo novo e relevante, sem precisar ler cada edital por inteiro.
- Zero infraestrutura: qualquer decisão de design/arquitetura deve continuar compatível com site estático + GitHub Pages + GitHub Actions, sem exigir servidor, banco de dados ou custo recorrente.
- Sinal sobre ruído: como o filtro já reduziu a lista à modalidade e ao perfil corretos, a interface deve priorizar prazo e relevância imediata em vez de forçar navegação/busca adicional.
- Confiabilidade da fonte: o dado exibido deve sempre refletir fielmente o que está publicado pela FAPESP (título, instituição, prazo, link original), já que o usuário toma decisões de inscrição com base nisso.
