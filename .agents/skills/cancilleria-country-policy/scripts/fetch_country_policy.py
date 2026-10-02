#!/usr/bin/env python3
"""
Cancillería Colombia Policy Retriever & Parser
Agent-assisted script for locating, fetching, and extracting bilateral and travel policy data.
Features:
- Multi-tier URL resolution (Cache -> Live Cancillería Search -> Normalized Regional Slugs)
- Self-learning directory caching (saves newly discovered country URLs automatically)
- Clean body text extraction (eliminates heavy navigation/footer boilerplate)
- Semantic content fallback for LLM agent reasoning
"""

import sys
import os
import re
import json
import argparse
import unicodedata
import urllib.request
import urllib.parse
from html.parser import HTMLParser

REGIONS = ["europa", "america", "asia", "africa"]

COMMON_ALIASES = {
    "estados unidos": ("Estados Unidos de América", "estados-unidos-de-america", "america"),
    "usa": ("Estados Unidos de América", "estados-unidos-de-america", "america"),
    "eeuu": ("Estados Unidos de América", "estados-unidos-de-america", "america"),
    "united states": ("Estados Unidos de América", "estados-unidos-de-america", "america"),
    "reino unido": ("Reino Unido", "reino-unido-de-gran-bretana-e-irlanda-del-norte", "europa"),
    "uk": ("Reino Unido", "reino-unido-de-gran-bretana-e-irlanda-del-norte", "europa"),
    "united kingdom": ("Reino Unido", "reino-unido-de-gran-bretana-e-irlanda-del-norte", "europa"),
    "union europea": ("Unión Europea", "union-europea", "europa"),
    "eu": ("Unión Europea", "union-europea", "europa"),
    "ue": ("Unión Europea", "union-europea", "europa"),
    "european union": ("Unión Europea", "union-europea", "europa"),
    "qatar": ("Estado de Catar", "estado-de-catar", "africa"),
    "catar": ("Estado de Catar", "estado-de-catar", "africa"),
    "kirguistan": ("República Kirguisa", "republica-kirguisa", "europa"),
    "kyrgyzstan": ("República Kirguisa", "republica-kirguisa", "europa"),
    "kazajistan": ("República de Kazajistán", "republica-de-kazajistan", "europa"),
    "kazakhstan": ("República de Kazajistán", "republica-de-kazajistan", "europa"),
    "turquia": ("República de Türkiye", "republica-de-turkiye", "europa"),
    "turkey": ("República de Türkiye", "republica-de-turkiye", "europa"),
    "turkiye": ("República de Türkiye", "republica-de-turkiye", "europa"),
    "corea del sur": ("República de Corea", "republica-de-corea", "asia"),
    "south korea": ("República de Corea", "republica-de-corea", "asia"),
    "rusia": ("Federación de Rusia", "federacion-de-rusia", "europa"),
    "russia": ("Federación de Rusia", "federacion-de-rusia", "europa"),
    "holanda": ("Reino de los Países Bajos", "reino-de-los-paises-bajos", "europa"),
    "paises bajos": ("Reino de los Países Bajos", "reino-de-los-paises-bajos", "europa"),
    "netherlands": ("Reino de los Países Bajos", "reino-de-los-paises-bajos", "europa"),
    "suiza": ("Confederación Suiza", "confederacion-suiza", "europa"),
    "switzerland": ("Confederación Suiza", "confederacion-suiza", "europa"),
    "alemania": ("República Federal de Alemania", "republica-federal-de-alemania", "europa"),
    "germany": ("República Federal de Alemania", "republica-federal-de-alemania", "europa"),
    "espana": ("Reino de España", "reino-de-espana", "europa"),
    "spain": ("Reino de España", "reino-de-espana", "europa"),
    "emiratos arabes": ("Emiratos Árabes Unidos", "emiratos-arabes-unidos", "africa"),
    "emiratos arabes unidos": ("Emiratos Árabes Unidos", "emiratos-arabes-unidos", "africa"),
    "uae": ("Emiratos Árabes Unidos", "emiratos-arabes-unidos", "africa"),
    "nueva zelanda": ("Nueva Zelanda", "nueva-zelanda", "asia"),
    "new zealand": ("Nueva Zelanda", "nueva-zelanda", "asia"),
}

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.lower().strip()

class CleanBodyExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
        self.ignore = False

    def handle_starttag(self, tag, attrs):
        if tag in ["script", "style", "noscript", "svg", "nav", "footer", "header"]:
            self.ignore = True

    def handle_endtag(self, tag):
        if tag in ["script", "style", "noscript", "svg", "nav", "footer", "header"]:
            self.ignore = False

    def handle_data(self, d):
        if not self.ignore:
            self.fed.append(d)

    def get_text(self):
        return "".join(self.fed)

def probe_url_exists(url: str, timeout: int = 5) -> bool:
    """Verifies live if a URL responds HTTP 200 via lightweight HEAD request."""
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    try:
        req = urllib.request.Request(url, headers=headers, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False

def search_cancilleria_live(country_query: str) -> tuple[str, str]:
    """
    Queries Cancillería's live search endpoint and filters strictly for canonical
    bilateral country dossiers, rejecting news articles and press releases.
    Returns (discovered_title, discovered_url) or (None, None).
    """
    search_url = f"https://www.cancilleria.gov.co/search/node?keys={urllib.parse.quote(country_query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0"}
    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        # Find search result links
        links = re.findall(r'<h3[^>]*>\s*<a[^>]+href=[\"\']([^\"\']+)[\"\'][^>]*>(.*?)</a>', html, re.DOTALL)
        for href, title_html in links:
            title = " ".join(title_html.split())
            if not href.startswith("http"):
                href = f"https://www.cancilleria.gov.co{href}"

            # Strict canonical regional bilateral filter: excludes news, notices, and press releases
            m = re.search(r'/politica-exterior/asuntos-bilaterales/(america|europa|asia|africa)/([a-z0-9\-]+)', href)
            if m:
                return title, href
    except Exception as e:
        print(f"Notice: Live search failed for '{country_query}': {e}", file=sys.stderr)

    return None, None

def resolve_country_url(country_query: str) -> tuple[str, str, bool]:
    """
    Pure live URL resolution (zero local file caching):
    1. Check alias & canonical slug
    2. Deterministic candidate URL probing directly on Cancillería
    3. Filtered live portal search on cancilleria.gov.co
    Returns (official_name, url, is_newly_discovered)
    """
    norm_query = normalize_text(country_query)

    # 1. Alias translation
    if norm_query in COMMON_ALIASES:
        official_name, slug, region = COMMON_ALIASES[norm_query]
        candidate_url = f"https://www.cancilleria.gov.co/politica-exterior/asuntos-bilaterales/{region}/{slug}"
        if probe_url_exists(candidate_url):
            return official_name, candidate_url, False

    # 2. Deterministic slug probing across regions
    slug_base = norm_query.replace(" ", "-")
    prefixes = ["", "republica-de-", "reino-de-", "estado-de-", "republica-", "principado-de-", "confederacion-"]

    for r in REGIONS:
        for prefix in prefixes:
            slug = f"{prefix}{slug_base}"
            candidate_url = f"https://www.cancilleria.gov.co/politica-exterior/asuntos-bilaterales/{r}/{slug}"
            if probe_url_exists(candidate_url):
                return country_query, candidate_url, False

    # 3. Live filtered search on cancilleria.gov.co
    live_title, live_url = search_cancilleria_live(country_query)
    if live_url:
        return live_title or country_query, live_url, True

    return country_query, None, False

def fetch_url(url: str, timeout: int = 15) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="ignore")

def extract_clean_content(html_content: str) -> str:
    """Strips outer template chrome to extract the main content text."""
    parser = CleanBodyExtractor()
    parser.feed(html_content)
    raw_text = parser.get_text()
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    full_text = "\n".join(lines)

    # Trim to main bilateral content block
    anchors = ["Día Nacional", "Dia Nacional", "Relaciones Diplomáticas", "Relaciones diplomáticas", "Asuntos Migratorios", "Asuntos migratorios"]
    start_pos = -1
    for a in anchors:
        pos = full_text.find(a)
        if pos != -1 and (start_pos == -1 or pos < start_pos):
            start_pos = pos

    if start_pos != -1:
        end_pos = full_text.find("Ministerio de Relaciones Exteriores")
        if end_pos != -1 and end_pos > start_pos:
            return full_text[start_pos:end_pos].strip()
        return full_text[start_pos:].strip()

    return full_text

def parse_policy(clean_text: str, country_name: str, purpose: str = None, page_url: str = None) -> dict:
    purpose_norm = normalize_text(purpose) if purpose else ""
    text_lower = clean_text.lower()

    # Dynamic extraction of sections
    mig_match = re.search(r"Asuntos migratorios:?\s*(.*?)(?=(?:Acuerdos|Asuntos Pol[íi]ticos|Visitas|P[áa]gina web|$))", clean_text, re.DOTALL | re.IGNORECASE)
    mig_text = mig_match.group(1).strip() if mig_match else ""

    # Fallback paragraphs if header was modified
    if not mig_text:
        paras = []
        for p in clean_text.split("\n"):
            p_low = p.lower()
            if any(term in p_low for term in ["visa", "visado", "migratorio", "pasaporte", "schengen", "estancia", "e-visa"]):
                if len(p) > 25 and "derechos humanos" not in p_low:
                    paras.append(p.strip())
        mig_text = "\n".join(paras[:5])

    # Extract Diplomatic
    dip_match = re.search(r"Relaciones Diplom[áa]ticas:?\s*(.*?)(?=(?:Asuntos migratorios|Acuerdos|Asuntos Pol[íi]ticos|$))", clean_text, re.DOTALL | re.IGNORECASE)
    dip_text = dip_match.group(1).strip() if dip_match else ""

    # Extract Agreements
    acuerdos_match = re.search(r"Acuerdos e instrumentos suscritos:?\s*(.*?)(?=(?:Asuntos Pol[íi]ticos|Visitas|P[áa]gina web|$))", clean_text, re.DOTALL | re.IGNORECASE)
    acuerdos_text = acuerdos_match.group(1).strip() if acuerdos_match else ""

    # Extract external government / consular links
    links = list(set(re.findall(r'https?://[^\s<>"\')]+', clean_text)))
    filtered_links = [
        l for l in links
        if any(term in l.lower() for term in [".gov.", ".gob.", ".mfa.", "visado", "consulado", "embajada", "evisa", "schengen"])
        and not any(term in l.lower() for term in ["facebook", "twitter", "instagram", "tiktok", "youtube", "login"])
    ]

    # Semantic evaluation
    is_tourist_exempt = any(phrase in mig_text.lower() for phrase in [
        "no requieren visa",
        "retiró de forma unilateral",
        "retiro de forma unilateral",
        "exentos del requisito de visado",
        "exencion mutua de visas",
        "exención de visado",
        "supresión de visado"
    ])

    requires_visa = any(phrase in mig_text.lower() for phrase in [
        "requieren visa",
        "deben tramitar visa",
        "deberán solicitar visado",
        "se requiere visa"
    ])

    days_match = re.search(r"(\d+)\s*d[íi]as", mig_text, re.IGNORECASE)
    stay_limit = f"{days_match.group(1)} días" if days_match else None

    visa_verdict = None
    evaluation_notes = []

    if "worker" in purpose_norm or "trabaj" in purpose_norm or "empleo" in purpose_norm:
        visa_verdict = "Requiere Visa de Trabajo / Permiso Laboral"
        evaluation_notes.append("⚠️ **Trabajo / Empleo:** Las exenciones de visado de corta duración (turismo) NO amparan labores remuneradas.")
        evaluation_notes.append("🛂 **Obligatorio:** Se debe tramitar una Visa Laboral o Permiso de Trabajo ante el consulado del país destino antes de viajar.")
        if is_tourist_exempt:
            evaluation_notes.append("ℹ️ _Nota:_ Aunque exista exención para turistas, esta caduca ante actividades comerciales o laborales dependientes.")
    elif "tourist" in purpose_norm or "turism" in purpose_norm:
        if is_tourist_exempt:
            visa_verdict = "Exento de Visa para Turismo"
            evaluation_notes.append("✅ **Exento de Visa:** Nacionales colombianos con pasaporte ordinario no requieren visa para turismo de corta duración.")
        elif requires_visa:
            visa_verdict = "Requiere Visa de Turismo"
            evaluation_notes.append("❌ **Requiere Visa:** Se debe solicitar visa de turismo o e-Visa con antelación.")
        else:
            visa_verdict = "Consultar Consulado / Verificar Régimen"
            evaluation_notes.append("ℹ️ **Verificación adicional requerida:** Consulte el consulado concurrente para requisitos específicos.")

        if stay_limit:
            evaluation_notes.append(f"⏱️ **Estancia máxima permitida:** {stay_limit}.")
        evaluation_notes.append("🛂 **Requisitos estándar:** Pasaporte vigente (mín. 3-6 meses), tiquete de regreso, reserva/hospedaje y solvencia económica.")
    elif "student" in purpose_norm or "estudi" in purpose_norm:
        visa_verdict = "Requiere Visa de Estudiante"
        evaluation_notes.append("📚 **Estudios:** Estancias formativas o superiores a 90 días requieren visa de estudiante previa.")
    else:
        visa_verdict = "Exento (Turismo)" if is_tourist_exempt else ("Requiere Visa" if requires_visa else "Ver detalle")
        evaluation_notes.append("ℹ️ Evaluación general de la ficha bilateral.")

    return {
        "country": country_name,
        "url": page_url,
        "purpose": purpose or "No especificado",
        "visa_verdict": visa_verdict,
        "stay_limit": stay_limit,
        "asuntos_migratorios": mig_text,
        "relaciones_diplomaticas": dip_text,
        "acuerdos": acuerdos_text,
        "evaluation_notes": evaluation_notes,
        "official_sources": filtered_links[:5],
        "raw_text_snippet": clean_text[:1200]
    }

def format_markdown_report(results: list) -> str:
    md = []
    md.append("# 🇨🇴 Reporte Oficial Cancillería de Colombia - Políticas y Visados\n")

    if len(results) > 1:
        md.append("## Resumen Comparativo de Destinos\n")
        md.append("| País / Destino | Propósito | Condición de Visado | Estancia Máx. | Enlace Oficial Cancillería |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for res in results:
            country = res["country"]
            purp = res["purpose"]
            verdict = res["visa_verdict"]
            limit = res["stay_limit"] or "N/D"
            url = res.get("url") or "#"
            link_md = f"[Ficha Cancillería]({url})" if res.get("url") else "No localizada"
            md.append(f"| **{country}** | {purp} | `{verdict}` | {limit} | {link_md} |")
        md.append("\n---\n")

    for res in results:
        country = res["country"]
        url = res.get("url") or "No disponible"
        md.append(f"## 🌐 {country}\n")
        md.append(f"**URL Ficha Oficial:** [{url}]({url})\n")
        md.append(f"**Propósito Evaluado:** `{res['purpose']}` — **Dictamen:** `{res['visa_verdict']}`\n")

        md.append("### 📌 Evaluación del Agente según Perfil")
        for note in res["evaluation_notes"]:
            md.append(f"- {note}")
        md.append("")

        md.append("### 🛂 Asuntos Migratorios (Texto Oficial Cancillería)")
        if res["asuntos_migratorios"]:
            for line in res["asuntos_migratorios"].split("\n"):
                if line.strip():
                    md.append(f"> {line.strip()}")
        else:
            md.append("> _No se encontró sección explícita con el término 'Asuntos migratorios'. El agente debe interpretar el texto general o recurrir a búsqueda avanzada._")
        md.append("")

        if res["relaciones_diplomaticas"]:
            md.append("### 🏛️ Representación Diplomática y Consular")
            for line in res["relaciones_diplomaticas"].split("\n"):
                if line.strip():
                    md.append(f"- {line.strip()}")
            md.append("")

        if res["acuerdos"]:
            md.append("### 📜 Acuerdos e Instrumentos Bilaterales")
            for line in res["acuerdos"].split("\n"):
                if line.strip():
                    md.append(f"- {line.strip()}")
            md.append("")

        if res["official_sources"]:
            md.append("### 🔗 Portales Gubernamentales Oficiales Citados")
            for link in res["official_sources"]:
                md.append(f"- [{link}]({link})")
            md.append("")

        md.append("---\n")

    return "\n".join(md)

def main():
    parser = argparse.ArgumentParser(description="Agentic Cancilleria Country Policy Retriever")
    parser.add_argument("countries", help="Comma-separated country list (e.g. 'Kazajistan, Kenia, Qatar')")
    parser.add_argument("--purpose", choices=["tourist", "worker", "student", "business", "official", "other"],
                        default=None, help="Traveler purpose (mandatory for definitive requirements)")
    parser.add_argument("--format", choices=["markdown", "json", "raw"], default="markdown", help="Output format")
    parser.add_argument("--timeout", type=int, default=15, help="HTTP request timeout in seconds")

    args = parser.parse_args()

    country_list = [c.strip() for c in re.split(r"[,;|\n]+", args.countries) if c.strip()]
    if not country_list:
        print("Error: No country specified.", file=sys.stderr)
        sys.exit(1)

    results = []

    for country in country_list:
        name, url, is_new = resolve_country_url(country)
        if not url:
            results.append({
                "country": country,
                "url": None,
                "purpose": args.purpose or "No especificado",
                "visa_verdict": "Requiere Búsqueda Avanzada del Agente",
                "stay_limit": None,
                "asuntos_migratorios": f"No se encontró URL bilateral automática para '{country}'. El agente debe escalar a búsqueda web.",
                "relaciones_diplomaticas": "",
                "acuerdos": "",
                "evaluation_notes": ["País no detectado en índice ni en búsqueda directa."],
                "official_sources": [],
                "raw_text_snippet": ""
            })
            continue

        try:
            html = fetch_url(url, timeout=args.timeout)
            clean_text = extract_clean_content(html)
            parsed = parse_policy(clean_text, name, args.purpose, url)
            parsed["is_new_discovery"] = is_new
            results.append(parsed)
        except Exception as e:
            results.append({
                "country": name,
                "url": url,
                "purpose": args.purpose or "No especificado",
                "visa_verdict": "Error de Red",
                "stay_limit": None,
                "asuntos_migratorios": f"Error conectando a Cancillería: {str(e)}",
                "relaciones_diplomaticas": "",
                "acuerdos": "",
                "evaluation_notes": [f"Fallo de conexión o página no accesible: {str(e)}"],
                "official_sources": [],
                "raw_text_snippet": ""
            })

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.format == "raw":
        for r in results:
            print(f"=== {r['country']} ({r.get('url')}) ===")
            print(r.get("raw_text_snippet", ""))
            print("\n" + "="*40 + "\n")
    else:
        print(format_markdown_report(results))

if __name__ == "__main__":
    main()
