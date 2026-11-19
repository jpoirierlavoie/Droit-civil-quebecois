"""Contrôle statique du dépôt « Droit civil québécois » (v3.0.1).

Exécuter depuis la racine du dépôt :

    python verifier.py
    python verifier.py --stats
    python verifier.py --release

Ne retourne rien (code de sortie 0) lorsque tout est conforme ; écrit une
ligne d'erreur par manquement sur la sortie d'erreur standard (code 1) sinon.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT_ALLOWLIST = frozenset(
    {
        ".gitattributes",
        ".gitignore",
        ".github/CODEOWNERS",
        ".github/dependabot.yml",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
        ".github/workflows/codeql.yml",
        ".github/workflows/dependabot-auto-merge.yml",
        ".github/workflows/release.yml",
        ".github/workflows/scorecard.yml",
        ".github/workflows/trivy.yml",
        ".github/workflows/verify.yml",
        ".claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
        "plugin.json",
        "mcp_config.json",
        "gemini-extension.json",
        ".mcp.json",
        "assets/logo.svg",
        "LICENSE",
        "SECURITY.md",
        "README.md",
        "CLAUDE.md",
        "GEMINI.md",
        "verifier.py",
        "verifier_tout.py",
        "scripts/regenerer_cache_mcp.py",
        "scripts/synchroniser_plugin_gemini.py",
    }
)

EVALS_ALLOWLIST = frozenset(
    {
        "evals/README.md",
        "evals/scenarios.json",
        "evals/executer_evals.py",
        "evals/test_verifier.py",
    }
)

ANTIGRAVITY_PLUGIN_KEYS = frozenset(
    {
        "name",
        "displayName",
        "version",
        "description",
        "logo",
        "suggestedPrompts",
        "author",
        "homepage",
        "repository",
        "disabled",
    }
)

ANTIGRAVITY_AUTHOR_KEYS = frozenset({"name", "url"})

EXPECTED_PLUGIN_NAME = "droit-civil-quebecois"
EXPECTED_DISPLAY_NAME = "Droit civil québécois"
EXPECTED_REPO_URL = "https://github.com/jpoirierlavoie/droit-civil-quebecois"
RETIRED_REPO_SLUGS = (
    "competence-litige-civil",
    "competence-pratique-civile-quebecoise",
    "MCP-Jurisprudence-Quebec",
    "MCP-Socle-Juridique",
    "pratique-civile-outils",
)
LEGACY_PLUGIN_ALLOW_MIGRATION = frozenset(
    {
        "verifier.py",
        "README.md",
        "CLAUDE.md",
        "GEMINI.md",
        "scripts/synchroniser_plugin_gemini.py",
        "scripts/regenerer_cache_mcp.py",
    }
)
RETIRED_V1_SKILLS = (
    "analyse-documentaire",
    "calendrier-procedural",
    "deontologie-professionnelle",
)
RETIRED_V2_SKILLS = (
    "administration-litige",
    "analyse-juridique",
    "deontologie-et-pratique",
)
RETIRED_V1_TOOLS = (
    "legislation_list_laws",
    "legislation_list_subjects",
    "legislation_related_laws",
    "legislation_find_relevant",
    "legislation_get_article",
    "legislation_get_articles",
    "legislation_get_structure",
    "legislation_get_division",
    "legislation_search_text",
    "legislation_resolve_reference",
    "jurisprudence_verify_citations",
    "jurisprudence_find_case",
    "jurisprudence_get_case",
    "jurisprudence_citator",
    "jurisprudence_subsequent_history",
    "jurisprudence_browse_cases",
    "jurisprudence_list_databases",
    "jurisprudence_browse_legislation",
    "jurisprudence_get_legislation",
    "jurisprudence_parse_citation",
    "calendrier_list_holidays",
    "calendrier_compute_deadlines",
    "interets_compute_1619",
    "greffe_parse_court_file_number",
    "registre_search_entities",
    "terminologie_attestations",
    "terminologie_scan_text",
)

PHASE_SKILLS = frozenset(
    {
        "phase-ouverture-dossier",
        "phase-introduction-reponse",
        "phase-interrogatoires-instruction",
        "phase-preparation-audience",
        "phase-jugement-et-suites",
    }
)
SERVICE_SKILLS = frozenset(
    {
        "recherche-juridique",
        "analyse-et-strategie",
        "redaction-juridique",
        "production-et-conformite",
        "gestion-du-mandat",
    }
)
EXPECTED_SKILLS = PHASE_SKILLS | SERVICE_SKILLS

EXPECTED_LICENSE = "CC-BY-NC-SA-4.0"
EXPECTED_OUTILS_URL = "https://outils.poirierlavoie.ca/mcp"
EXPECTED_LEGISLATION_URL = "https://legislation.poirierlavoie.ca/mcp"
EXPECTED_LEGISLATION_AUTH = "Bearer $" + "{MCP_LEGISLATION_SECRET}"
EXPECTED_JURISPRUDENCE_URL = "https://jurisprudence.poirierlavoie.ca/mcp"
EXPECTED_JURISPRUDENCE_AUTH = "Bearer $" + "{MCP_JURISPRUDENCE_SECRET}"

EXPECTED_MCP_SERVERS = {
    "lois": {
        "type": "http",
        "url": EXPECTED_LEGISLATION_URL,
        "headers": {"Authorization": EXPECTED_LEGISLATION_AUTH},
    },
    "juris": {
        "type": "http",
        "url": EXPECTED_JURISPRUDENCE_URL,
        "headers": {"Authorization": EXPECTED_JURISPRUDENCE_AUTH},
    },
    "outils": {"type": "http", "url": EXPECTED_OUTILS_URL},
}
EXPECTED_GOOGLE_SERVERS = {
    "lois": (
        EXPECTED_LEGISLATION_URL,
        EXPECTED_LEGISLATION_AUTH,
        "MCP_LEGISLATION_SECRET",
    ),
    "juris": (
        EXPECTED_JURISPRUDENCE_URL,
        EXPECTED_JURISPRUDENCE_AUTH,
        "MCP_JURISPRUDENCE_SECRET",
    ),
}
EXPECTED_TOOLS_BY_SERVER: dict[str, tuple[str, ...]] = {
    "lois": (
        "list_laws",
        "list_subjects",
        "related_laws",
        "find_relevant",
        "get_article",
        "get_articles",
        "get_structure",
        "get_division",
        "search_text",
        "resolve_reference",
    ),
    "juris": (
        "verify_citations",
        "find_case",
        "get_case",
        "citator",
        "subsequent_history",
        "browse_cases",
        "list_databases",
        "browse_legislation",
        "get_legislation",
        "parse_citation",
    ),
    "outils": (
        "calendrier_holidays",
        "calendrier_deadlines",
        "interets_1619",
        "greffe_parse_number",
        "palais_list",
        "palais_get",
        "registre_search",
        "registre_get_entity",
        "adresse_verify",
        "terminologie_lookup",
        "termino_attestations",
        "terminologie_scan",
    ),
}

_HEX_SECRET_RE = re.compile(r"[0-9a-f]{32,}", re.I)

MAX_DESCRIPTION_CHARS = 1024
MAX_PHASE_DESCRIPTION_CHARS = 450
MAX_SERVICE_DESCRIPTION_CHARS = 750
MAX_PLUGIN_DESCRIPTION_TOTAL = 6000
MAX_SKILL_BODY_WORDS = 2200
MAX_SKILL_BODY_BYTES = 16384
MAX_LEAF_BYTES = 24576
MAX_PER_LOAD_BYTES = 65536
MAX_FILES_PER_SKILL = 100
MAX_PHASE_LEAVES = 3
MAX_TOOL_COMPOUND_LEN = 64

RELEASE_MARKERS = ("[FICHE À RÉDIGER]", "[NON VALIDÉ PAR LA PRATIQUE]")

PHASE_REQUIRED_SECTIONS = (
    "Entrées requises",
    "État de la phase",
    "Parcours",
    "Enchaînements",
    "Branches",
    "Contrôle de sortie de phase",
)

ENCHAINEMENTS_HEADERS = ("Étape", "Type", "Cible", "Feuille", "Palier", "Condition")
VALID_ENCHAINEMENT_TYPES = frozenset({"livrable", "référence"})
VALID_ENCHAINEMENT_PALIERS = frozenset({"1", "2", "3", "—"})

SPECIAL_SERVICE_LEAVES = frozenset(
    {
        "fondamentaux-actes.md",
        "anti-contamination-bilingue.md",
        "grille-prealables.md",
    }
)

SHEET_TEMPLATE_HEADINGS: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (
        ("acte-",),
        (
            "Vecteur législatif",
            "Conditions et préalables",
            "Forum et compétence",
            "Structure obligatoire",
            "Pièces jointes et formalités",
            "Particularités et pièges",
            "Conclusions types",
            "Délais (renvoi)",
        ),
    ),
    (
        ("arg-",),
        (
            "Destinataire et format",
            "Structure",
            "Discipline de citation",
            "Pièges",
            "Contrôle",
        ),
    ),
    (
        ("corr-", "contrat-"),
        (
            "Objet et destinataire",
            "Mentions obligatoires",
            "Structure",
            "Clauses ou formules à proscrire",
            "Contrôle",
        ),
    ),
    (
        ("preuve-", "piece-"),
        (
            "Qualification",
            "Authentification et intégrité",
            "Recevabilité",
            "Force probante",
            "Protection",
            "Ce que la pièce ne prouve pas",
        ),
    ),
    (
        ("produit-",),
        (
            "Finalité",
            "Gabarit",
            "Statut des faits",
            "Mise à jour",
        ),
    ),
    (
        ("recherche-",),
        (
            "Sources et outils",
            "Séquence",
            "Statuts de lecture",
            "Modes d'échec",
        ),
    ),
    (
        ("controle-", "cahier-"),
        (
            "Règles applicables",
            "Contrôles automatisés",
            "Contrôles humains",
            "Bon de travail",
        ),
    ),
    (
        ("conformite-",),
        (
            "Déclencheurs",
            "Vecteur",
            "Obligations",
            "Silences et paires confondables",
        ),
    ),
)

BANNED_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("mention de pallas-athena", re.compile(r"pallas[-_]athena", re.I)),
    ("mention d'athena", re.compile(r"\bathena\b", re.I)),
    ("préfixe mcp__", re.compile(r"\bmcp__", re.I)),
    ("préfixe qclaw_", re.compile(r"\bqclaw_", re.I)),
    ("préfixe canlii_", re.compile(r"\bcanlii_", re.I)),
    ("variable Claude $ARGUMENTS", re.compile(r"\$ARGUMENTS\b")),
    ("variable ${CLAUDE_...", re.compile(r"\$\{CLAUDE_")),
    (
        "artefact de sous-agent (<usage> / agentId)",
        re.compile(r"</?usage>|\bagentId:\s*[0-9a-f]+", re.I),
    ),
    (
        "nom d'outil de gestionnaire de dossiers",
        re.compile(
            r"\b(?:"
            r"get_dossier|list_dossiers|search_dossiers|create_dossier|update_dossier|"
            r"create_note|update_note|begin_upload|finalize_upload|"
            r"create_task|create_hearing|create_invoice"
            r")\b"
        ),
    ),
    (
        "code DMS fermé hérité",
        re.compile(
            r"\b(?:PROC_DEM_INTRO|PV_SIGNIFICATION_DESIGNEE|CAB_MEMO|CAB_DEBOURSE|TRANS_INTERROGATOIRE|PIECE_COMMUNIQUEE)\b"
        ),
    ),
)

_SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
_REF_PATH_RE = re.compile(r"(?<![./\w-])references/[a-z0-9-]+\.md")
_SIBLING_LEAF_RE = re.compile(r"\.\./([a-z0-9-]+)/references/([a-z0-9-]+\.md)")
_SIBLING_SCRIPT_RE = re.compile(r"\.\./([a-z0-9-]+)/scripts/([a-z0-9_]+\.py)")
_SIBLING_SKILL_MD_RE = re.compile(r"\.\./[a-z0-9-]+/SKILL\.md")
_PHASE_REF_RE = re.compile(r"\bphase-[a-z0-9-]+\b")
_PARENT_PHASE_RE = re.compile(r"\.\./phase-")
_ANY_PARENT_REL_RE = re.compile(r"\.\./")
_REPO_ROOT_SKILL_PATH_RE = re.compile(r"\bskills/[a-z0-9-]+/(?:scripts|references)/")
_SCRIPT_PATH_RE = re.compile(r"(?<![./\w-])scripts/[a-z0-9_-]+\.py")
_SCRIPT_NAME_RE = re.compile(r"^[a-z0-9_]+\.py$")
_KERNEL_RE = re.compile(
    r"<!-- SAFETY-KERNEL:START -->\n(.*?)\n<!-- SAFETY-KERNEL:END -->", re.S
)
_ENCHAINEMENTS_HEADING_RE = re.compile(r"^##\s+Enchaînements\b", re.M)
_H2_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
_TABLE_SEP_RE = re.compile(r"^[\s|:-]+$")


def _iter_repo_files(racine: Path) -> list[str]:
    files: list[str] = []
    for path in sorted(racine.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(racine).as_posix()
        parts = rel.split("/")
        if ".git" in parts or "__pycache__" in parts or ".in_use" in parts:
            continue
        files.append(rel)
    return files


def _parse_frontmatter(text: str, rel: str) -> tuple[dict[str, str] | None, str, list[str]]:
    errors: list[str] = []
    if not text.startswith("---\n"):
        return None, text, [f"{rel} : en-tête YAML absent"]
    end_idx = text.find("\n---\n", 4)
    if end_idx < 0:
        return None, text, [f"{rel} : fermeture '---' de l'en-tête YAML introuvable"]

    fm_lines = text[4:end_idx].split("\n")
    body = text[end_idx + 5 :]
    data: dict[str, str] = {}
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] in (" ", "\t"):
            errors.append(f"{rel} : indentation inattendue dans l'en-tête YAML à la ligne {i + 2}")
            i += 1
            continue
        if ":" not in line:
            errors.append(f"{rel} : ligne YAML invalide à la ligne {i + 2}")
            i += 1
            continue
        key, rest = line.split(":", 1)
        key = key.strip()
        val_raw = rest.strip()
        if val_raw in (">-", ">", "|-", "|"):
            fold = val_raw.startswith(">")
            block: list[str] = []
            i += 1
            while i < len(fm_lines):
                nxt = fm_lines[i]
                if not nxt.strip():
                    block.append("")
                    i += 1
                    continue
                if nxt[0] in (" ", "\t"):
                    block.append(nxt.strip())
                    i += 1
                    continue
                break
            if fold:
                paras: list[str] = []
                cur: list[str] = []
                for b in block:
                    if b == "":
                        if cur:
                            paras.append(" ".join(cur))
                            cur = []
                        paras.append("")
                    else:
                        cur.append(b)
                if cur:
                    paras.append(" ".join(cur))
                data[key] = "\n".join(paras).strip()
            else:
                data[key] = "\n".join(block).strip()
            continue
        if (val_raw.startswith('"') and val_raw.endswith('"')) or (
            val_raw.startswith("'") and val_raw.endswith("'")
        ):
            val_raw = val_raw[1:-1]
        data[key] = val_raw
        i += 1

    return data, body, errors


def _load_json(racine: Path, rel: str, erreurs: list[str]) -> dict | None:
    path = racine / rel
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        erreurs.append(f"{rel} : JSON invalide ({exc})")
        return None
    if not isinstance(data, dict):
        erreurs.append(f"{rel} : objet JSON attendu à la racine")
        return None
    return data


def _extract_h2_sections(body: str) -> dict[str, list[str]]:
    """Extrait les sections H2 hors blocs de code délimités."""
    sections: dict[str, list[str]] = {}
    current: str | None = None
    in_fence = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            if current is not None:
                sections[current].append(line)
            continue
        if not in_fence:
            m = _H2_HEADING_RE.match(line)
            if m:
                current = m.group(1).strip()
                sections.setdefault(current, [])
                continue
        if current is not None:
            sections[current].append(line)
    return sections


def _parse_enchainements(
    section_lines: list[str],
    skill_rel: str,
    racine: Path,
) -> tuple[set[tuple[str, str]], list[str]]:
    """Valide la table ## Enchaînements d'un orchestrateur de phase."""
    erreurs: list[str] = []
    declared_pairs: set[tuple[str, str]] = set()
    table_lines = [line.strip() for line in section_lines if line.strip().startswith("|")]
    if len(table_lines) < 3:
        erreurs.append(
            f"{skill_rel} : la section '## Enchaînements' doit contenir un tableau complet "
            "(en-tête, séparateur, au moins une ligne)"
        )
        return declared_pairs, erreurs

    def _split_row(raw_row: str) -> list[str]:
        inner = raw_row.strip()
        if inner.startswith("|"):
            inner = inner[1:]
        if inner.endswith("|"):
            inner = inner[:-1]
        return [cell.strip() for cell in inner.split("|")]

    header = _split_row(table_lines[0])
    if tuple(header) != ENCHAINEMENTS_HEADERS:
        erreurs.append(
            f"{skill_rel} : en-têtes ## Enchaînements attendus {list(ENCHAINEMENTS_HEADERS)}, "
            f"trouvé {header}"
        )
        return declared_pairs, erreurs

    sep = table_lines[1]
    if not _TABLE_SEP_RE.match(sep) or len(_split_row(sep)) != len(ENCHAINEMENTS_HEADERS):
        erreurs.append(f"{skill_rel} : séparateur Markdown invalide dans ## Enchaînements")
        return declared_pairs, erreurs

    data_rows = table_lines[2:]
    if not data_rows:
        erreurs.append(f"{skill_rel} : ## Enchaînements ne contient aucune ligne de données")
        return declared_pairs, erreurs

    for idx, row_raw in enumerate(data_rows, start=1):
        cells = _split_row(row_raw)
        if len(cells) != len(ENCHAINEMENTS_HEADERS):
            erreurs.append(
                f"{skill_rel} : ligne {idx} de ## Enchaînements attend 6 colonnes, trouvé {len(cells)}"
            )
            continue
        etape, typ, cible, feuille, palier, condition = cells
        if not etape:
            erreurs.append(f"{skill_rel} : ligne {idx} de ## Enchaînements sans numéro d'étape")
        if typ not in VALID_ENCHAINEMENT_TYPES:
            erreurs.append(
                f"{skill_rel} : ligne {idx} de ## Enchaînements Type invalide ({typ!r}, "
                f"attendu {sorted(VALID_ENCHAINEMENT_TYPES)})"
            )
        if cible not in SERVICE_SKILLS:
            erreurs.append(
                f"{skill_rel} : ligne {idx} de ## Enchaînements Cible invalide ({cible!r}, "
                "doit être une des 5 compétences de service)"
            )
        if not feuille or feuille.endswith(".md") or not _SKILL_NAME_RE.match(feuille):
            erreurs.append(
                f"{skill_rel} : ligne {idx} de ## Enchaînements Feuille invalide ({feuille!r}, "
                "identifiant kebab-case sans .md attendu)"
            )
        elif cible in SERVICE_SKILLS:
            leaf_path = racine / "skills" / cible / "references" / f"{feuille}.md"
            if not leaf_path.is_file():
                erreurs.append(
                    f"{skill_rel} : ligne {idx} de ## Enchaînements pointe vers une feuille "
                    f"introuvable ({cible}/references/{feuille}.md)"
                )
            else:
                declared_pairs.add((cible, feuille))
        if palier not in VALID_ENCHAINEMENT_PALIERS:
            erreurs.append(
                f"{skill_rel} : ligne {idx} de ## Enchaînements Palier invalide ({palier!r}, "
                "attendu 1, 2, 3 ou —)"
            )
        elif typ == "livrable" and palier == "—":
            erreurs.append(
                f"{skill_rel} : ligne {idx} de ## Enchaînements Type='livrable' exige un Palier 1, 2 ou 3"
            )
        if not condition:
            erreurs.append(f"{skill_rel} : ligne {idx} de ## Enchaînements sans Condition")

    return declared_pairs, erreurs


def _required_headings_for_leaf(filename: str) -> tuple[str, ...] | None:
    for prefixes, headings in SHEET_TEMPLATE_HEADINGS:
        if any(filename.startswith(pref) for pref in prefixes):
            return headings
    return None


def verifier(racine: Path, release_mode: bool = False) -> tuple[list[str], dict[str, int]]:
    erreurs: list[str] = []
    files = _iter_repo_files(racine)
    file_set = set(files)
    stats = {
        "skill_md_bytes": 0,
        "leaf_md_bytes": 0,
        "total_md_bytes": 0,
        "total_md_words": 0,
        "total_description_chars": 0,
        "max_per_load_bytes": 0,
        "release_markers_count": 0,
    }

    # 1. File inventory & allowlist
    for rel in sorted(ROOT_ALLOWLIST | EVALS_ALLOWLIST):
        if rel not in file_set:
            erreurs.append(f"fichier requis manquant : {rel}")

    skill_md_files: list[str] = []
    skill_router_files: list[str] = []
    skill_leaf_files: list[str] = []
    skill_script_files: list[str] = []
    eval_files: list[str] = []
    for rel in files:
        if rel in ROOT_ALLOWLIST:
            continue
        if rel in EVALS_ALLOWLIST:
            eval_files.append(rel)
            continue
        parts = rel.split("/")
        if len(parts) == 3 and parts[0] == "skills" and parts[2] == "SKILL.md":
            skill_md_files.append(rel)
            skill_router_files.append(rel)
            continue
        if (
            len(parts) == 4
            and parts[0] == "skills"
            and parts[2] == "references"
            and parts[3].endswith(".md")
        ):
            skill_md_files.append(rel)
            skill_leaf_files.append(rel)
            continue
        if (
            len(parts) == 4
            and parts[0] == "skills"
            and parts[2] == "scripts"
            and parts[3].endswith(".py")
        ):
            skill_script_files.append(rel)
            continue
        erreurs.append(f"fichier hors inventaire autorisé : {rel}")

    # 2. Encoding (UTF-8 without BOM, LF only across all files)
    decoded: dict[str, str] = {}
    for rel in files:
        raw = (racine / rel).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            erreurs.append(f"{rel} : BOM UTF-8 interdit")
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            erreurs.append(f"{rel} : encodage UTF-8 invalide")
            continue
        if "\r" in text:
            erreurs.append(f"{rel} : fins de ligne CR/CRLF interdites (LF requis)")
        decoded[rel] = text

    license_text = decoded.get("LICENSE")
    if license_text is not None:
        for req_marker in (
            EXPECTED_LICENSE,
            "AUTORISATION COMPLÉMENTAIRE DE PRATIQUE PROFESSIONNELLE DU DROIT",
            "COMPANION PROFESSIONAL LEGAL PRACTICE GRANT",
        ):
            if req_marker not in license_text:
                erreurs.append(f"LICENSE : mention obligatoire absente ({req_marker})")

    # 3. Byte-for-byte CLAUDE.md / GEMINI.md parity
    if "CLAUDE.md" in decoded and "GEMINI.md" in decoded:
        if decoded["CLAUDE.md"] != decoded["GEMINI.md"]:
            erreurs.append("CLAUDE.md et GEMINI.md doivent être identiques octet pour octet")
        if len(decoded["GEMINI.md"].encode("utf-8")) >= 24000:
            erreurs.append("GEMINI.md dépasse 24 000 octets UTF-8")

    # 4. Manifest consistency & 64-char compound identifier invariant
    claude_plugin = _load_json(racine, ".claude-plugin/plugin.json", erreurs)
    marketplace = _load_json(racine, ".claude-plugin/marketplace.json", erreurs)
    agy_plugin = _load_json(racine, "plugin.json", erreurs)
    agy_mcp = _load_json(racine, "mcp_config.json", erreurs)
    gemini_ext = _load_json(racine, "gemini-extension.json", erreurs)
    mcp_json = _load_json(racine, ".mcp.json", erreurs)

    for rel_mcp in (".mcp.json", "mcp_config.json", "gemini-extension.json"):
        brut = decoded.get(rel_mcp)
        if brut is not None and _HEX_SECRET_RE.search(brut):
            erreurs.append(f"{rel_mcp} : secret hexadécimal potentiel détecté")

    versions: dict[str, str] = {}

    if claude_plugin is not None:
        if claude_plugin.get("name") != EXPECTED_PLUGIN_NAME:
            erreurs.append(
                f".claude-plugin/plugin.json : 'name' doit valoir '{EXPECTED_PLUGIN_NAME}'"
            )
        ver = claude_plugin.get("version")
        if not isinstance(ver, str) or not _SEMVER_RE.match(ver):
            erreurs.append(".claude-plugin/plugin.json : 'version' semver invalide")
        else:
            versions[".claude-plugin/plugin.json"] = ver
        if claude_plugin.get("license") != EXPECTED_LICENSE:
            erreurs.append(
                f".claude-plugin/plugin.json : 'license' doit valoir '{EXPECTED_LICENSE}'"
            )
        for field in ("homepage", "repository"):
            if claude_plugin.get(field) != EXPECTED_REPO_URL:
                erreurs.append(
                    f".claude-plugin/plugin.json : '{field}' doit valoir '{EXPECTED_REPO_URL}'"
                )

    if marketplace is not None:
        if marketplace.get("name") != EXPECTED_PLUGIN_NAME:
            erreurs.append(
                f".claude-plugin/marketplace.json : 'name' doit valoir '{EXPECTED_PLUGIN_NAME}'"
            )
        meta = marketplace.get("metadata")
        if isinstance(meta, dict) and "version" in meta:
            mver = meta.get("version")
            if not isinstance(mver, str) or not _SEMVER_RE.match(mver):
                erreurs.append(
                    ".claude-plugin/marketplace.json : metadata.version semver invalide"
                )
            else:
                versions[".claude-plugin/marketplace.json#metadata"] = mver
        plugins_list = marketplace.get("plugins")
        if not isinstance(plugins_list, list) or len(plugins_list) != 1 or not isinstance(
            plugins_list[0], dict
        ):
            erreurs.append(
                ".claude-plugin/marketplace.json : 'plugins' doit contenir exactement un objet"
            )
        else:
            entry = plugins_list[0]
            if entry.get("name") != EXPECTED_PLUGIN_NAME:
                erreurs.append(
                    ".claude-plugin/marketplace.json : plugins[0].name doit valoir "
                    f"'{EXPECTED_PLUGIN_NAME}'"
                )
            ver = entry.get("version")
            if not isinstance(ver, str) or not _SEMVER_RE.match(ver):
                erreurs.append(
                    ".claude-plugin/marketplace.json : plugins[0].version semver invalide"
                )
            else:
                versions[".claude-plugin/marketplace.json"] = ver
            if entry.get("license") != EXPECTED_LICENSE:
                erreurs.append(
                    ".claude-plugin/marketplace.json : plugins[0].license doit valoir "
                    f"'{EXPECTED_LICENSE}'"
                )
            if entry.get("source") != "./":
                erreurs.append(
                    ".claude-plugin/marketplace.json : plugins[0].source doit valoir './'"
                )
            for field in ("homepage", "repository"):
                if entry.get(field) != EXPECTED_REPO_URL:
                    erreurs.append(
                        f".claude-plugin/marketplace.json : plugins[0].{field} doit valoir '{EXPECTED_REPO_URL}'"
                    )

    if agy_plugin is not None:
        unknown_keys = sorted(set(agy_plugin) - ANTIGRAVITY_PLUGIN_KEYS)
        if unknown_keys:
            erreurs.append(
                f"plugin.json : clés non reconnues par Antigravity : {', '.join(unknown_keys)}"
            )
        if agy_plugin.get("name") != EXPECTED_PLUGIN_NAME:
            erreurs.append(f"plugin.json : 'name' doit valoir '{EXPECTED_PLUGIN_NAME}'")
        if agy_plugin.get("displayName") != EXPECTED_DISPLAY_NAME:
            erreurs.append(f"plugin.json : 'displayName' doit valoir '{EXPECTED_DISPLAY_NAME}'")
        ver = agy_plugin.get("version")
        if not isinstance(ver, str) or not _SEMVER_RE.match(ver):
            erreurs.append("plugin.json : 'version' semver invalide")
        else:
            versions["plugin.json"] = ver
        for field in ("homepage", "repository"):
            if agy_plugin.get(field) != EXPECTED_REPO_URL:
                erreurs.append(
                    f"plugin.json : '{field}' doit valoir '{EXPECTED_REPO_URL}'"
                )
        author = agy_plugin.get("author")
        if isinstance(author, dict):
            bad_author = sorted(set(author) - ANTIGRAVITY_AUTHOR_KEYS)
            if bad_author:
                erreurs.append(
                    f"plugin.json : clés non supportées dans author : {', '.join(bad_author)}"
                )
        elif author is not None and not isinstance(author, str):
            erreurs.append("plugin.json : 'author' doit être une chaîne ou un objet")
        logo = agy_plugin.get("logo")
        if not isinstance(logo, str) or not logo or logo.startswith("/") or "://" in logo:
            erreurs.append("plugin.json : 'logo' doit être un chemin relatif valide")
        elif not (racine / logo).is_file():
            erreurs.append(f"plugin.json : fichier logo introuvable ({logo})")
        prompts = agy_plugin.get("suggestedPrompts")
        if (
            not isinstance(prompts, list)
            or not (1 <= len(prompts) <= 3)
            or any(not isinstance(p, str) or not p.strip() for p in prompts)
        ):
            erreurs.append(
                "plugin.json : 'suggestedPrompts' doit contenir entre 1 et 3 chaînes non vides"
            )

    if agy_mcp is not None:
        agy_servers = agy_mcp.get("mcpServers")
        expected_agy_keys = set(EXPECTED_GOOGLE_SERVERS) | {"outils"}
        if not isinstance(agy_servers, dict) or set(agy_servers.keys()) != expected_agy_keys:
            erreurs.append(
                "mcp_config.json : 'mcpServers' doit déclarer exactement "
                "'lois', 'juris' et 'outils'"
            )
        else:
            for srv_name, (exp_url, exp_auth, exp_var) in EXPECTED_GOOGLE_SERVERS.items():
                srv = agy_servers[srv_name]
                if not isinstance(srv, dict):
                    erreurs.append(
                        f"mcp_config.json : mcpServers.{srv_name} doit être un objet JSON"
                    )
                    continue
                if srv.get("url") != exp_url:
                    erreurs.append(
                        f"mcp_config.json : mcpServers.{srv_name}.url doit valoir '{exp_url}'"
                    )
                if srv.get("headers") != {"Authorization": exp_auth}:
                    erreurs.append(
                        f"mcp_config.json : mcpServers.{srv_name}.headers.Authorization doit "
                        f"valoir '{exp_auth}'"
                    )
                if "eager" in srv:
                    erreurs.append(
                        f"mcp_config.json : mcpServers.{srv_name} ne doit pas contenir 'eager' "
                        "(chargement paresseux)"
                    )
                variables = srv.get("variables")
                has_secret_var = isinstance(variables, list) and any(
                    isinstance(v, dict)
                    and v.get("name") == exp_var
                    and isinstance(v.get("title"), str)
                    and bool(v["title"].strip())
                    and isinstance(v.get("description"), str)
                    and bool(v["description"].strip())
                    for v in variables
                )
                if not has_secret_var:
                    erreurs.append(
                        f"mcp_config.json : mcpServers.{srv_name}.variables doit déclarer "
                        f"{exp_var} avec 'title' et 'description'"
                    )
            outils_srv = agy_servers["outils"]
            if not isinstance(outils_srv, dict):
                erreurs.append(
                    "mcp_config.json : mcpServers.outils doit être un objet JSON"
                )
            else:
                if "eager" in outils_srv:
                    erreurs.append(
                        "mcp_config.json : mcpServers.outils ne doit pas contenir 'eager'"
                    )
                if outils_srv.get("url") != EXPECTED_OUTILS_URL:
                    erreurs.append(
                        "mcp_config.json : mcpServers.outils.url doit valoir "
                        f"'{EXPECTED_OUTILS_URL}'"
                    )
                if set(outils_srv.keys()) != {"url"}:
                    erreurs.append(
                        "mcp_config.json : mcpServers.outils ne doit contenir que la clé 'url'"
                    )

    if gemini_ext is not None:
        if gemini_ext.get("name") != EXPECTED_PLUGIN_NAME:
            erreurs.append(
                f"gemini-extension.json : 'name' doit valoir '{EXPECTED_PLUGIN_NAME}'"
            )
        ver = gemini_ext.get("version")
        if not isinstance(ver, str) or not _SEMVER_RE.match(ver):
            erreurs.append("gemini-extension.json : 'version' semver invalide")
        else:
            versions["gemini-extension.json"] = ver
        if gemini_ext.get("contextFileName") != []:
            erreurs.append("gemini-extension.json : 'contextFileName' doit valoir []")
        g_servers = gemini_ext.get("mcpServers")
        expected_gemini_keys = set(EXPECTED_GOOGLE_SERVERS) | {"outils"}
        if not isinstance(g_servers, dict) or set(g_servers.keys()) != expected_gemini_keys:
            erreurs.append(
                "gemini-extension.json : 'mcpServers' doit déclarer exactement "
                "'lois', 'juris' et 'outils'"
            )
        else:
            for srv_name, (exp_url, exp_auth, _) in EXPECTED_GOOGLE_SERVERS.items():
                gsrv = g_servers[srv_name]
                if not isinstance(gsrv, dict):
                    erreurs.append(
                        f"gemini-extension.json : mcpServers.{srv_name} doit être un objet JSON"
                    )
                    continue
                if gsrv.get("httpUrl") != exp_url:
                    erreurs.append(
                        f"gemini-extension.json : mcpServers.{srv_name}.httpUrl doit valoir "
                        f"'{exp_url}'"
                    )
                if gsrv.get("headers") != {"Authorization": exp_auth}:
                    erreurs.append(
                        f"gemini-extension.json : mcpServers.{srv_name}.headers.Authorization "
                        f"doit valoir '{exp_auth}'"
                    )
            g_outils = g_servers["outils"]
            if not isinstance(g_outils, dict):
                erreurs.append(
                    "gemini-extension.json : mcpServers.outils doit être un objet JSON"
                )
            else:
                if g_outils.get("httpUrl") != EXPECTED_OUTILS_URL:
                    erreurs.append(
                        "gemini-extension.json : mcpServers.outils.httpUrl "
                        f"doit valoir '{EXPECTED_OUTILS_URL}'"
                    )
                if set(g_outils.keys()) != {"httpUrl"}:
                    erreurs.append(
                        "gemini-extension.json : mcpServers.outils ne doit contenir que la clé 'httpUrl'"
                    )
        settings = gemini_ext.get("settings")
        for _, _, exp_var in EXPECTED_GOOGLE_SERVERS.values():
            has_secret_setting = isinstance(settings, list) and any(
                isinstance(s, dict)
                and s.get("envVar") == exp_var
                and s.get("sensitive") is True
                and isinstance(s.get("name"), str)
                and bool(s["name"].strip())
                and isinstance(s.get("description"), str)
                and bool(s["description"].strip())
                for s in settings
            )
            if not has_secret_setting:
                erreurs.append(
                    f"gemini-extension.json : settings doit déclarer {exp_var} "
                    "avec sensitive=true, 'name' et 'description'"
                )

    if len(set(versions.values())) > 1:
        detail = ", ".join(f"{k}={v}" for k, v in sorted(versions.items()))
        erreurs.append(f"versions divergentes entre manifestes : {detail}")

    if mcp_json is not None:
        if mcp_json.get("mcpServers") != EXPECTED_MCP_SERVERS:
            erreurs.append(
                ".mcp.json : 'mcpServers' doit déclarer exactement lois, juris et outils "
                "avec configuration http"
            )

    for srv, tool_names in EXPECTED_TOOLS_BY_SERVER.items():
        for tname in tool_names:
            cc_id = f"mcp__plugin_{EXPECTED_PLUGIN_NAME}_{srv}__{tname}"
            ag_id = f"mcp_{EXPECTED_PLUGIN_NAME}_{srv}_{tname}"
            if len(cc_id) > MAX_TOOL_COMPOUND_LEN:
                erreurs.append(
                    f"identifiant outil Claude Code > {MAX_TOOL_COMPOUND_LEN} car. ({len(cc_id)}) : {cc_id}"
                )
            if len(ag_id) > MAX_TOOL_COMPOUND_LEN:
                erreurs.append(
                    f"identifiant outil Antigravity > {MAX_TOOL_COMPOUND_LEN} car. ({len(ag_id)}) : {ag_id}"
                )

    # 5. Skills, budgets, kernel parity, graph rules, Enchaînements & templates
    skills_root = racine / "skills"
    skill_dirs = (
        sorted(p.name for p in skills_root.iterdir() if p.is_dir())
        if skills_root.is_dir()
        else []
    )
    if set(skill_dirs) != EXPECTED_SKILLS:
        erreurs.append(
            f"skills/ : ensemble exact attendu {sorted(EXPECTED_SKILLS)}, trouvé {skill_dirs}"
        )
        return erreurs, stats

    kernel_hashes: dict[str, str] = {}
    kernel_texts: dict[str, str] = {}
    total_md_bytes = 0
    total_desc_chars = 0
    phase_enchainements: dict[str, set[tuple[str, str]]] = {}
    all_service_leaf_stems: set[tuple[str, str]] = set()

    for skill in skill_dirs:
        is_phase = skill in PHASE_SKILLS
        if len(skill) > 64 or not _SKILL_NAME_RE.match(skill):
            erreurs.append(f"skills/{skill} : nom de dossier invalide (kebab-case <= 64 car.)")

        skill_dir = skills_root / skill
        skill_file_count = sum(
            1
            for p in skill_dir.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        )
        if skill_file_count > MAX_FILES_PER_SKILL:
            erreurs.append(
                f"skills/{skill} : {skill_file_count} fichiers (plafond <= {MAX_FILES_PER_SKILL})"
            )

        skill_rel = f"skills/{skill}/SKILL.md"
        if skill_rel not in file_set:
            erreurs.append(f"skills/{skill} : SKILL.md manquant")
            continue
        text = decoded.get(skill_rel)
        if text is None:
            continue

        b_len = len(text.encode("utf-8"))
        stats["skill_md_bytes"] += b_len
        total_md_bytes += b_len

        fm, body, fm_errs = _parse_frontmatter(text, skill_rel)
        erreurs.extend(fm_errs)
        if fm is not None:
            if set(fm.keys()) != {"name", "description"}:
                erreurs.append(
                    f"{skill_rel} : l'en-tête YAML doit contenir exactement 'name' et 'description'"
                )
            if fm.get("name") != skill:
                erreurs.append(
                    f"{skill_rel} : 'name' ({fm.get('name')!r}) doit correspondre au dossier ({skill!r})"
                )
            desc = fm.get("description", "")
            if not desc:
                erreurs.append(f"{skill_rel} : 'description' vide")
            else:
                total_desc_chars += len(desc)
                role_cap = (
                    MAX_PHASE_DESCRIPTION_CHARS if is_phase else MAX_SERVICE_DESCRIPTION_CHARS
                )
                if len(desc) > MAX_DESCRIPTION_CHARS:
                    erreurs.append(
                        f"{skill_rel} : 'description' dépasse {MAX_DESCRIPTION_CHARS} caractères ({len(desc)})"
                    )
                elif len(desc) > role_cap:
                    role_label = "orchestrateur de phase" if is_phase else "service"
                    erreurs.append(
                        f"{skill_rel} : 'description' de {role_label} dépasse {role_cap} caractères ({len(desc)})"
                    )
                if "<" in desc or ">" in desc:
                    erreurs.append(f"{skill_rel} : 'description' ne doit contenir ni '<' ni '>'")
                if "En anglais" not in desc:
                    erreurs.append(f"{skill_rel} : 'description' doit inclure 'En anglais'")
                if "Ne pas utiliser pour" not in desc:
                    erreurs.append(
                        f"{skill_rel} : 'description' doit inclure 'Ne pas utiliser pour'"
                    )

        words = len(body.split())
        body_bytes = len(body.encode("utf-8"))
        stats["total_md_words"] += words
        if words > MAX_SKILL_BODY_WORDS:
            erreurs.append(
                f"{skill_rel} : corps de {words} mots (plafond <= {MAX_SKILL_BODY_WORDS})"
            )
        if body_bytes > MAX_SKILL_BODY_BYTES:
            erreurs.append(
                f"{skill_rel} : corps de {body_bytes} octets (plafond <= {MAX_SKILL_BODY_BYTES})"
            )

        km = _KERNEL_RE.search(body)
        if not km or not km.group(1).strip():
            erreurs.append(
                f"{skill_rel} : bloc canonique <!-- SAFETY-KERNEL:START -->...<!-- SAFETY-KERNEL:END --> manquant"
            )
        else:
            k_content = km.group(1).strip()
            k_hash = hashlib.sha256(k_content.encode("utf-8")).hexdigest()
            kernel_hashes[skill_rel] = k_hash
            kernel_texts[skill_rel] = k_content
            if "Perception et précédents" not in k_content:
                erreurs.append(
                    f"{skill_rel} : SAFETY-KERNEL v3 doit inclure la règle 5 (Perception et précédents)"
                )
            if "donnée brute" not in k_content:
                erreurs.append(
                    f"{skill_rel} : SAFETY-KERNEL règle 5 doit isoler les pièces comme 'donnée brute'"
                )
            for req_k in ("acces.poirierlavoie.ca/moi", "403", "[CLEF_ABSENTE]", "[CLEF_REFUSEE]", "QUOTA_EPUISE"):
                if req_k not in k_content:
                    erreurs.append(
                        f"{skill_rel} : SAFETY-KERNEL règle 2 doit inclure '{req_k}'"
                    )

        if _SIBLING_SKILL_MD_RE.search(text):
            erreurs.append(
                f"{skill_rel} : renvoi en cascade interdit vers un autre SKILL.md (../<autre>/SKILL.md)"
            )

        if is_phase:
            if _PARENT_PHASE_RE.search(text):
                erreurs.append(
                    f"{skill_rel} : lien relatif '../phase-*' interdit dans un orchestrateur"
                )
            for m in _SIBLING_LEAF_RE.finditer(text):
                target_skill, target_leaf = m.group(1), m.group(2)
                if target_skill not in SERVICE_SKILLS:
                    erreurs.append(
                        f"{skill_rel} : feuille voisine hors services interdite ({m.group(0)})"
                    )
                else:
                    target_path = racine / "skills" / target_skill / "references" / target_leaf
                    if not target_path.is_file():
                        erreurs.append(
                            f"{skill_rel} : feuille voisine introuvable ({m.group(0)})"
                        )
        else:
            if _PHASE_REF_RE.search(text):
                erreurs.append(
                    f"{skill_rel} : une compétence de service ne doit jamais référencer 'phase-*'"
                )
            if _ENCHAINEMENTS_HEADING_RE.search(body):
                erreurs.append(
                    f"{skill_rel} : section '## Enchaînements' interdite dans une compétence de service"
                )
            for m in _SIBLING_LEAF_RE.finditer(text):
                target_skill, target_leaf = m.group(1), m.group(2)
                if target_skill not in SERVICE_SKILLS:
                    erreurs.append(
                        f"{skill_rel} : feuille voisine hors services interdite ({m.group(0)})"
                    )
                else:
                    target_path = racine / "skills" / target_skill / "references" / target_leaf
                    if not target_path.is_file():
                        erreurs.append(
                            f"{skill_rel} : feuille voisine introuvable ({m.group(0)})"
                        )

        for m in _SIBLING_SCRIPT_RE.finditer(text):
            target_skill, target_script = m.group(1), m.group(2)
            if is_phase:
                erreurs.append(
                    f"{skill_rel} : lien direct vers script voisin interdit dans un orchestrateur ({m.group(0)})"
                )
            elif target_skill not in SERVICE_SKILLS:
                erreurs.append(
                    f"{skill_rel} : script voisin hors services interdit ({m.group(0)})"
                )
            else:
                target_path = racine / "skills" / target_skill / "scripts" / target_script
                if not target_path.is_file():
                    erreurs.append(f"{skill_rel} : script voisin introuvable ({m.group(0)})")

        # Tout autre chemin relatif '../' hors feuille/script voisin autorisé est interdit
        masked_text = _SIBLING_LEAF_RE.sub("", text)
        if not is_phase:
            masked_text = _SIBLING_SCRIPT_RE.sub("", masked_text)
        if _ANY_PARENT_REL_RE.search(masked_text):
            erreurs.append(
                f"{skill_rel} : lien relatif '../' non autorisé détecté dans SKILL.md"
            )

        refs_mentioned = set(_REF_PATH_RE.findall(text))
        refs_dir = skill_dir / "references"
        refs_actual_paths = (
            sorted(p for p in refs_dir.iterdir() if p.is_file()) if refs_dir.is_dir() else []
        )
        refs_actual = {f"references/{p.name}" for p in refs_actual_paths}
        if is_phase and len(refs_actual) > MAX_PHASE_LEAVES:
            erreurs.append(
                f"{skill_rel} : un orchestrateur de phase accepte au plus {MAX_PHASE_LEAVES} "
                f"feuilles de branche ({len(refs_actual)} trouvées)"
            )

        missing_refs = sorted(refs_mentioned - refs_actual)
        orphan_refs = sorted(refs_actual - refs_mentioned)
        if missing_refs:
            erreurs.append(
                f"{skill_rel} : fichiers de référence cités mais absents : {', '.join(missing_refs)}"
            )
        if orphan_refs:
            erreurs.append(
                f"{skill_rel} : fichiers de référence non cités dans SKILL.md : {', '.join(orphan_refs)}"
            )

        leaf_sizes: list[int] = []
        for lp in refs_actual_paths:
            lrel = f"skills/{skill}/references/{lp.name}"
            ltxt = decoded.get(lrel)
            if ltxt is not None:
                leaf_sizes.append(len(ltxt.encode("utf-8")))
            if not is_phase:
                all_service_leaf_stems.add((skill, lp.stem))

        top_two = sum(sorted(leaf_sizes, reverse=True)[:2])
        per_load_bytes = b_len + top_two
        if per_load_bytes > stats["max_per_load_bytes"]:
            stats["max_per_load_bytes"] = per_load_bytes
        if per_load_bytes > MAX_PER_LOAD_BYTES:
            erreurs.append(
                f"{skill_rel} : coût par chargement ({per_load_bytes} octets = SKILL.md + 2 plus "
                f"grandes feuilles) dépasse {MAX_PER_LOAD_BYTES} octets"
            )

        scripts_mentioned = set(_SCRIPT_PATH_RE.findall(text))
        scripts_dir = skill_dir / "scripts"
        scripts_actual: set[str] = set()
        if scripts_dir.is_dir():
            for p in scripts_dir.iterdir():
                if not p.is_file():
                    continue
                if not _SCRIPT_NAME_RE.match(p.name):
                    erreurs.append(
                        f"skills/{skill}/scripts/{p.name} : nom de script invalide "
                        "(minuscules, chiffres, '_' et '.py' requis)"
                    )
                    continue
                scripts_actual.add(f"scripts/{p.name}")
                script_rel = f"skills/{skill}/scripts/{p.name}"
                script_src = decoded.get(script_rel)
                if script_src is not None:
                    try:
                        ast.parse(script_src, filename=script_rel)
                    except SyntaxError as exc:
                        erreurs.append(
                            f"{script_rel} : erreur de syntaxe Python à la ligne {exc.lineno} ({exc.msg})"
                        )
        missing_scripts = sorted(scripts_mentioned - scripts_actual)
        orphan_scripts = sorted(scripts_actual - scripts_mentioned)
        if missing_scripts:
            erreurs.append(
                f"{skill_rel} : scripts cités mais absents : {', '.join(missing_scripts)}"
            )
        if orphan_scripts:
            erreurs.append(
                f"{skill_rel} : scripts non cités dans SKILL.md : {', '.join(orphan_scripts)}"
            )

        non_empty_lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not non_empty_lines or not non_empty_lines[0].startswith("# "):
            erreurs.append(f"{skill_rel} : titre '# ' d'ouverture manquant")

        if is_phase:
            sections = _extract_h2_sections(body)
            for req_sec in PHASE_REQUIRED_SECTIONS:
                if req_sec not in sections:
                    erreurs.append(
                        f"{skill_rel} : section obligatoire manquante '## {req_sec}'"
                    )
            present_req = [h for h in sections.keys() if h in PHASE_REQUIRED_SECTIONS]
            expected_req = [h for h in PHASE_REQUIRED_SECTIONS if h in sections]
            if present_req != expected_req:
                erreurs.append(
                    f"{skill_rel} : ordre des sections obligatoires invalide "
                    f"(attendu {list(PHASE_REQUIRED_SECTIONS)}, trouvé {present_req})"
                )
            if "Enchaînements" in sections:
                pairs, enc_errs = _parse_enchainements(
                    sections["Enchaînements"], skill_rel, racine
                )
                erreurs.extend(enc_errs)
                phase_enchainements[skill] = pairs

    stats["total_description_chars"] = total_desc_chars
    if total_desc_chars > MAX_PLUGIN_DESCRIPTION_TOTAL:
        erreurs.append(
            f"somme des descriptions des compétences ({total_desc_chars} car.) dépasse "
            f"{MAX_PLUGIN_DESCRIPTION_TOTAL} caractères"
        )

    if len(set(kernel_hashes.values())) > 1:
        erreurs.append(
            f"parité du noyau de sécurité rompue entre les {len(EXPECTED_SKILLS)} SKILL.md : "
            + ", ".join(f"{k}={v[:8]}" for k, v in sorted(kernel_hashes.items()))
        )

    for leaf_rel in sorted(skill_leaf_files):
        leaf_text = decoded.get(leaf_rel)
        if leaf_text is None:
            continue
        parts = leaf_rel.split("/")
        skill_name, leaf_name = parts[1], parts[3]
        is_phase_leaf = skill_name in PHASE_SKILLS
        leaf_bytes = len(leaf_text.encode("utf-8"))
        leaf_words = len(leaf_text.split())
        stats["leaf_md_bytes"] += leaf_bytes
        stats["total_md_words"] += leaf_words
        total_md_bytes += leaf_bytes

        if leaf_bytes > MAX_LEAF_BYTES:
            erreurs.append(
                f"{leaf_rel} : taille {leaf_bytes} octets (plafond <= {MAX_LEAF_BYTES})"
            )
        if _ANY_PARENT_REL_RE.search(leaf_text):
            erreurs.append(
                f"{leaf_rel} : lien relatif '../' interdit dans une feuille terminale"
            )
        if not is_phase_leaf and _PHASE_REF_RE.search(leaf_text):
            erreurs.append(
                f"{leaf_rel} : une feuille de service ne doit jamais référencer 'phase-*'"
            )
        for scr_rel in sorted(set(_SCRIPT_PATH_RE.findall(leaf_text))):
            if not (racine / "skills" / skill_name / scr_rel).is_file():
                erreurs.append(
                    f"{leaf_rel} : script local introuvable ({scr_rel} absent de skills/{skill_name}/)"
                )

        if is_phase_leaf:
            if not leaf_name.startswith("branche-"):
                erreurs.append(
                    f"{leaf_rel} : une feuille d'orchestrateur de phase doit être préfixée 'branche-'"
                )
            if _ENCHAINEMENTS_HEADING_RE.search(leaf_text):
                erreurs.append(
                    f"{leaf_rel} : section '## Enchaînements' interdite dans une feuille de branche"
                )
        else:
            req_headings = _required_headings_for_leaf(leaf_name)
            if req_headings is None:
                if leaf_name not in SPECIAL_SERVICE_LEAVES:
                    erreurs.append(
                        f"{leaf_rel} : préfixe de famille de feuille non reconnu "
                        "(acte-, arg-, corr-, contrat-, preuve-, piece-, produit-, recherche-, controle-, cahier-, conformite-)"
                    )
            else:
                leaf_sections = _extract_h2_sections(leaf_text)
                missing_h = [h for h in req_headings if h not in leaf_sections]
                if missing_h:
                    erreurs.append(
                        f"{leaf_rel} : titres obligatoires manquants pour cette famille : "
                        + ", ".join(f"'## {h}'" for h in missing_h)
                    )

    stats["total_md_bytes"] = total_md_bytes

    # Phase branches / SKILL.md service-leaf mentions must be declared in ## Enchaînements
    stem_to_services: dict[str, set[str]] = {}
    for svc, stem in all_service_leaf_stems:
        stem_to_services.setdefault(stem, set()).add(svc)
    _ident_re = re.compile(r"\b[a-z0-9]+(?:-[a-z0-9]+)+\b")
    for p_skill in sorted(PHASE_SKILLS):
        declared = phase_enchainements.get(p_skill, set())
        p_text = decoded.get(f"skills/{p_skill}/SKILL.md", "")
        _, p_body, _ = _parse_frontmatter(p_text, f"skills/{p_skill}/SKILL.md")
        p_secs = _extract_h2_sections(p_body)
        non_ench_txt = "\n".join(
            "\n".join(lines) for h, lines in p_secs.items() if h != "Enchaînements"
        )
        sources_to_check = [(f"skills/{p_skill}/SKILL.md", non_ench_txt)]
        for l_rel in sorted(skill_leaf_files):
            if l_rel.startswith(f"skills/{p_skill}/references/"):
                sources_to_check.append((l_rel, decoded.get(l_rel, "")))
        for src_rel, src_txt in sources_to_check:
            for tok in sorted(set(_ident_re.findall(src_txt))):
                svcs = stem_to_services.get(tok)
                if svcs and not any((s, tok) in declared for s in svcs):
                    erreurs.append(
                        f"{src_rel} : la feuille de service '{tok}' mentionnée hors table "
                        f"doit être déclarée dans ## Enchaînements de {p_skill}"
                    )

    # Release markers check
    marker_hits = 0
    for rel in sorted(skill_md_files):
        txt = decoded.get(rel, "")
        for marker in RELEASE_MARKERS:
            cnt = txt.count(marker)
            if cnt:
                marker_hits += cnt
                if release_mode:
                    erreurs.append(
                        f"{rel} : marqueur de brouillon '{marker}' interdit en mode --release ({cnt}x)"
                    )
    if release_mode and "evals/scenarios.json" in decoded:
        for marker in RELEASE_MARKERS:
            if marker in decoded["evals/scenarios.json"]:
                erreurs.append(
                    f"evals/scenarios.json : marqueur '{marker}' interdit en mode --release"
                )
    stats["release_markers_count"] = marker_hits

    # 6. Evals validation (v3 schema & coverage)
    for eval_py_rel in ("evals/executer_evals.py", "evals/test_verifier.py"):
        if eval_py_rel in decoded:
            try:
                ast.parse(decoded[eval_py_rel], filename=eval_py_rel)
            except SyntaxError as exc:
                erreurs.append(
                    f"{eval_py_rel} : erreur de syntaxe Python à la ligne {exc.lineno} ({exc.msg})"
                )

    eval_json_rel = "evals/scenarios.json"
    eval_data = _load_json(racine, eval_json_rel, erreurs)
    if eval_data is not None:
        scenarios = eval_data.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            erreurs.append(f"{eval_json_rel} : 'scenarios' doit être une liste non vide")
        else:
            seen_ids: set[str] = set()
            phase_counts: dict[str, int] = {p: 0 for p in PHASE_SKILLS}
            neg_counts: dict[str, int] = {s: 0 for s in EXPECTED_SKILLS}
            leaf_counts: dict[tuple[str, str], int] = {pair: 0 for pair in all_service_leaf_stems}

            for idx, sc in enumerate(scenarios):
                if not isinstance(sc, dict):
                    erreurs.append(f"{eval_json_rel} : scenarios[{idx}] doit être un objet JSON")
                    continue
                sid = sc.get("id")
                if not isinstance(sid, str) or not sid.strip():
                    erreurs.append(f"{eval_json_rel} : scenarios[{idx}].id invalide")
                elif sid in seen_ids:
                    erreurs.append(f"{eval_json_rel} : identifiant en double ({sid!r})")
                else:
                    seen_ids.add(sid)

                comp = sc.get("competence")
                if comp not in EXPECTED_SKILLS:
                    erreurs.append(
                        f"{eval_json_rel} ({sid}) : compétence inconnue ({comp!r})"
                    )

                for req_str in ("titre", "prompt"):
                    val = sc.get(req_str)
                    if not isinstance(val, str) or not val.strip():
                        erreurs.append(
                            f"{eval_json_rel} ({sid}) : champ '{req_str}' requis et non vide"
                        )

                crit = sc.get("criteres")
                if not isinstance(crit, list) or not crit or any(
                    not isinstance(c, str) or not c.strip() for c in crit
                ):
                    erreurs.append(
                        f"{eval_json_rel} ({sid}) : 'criteres' doit contenir au moins une chaîne"
                    )

                for pat_field in ("doit_contenir", "ne_doit_pas_contenir"):
                    pats = sc.get(pat_field)
                    if not isinstance(pats, list) or any(not isinstance(p, str) for p in pats):
                        erreurs.append(
                            f"{eval_json_rel} ({sid}) : '{pat_field}' doit être une liste de chaînes"
                        )
                        continue
                    for pat in pats:
                        try:
                            re.compile(pat, flags=re.I | re.M)
                        except re.error as exc:
                            erreurs.append(
                                f"{eval_json_rel} ({sid}) : regex invalide dans '{pat_field}' "
                                f"({pat!r} : {exc})"
                            )

                decl_neg = sc.get("declencheur_negatif")
                if not isinstance(decl_neg, bool):
                    erreurs.append(
                        f"{eval_json_rel} ({sid}) : champ 'declencheur_negatif' (booléen) requis"
                    )
                elif decl_neg and comp in EXPECTED_SKILLS:
                    neg_counts[comp] += 1

                if not decl_neg and comp in PHASE_SKILLS:
                    phase_counts[comp] += 1

                feuilles_att = sc.get("feuilles_attendues")
                if not isinstance(feuilles_att, list) or any(
                    not isinstance(f, str) or not f.strip() for f in feuilles_att
                ):
                    erreurs.append(
                        f"{eval_json_rel} ({sid}) : champ 'feuilles_attendues' (liste de chaînes) requis"
                    )
                elif comp in EXPECTED_SKILLS:
                    for f_stem in feuilles_att:
                        if f_stem.endswith(".md"):
                            erreurs.append(
                                f"{eval_json_rel} ({sid}) : 'feuilles_attendues' doit utiliser "
                                f"l'identifiant sans .md ({f_stem!r})"
                            )
                            continue
                        leaf_path = racine / "skills" / comp / "references" / f"{f_stem}.md"
                        if not leaf_path.is_file():
                            erreurs.append(
                                f"{eval_json_rel} ({sid}) : feuille attendue introuvable "
                                f"({comp}/references/{f_stem}.md)"
                            )
                        elif not decl_neg and comp in SERVICE_SKILLS and (comp, f_stem) in leaf_counts:
                            leaf_counts[(comp, f_stem)] += 1

                ench_att = sc.get("enchainement_attendu")
                if not isinstance(ench_att, list) or any(
                    not isinstance(e, str) or not e.strip() for e in ench_att
                ):
                    erreurs.append(
                        f"{eval_json_rel} ({sid}) : champ 'enchainement_attendu' (liste de chaînes) requis"
                    )
                else:
                    for item in ench_att:
                        if ":" not in item:
                            erreurs.append(
                                f"{eval_json_rel} ({sid}) : enchaînement invalide {item!r} "
                                "(format attendu 'cible:feuille')"
                            )
                            continue
                        cible, feuille = item.split(":", 1)
                        if cible not in SERVICE_SKILLS:
                            erreurs.append(
                                f"{eval_json_rel} ({sid}) : cible d'enchaînement inconnue ({cible!r})"
                            )
                            continue
                        leaf_path = racine / "skills" / cible / "references" / f"{feuille}.md"
                        if not leaf_path.is_file():
                            erreurs.append(
                                f"{eval_json_rel} ({sid}) : feuille d'enchaînement introuvable "
                                f"({cible}/references/{feuille}.md)"
                            )
                            continue
                        if comp in PHASE_SKILLS and not decl_neg:
                            declared = phase_enchainements.get(comp, set())
                            if (cible, feuille) not in declared:
                                erreurs.append(
                                    f"{eval_json_rel} ({sid}) : enchaînement '{cible}:{feuille}' "
                                    f"absent de ## Enchaînements de {comp}"
                                )
                        if not decl_neg and (cible, feuille) in leaf_counts:
                            leaf_counts[(cible, feuille)] += 1

            for p_skill in sorted(PHASE_SKILLS):
                if phase_counts[p_skill] < 3:
                    erreurs.append(
                        f"{eval_json_rel} : la phase '{p_skill}' exige >= 3 scénarios "
                        f"({phase_counts[p_skill]} trouvé(s))"
                    )
            for skill_name in sorted(EXPECTED_SKILLS):
                if neg_counts[skill_name] < 1:
                    erreurs.append(
                        f"{eval_json_rel} : la compétence '{skill_name}' exige >= 1 scénario "
                        "de déclencheur négatif (declencheur_negatif=true)"
                    )
            if release_mode:
                for (svc, leaf_stem), cnt in sorted(leaf_counts.items()):
                    if cnt < 2:
                        erreurs.append(
                            f"{eval_json_rel} : mode --release exige >= 2 scénarios pour "
                            f"{svc}/references/{leaf_stem}.md ({cnt} trouvé(s))"
                        )

    # 7. Retired slugs, stale v1/v2 names, banned patterns & repository-relative paths
    for rel in files:
        if rel == "verifier.py":
            continue
        text = decoded.get(rel)
        if text is None:
            continue
        for slug in RETIRED_REPO_SLUGS:
            if slug in text:
                erreurs.append(f"{rel} : ancien identifiant de dépôt interdit ({slug})")
        if rel not in LEGACY_PLUGIN_ALLOW_MIGRATION and "pratique-civile-quebecoise" in text:
            erreurs.append(
                f"{rel} : ancien identifiant de greffon 'pratique-civile-quebecoise' interdit en v3"
            )

    for rel in sorted(skill_md_files + skill_script_files + eval_files):
        text = decoded.get(rel)
        if text is None:
            continue
        for label, pat in BANNED_PATTERNS:
            if pat.search(text):
                erreurs.append(f"{rel} : {label} interdit")
        for old_skill in RETIRED_V1_SKILLS:
            if old_skill in text:
                erreurs.append(f"{rel} : ancien nom de compétence v1 interdit ({old_skill})")
        for old_v2_skill in RETIRED_V2_SKILLS:
            if old_v2_skill in text:
                erreurs.append(f"{rel} : ancien nom de compétence v2 interdit ({old_v2_skill})")
        for old_tool in RETIRED_V1_TOOLS:
            if re.search(rf"\b{re.escape(old_tool)}\b", text):
                erreurs.append(f"{rel} : ancien nom d'outil MCP v1 interdit ({old_tool})")

    for rel in sorted(skill_md_files):
        text = decoded.get(rel)
        if text is not None and _REPO_ROOT_SKILL_PATH_RE.search(text):
            erreurs.append(
                f"{rel} : chemin relatif à la racine du dépôt interdit dans une compétence "
                "(utiliser scripts/... ou references/...)"
            )

    return erreurs, stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Contrôle statique Droit civil québécois v3.")
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Afficher le bilan de taille des compétences après validation.",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Mode publication : interdit les marqueurs de brouillon et exige la couverture complète.",
    )
    args = parser.parse_args(argv)
    racine = Path(__file__).resolve().parent
    erreurs, stats = verifier(racine, release_mode=args.release)
    if erreurs:
        for err in erreurs:
            print(err, file=sys.stderr)
        return 1
    if args.stats:
        print(
            f"OK — SKILL.md={stats['skill_md_bytes']} B, feuilles={stats['leaf_md_bytes']} B, "
            f"total={stats['total_md_bytes']} B ({stats['total_md_bytes']/1024:.1f} KB), "
            f"mots={stats['total_md_words']}, descriptions={stats['total_description_chars']}/{MAX_PLUGIN_DESCRIPTION_TOTAL} car., "
            f"max_chargement={stats['max_per_load_bytes']}/{MAX_PER_LOAD_BYTES} B, "
            f"marqueurs={stats['release_markers_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
