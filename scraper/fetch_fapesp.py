"""Coleta oportunidades de Treinamento Técnico (TT-IV, TT-IV-A, TT-V) do site da FAPESP.

Fonte: https://fapesp.br/oportunidades/mais-recentes/
A página lista todas as oportunidades abertas em um único HTML server-side
(sem paginação), com cada item marcado com uma classe `tipo_N` que identifica
a modalidade e uma classe `pt`/`en` que identifica o idioma da entrada.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://fapesp.br/oportunidades/mais-recentes/"
BASE_URL = "https://fapesp.br"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "oportunidades.json"

# Mapeamento das classes tipo_N (extraídas do filtro lateral da página) para as
# modalidades que interessam a este projeto.
MODALIDADES = {
    "tipo_7": "TT-IV",
    "tipo_8": "TT-IV-A",
    "tipo_9": "TT-V",
}

# Mapeamento das classes area_N (extraídas do filtro lateral "Área" da página)
# para o nome da área em português.
AREAS = {
    "area_52": "Administração",
    "area_44": "Agronomia",
    "area_54": "Arquitetura e Urbanismo",
    "area_4": "Astronomia",
    "area_17": "Biofísica",
    "area_9": "Biologia Geral",
    "area_16": "Bioquímica",
    "area_3": "Ciência da Computação",
    "area_57": "Ciência da Informação",
    "area_50": "Ciência e Tecnologia de Alimentos",
    "area_51": "Direito",
    "area_13": "Ecologia",
    "area_43": "Educação Física",
    "area_33": "Engenharia",
    "area_37": "Farmácia",
    "area_18": "Farmacologia",
    "area_5": "Física",
    "area_15": "Fisiologia",
    "area_10": "Genética",
    "area_7": "Geociências",
    "area_69": "Geografia",
    "area_68": "História",
    "area_77": "Interdisciplinar",
    "area_1": "Matemática",
    "area_35": "Medicina",
    "area_48": "Medicina Veterinária",
    "area_8": "Oceanografia",
    "area_36": "Odontologia",
    "area_70": "Psicologia",
    "area_6": "Química",
    "area_45": "Recursos Florestais e Engenharia Florestal",
    "area_40": "Saúde Coletiva",
    "area_78": "Todas as áreas",
}

# Áreas que, por si só, já são consideradas núcleo do perfil (física,
# matemática, computação e áreas diretamente adjacentes) — qualquer
# oportunidade nessas áreas é mantida independentemente do texto.
CORE_AREAS = {"area_5", "area_1", "area_3", "area_17", "area_4"}

# Termos (normalizados, sem acento, minúsculos) que indicam interseção com o
# perfil de física / matemática / computação / ciência de dados / IA /
# modelagem, usados para incluir oportunidades de áreas interdisciplinares
# que tenham relação real com essas especialidades. É um filtro simples por
# palavra-chave (V1) — ajuste esta lista conforme o radar errar por falta ou
# excesso de resultados.
RELEVANCE_KEYWORDS = [
    "computacional",
    "inteligencia artificial",
    "aprendizado de maquina",
    "aprendizado profundo",
    "machine learning",
    "deep learning",
    "rede neural",
    "redes neurais",
    "processamento de linguagem natural",
    "visao computacional",
    "ciencia de dados",
    "analise de dados",
    "mineracao de dados",
    "big data",
    "algoritmo",
    "simulacao",
    "simulacoes",
    "modelagem",
    "bioinformatica",
    "geoprocessamento",
    "processamento de sinais",
    "series temporais",
    "sistemas complexos",
    "dinamica de sistemas",
    "ciencia da computacao",
    "engenharia de software",
    "robotica",
    "estatistica",
    "bioestatistica",
    "probabilidade",
    "algebra linear",
    "equacoes diferenciais",
    "metodos numericos",
    "analise numerica",
    "matematica aplicada",
    "astrofisica",
    "cosmologia",
    "mecanica quantica",
    "mecanica estatistica",
    "termodinamica",
    "eletromagnetismo",
    "fisica de particulas",
    "fisica teorica",
    "fisica experimental",
    "in silico",
    "dft",
    "qm/mm",
]


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def is_relevant(area_class: str | None, title: str, summary: str) -> bool:
    if area_class in CORE_AREAS:
        return True
    haystack = normalize(f"{title} {summary}")
    return any(keyword in haystack for keyword in RELEVANCE_KEYWORDS)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_html() -> str:
    resp = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_deadline(raw: str) -> tuple[str, str]:
    """Recebe 'dd/mm/aaaa' e retorna (iso, display)."""
    raw = raw.strip()
    match = re.match(r"(\d{2})/(\d{2})/(\d{4})", raw)
    if not match:
        return "", raw
    day, month, year = match.groups()
    iso = f"{year}-{month}-{day}"
    return iso, raw


def extract_field(text_principal, label: str) -> str:
    """Extrai o valor após um <strong>label:</strong> dentro de text_principal."""
    for strong in text_principal.find_all("strong"):
        if strong.get_text(strip=True).rstrip(":").lower() == label.lower():
            value = strong.next_sibling
            parts = []
            while value is not None and getattr(value, "name", None) != "br":
                parts.append(str(value))
                value = value.next_sibling
            text = html.unescape(re.sub(r"<[^>]+>", "", "".join(parts)))
            return text.strip()
    return ""


def parse_opportunities(raw_html: str) -> list[dict]:
    soup = BeautifulSoup(raw_html, "html.parser")
    items = []

    for li in soup.select("li.box_col.pt"):
        classes = li.get("class", [])
        modalidade_class = next((c for c in classes if c in MODALIDADES), None)
        if modalidade_class is None:
            continue
        area_class = next((c for c in classes if c in AREAS), None)

        link_tag = li.find("a", class_="link_col")
        if link_tag is None:
            continue

        title_tag = li.find("strong", class_="title")
        text_principal = li.find("span", class_="text-principal")
        text_resumo = li.find("span", class_="text-resumo")

        title = title_tag.get_text(strip=True) if title_tag else ""
        institution = extract_field(text_principal, "Instituição") if text_principal else ""
        city = extract_field(text_principal, "Cidade") if text_principal else ""
        deadline_raw = extract_field(text_principal, "Inscrições até") if text_principal else ""
        deadline_iso, deadline_display = parse_deadline(deadline_raw)
        summary = text_resumo.get_text(strip=True) if text_resumo else ""

        if not is_relevant(area_class, title, summary):
            continue

        url = urljoin(BASE_URL + "/", link_tag["href"].replace("Control/../", ""))
        id_match = re.search(r"/(\d+)/?$", url)
        opportunity_id = id_match.group(1) if id_match else url

        items.append(
            {
                "id": opportunity_id,
                "title": title,
                "modality": MODALIDADES[modalidade_class],
                "area": AREAS.get(area_class, ""),
                "interdisciplinary": area_class not in CORE_AREAS,
                "institution": institution,
                "city": city,
                "deadline": deadline_iso,
                "deadline_display": deadline_display,
                "summary": summary,
                "url": url,
            }
        )

    items.sort(key=lambda o: o["deadline"] or "9999-99-99")
    return items


def main() -> int:
    raw_html = fetch_html()
    opportunities = parse_opportunities(raw_html)

    payload = {
        "source": SOURCE_URL,
        "scraped_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "modalities": sorted(set(MODALIDADES.values())),
        "count": len(opportunities),
        "opportunities": opportunities,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"{len(opportunities)} oportunidades salvas em {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
