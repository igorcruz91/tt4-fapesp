# Propostas de Projeto — Radar de Oportunidades Acadêmicas

Objetivo: uma plataforma web que agrega oportunidades de bolsas de PD (pós-doutorado/pesquisa e desenvolvimento) e doutorado, vindas de fontes como FAPESP e LinkedIn, filtradas pela área de atuação/formação do usuário, mostrando apenas oportunidades recentes com inscrições ainda abertas.

Abaixo estão três abordagens com escopo, arquitetura e trade-offs diferentes. Todas resolvem o mesmo problema central, mas variam em complexidade de implementação, manutenção e "inteligência" do sistema.

---

## Versão 1 — MVP Estático (baixo esforço, baixa manutenção)

**Ideia:** um scraper agendado que roda periodicamente, gera um arquivo de dados (JSON) e publica um site estático simples que lê esse arquivo. Sem backend, sem banco de dados.

**Como funciona:**
1. Um script (Python, rodando via cron/GitHub Actions) acessa páginas públicas de editais da FAPESP (e possivelmente feeds/RSS ou buscas específicas do LinkedIn Jobs) e extrai: título, instituição, área, nível (doutorado/PD), data de publicação, prazo de inscrição, link original.
2. O script filtra automaticamente por palavras-chave da sua área/formação e descarta oportunidades com prazo vencido.
3. Os dados filtrados são salvos em um `oportunidades.json`, versionado no repositório.
4. Um site estático (HTML/CSS/JS puro, ou um artifact) lê esse JSON e exibe cards com as oportunidades, com filtros simples (área, nível, prazo) feitos em JavaScript no navegador.
5. GitHub Actions roda o scraper 1x por dia e faz commit automático do JSON atualizado, republicando o site (GitHub Pages).

**Vantagens:**
- Muito rápido de construir e colocar no ar.
- Zero custo de infraestrutura (GitHub Pages + Actions no plano gratuito).
- Sem banco de dados para manter.

**Desvantagens:**
- Scraping do LinkedIn é frágil e pode violar termos de uso — melhor focar em FAPESP e outras fontes abertas (editais de universidades, CNPq, Capes) nessa versão.
- Sem histórico consultável nem notificações proativas (você precisa acessar o site para ver novidades).
- Filtro de relevância é só por palavra-chave, sem entender contexto.

**Ideal se:** você quer algo funcional em poucos dias e não se importa em checar o site manualmente.

---

## Versão 2 — Aplicação Web Completa com Backend (equilíbrio)

**Ideia:** uma aplicação web tradicional com backend, banco de dados e agendador de tarefas, permitindo histórico, busca avançada, autenticação e notificações por e-mail.

**Como funciona:**
1. **Backend** (Python/FastAPI ou Node/Express) com um banco de dados (PostgreSQL/SQLite) armazenando as oportunidades coletadas.
2. **Coletores (workers)** rodando em background (via APScheduler, Celery, ou cron) para cada fonte:
   - FAPESP: scraping estruturado da página de "Bolsas e Auxílios" / chamadas abertas.
   - LinkedIn: uso da API oficial (se disponível/aprovada) ou integração via serviços de agregação de vagas (ex.: RSS de buscas salvas), evitando scraping direto por questões de ToS.
   - Fontes adicionais: CNPq, CAPES, editais de universidades específicas, Euraxess (para bolsas internacionais).
3. Cada oportunidade é normalizada em um schema comum (título, instituição, área, nível, prazo, fonte, link) e deduplicada.
4. **Frontend** (React/Vue) consumindo uma API REST/GraphQL, com:
   - Filtros por área, nível (PD/doutorado), instituição, prazo.
   - Busca textual.
   - Marcação de "favoritos" e "já me candidatei".
5. **Notificações**: e-mail semanal (ou diário) resumindo novas oportunidades relevantes, via um serviço tipo SendGrid ou SMTP simples.
6. Autenticação simples (login único, já que é uso pessoal) para persistir favoritos/preferências.

**Vantagens:**
- Histórico completo e busca robusta.
- Notificações proativas — você não precisa lembrar de checar o site.
- Arquitetura extensível: fácil adicionar novas fontes no futuro.

**Desvantagens:**
- Mais componentes para manter (backend, banco, workers, deploy).
- Exige hospedagem (Railway, Render, Fly.io, VPS) — pode ter custo baixo, mas não é gratuito como a Versão 1.
- Maior tempo de desenvolvimento inicial.

**Ideal se:** você quer uma ferramenta robusta de uso contínuo, com notificações e histórico, e não se importa em investir mais tempo/infra.

---

## Versão 3 — Curadoria Inteligente com LLM (alta sofisticação)

**Ideia:** tudo da Versão 2, mas com uma camada de IA que entende seu perfil (formação, currículo, interesses de pesquisa) e faz *matching* semântico das oportunidades, em vez de depender só de palavras-chave — reduzindo ruído e trazendo oportunidades que um filtro simples deixaria passar.

**Como funciona:**
1. Mesma base de coleta multi-fonte da Versão 2 (FAPESP, LinkedIn via meios permitidos, CNPq, Euraxess, editais de universidades).
2. Você fornece um "perfil" (resumo da sua formação, linha de pesquisa, palavras-chave de interesse, opcionalmente seu currículo/lattes).
3. Cada oportunidade coletada é processada por um LLM (via API Claude) que:
   - Extrai e padroniza campos de editais em formatos variados/não estruturados (texto livre de PDF, HTML bagunçado etc.).
   - Calcula uma pontuação de relevância comparando a descrição da oportunidade com seu perfil (via embeddings + similaridade semântica, ou prompt direto de classificação).
   - Gera um resumo curto de "por que essa oportunidade é relevante para você".
4. O frontend exibe as oportunidades ordenadas por relevância (não só por data), com o resumo gerado pela IA e destaque para prazos próximos do vencimento.
5. Opcional: um chat na própria plataforma onde você pergunta "quais bolsas de PD em [tema] fecham esse mês?" e a IA responde consultando a base.

**Vantagens:**
- Melhor sinal/ruído: prioriza o que realmente combina com seu perfil, mesmo que a oportunidade não use as palavras-chave exatas.
- Lida bem com editais em formatos inconsistentes (PDFs, páginas mal estruturadas), comuns em editais acadêmicos.
- Evolui com você: pode reajustar o perfil e ver a pontuação de relevância mudar.

**Desvantagens:**
- Maior complexidade técnica e de custo (chamadas de API de LLM têm custo por uso, embora baixo em escala pessoal).
- Precisa de mais cuidado com prompt design e validação (evitar alucinação nos dados extraídos, ex.: datas erradas).
- É a versão com maior tempo de desenvolvimento entre as três.

**Ideal se:** você quer o sistema mais "esperto" possível, disposto a lidar com uma camada extra de IA e não se importa com o custo/tempo adicional.

---

## Resumo comparativo

| Critério | V1 — MVP Estático | V2 — Web Completa | V3 — Curadoria com IA |
|---|---|---|---|
| Tempo de implementação | Baixo (dias) | Médio (semanas) | Alto (semanas+) |
| Infra/custo | Gratuito | Baixo custo | Baixo custo + uso de API LLM |
| Notificações proativas | Não | Sim (e-mail) | Sim (e-mail + chat) |
| Qualidade do filtro | Palavra-chave | Palavra-chave + categorização manual | Semântico, baseado em perfil |
| Manutenção | Muito baixa | Média | Média-alta |
| Fontes práticas | FAPESP + editais abertos | FAPESP + CNPq + Euraxess + LinkedIn (via API/RSS) | Mesmas da V2, com extração via LLM |

**Observação sobre o LinkedIn:** em todas as versões, scraping direto do LinkedIn é arriscado (viola termos de uso e é tecnicamente instável). As alternativas mais seguras são: usar buscas salvas com feed RSS, a API oficial do LinkedIn (acesso restrito), ou serviços agregadores de vagas acadêmicas que já indexam o LinkedIn.

---

## Próximos passos sugeridos

1. Escolher uma das três versões (ou um ponto de partida na V1 com evolução planejada para V2/V3).
2. Definir o perfil de área/formação que servirá de filtro inicial.
3. Levantar as fontes específicas de dados (URLs de editais FAPESP, buscas do LinkedIn, outras agências de fomento).
