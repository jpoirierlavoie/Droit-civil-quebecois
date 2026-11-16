"""Contrôle statique du dépôt « Droit civil québécois ».

Exécuter depuis la racine du dépôt :

    python verifier.py
    python verifier.py --stats

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
EXPECTED_SKILLS = frozenset(
    {
        "recherche-juridique",
        "analyse-juridique",
        "redaction-juridique",
        "administration-litige",
        "deontologie-et-pratique",
    }
)
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

MAX_DESCRIPTION_CHARS = 850
MAX_SKILL_BODY_WORDS = 1000
MAX_LEAF_WORDS = 1500
MAX_LEAF_BYTES = 12288
MAX_TOTAL_SKILLS_BYTES = 143360  # 140 KB
MAX_TOOL_COMPOUND_LEN = 64

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
        "code DMS fermé hérité de v1",
        re.compile(
            r"\b(?:PROC_DEM_INTRO|PV_SIGNIFICATION_DESIGNEE|CAB_MEMO|CAB_DEBOURSE|TRANS_INTERROGATOIRE|PIECE_COMMUNIQUEE)\b"
        ),
    ),
)

_SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
_REF_PATH_RE = re.compile(r"(?<![./\w-])references/[a-z0-9-]+\.md")
_SIBLING_LEAF_RE = re.compile(r"\.\./([a-z0-9-]+)/references/([a-z0-9-]+\.md)")
_SIBLING_SKILL_MD_RE = re.compile(r"\.\./[a-z0-9-]+/SKILL\.md")
_ANY_PARENT_REL_RE = re.compile(r"\.\./")
_SCRIPT_PATH_RE = re.compile(r"(?<![./\w-])scripts/[a-z0-9_-]+\.py")
_SCRIPT_NAME_RE = re.compile(r"^[a-z0-9_]+\.py$")
_KERNEL_RE = re.compile(
    r"<!-- SAFETY-KERNEL:START -->\n(.*?)\n<!-- SAFETY-KERNEL:END -->", re.S
)


def _iter_repo_files(racine: Path) -> list[str]:
    files: list[str] = []
    for path in sorted(racine.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(racine).as_posix()
        parts = rel.split("/")
        if ".git" in parts or "__pycache__" in parts:
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


def verifier(racine: Path) -> tuple[list[str], dict[str, int]]:
    erreurs: list[str] = []
    files = _iter_repo_files(racine)
    file_set = set(files)
    stats = {"skill_md_bytes": 0, "leaf_md_bytes": 0, "total_md_bytes": 0, "total_md_words": 0}

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

    # 2. Encoding (UTF-8 without BOM, LF only except LICENSE)
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
        if rel != "LICENSE" and "\r" in text:
            erreurs.append(f"{rel} : fins de ligne CR/CRLF interdites (LF requis)")
        decoded[rel] = text

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

    # 5. Skills, budgets, kernel parity & dead-end leaf checks
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
    total_md_bytes = 0

    for skill in skill_dirs:
        if len(skill) > 64 or not _SKILL_NAME_RE.match(skill):
            erreurs.append(f"skills/{skill} : nom de dossier invalide (kebab-case <= 64 car.)")
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
                if len(desc) > MAX_DESCRIPTION_CHARS:
                    erreurs.append(
                        f"{skill_rel} : 'description' dépasse {MAX_DESCRIPTION_CHARS} caractères ({len(desc)})"
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
        stats["total_md_words"] += words
        if words > MAX_SKILL_BODY_WORDS:
            erreurs.append(
                f"{skill_rel} : corps de {words} mots (plafond <= {MAX_SKILL_BODY_WORDS})"
            )

        km = _KERNEL_RE.search(body)
        if not km or not km.group(1).strip():
            erreurs.append(
                f"{skill_rel} : bloc canonique <!-- SAFETY-KERNEL:START -->...<!-- SAFETY-KERNEL:END --> manquant"
            )
        else:
            k_hash = hashlib.sha256(km.group(1).strip().encode("utf-8")).hexdigest()
            kernel_hashes[skill_rel] = k_hash

        if _SIBLING_SKILL_MD_RE.search(text):
            erreurs.append(
                f"{skill_rel} : renvoi en cascade interdit vers un autre SKILL.md (../<autre>/SKILL.md)"
            )
        for m in _SIBLING_LEAF_RE.finditer(text):
            target_skill, target_leaf = m.group(1), m.group(2)
            target_path = racine / "skills" / target_skill / "references" / target_leaf
            if not target_path.is_file():
                erreurs.append(
                    f"{skill_rel} : feuille voisine introuvable ({m.group(0)})"
                )

        refs_mentioned = set(_REF_PATH_RE.findall(text))
        refs_dir = racine / "skills" / skill / "references"
        refs_actual = (
            {f"references/{p.name}" for p in refs_dir.iterdir() if p.is_file()}
            if refs_dir.is_dir()
            else set()
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

        scripts_mentioned = set(_SCRIPT_PATH_RE.findall(text))
        scripts_dir = racine / "skills" / skill / "scripts"
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

    if len(set(kernel_hashes.values())) > 1:
        erreurs.append(
            "parité du noyau de sécurité rompue entre les 5 SKILL.md : "
            + ", ".join(f"{k}={v[:8]}" for k, v in sorted(kernel_hashes.items()))
        )

    for leaf_rel in sorted(skill_leaf_files):
        leaf_text = decoded.get(leaf_rel)
        if leaf_text is None:
            continue
        leaf_bytes = len(leaf_text.encode("utf-8"))
        leaf_words = len(leaf_text.split())
        stats["leaf_md_bytes"] += leaf_bytes
        stats["total_md_words"] += leaf_words
        total_md_bytes += leaf_bytes
        if leaf_bytes > MAX_LEAF_BYTES:
            erreurs.append(
                f"{leaf_rel} : taille {leaf_bytes} octets (plafond <= {MAX_LEAF_BYTES})"
            )
        if leaf_words > MAX_LEAF_WORDS:
            erreurs.append(
                f"{leaf_rel} : {leaf_words} mots (plafond <= {MAX_LEAF_WORDS})"
            )
        if _ANY_PARENT_REL_RE.search(leaf_text):
            erreurs.append(
                f"{leaf_rel} : lien relatif '../' interdit dans une feuille terminale"
            )

    stats["total_md_bytes"] = total_md_bytes
    if total_md_bytes > MAX_TOTAL_SKILLS_BYTES:
        erreurs.append(
            f"skills/**/*.md : total {total_md_bytes} octets (plafond <= {MAX_TOTAL_SKILLS_BYTES})"
        )

    # 6. Evals validation
    eval_py_rel = "evals/executer_evals.py"
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

    # 7. Retired slugs, stale v1 names, and banned patterns
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
                f"{rel} : ancien identifiant de greffon 'pratique-civile-quebecoise' interdit en v2"
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
        for old_tool in RETIRED_V1_TOOLS:
            if re.search(rf"\b{re.escape(old_tool)}\b", text):
                erreurs.append(f"{rel} : ancien nom d'outil MCP v1 interdit ({old_tool})")

    return erreurs, stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Contrôle statique Droit civil québécois v2.")
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Afficher le bilan de taille des compétences après validation.",
    )
    args = parser.parse_args(argv)
    racine = Path(__file__).resolve().parent
    erreurs, stats = verifier(racine)
    if erreurs:
        for err in erreurs:
            print(err, file=sys.stderr)
        return 1
    if args.stats:
        print(
            f"OK — SKILL.md={stats['skill_md_bytes']} B, feuilles={stats['leaf_md_bytes']} B, "
            f"total={stats['total_md_bytes']} B ({stats['total_md_bytes']/1024:.1f} KB), "
            f"mots={stats['total_md_words']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
