#!/usr/bin/env python3
"""
verifier_tout.py — Suite de vérification E2E multi-paliers pour droit-civil-quebecois.

Valide de bout en bout l'intégration du greffon et de ses serveurs MCP (Législation,
Jurisprudence, Outils) pour Claude, ChatGPT/Codex et Gemini/Antigravity, en mode simulation locale (Mock) ou
réseau en direct (Live).

Paliers de vérification :
- Palier 1 : Couverture fonctionnelle (manifestes, poignées de main, 35 outils)
- Palier 2 : Conditions aux limites & cas négatifs (auth 401/404, schémas, JSON-RPC)
- Palier 3 : Compatibilité inter-plateformes (parité Claude/Gemini, cache Antigravity)
- Palier 4 : Scénarios réels de pratique juridique québécoise (4 workflows complets)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import datetime
import http.client
import json
import os
from pathlib import Path
import re
import socket
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import urllib.error
import urllib.parse
import urllib.request

def _lire_version_manifeste() -> str:
    manifest_path = Path(__file__).resolve().parent / "plugin.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"Manifeste introuvable pour lire la version : {manifest_path}")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    ver = data.get("version") if isinstance(data, dict) else None
    if not isinstance(ver, str) or not re.match(r"^\d+\.\d+\.\d+$", ver):
        raise RuntimeError(f"Version invalide dans {manifest_path} : {ver!r}")
    return ver


# Constantes de version et d'environnement
VERSION_ATTENDUE = _lire_version_manifeste()
USER_AGENT_VERIFICATEUR = (
    "DroitCivilQuebecois-Verifier/3.1 (DroitCivil; Windows NT 10.0; Win64; x64) "
    "Python-urllib-E2E"
)

URL_SERVEURS = {
    "lois": "https://legislation.poirierlavoie.ca/mcp",
    "juris": "https://jurisprudence.poirierlavoie.ca/mcp",
    "outils": "https://outils.poirierlavoie.ca/mcp",
}

URL_MANIFESTES_ATTENDUES = {
    "lois": "https://legislation.poirierlavoie.ca/mcp/oauth",
    "juris": "https://jurisprudence.poirierlavoie.ca/mcp/oauth",
    "outils": "https://outils.poirierlavoie.ca/mcp",
}

SLUGS_CARTE_SERVEUR = {
    "lois": "legislation",
    "juris": "jurisprudence",
    "outils": "outils",
}

URL_COURTE_OUTILS = "https://outils.poirierlavoie.ca"

NOMS_OUTILS_ATTENDUS = {
    "lois": [
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
    ],
    "juris": [
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
    ],
    "outils": [
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
        "taux_boc_rates",
        "indice_ipc",
        "loyer_tal",
    ],
}


# ============================================================================
# Modèles de données de test
# ============================================================================


@dataclass
class TestResult:
    test_id: str
    name: str
    tier: int
    server: str
    passed: bool
    duration_ms: float
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    skipped: bool = False


# ============================================================================
# Moteur de simulation en mémoire (Mock Engine)
# ============================================================================


class MockMcpServer:
    """Simulateur conforme JSON-RPC 2.0 pour les 3 serveurs MCP et leurs 35 outils."""

    def __init__(self, server_name: str, secret_token: Optional[str] = None):
        self.server_name = server_name
        if secret_token is not None:
            self.secret_token = secret_token
        elif server_name == "lois":
            self.secret_token = os.environ.get("MCP_LEGISLATION_SECRET", "mock-secret-token")
        elif server_name == "juris":
            self.secret_token = os.environ.get("MCP_JURISPRUDENCE_SECRET", "mock-secret-token")
        else:
            self.secret_token = "mock-secret-token"
        self.tool_definitions = self._build_tool_definitions()

    def _build_tool_definitions(self) -> Dict[str, Dict[str, Any]]:
        tools: Dict[str, Dict[str, Any]] = {}

        if self.server_name == "lois":
            tools["list_laws"] = {
                "name": "list_laws",
                "description": "Carte du corpus avec métadonnées et plans des grands codes.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "fonction": {"type": "string"},
                        "forum": {"type": "string"},
                        "subject": {"type": "string"},
                        "structure": {"type": "boolean"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "additionalProperties": False,
                },
            }
            tools["list_subjects"] = {
                "name": "list_subjects",
                "description": "Matières de la taxonomie juridique québécoise.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "additionalProperties": False,
                },
            }
            tools["related_laws"] = {
                "name": "related_laws",
                "description": "Graphe d'interconnexion (lois habilitantes, règlements).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "law": {"type": "string"},
                        "rel_type": {"type": "string"},
                        "direction": {"type": "string", "enum": ["out", "in", "both"]},
                        "limit": {"type": "integer"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "required": ["law"],
                    "additionalProperties": False,
                },
            }
            tools["find_relevant"] = {
                "name": "find_relevant",
                "description": "Repérage heuristique déterministe de lois et divisions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            }
            tools["get_article"] = {
                "name": "get_article",
                "description": "Texte officiel verbatim d'un article avec historique.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "law": {"type": "string"},
                        "article": {"type": ["string", "integer"]},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "required": ["law", "article"],
                    "additionalProperties": False,
                },
            }
            tools["get_articles"] = {
                "name": "get_articles",
                "description": "Extraction en lot d'articles (plage from..to ou numbers).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "law": {"type": "string"},
                        "from": {"type": "string"},
                        "to": {"type": "string"},
                        "numbers": {"type": "array", "items": {"type": "string"}},
                        "limit": {"type": "integer"},
                        "offset": {"type": "integer"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "required": ["law"],
                    "additionalProperties": False,
                },
            }
            tools["get_structure"] = {
                "name": "get_structure",
                "description": "Arbre des divisions d'une loi sans les articles.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "law": {"type": "string"},
                        "root_path": {"type": "string"},
                        "depth": {"type": "integer"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "required": ["law"],
                    "additionalProperties": False,
                },
            }
            tools["get_division"] = {
                "name": "get_division",
                "description": "Texte officiel complet des articles d'une division.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "law": {"type": "string"},
                        "path": {"type": "string"},
                        "division_id": {"type": "integer"},
                        "include_text": {"type": "boolean"},
                        "limit": {"type": "integer"},
                        "offset": {"type": "integer"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "required": ["law"],
                    "additionalProperties": False,
                },
            }
            tools["search_text"] = {
                "name": "search_text",
                "description": "Recherche plein texte FTS5 avec extraits surlignés.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "law": {"type": "string"},
                        "limit": {"type": "integer"},
                        "offset": {"type": "integer"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            }
            tools["resolve_reference"] = {
                "name": "resolve_reference",
                "description": "Résolution d'une citation libre vers un article officiel.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "citation": {"type": "string"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "required": ["citation"],
                    "additionalProperties": False,
                },
            }

        elif self.server_name == "juris":
            tools["verify_citations"] = {
                "name": "verify_citations",
                "description": "Vérification de citations contre CanLII (6 verdicts).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "citations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "citation": {"type": "string"},
                                    "expected_title": {"type": "string"},
                                    "expected_year": {"type": "integer"},
                                },
                                "required": ["citation"],
                            },
                        },
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                        "refresh": {"type": "boolean"},
                    },
                    "required": ["citations"],
                    "additionalProperties": False,
                },
            }
            tools["find_case"] = {
                "name": "find_case",
                "description": "Recherche par noms des parties ou fragment d'intitulé.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "database_id": {"type": "string"},
                        "year_from": {"type": "integer"},
                        "year_to": {"type": "integer"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                        "limit": {"type": "integer"},
                        "live": {"type": "boolean"},
                    },
                    "required": ["title"],
                    "additionalProperties": False,
                },
            }
            tools["get_case"] = {
                "name": "get_case",
                "description": "Fiche CanLII complète d'une décision.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "citation": {"type": "string"},
                        "database_id": {"type": "string"},
                        "case_id": {"type": "string"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                        "refresh": {"type": "boolean"},
                    },
                    "additionalProperties": False,
                },
            }
            tools["citator"] = {
                "name": "citator",
                "description": "Citateur brut de décisions citées, citantes ou textes.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "rel": {"type": "string", "enum": ["cited", "citing", "legislation"]},
                        "citation": {"type": "string"},
                        "database_id": {"type": "string"},
                        "case_id": {"type": "string"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                        "limit": {"type": "integer"},
                        "offset": {"type": "integer"},
                        "refresh": {"type": "boolean"},
                    },
                    "required": ["rel"],
                    "additionalProperties": False,
                },
            }
            tools["subsequent_history"] = {
                "name": "subsequent_history",
                "description": "Indice heuristique de sorts ultérieurs.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "citation": {"type": "string"},
                        "database_id": {"type": "string"},
                        "case_id": {"type": "string"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                        "limit": {"type": "integer"},
                        "refresh": {"type": "boolean"},
                    },
                    "additionalProperties": False,
                },
            }
            tools["browse_cases"] = {
                "name": "browse_cases",
                "description": "Parcours chronologique des décisions d'un tribunal.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database_id": {"type": "string"},
                        "decision_date_after": {"type": "string"},
                        "decision_date_before": {"type": "string"},
                        "limit": {"type": "integer"},
                        "offset": {"type": "integer"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "required": ["database_id"],
                    "additionalProperties": False,
                },
            }
            tools["list_databases"] = {
                "name": "list_databases",
                "description": "Répertoire des tribunaux et corpus législatifs CanLII.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "kind": {"type": "string", "enum": ["case", "legislation"]},
                        "jurisdiction": {"type": "string"},
                        "query": {"type": "string"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                        "refresh": {"type": "boolean"},
                    },
                    "additionalProperties": False,
                },
            }
            tools["browse_legislation"] = {
                "name": "browse_legislation",
                "description": "Liste des lois/règlements d'un corpus législatif CanLII.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database_id": {"type": "string"},
                        "query": {"type": "string"},
                        "limit": {"type": "integer"},
                        "offset": {"type": "integer"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "required": ["database_id"],
                    "additionalProperties": False,
                },
            }
            tools["get_legislation"] = {
                "name": "get_legislation",
                "description": "Fiche CanLII d'une loi/règlement avec historique.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database_id": {"type": "string"},
                        "legislation_id": {"type": "string"},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "required": ["database_id", "legislation_id"],
                    "additionalProperties": False,
                },
            }
            tools["parse_citation"] = {
                "name": "parse_citation",
                "description": "Analyseur syntaxique hors ligne de citation canadienne.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "citation": {"type": "string"},
                    },
                    "required": ["citation"],
                    "additionalProperties": False,
                },
            }

        elif self.server_name == "outils":
            provinces_enum = ["QC", "ON", "BC", "AB", "SK", "MB", "NB", "NS", "PE", "NL", "YT", "NT", "NU"]
            tools["calendrier_holidays"] = {
                "name": "calendrier_holidays",
                "description": "Calendrier des jours fériés et non juridiques (QC / CA).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {"type": "integer", "minimum": 1900, "maximum": 2300},
                        "regime": {"type": "string", "enum": ["qc_cpc", "qc_prescription", "qc_li", "ca_li"]},
                        "province": {"type": "string", "enum": provinces_enum},
                    },
                    "required": ["year"],
                    "additionalProperties": False,
                },
            }
            tools["calendrier_deadlines"] = {
                "name": "calendrier_deadlines",
                "description": "Calculateur arithmétique exact de délais procéduraux.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "event_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                        "deadlines": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 25,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "label": {"type": "string", "minLength": 1, "maxLength": 120},
                                    "amount": {"type": "integer", "minimum": 1, "maximum": 36500},
                                    "unit": {"type": "string", "enum": ["days", "months", "years"]},
                                    "direction": {"type": "string", "enum": ["forward", "backward"]},
                                    "anchor_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                                    "anchor_time": {"type": "string", "pattern": r"^\d{2}:\d{2}(?::\d{2})?$"},
                                    "notification_mode": {"type": "string", "enum": ["none", "technological", "physical"]},
                                    "depends_on_index": {"type": "integer", "minimum": 0, "maximum": 24},
                                },
                                "required": ["amount"],
                                "additionalProperties": False,
                            },
                        },
                        "event_time": {"type": "string", "pattern": r"^\d{2}:\d{2}(?::\d{2})?$"},
                        "notification_mode": {"type": "string", "enum": ["none", "technological", "physical"]},
                        "regime": {"type": "string", "enum": ["qc_cpc", "qc_prescription", "qc_li", "ca_li"]},
                        "province": {"type": "string", "enum": provinces_enum},
                        "rollover_saturday": {"type": "boolean"},
                        "extra_non_juridical_dates": {
                            "type": "array",
                            "maxItems": 50,
                            "items": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                        },
                    },
                    "required": ["event_date", "deadlines"],
                    "additionalProperties": False,
                },
            }
            tools["interets_1619"] = {
                "name": "interets_1619",
                "description": "Calcul d'intérêts légaux (5%), indemnité art. 1619 C.c.Q., taux contractuel ou taux préférentiel BDC V80691311 + marge.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mode": {"type": "string", "enum": ["legal_plus_1619", "legal_only", "contractual", "prime_plus_margin"]},
                        "end_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                        "rate_bps": {"type": "integer", "minimum": 0, "maximum": 50000},
                        "spread_bps": {"type": "integer", "minimum": -5000, "maximum": 50000},
                        "rate_overrides": {
                            "type": "array",
                            "maxItems": 40,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "quarter": {"type": "string", "pattern": r"^\d{4}-Q[1-4]$"},
                                    "laf_rate_bps": {"type": "integer", "minimum": 0, "maximum": 50000},
                                },
                                "required": ["quarter", "laf_rate_bps"],
                                "additionalProperties": False,
                            },
                        },
                        "tranches": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 50,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "label": {"type": "string", "minLength": 1, "maxLength": 120},
                                    "principal_cents": {"type": "integer", "minimum": 1, "maximum": 1000000000000},
                                    "start_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                                    "end_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                                    "rate_bps": {"type": "integer", "minimum": 0, "maximum": 50000},
                                    "spread_bps": {"type": "integer", "minimum": -5000, "maximum": 50000},
                                },
                                "required": ["principal_cents", "start_date"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["end_date", "tranches"],
                    "additionalProperties": False,
                },
            }
            tools["greffe_parse_number"] = {
                "name": "greffe_parse_number",
                "description": "Décomposition hors ligne de numéro de dossier de cour.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "court_file_number": {"type": "string", "minLength": 1, "maxLength": 40},
                    },
                    "required": ["court_file_number"],
                    "additionalProperties": False,
                },
            }
            tools["palais_list"] = {
                "name": "palais_list",
                "description": "Répertoire des palais de justice et points de service.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "district": {"type": "string", "maxLength": 60},
                        "query": {"type": "string", "maxLength": 60},
                        "type": {"type": "string", "enum": ["palais", "point_de_service"]},
                    },
                    "additionalProperties": False,
                },
            }
            tools["palais_get"] = {
                "name": "palais_get",
                "description": "Fiche d'un lieu de justice par numéro de greffe ou nom.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "greffe_number": {"type": "string", "minLength": 1, "maxLength": 3},
                        "palais": {"type": "string", "minLength": 1, "maxLength": 60},
                    },
                    "additionalProperties": False,
                },
            }
            tools["registre_search"] = {
                "name": "registre_search",
                "description": "Recherche hors ligne dans les instantanés locaux du REQ (RBQ/OPC/RENA), Corporations Canada et GLEIF (LEI canadiens).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "minLength": 2, "maxLength": 200},
                        "jurisdiction": {"type": "string", "enum": ["qc", "ca", "gleif", "all"]},
                        "active_only": {"type": "boolean"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 25},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            }
            tools["registre_get_entity"] = {
                "name": "registre_get_entity",
                "description": "Fiche détaillée hors ligne d'une entreprise par NEQ, numéro fédéral, NE ou LEI (GLEIF Level 1/2 et liens vers portails officiels).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "neq": {"type": "string", "minLength": 1, "maxLength": 20},
                        "corporation_number": {"type": "string", "minLength": 1, "maxLength": 20},
                        "bn_ne": {"type": "string", "minLength": 1, "maxLength": 20},
                        "lei": {"type": "string", "minLength": 1, "maxLength": 40},
                    },
                    "additionalProperties": False,
                },
            }
            tools["adresse_verify"] = {
                "name": "adresse_verify",
                "description": "Vérification et normalisation hors ligne d'une adresse québécoise selon le RQA (MRNF) ou recherche inversée par lot cadastral / matricule.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "address": {"type": "string", "minLength": 2, "maxLength": 300},
                        "civic_number": {"type": "string", "minLength": 1, "maxLength": 20},
                        "street": {"type": "string", "minLength": 1, "maxLength": 160},
                        "unit": {"type": "string", "minLength": 1, "maxLength": 40},
                        "municipality": {"type": "string", "minLength": 1, "maxLength": 120},
                        "postal_code": {"type": "string", "minLength": 3, "maxLength": 10},
                        "lot_number": {"type": "string", "minLength": 1, "maxLength": 30},
                        "matricule": {"type": "string", "minLength": 4, "maxLength": 30},
                        "max_candidates": {"type": "integer", "minimum": 1, "maximum": 10},
                    },
                    "additionalProperties": False,
                },
            }
            tools["terminologie_lookup"] = {
                "name": "terminologie_lookup",
                "description": "Recherche bilingue FR/EN dans la base terminologique juridique hiérarchisée (rangs 1 à 4).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "minLength": 1, "maxLength": 200},
                        "source_lang": {"type": "string", "enum": ["fr", "en", "auto"]},
                        "domain_filter": {"type": "string", "minLength": 1, "maxLength": 100},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 25},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            }
            tools["termino_attestations"] = {
                "name": "termino_attestations",
                "description": "Attestations statutaires bilingues FR/EN alignées dans le corpus législatif consolidé.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "term": {"type": "string", "minLength": 2, "maxLength": 160},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                        "law_filter": {"type": "string", "minLength": 1, "maxLength": 80},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                    },
                    "required": ["term", "lang"],
                    "additionalProperties": False,
                },
            }
            tools["terminologie_scan"] = {
                "name": "terminologie_scan",
                "description": "Détection en lecture seule des contaminations de droit français, de common law et d'archaïsmes.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "minLength": 1, "maxLength": 32000},
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                        "context_system": {"type": "string", "enum": ["droit_civil_qc", "bijuridique_federal"]},
                    },
                    "required": ["text", "lang"],
                    "additionalProperties": False,
                },
            }
            tools["taux_boc_rates"] = {
                "name": "taux_boc_rates",
                "description": "Consultation hors ligne des taux de change Banque du Canada / StatCan et taux V39079/V122530/V80691311 avec conversion BigInt (art. 12 Loi sur la monnaie).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "enum": ["fx", "policy", "bank", "prime", "all_rates"]},
                        "currency": {"type": "string", "minLength": 3, "maxLength": 16},
                        "date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                        "start_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                        "end_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                        "amount": {"type": "string", "pattern": r"^\d+(?:\.\d{1,6})?$"},
                        "direction": {"type": "string", "enum": ["foreign_to_cad", "cad_to_foreign"]},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    },
                    "additionalProperties": False,
                },
            }
            tools["indice_ipc"] = {
                "name": "indice_ipc",
                "description": "Consultation hors ligne de l'IPC StatCan (18-10-0004-01 / 18-10-0005-01) et indexation contractuelle exacte en BigInt avec contrôle strict d'année de base.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "geo": {"type": "string", "enum": ["quebec", "montreal_rmr", "quebec_rmr", "canada"]},
                        "product": {"type": "string", "enum": ["all_items", "shelter", "rented_accommodation", "rent", "health_care_services"]},
                        "frequency": {"type": "string", "enum": ["monthly", "annual"]},
                        "uom": {"type": "string", "enum": ["2002=100", "1992=100"]},
                        "end_uom": {"type": "string", "enum": ["2002=100", "1992=100"]},
                        "period": {"type": "string", "pattern": r"^\d{4}(?:-\d{2})?$"},
                        "start_period": {"type": "string", "pattern": r"^\d{4}(?:-\d{2})?$"},
                        "end_period": {"type": "string", "pattern": r"^\d{4}(?:-\d{2})?$"},
                        "amount": {"type": "string", "pattern": r"^\d+(?:\.\d{1,6})?$"},
                        "floor_bps": {"type": "integer", "minimum": -5000, "maximum": 50000},
                        "cap_bps": {"type": "integer", "minimum": -5000, "maximum": 50000},
                        "rounding": {"type": "string", "enum": ["half_away_from_zero", "half_up"]},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    },
                    "additionalProperties": False,
                },
            }
            tools["loyer_tal"] = {
                "name": "loyer_tal",
                "description": "Barèmes officiels du TAL (2015–2027), calculateur post-1er janv. 2026 (RLRQ, c. T-15.01, r. 2) en BigInt et loyers moyens du marché SCHL.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mode": {"type": "string", "enum": ["calcul_2026", "bareme", "schl"]},
                        "year": {"type": "integer", "minimum": 1987, "maximum": 2027},
                        "notice_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                        "lease_renewal_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                        "section_f_exemption_5_ans": {"type": "boolean"},
                        "current_rent_cents": {"type": "integer", "minimum": 1, "maximum": 100000000},
                        "is_rpa": {"type": "boolean"},
                        "rpa_personal_services_cents": {"type": "integer", "minimum": 0, "maximum": 100000000},
                        "building_residential_rents_cents": {"type": "integer", "minimum": 1, "maximum": 1000000000},
                        "building_non_residential_rents_cents": {"type": "integer", "minimum": 0, "maximum": 1000000000},
                        "other_annual_revenue_cents": {"type": "integer", "minimum": 0, "maximum": 1000000000},
                        "municipal_taxes_prev_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                        "municipal_taxes_curr_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                        "school_taxes_prev_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                        "school_taxes_curr_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                        "insurance_prev_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                        "insurance_curr_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                        "snow_removal_prev_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                        "snow_removal_curr_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                        "capital_works": {
                            "type": "array",
                            "maxItems": 30,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "label": {"type": "string", "minLength": 1, "maxLength": 120},
                                    "gross_amount_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                                    "grant_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                                    "third_party_indemnity_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                                    "reduced_interest_loan_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                                    "annual_loan_repayment_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                                    "target_unit_benefits": {"type": "boolean"},
                                    "beneficiary_scope": {"type": "string", "enum": ["all_units", "residential_only", "target_unit_only"]},
                                    "beneficiary_rents_monthly_cents": {"type": "integer", "minimum": 1, "maximum": 1000000000},
                                },
                                "required": ["gross_amount_cents"],
                                "additionalProperties": False,
                            },
                        },
                        "new_expenses": {
                            "type": "array",
                            "maxItems": 30,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "label": {"type": "string", "minLength": 1, "maxLength": 120},
                                    "annual_amount_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                                    "grant_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                                    "target_unit_benefits": {"type": "boolean"},
                                    "beneficiary_scope": {"type": "string", "enum": ["all_units", "residential_only", "target_unit_only"]},
                                    "beneficiary_rents_monthly_cents": {"type": "integer", "minimum": 1, "maximum": 1000000000},
                                },
                                "required": ["annual_amount_cents"],
                                "additionalProperties": False,
                            },
                        },
                        "aid_variations": {
                            "type": "array",
                            "maxItems": 30,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "label": {"type": "string", "minLength": 1, "maxLength": 120},
                                    "previous_annual_aid_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                                    "current_annual_aid_cents": {"type": "integer", "minimum": 0, "maximum": 10000000000},
                                    "target_unit_benefits": {"type": "boolean"},
                                    "beneficiary_scope": {"type": "string", "enum": ["all_units", "residential_only", "target_unit_only"]},
                                    "beneficiary_rents_monthly_cents": {"type": "integer", "minimum": 1, "maximum": 1000000000},
                                },
                                "required": ["previous_annual_aid_cents", "current_annual_aid_cents"],
                                "additionalProperties": False,
                            },
                        },
                        "cmhc_geo": {"type": "string", "minLength": 2, "maxLength": 120},
                        "structure_type": {"type": "string", "enum": ["row_and_apartment_3_plus", "apartment_3_plus", "apartment_6_plus", "row_3_plus"]},
                        "unit_type": {"type": "string", "enum": ["all", "bachelor", "one_bedroom", "two_bedroom", "three_bedroom"]},
                    },
                    "required": ["mode"],
                    "additionalProperties": False,
                },
            }

        return tools

    def handle_request(
        self,
        raw_body: bytes,
        headers: Dict[str, str],
        method: str = "POST",
        path: str = "/mcp",
    ) -> Tuple[int, Dict[str, str], bytes]:
        """Traite une requête HTTP simulée et renvoie (status_code, headers, body_bytes)."""
        self.last_received_headers = dict(headers)

        # Règle WAF Cloudflare : blocage des agents automatisés sans User-Agent conforme
        ua = headers.get("user-agent") or headers.get("User-Agent") or ""
        if not ua or ("Python-urllib" in ua and "DroitCivil" not in ua and "PratiqueCivile" not in ua):
            return 403, {"Content-Type": "application/json"}, b'{"error":"Forbidden: Cloudflare WAF bot block"}'

        # 1. CORS Preflight OPTIONS (doit répondre avant auth, statut 204 No Content)
        if method == "OPTIONS" and not path.startswith("/.well-known/oauth-protected-resource"):
            origin = headers.get("origin") or headers.get("Origin") or "*"
            return 204, {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": (
                    "Content-Type, Authorization, MCP-Protocol-Version, "
                    "Mcp-Method, Mcp-Name, Mcp-Session-Id, Last-Event-ID, Accept"
                ),
                "Access-Control-Max-Age": "86400",
                "Vary": "Origin",
            }, b""

        # 2. Garde d'hôte (Host header security whitelist)
        host_header = headers.get("host") or headers.get("Host") or ""
        if host_header:
            hostname = host_header.split(":")[0].strip().lower()
            allowed_hosts = {
                "outils.poirierlavoie.ca",
                "legislation.poirierlavoie.ca",
                "jurisprudence.poirierlavoie.ca",
                "localhost",
                "127.0.0.1",
                "::1",
            }
            if hostname not in allowed_hosts:
                return 403, {"Content-Type": "application/json"}, b'{"error":"Forbidden: invalid host"}'

        # 3. Endpoint healthz / health
        if path in ("/health", "/healthz") and method == "GET":
            svc_name = "mcp-outils" if self.server_name == "outils" else self.server_name
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps({
                    "status": "ok",
                    "service": svc_name,
                    "version": VERSION_ATTENDUE,
                    "tools": list(self.tool_definitions.keys()),
                }).encode("utf-8"),
            )

        # 4. Endpoint server card SEP-2127
        if path == "/mcp/server-card" and method == "GET":
            repo_slugs = {
                "lois": "MCP-Legislation",
                "juris": "MCP-Jurisprudence",
                "outils": "MCP-Outils",
            }
            card_slug = SLUGS_CARTE_SERVEUR[self.server_name]
            card_headers = (
                []
                if self.server_name == "outils"
                else [
                    {
                        "name": "Authorization",
                        "description": "Jeton individuel de titulaire (« Bearer <jeton> ») ou connexion OAuth 2.1 sur /mcp/oauth via acces.poirierlavoie.ca.",
                        "isRequired": True,
                        "isSecret": True,
                    }
                ]
            )
            return (
                200,
                {"Content-Type": "application/mcp-server-card+json; charset=utf-8"},
                json.dumps({
                    "$schema": "https://static.modelcontextprotocol.io/schemas/v1/server-card.schema.json",
                    "name": f"ca.poirierlavoie.{card_slug}/mcp-{card_slug}",
                    "title": f"MCP {card_slug.capitalize()}",
                    "description": f"MCP Server {card_slug} pour droit civil québécois",
                    "version": VERSION_ATTENDUE,
                    "repository": {
                        "url": f"https://github.com/jpoirierlavoie/{repo_slugs[self.server_name]}",
                        "source": "github",
                    },
                    "remotes": [
                        {
                            "type": "streamable-http",
                            "url": URL_SERVEURS[self.server_name],
                            "supportedProtocolVersions": ["2026-07-28", "2025-11-25", "2025-06-18", "2025-03-26"],
                            "headers": card_headers,
                        }
                    ],
                }).encode("utf-8"),
            )

        # 4b. Métadonnées RFC 9728 (OAuth 2.1 sur /mcp/oauth uniquement ; racine en 404)
        if path == "/.well-known/oauth-protected-resource":
            return 404, {"Content-Type": "text/plain; charset=utf-8"}, b"Not found"
        if path == "/.well-known/oauth-protected-resource/mcp/oauth":
            if self.server_name == "outils":
                return 404, {"Content-Type": "text/plain; charset=utf-8"}, b"Not found"
            if method == "OPTIONS":
                return (
                    204,
                    {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                        "Access-Control-Allow-Headers": "Accept, Content-Type, MCP-Protocol-Version",
                        "Access-Control-Max-Age": "86400",
                    },
                    b"",
                )
            if method not in ("GET", "HEAD"):
                return (
                    405,
                    {"Content-Type": "application/json; charset=utf-8", "Allow": "GET, HEAD, OPTIONS"},
                    b'{"error":"method_not_allowed"}',
                )
            srv_slug = SLUGS_CARTE_SERVEUR[self.server_name]
            doc = {
                "resource": f"https://{srv_slug}.poirierlavoie.ca/mcp/oauth",
                "authorization_servers": ["https://acces.poirierlavoie.ca"],
                "bearer_methods_supported": ["header"],
                "scopes_supported": ["les_deux", srv_slug],
                "resource_documentation": f"https://{srv_slug}.poirierlavoie.ca/",
            }
            return (
                200,
                {"Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*"},
                b"" if method == "HEAD" else json.dumps(doc).encode("utf-8"),
            )

        # 5. Authentification selon doctrine Phase 3 :
        # - Montage direct /mcp sur lois et juris : refus uniforme 404 sans corps ni WWW-Authenticate
        # - Montage OAuth /mcp/oauth sur lois et juris : refus 401 RFC 9728 avec WWW-Authenticate
        # - Outils : accès public sans secret
        est_oauth_mount = path == "/mcp/oauth"
        if path.startswith("/mcp/oauth/"):
            return 404, {"Content-Type": "application/json"}, b""

        auth_header = headers.get("authorization") or headers.get("Authorization") or ""
        is_authenticated = bool(auth_header) and (
            auth_header in (f"Bearer {self.secret_token}", "Bearer mock-secret-token")
        ) and not auth_header.startswith("Bearer invalid")

        if self.server_name in ("lois", "juris") and not is_authenticated:
            if est_oauth_mount:
                srv_slug = SLUGS_CARTE_SERVEUR[self.server_name]
                www_auth = (
                    f'Bearer resource_metadata="https://{srv_slug}.poirierlavoie.ca/.well-known/oauth-protected-resource/mcp/oauth", '
                    f'scope="{srv_slug} les_deux"'
                )
                return (
                    401,
                    {
                        "Content-Type": "application/json; charset=utf-8",
                        "WWW-Authenticate": www_auth,
                        "Cache-Control": "no-store",
                    },
                    json.dumps({"error": "unauthorized"}).encode("utf-8"),
                )
            return 404, {"Cache-Control": "no-store"}, b""

        # 6. Vérification méthode HTTP (après identité pour S8 non-oracle)
        if method not in ("GET", "POST", "HEAD"):
            return 405, {"Content-Type": "application/json"}, b'{"error":"Method Not Allowed"}'

        # 7. Garde de sécurité sur la taille du corps (>64 Kio)
        if len(raw_body) > 65536:
            return 413, {"Content-Type": "application/json"}, b'{"error":"Payload Too Large"}'

        # 7. Décodage JSON-RPC
        try:
            req_text = raw_body.decode("utf-8")
        except UnicodeDecodeError:
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error: invalid UTF-8"},
                    "id": None,
                }).encode("utf-8"),
            )

        if not req_text.strip():
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error: empty request body"},
                    "id": None,
                }).encode("utf-8"),
            )

        try:
            req_data = json.loads(req_text)
        except json.JSONDecodeError:
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error: invalid JSON"},
                    "id": None,
                }).encode("utf-8"),
            )

        # Détection des requêtes par lots interdites
        if isinstance(req_data, list):
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: Batch requests are not supported.",
                    },
                    "id": None,
                }).encode("utf-8"),
            )

        if not isinstance(req_data, dict):
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32600, "message": "Invalid Request: Root must be object"},
                    "id": None,
                }).encode("utf-8"),
            )

        if req_data.get("jsonrpc") != "2.0":
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32600, "message": "Invalid Request: missing jsonrpc 2.0"},
                    "id": req_data.get("id") if not isinstance(req_data.get("id"), (dict, list)) else None,
                }).encode("utf-8"),
            )

        rpc_id = req_data.get("id")
        if isinstance(rpc_id, (dict, list)):
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: id must be a string, number, or null",
                    },
                    "id": None,
                }).encode("utf-8"),
            )

        method = req_data.get("method", "")
        params = req_data.get("params") or {}

        # 8. Traitement des méthodes JSON-RPC
        if method == "initialize":
            res = {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": f"poirierlavoie-{self.server_name}",
                        "version": VERSION_ATTENDUE,
                    },
                    "capabilities": {"tools": {}},
                },
            }
            return 200, {"Content-Type": "application/json"}, json.dumps(res).encode("utf-8")

        elif method == "tools/list":
            tools_list = list(self.tool_definitions.values())
            res = {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {"tools": tools_list},
            }
            return 200, {"Content-Type": "application/json"}, json.dumps(res).encode("utf-8")

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments") or {}

            if tool_name not in self.tool_definitions:
                return (
                    200,
                    {"Content-Type": "application/json"},
                    json.dumps({
                        "jsonrpc": "2.0",
                        "id": rpc_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: tool '{tool_name}' unknown",
                        },
                    }).encode("utf-8"),
                )

            # Validation du schéma d'entrée
            schema = self.tool_definitions[tool_name].get("inputSchema", {})
            val_err = self._validate_args(tool_name, tool_args, schema)
            if val_err:
                res = {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "result": {
                        "isError": True,
                        "content": [{"type": "text", "text": f"Erreur de validation : {val_err}"}],
                    },
                }
                return 200, {"Content-Type": "application/json"}, json.dumps(res).encode("utf-8")

            # Exécution déterministe de l'outil
            exec_result = self._execute_tool(tool_name, tool_args)
            res = {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": exec_result,
            }
            return 200, {"Content-Type": "application/json"}, json.dumps(res).encode("utf-8")

        else:
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps({
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: unknown method '{method}'",
                    },
                }).encode("utf-8"),
            )

    def _validate_schema_value(
        self, value: Any, schema: Dict[str, Any], path: str = ""
    ) -> Optional[str]:
        """Valide récursivement une valeur contre un sous-schéma JSON Schema."""
        expected_type = schema.get("type")
        if expected_type == "object":
            if not isinstance(value, dict):
                label = path or "arguments"
                return f"Type invalide pour '{label}' : attendu object, reçu {type(value).__name__}."
            props = schema.get("properties", {})
            if schema.get("additionalProperties") is False:
                for key in value:
                    if key not in props:
                        prefix = f"{path}." if path else ""
                        return f"Propriété non autorisée '{prefix}{key}' détectée (additionalProperties: false)."
            for req_key in schema.get("required", []):
                if req_key not in value or value[req_key] is None:
                    prefix = f"{path}." if path else ""
                    return f"Paramètre requis manquant : '{prefix}{req_key}'."
            for k, v in value.items():
                if k in props:
                    sub_path = f"{path}.{k}" if path else k
                    err = self._validate_schema_value(v, props[k], sub_path)
                    if err:
                        return err
            return None

        if expected_type == "array":
            if not isinstance(value, list):
                return f"Type invalide pour '{path}' : attendu array, reçu {type(value).__name__}."
            if "minItems" in schema and len(value) < schema["minItems"]:
                return f"Tableau '{path}' doit contenir au moins {schema['minItems']} élément(s)."
            if "maxItems" in schema and len(value) > schema["maxItems"]:
                return f"Tableau '{path}' dépasse le maximum de {schema['maxItems']} élément(s)."
            items_schema = schema.get("items")
            if isinstance(items_schema, dict):
                for idx, item in enumerate(value):
                    err = self._validate_schema_value(item, items_schema, f"{path}[{idx}]")
                    if err:
                        return err
            return None

        if expected_type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                return f"Type invalide pour '{path}' : attendu integer, reçu {type(value).__name__}."
            if "minimum" in schema and value < schema["minimum"]:
                return f"Valeur hors borne pour '{path}' : {value} < minimum {schema['minimum']}."
            if "maximum" in schema and value > schema["maximum"]:
                return f"Valeur hors borne pour '{path}' : {value} > maximum {schema['maximum']}."
            return None

        if expected_type == "boolean":
            if not isinstance(value, bool):
                return f"Type invalide pour '{path}' : attendu boolean, reçu {type(value).__name__}."
            return None

        if expected_type == "string":
            if not isinstance(value, str):
                return f"Type invalide pour '{path}' : attendu string, reçu {type(value).__name__}."
            if "minLength" in schema and len(value) < schema["minLength"]:
                return f"Chaîne trop courte pour '{path}' (minimum {schema['minLength']} car.)."
            if "maxLength" in schema and len(value) > schema["maxLength"]:
                return f"Chaîne trop longue pour '{path}' (maximum {schema['maxLength']} car.)."
            if "pattern" in schema:
                target_s = value.strip() if path in ("amount", "currency") else value
                if not re.match(schema["pattern"], target_s):
                    return f"Format invalide pour '{path}' : '{value}'."
            if "enum" in schema and value not in schema["enum"]:
                return f"Valeur invalide '{value}' pour '{path}' : attendu parmi {schema['enum']}."
            return None

        return None

    def _validate_args(
        self, tool_name: str, args: Dict[str, Any], schema: Dict[str, Any]
    ) -> Optional[str]:
        """Valide strictement les arguments contre le schéma de l'outil."""
        if not isinstance(args, dict):
            return "Les arguments doivent être un objet JSON."

        schema_err = self._validate_schema_value(args, schema, "")
        if schema_err:
            return schema_err

        # Règle XOR pour palais_get
        if tool_name == "palais_get":
            has_greffe = bool(args.get("greffe_number"))
            has_palais = bool(args.get("palais"))
            if has_greffe and has_palais:
                return "Exclusion mutuelle (XOR) violée : fournir soit greffe_number soit palais, pas les deux."
            if not has_greffe and not has_palais:
                return "Exclusion mutuelle (XOR) violée : fournir au moins greffe_number ou palais."

        # Règle XOR pour registre_get_entity (exactement l'un de neq, corporation_number, bn_ne, lei)
        if tool_name == "registre_get_entity":
            provided = [k for k in ("neq", "corporation_number", "bn_ne", "lei") if bool(str(args.get(k, "")).strip())]
            if len(provided) != 1:
                return "Exclusion mutuelle (XOR) violée : fournir exactement l'un des identifiants neq, corporation_number, bn_ne ou lei."
            if "lei" in provided:
                lei_clean = str(args["lei"]).strip().upper()
                if not re.match(r"^[A-Z0-9]{20}$", lei_clean):
                    return "LEI invalide : 20 caractères alphanumériques ISO 17442 attendus."

        # Règles directe vs recherche inversée (lot_number / matricule) pour adresse_verify
        if tool_name == "adresse_verify":
            has_lot = bool(str(args.get("lot_number", "")).strip())
            has_mat = bool(str(args.get("matricule", "")).strip())
            has_forward = any(
                bool(str(args.get(k, "")).strip())
                for k in ("address", "civic_number", "street", "unit", "postal_code")
            )
            if has_lot and has_mat:
                return "Paramètres incompatibles : fournir lot_number ou matricule, pas les deux."
            if (has_lot or has_mat) and has_forward:
                return "Recherche inversée (lot_number/matricule) incompatible avec les paramètres d'adresse directe."
            if not (has_lot or has_mat) and not any(bool(str(args.get(k, "")).strip()) for k in ("address", "street", "postal_code")):
                return "Paramètre requis manquant : fournir address, street, postal_code, lot_number ou matricule."

        # Règles interets_1619 (prime_plus_margin, spread_bps, rate_overrides, contractual)
        if tool_name == "interets_1619":
            end_d = str(args.get("end_date", ""))
            try:
                datetime.date.fromisoformat(end_d)
            except ValueError:
                return f"Date de fin invalide '{end_d}'."
            mode = args.get("mode", "legal_plus_1619")
            tranches = args.get("tranches", [])
            if not tranches:
                return "La liste des tranches ne peut pas être vide."
            if mode == "prime_plus_margin":
                if args.get("rate_overrides"):
                    return "rate_overrides est interdit en mode 'prime_plus_margin'."
                if args.get("rate_bps") is not None:
                    return "rate_bps est réservé au mode 'contractual'."
            else:
                if args.get("spread_bps") is not None or any(
                    isinstance(t, dict) and t.get("spread_bps") is not None for t in tranches
                ):
                    return "spread_bps est réservé au mode 'prime_plus_margin'."
            if mode != "contractual" and (
                args.get("rate_bps") is not None
                or any(isinstance(t, dict) and t.get("rate_bps") is not None for t in tranches)
            ):
                return "rate_bps est réservé au mode 'contractual'."
            for idx, t in enumerate(tranches):
                st_d = str(t.get("start_date", ""))
                tr_end = str(t.get("end_date") or end_d)
                try:
                    datetime.date.fromisoformat(st_d)
                    datetime.date.fromisoformat(tr_end)
                except ValueError as err:
                    return f"Tranche #{idx + 1} : date invalide ({err})."
                if tr_end < st_d:
                    return f"Tranche #{idx + 1} : end_date ({tr_end}) précède start_date ({st_d})."
                if mode == "contractual" and t.get("rate_bps") is None and args.get("rate_bps") is None:
                    return f"Tranche #{idx + 1} : rate_bps est requis (par tranche ou globalement) en mode 'contractual'."

        # Règles taux_boc_rates
        if tool_name == "taux_boc_rates":
            has_date = args.get("date") is not None
            has_start = args.get("start_date") is not None
            has_end = args.get("end_date") is not None
            if has_date and (has_start or has_end):
                return "date est exclusif avec start_date et end_date."
            if has_start != has_end:
                return "start_date et end_date doivent être fournis ensemble."
            if not has_date and not (has_start and has_end):
                return "Préciser soit 'date', soit la paire complète 'start_date' et 'end_date'."
            for dk in ("date", "start_date", "end_date"):
                if args.get(dk):
                    try:
                        datetime.date.fromisoformat(str(args[dk]))
                    except ValueError:
                        return f"Date invalide pour {dk} : '{args[dk]}'."
            if has_start and has_end and str(args["start_date"]) > str(args["end_date"]):
                return f"start_date ({args['start_date']}) ne peut pas être postérieure à end_date ({args['end_date']})."
            eff_cat = args.get("category") or (
                "fx" if (args.get("currency") is not None or args.get("amount") is not None) else "all_rates"
            )
            cur = args.get("currency")
            if cur is not None:
                cur_u = cur.strip().upper()
                m_valet = re.match(r"^FX([A-Z]{3})CAD$", cur_u)
                code_u = m_valet.group(1) if m_valet else cur_u
                if code_u == "CAD":
                    return "Ne pas passer 'CAD' pour currency : tous les taux BdC sont déjà exprimés face au CAD."
                if not re.match(r"^[A-Z]{3}$", code_u):
                    return f"Code de devise invalide « {cur} »."
                if eff_cat != "fx":
                    return "currency requiert category='fx'."
            if eff_cat == "fx" and not (cur and cur.strip()):
                return "Préciser 'currency' (p. ex. 'USD', 'EUR', 'GBP', 'JPY') pour consulter un taux de change."
            if args.get("amount") is not None:
                amt_s = str(args["amount"]).strip()
                if not re.match(r"^\d+(?:\.\d{1,6})?$", amt_s):
                    return f"Format de montant invalide pour 'amount' : '{args['amount']}'."
                whole, _, frac = amt_s.partition(".")
                if int(whole) == 0 and (not frac or int(frac) == 0):
                    return "Le montant 'amount' doit être strictement supérieur à zéro."
                if eff_cat != "fx" or not has_date or not cur:
                    return "La conversion avec amount requiert category='fx', date et currency."
            elif args.get("direction") is not None:
                return "direction requiert amount."

        # Règles indice_ipc
        if tool_name == "indice_ipc":
            has_per = args.get("period") is not None
            has_start = args.get("start_period") is not None
            has_end = args.get("end_period") is not None
            if has_per and (has_start or has_end):
                return "period est exclusif avec start_period et end_period."
            if has_start != has_end:
                return "start_period et end_period doivent être fournis ensemble."
            if not has_per and not (has_start and has_end):
                return "Préciser soit 'period', soit la paire complète 'start_period' et 'end_period'."
            if has_per and args.get("end_uom") is not None:
                return "Le paramètre 'end_uom' s'applique uniquement avec 'start_period' et 'end_period'."
            parsed_freqs: Dict[str, Tuple[str, int]] = {}
            for pk in ("period", "start_period", "end_period"):
                pval = args.get(pk)
                if pval is not None:
                    m_p = re.match(r"^(\d{4})(?:-(\d{2}))?$", pval.strip())
                    if not m_p:
                        return f"Période IPC invalide '{pval}'."
                    yr = int(m_p.group(1))
                    if yr < 1914:
                        return f"Année IPC hors plage ({yr}) : >= 1914 requis."
                    if m_p.group(2) is not None:
                        mo = int(m_p.group(2))
                        if mo < 1 or mo > 12:
                            return f"Mois IPC invalide dans '{pval}' (01..12)."
                        pf = ("monthly", yr * 100 + mo)
                    else:
                        pf = ("annual", yr)
                    if args.get("frequency") and args["frequency"] != pf[0]:
                        return f"Incohérence entre frequency='{args['frequency']}' et {pk}='{pval}'."
                    parsed_freqs[pk] = pf
            if has_start and has_end:
                if parsed_freqs["start_period"][0] != parsed_freqs["end_period"][0]:
                    return "start_period et end_period doivent avoir la même fréquence ('YYYY-MM' ou 'YYYY')."
                if parsed_freqs["start_period"][1] > parsed_freqs["end_period"][1]:
                    return "start_period ne peut pas être postérieure à end_period."
            geo = args.get("geo", "quebec")
            product = args.get("product", "all_items")
            if geo in ("montreal_rmr", "quebec_rmr") and product in ("rent", "health_care_services"):
                return f"La composante '{product}' est absente à l'échelle RMR ({geo}, vectorId=0)."
            uom = args.get("uom", "2002=100")
            end_uom = args.get("end_uom", uom)
            if args.get("amount") is not None:
                amt_s = str(args["amount"]).strip()
                if not re.match(r"^\d+(?:\.\d{1,6})?$", amt_s):
                    return f"Format de montant invalide pour 'amount' : '{args['amount']}'."
                whole, _, frac = amt_s.partition(".")
                if int(whole) == 0 and (not frac or int(frac) == 0):
                    return "Le montant 'amount' doit être strictement supérieur à zéro."
                if not (has_start and has_end):
                    return "L'indexation contractuelle avec amount requiert start_period et end_period."
                if uom != end_uom:
                    return f"Divergence d'année de base ({uom} vs {end_uom}) : indexation bloquée sans facteur de raccordement officiel StatCan."
                if (
                    args.get("floor_bps") is not None
                    and args.get("cap_bps") is not None
                    and args["floor_bps"] > args["cap_bps"]
                ):
                    return f"Plancher incohérent : floor_bps ({args['floor_bps']}) > cap_bps ({args['cap_bps']})."
            elif any(args.get(k) is not None for k in ("floor_bps", "cap_bps", "rounding")):
                return "floor_bps, cap_bps et rounding requièrent amount."

        # Règles loyer_tal
        if tool_name == "loyer_tal":
            if args.get("mode") == "calcul_2026":
                if not args.get("lease_renewal_date") or args.get("current_rent_cents") is None:
                    return "Le mode 'calcul_2026' requiert lease_renewal_date et current_rent_cents."
                try:
                    datetime.date.fromisoformat(str(args["lease_renewal_date"]))
                    if args.get("notice_date"):
                        datetime.date.fromisoformat(str(args["notice_date"]))
                except ValueError as err:
                    return f"Date invalide dans loyer_tal : {err}"
                for pair_label, k_prev, k_curr in (
                    ("taxes municipales", "municipal_taxes_prev_cents", "municipal_taxes_curr_cents"),
                    ("taxes scolaires", "school_taxes_prev_cents", "school_taxes_curr_cents"),
                    ("assurances", "insurance_prev_cents", "insurance_curr_cents"),
                    ("déneigement", "snow_removal_prev_cents", "snow_removal_curr_cents"),
                ):
                    if (args.get(k_prev) is not None) != (args.get(k_curr) is not None):
                        return f"Paramètre incomplet pour {pair_label} : fournir simultanément précédent et courant."
                if (args.get("rpa_personal_services_cents") or 0) > 0 and not args.get("is_rpa"):
                    return "rpa_personal_services_cents > 0 requiert is_rpa=true."
                notice_d = args.get("notice_date")
                if str(args["lease_renewal_date"]) < "2026-01-01" and not (notice_d and str(notice_d) < "2026-01-01"):
                    return "En mode 'calcul_2026', lease_renewal_date doit être >= 2026-01-01 (sauf avis < 2026-01-01)."

        # Règle XOR pour get_case, citator et subsequent_history
        if tool_name in ("get_case", "citator", "subsequent_history"):
            has_cit = bool(str(args.get("citation", "")).strip())
            has_db = bool(str(args.get("database_id", "")).strip())
            has_case = bool(str(args.get("case_id", "")).strip())
            any_id = has_db or has_case
            both_ids = has_db and has_case
            if (has_cit and any_id) or (not has_cit and not both_ids):
                return (
                    "Fournir EXACTEMENT l'une des deux formes : soit « citation », "
                    "soit le couple « database_id » + « case_id »."
                )

        # Règle citation vide
        if tool_name == "parse_citation":
            if not args.get("citation", "").strip():
                return "La citation ne peut pas être vide."

        # Contrôle de date pour calendrier
        if tool_name == "calendrier_deadlines":
            ev_date = args.get("event_date", "")
            try:
                datetime.date.fromisoformat(ev_date)
            except ValueError:
                return f"Date invalide '{ev_date}' : format attendu YYYY-MM-DD valide."
            if not args.get("deadlines"):
                return "La liste des délais (deadlines) ne peut pas être vide."

        return None

    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute la logique métier de l'outil simulé avec des retours réalistes."""
        # --- Législation ---
        if tool_name == "list_laws":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps([
                            {"code": "ccq", "titre": "Code civil du Québec", "chapitre": "CCQ-1991"},
                            {"code": "cpc", "titre": "Code de procédure civile", "chapitre": "C-25.01"},
                            {"code": "laf", "titre": "Loi sur l'administration fiscale", "chapitre": "A-6.002"},
                        ], ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "list_subjects":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps([
                            {"id": "obligations", "titre": "Obligations et contrats"},
                            {"id": "biens", "titre": "Biens et propriété"},
                            {"id": "famille", "titre": "Droit de la famille"},
                            {"id": "procedure", "titre": "Procédure civile"},
                        ], ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "related_laws":
            law = args.get("law", "").lower()
            relations = [
                {"law": "cpc", "target": "Tarif des honoraires judiciaires", "rel_type": "reglement-de"},
                {"law": "cpc", "target": "Règlement de la Cour supérieure (civile)", "rel_type": "reglement-de"},
            ]
            return {"content": [{"type": "text", "text": json.dumps(relations, ensure_ascii=False)}]}

        elif tool_name == "find_relevant":
            query = args.get("query", "").lower()
            results = []
            if "vice" in query or "cach" in query or "infiltration" in query or "garantie" in query:
                results.append({
                    "law": "ccq",
                    "article": "1726",
                    "division": "Livre Cinquième, Des contrats nommés, De la vente",
                    "score": 0.95,
                })
            else:
                results.append({"law": "ccq", "article": "1457", "score": 0.70})
            return {"content": [{"type": "text", "text": json.dumps(results, ensure_ascii=False)}]}

        elif tool_name == "get_article":
            law = args.get("law", "").lower()
            art = str(args.get("article", "")).strip()
            textes = {
                ("ccq", "1726"): (
                    "Le vendeur est tenu de garantir à l'acheteur que le bien et ses accessoires sont, "
                    "lors de la vente, exempts de vices cachés qui le rendent impropre à l'usage auquel "
                    "on le destine ou qui diminuent tellement son utilité que l'acheteur ne l'aurait "
                    "pas acheté, ou n'aurait pas donné si haut prix, s'il les avait connus. Il n'est "
                    "cependant pas tenu de garantir le vice caché que l'acheteur connaissait ou qu'un "
                    "acheteur prudent et diligent aurait pu constater."
                ),
                ("ccq", "1457"): (
                    "Toute personne a le devoir de respecter les règles de conduite qui, suivant les "
                    "circonstances, les usages ou la loi, s'imposent à elle, de manière à ne pas causer "
                    "de préjudice à autrui."
                ),
                ("ccq", "2925"): (
                    "L'action qui tend à faire valoir un droit personnel ou un droit réel mobilier se "
                    "prescrit par trois ans, s'il n'est pas autrement pourvu."
                ),
                ("ccq", "1619"): (
                    "Des dommages-intérêts additionnels sont alloués pour la réparation d'un préjudice "
                    "matériel ou corporel... calculés au taux fixé pour les créances de l'État."
                ),
                ("cpc", "145"): (
                    "Le défendeur dispose d'un délai de 15 jours à compter de la notification de la demande "
                    "introductive d'instance pour y répondre..."
                ),
                ("cpc", "111"): (
                    "La notification faite par un moyen technologique après 17 heures est réputée avoir "
                    "été faite le jour ouvrable juridique suivant."
                ),
            }
            corps = textes.get((law, art), f"Texte officiel de l'article {art} du {law.upper()}.")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "law": law,
                            "article": art,
                            "text": corps,
                            "consolidation_date": "2026-01-01",
                        }, ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "get_articles":
            law = args.get("law", "").lower()
            from_art = int(args.get("from", "1726")) if args.get("from", "").isdigit() else 1726
            to_art = int(args.get("to", "1731")) if args.get("to", "").isdigit() else 1731
            arts = [
                {"law": law, "article": str(num), "text": f"Texte de l'article {num} du {law.upper()}"}
                for num in range(from_art, min(to_art + 1, from_art + 20))
            ]
            return {"content": [{"type": "text", "text": json.dumps(arts, ensure_ascii=False)}]}

        elif tool_name == "get_structure":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "law": args.get("law"),
                            "divisions": [
                                {"path": "ga:l_cinquieme", "titre": "Livre Cinquième — Des obligations"},
                                {"path": "ga:l_dixieme", "titre": "Livre Dixième — De la prescription"},
                            ],
                        }, ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "get_division":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "law": args.get("law"),
                            "path": args.get("path"),
                            "titre": "De la prescription extinctive",
                            "articles": ["2921", "2922", "2925", "2930"],
                        }, ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "search_text":
            query = args.get("query", "")
            hits = []
            if "corporel" in query.lower():
                hits.append({
                    "law": args.get("law", "ccq"),
                    "article": "2930",
                    "snippet": f"Correspondance avec '{query}' : l'action fondée sur l'obligation de réparer un préjudice corporel se prescrit par trois ans.",
                    "score": 0.94,
                })
            hits.append({
                "law": args.get("law", "ccq"),
                "article": "2925",
                "snippet": f"Correspondance avec '{query}' : action personnelle se prescrit par trois ans.",
                "score": 0.88,
            })
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(hits, ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "resolve_reference":
            cit = args.get("citation", "")
            cit_norm = re.sub(r"[.\s]", "", cit.lower())
            if "145" in cit and ("cpc" in cit_norm or "c-25" in cit_norm):
                res = {"law": "cpc", "article": "145", "titre": "Délai de réponse de 15 jours"}
            elif "1619" in cit and ("ccq" in cit_norm or "codecivil" in cit_norm):
                res = {"law": "ccq", "article": "1619", "titre": "Indemnité additionnelle"}
            else:
                res = {"law": "ccq", "article": "1726", "titre": "Garantie légale de qualité"}
            return {
                "content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False)}],
                "structuredContent": {
                    "input": cit,
                    "resolved": {
                        "kind": "article",
                        "law": res["law"],
                        "number": res["article"],
                        "title": res["titre"],
                    },
                },
            }

        # --- Jurisprudence ---
        elif tool_name == "verify_citations":
            citations = args.get("citations", [])
            rapports = []
            for item in citations:
                cit_str = item.get("citation", "")
                exp_title = (item.get("expected_title") or "").strip()
                if "2020 QCCA 495" in cit_str:
                    real_title = "SNC-Lavalin inc. (Terratech inc. et SNC-Lavalin Environnement inc.) c. Deguise"
                    verdict = (
                        "DISCORDANTE"
                        if exp_title and exp_title.lower() not in real_title.lower()
                        else "CONFIRMÉE"
                    )
                    rapports.append({
                        "citation": cit_str,
                        "verdict": verdict,
                        "title": real_title,
                        "database_id": "qcca",
                        "case_id": "2020qcca495",
                        "url": "https://www.canlii.org/fr/qc/qcca/doc/2020/2020qcca495/2020qcca495.html",
                    })
                elif "2015 QCCA 1526" in cit_str:
                    real_title = "Droit de la famille — 152325"
                    verdict = (
                        "DISCORDANTE"
                        if exp_title and exp_title.lower() not in real_title.lower()
                        else "CONFIRMÉE"
                    )
                    rapports.append({
                        "citation": cit_str,
                        "verdict": verdict,
                        "title": real_title,
                        "database_id": "qcca",
                        "case_id": "2015qcca1526",
                        "url": "https://www.canlii.org/fr/qc/qcca/doc/2015/2015qcca1526/2015qcca1526.html",
                    })
                else:
                    rapports.append({
                        "citation": cit_str,
                        "verdict": "INTROUVABLE",
                        "details": "Aucune concordance exacte CanLII.",
                    })
            return {"content": [{"type": "text", "text": json.dumps(rapports, ensure_ascii=False)}]}

        elif tool_name == "find_case":
            title = args.get("title", "")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps([
                            {
                                "title": f"Affaire concernant {title}",
                                "citation": "2020 QCCA 495",
                                "database_id": "qcca",
                                "year": 2020,
                            }
                        ], ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "get_case":
            cit = args.get("citation") or f"{args.get('database_id')} {args.get('case_id')}"
            if "2015" in str(cit):
                fiche = (
                    "**Droit de la famille — 152325**\n"
                    "- Référence : 2015 QCCA 1526 (qcca/2015qcca1526)\n"
                    "- Tribunal : Cour d'appel du Québec\n"
                    "- Date : 22 septembre 2015\n"
                    "- N° de dossier : 500-09-024761-140\n"
                    "- URL : https://www.canlii.org/fr/qc/qcca/doc/2015/2015qcca1526/2015qcca1526.html"
                )
            else:
                fiche = (
                    "**SNC-Lavalin inc. (Terratech inc. et SNC-Lavalin Environnement inc.) c. Deguise**\n"
                    "- Référence : 2020 QCCA 495 (qcca/2020qcca495)\n"
                    "- Tribunal : Cour d'appel du Québec\n"
                    "- Date : 6 avril 2020\n"
                    "- N° de dossier : 200-09-008788-140\n"
                    "- URL : https://www.canlii.org/fr/qc/qcca/doc/2020/2020qcca495/2020qcca495.html"
                )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": fiche,
                    }
                ]
            }

        elif tool_name == "citator":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps([
                            {"citation": "2018 QCCS 1234", "title": "Décision citante A"},
                            {"citation": "2021 QCCA 789", "title": "Décision citante B"},
                        ], ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "subsequent_history":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps([
                            {
                                "citation": "2021 CSC 12",
                                "title": "Pourvoi rejeté par la Cour suprême du Canada",
                                "verdict": "CONFIRMÉ",
                            }
                        ], ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "browse_cases":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps([
                            {"citation": "2026 QCCA 10", "date": "2026-01-15"},
                            {"citation": "2026 QCCA 11", "date": "2026-01-16"},
                        ], ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "list_databases":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps([
                            {"database_id": "qcca", "name": "Cour d'appel du Québec"},
                            {"database_id": "qccs", "name": "Cour supérieure du Québec"},
                            {"database_id": "qccq", "name": "Cour du Québec"},
                        ], ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "browse_legislation":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps([
                            {"legislation_id": "rlrq-c-c-25.01", "title": "Code de procédure civile"},
                        ], ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "get_legislation":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "legislation_id": args.get("legislation_id"),
                            "database_id": args.get("database_id"),
                            "status": "in_force",
                        }, ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "parse_citation":
            cit = args.get("citation", "").strip()
            # Analyse de format déterministe
            m = re.match(r"^(\d{4})\s+([A-Z]+)\s+(\d+)$", cit)
            if m:
                year, tribunal, num = m.groups()
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "citation": cit,
                                "style": "neutral",
                                "year": int(year),
                                "tribunal": tribunal,
                                "database_id": tribunal.lower(),
                                "case_id": f"{year}{tribunal.lower()}{num}",
                                "constructible": True,
                            }, ensure_ascii=False),
                        }
                    ]
                }
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "citation": cit,
                            "style": "unknown",
                            "constructible": False,
                        }, ensure_ascii=False),
                    }
                ]
            }

        # --- Outils ---
        elif tool_name == "calendrier_holidays":
            year = args.get("year", 2026)
            holidays = [
                {"date": f"{year}-01-01", "nom": "Jour de l'An", "basis": "art. 82 al. 1 C.p.c."},
                {"date": f"{year}-04-03", "nom": "Vendredi saint", "basis": "art. 82 al. 2 C.p.c."},
                {"date": f"{year}-04-06", "nom": "Lundi de Pâques", "basis": "art. 82 al. 2 C.p.c."},
                {"date": f"{year}-05-18", "nom": "Journée nationale des patriotes", "basis": "art. 82 al. 3 C.p.c."},
                {"date": f"{year}-06-24", "nom": "Fête nationale du Québec", "basis": "art. 82 al. 4 C.p.c."},
                {"date": f"{year}-07-01", "nom": "Fête du Canada", "basis": "art. 82 al. 5 C.p.c."},
                {"date": f"{year}-09-07", "nom": "Fête du Travail", "basis": "art. 82 al. 6 C.p.c."},
                {"date": f"{year}-10-12", "nom": "Action de grâce", "basis": "art. 82 al. 7 C.p.c."},
                {"date": f"{year}-12-25", "nom": "Noël", "basis": "art. 82 al. 8 C.p.c."},
            ]
            return {"content": [{"type": "text", "text": json.dumps(holidays, ensure_ascii=False)}]}

        elif tool_name == "calendrier_deadlines":
            ev_date_str = args.get("event_date", "2026-07-03")
            d_date = datetime.date.fromisoformat(ev_date_str)
            mode = args.get("notification_mode", "none")
            ev_time = args.get("event_time", "")

            # Art. 111 al. 2 C.p.c. : notification techno après 17h00 strictly -> report au prochain jour ouvrable
            shifted_start = d_date
            is_after_17h = False
            if ev_time:
                parts = [int(p) for p in ev_time.split(":") if p.isdigit()]
                if len(parts) >= 2:
                    h, m = parts[0], parts[1]
                    s = parts[2] if len(parts) >= 3 else 0
                    is_after_17h = (h * 3600 + m * 60 + s) > 17 * 3600

            if mode == "technological" and is_after_17h:
                shifted_start += datetime.timedelta(days=1)
                while shifted_start.weekday() >= 5:  # Samedi ou dimanche
                    shifted_start += datetime.timedelta(days=1)

            results = []
            for idx, item in enumerate(args.get("deadlines", [])):
                amt = item.get("amount", 15)
                due = shifted_start + datetime.timedelta(days=amt)
                # Art. 83 C.p.c. : si samedi ou dimanche, reporte au lundi
                while due.weekday() >= 5:
                    due += datetime.timedelta(days=1)
                results.append({
                    "index": idx,
                    "label": item.get("label", "Délai"),
                    "amount": amt,
                    "input_anchor_date": d_date.isoformat(),
                    "effective_anchor_date": shifted_start.isoformat(),
                    "anchor_shifted_art_111": shifted_start != d_date,
                    "effective_date": due.isoformat(),
                })

            summary_lines = [
                f"- {r['label']} : échéance effective {r['effective_date']} (ancre {r['effective_anchor_date']})"
                for r in results
            ]
            return {
                "content": [{"type": "text", "text": "\n".join(summary_lines)}],
                "structuredContent": {
                    "regime": args.get("regime", "qc_cpc"),
                    "results": results,
                },
            }

        elif tool_name == "interets_1619":
            tranches = args.get("tranches", [])
            mode = args.get("mode", "legal_plus_1619")
            total_principal = sum(t.get("principal_cents", 0) for t in tranches)
            interet_legal_cents = 0
            indemnite_cents = 0
            contractual_cents = 0
            if mode == "legal_plus_1619":
                interet_legal_cents = int(total_principal * 0.05)
                indemnite_cents = int(total_principal * 0.04)
            elif mode == "legal_only":
                interet_legal_cents = int(total_principal * 0.05)
            elif mode == "contractual":
                rate_bps = args.get("rate_bps", 800)
                contractual_cents = int(total_principal * rate_bps / 10000)
            elif mode == "prime_plus_margin":
                prime_bps = 495
                spread_bps = args.get("spread_bps", 0)
                eff_bps = max(0, prime_bps + spread_bps)
                contractual_cents = int(total_principal * eff_bps / 10000)

            total_interest_cents = interet_legal_cents + indemnite_cents + contractual_cents
            grand_total_cents = total_principal + total_interest_cents
            gardes = [
                {"code": "INTERET_SIMPLE_ART_1620_CCQ", "message": "Calcul en intérêt simple (art. 1620 C.c.Q.), convention Exact/Exact."},
            ]
            if mode == "prime_plus_margin":
                gardes.append({
                    "code": "TAUX_BOC_PRIME_INDICATIF_BANCAIRE",
                    "message": "Fondé sur le taux préférentiel indicatif BDC V80691311 ; vérifier le taux du prêteur contractuel, la date de prise d'effet et tout plancher.",
                })

            return {
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Calcul ({mode}) jusqu'au {args.get('end_date')} — "
                            f"Capital : {total_principal} cents, Intérêt légal : {interet_legal_cents} cents, "
                            f"Indemnité additionnelle : {indemnite_cents} cents, "
                            f"Intérêt contractuel/préférentiel : {contractual_cents} cents, "
                            f"Total général : {grand_total_cents} cents."
                        ),
                    }
                ],
                "structuredContent": {
                    "mode": mode,
                    "convention": "Exact/Exact (365/366), date de départ exclue / date de fin incluse",
                    "laf_table_last_quarter": "2026-Q4",
                    "prime_table_last_verified_date": "2026-11-18",
                    "truncated_any": False,
                    "total_principal_cents": total_principal,
                    "total_legal_interest_cents": interet_legal_cents,
                    "total_additional_indemnity_cents": indemnite_cents,
                    "total_contractual_interest_cents": contractual_cents,
                    "total_interest_cents": total_interest_cents,
                    "grand_total_cents": grand_total_cents,
                    "end_date": args.get("end_date"),
                    "provenance": {"source": "Art. 28 L.A.F. (Revenu Québec) / BDC V80691311", "verified_at": "2026-11-18"},
                    "gardes": gardes,
                },
            }

        elif tool_name == "greffe_parse_number":
            num = args.get("court_file_number", "")
            # Format standard québécois : 500-17-012345-211
            parts = num.split("-")
            greffe = parts[0] if len(parts) >= 1 else "500"
            court_code = parts[1] if len(parts) >= 2 else "17"
            districts = {"500": "Montréal", "200": "Québec", "400": "Trois-Rivières"}
            district = districts.get(greffe, "District québécois")
            court = "Cour supérieure" if court_code == "17" else "Cour d'appel" if court_code == "09" else "Cour du Québec"
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Dossier {num} — Greffe {greffe} ({district}), {court}.",
                    }
                ],
                "structuredContent": {
                    "outcome": "judicial",
                    "court_file_number": num,
                    "greffe_number": greffe,
                    "district": district,
                    "court": court,
                    "matter": "civil",
                },
            }

        elif tool_name == "palais_list":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps([
                            {"palais": "Montréal", "greffe_number": "500", "district": "Montréal"},
                            {"palais": "Québec", "greffe_number": "200", "district": "Québec"},
                        ], ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "palais_get":
            greffe = args.get("greffe_number")
            palais = args.get("palais")
            if greffe == "500" or (palais and "montr" in palais.lower()):
                info = {
                    "name": "Montréal",
                    "greffe_number": "500",
                    "district": "Montréal",
                    "street_address": "1, rue Notre-Dame Est, Montréal (Québec) H2Y 1B6",
                }
            else:
                info = {
                    "name": "Québec",
                    "greffe_number": "200",
                    "district": "Québec",
                    "street_address": "300, boulevard Jean-Lesage, Québec (Québec) G1K 8K6",
                }
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Palais de justice de {info['name']} (greffe {info['greffe_number']}) — {info['street_address']}.",
                    }
                ],
                "structuredContent": {"palais": info},
            }

        elif tool_name == "registre_search":
            q = args.get("query", "")
            jur = args.get("jurisdiction", "all")
            is_gleif = jur == "gleif" or bool(re.match(r"^[A-Za-z0-9]{20}$", q.strip()))
            cand = {
                "jurisdiction": "gleif" if is_gleif else "qc",
                "neq": None if is_gleif else "1172345678",
                "corporation_number": None,
                "bn_ne": None,
                "lei": "549300BOREALE0000001",
                "has_lei": True,
                "nom_officiel": "BANQUE BORÉALE DU CANADA" if is_gleif else "9123-4567 QUÉBEC INC.",
                "autres_noms": [] if is_gleif else ["Construction Boréale"],
                "forme_juridique": "Banque" if is_gleif else "Société par actions ou compagnie",
                "statut": "ACTIVE" if is_gleif else "Immatriculée",
                "is_active": True,
                "faillite_declaree": False,
                "date_constitution": "2018-04-12",
                "ville": "Montréal",
                "has_rbq_licence": not is_gleif,
                "has_opc_permit": False,
                "in_rena": False,
            }
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Recherche d'entreprises pour « {q} » : 1 candidat ({cand['nom_officiel']}, LEI {cand['lei']}).",
                    }
                ],
                "structuredContent": {
                    "query": q,
                    "jurisdiction": jur,
                    "active_only": bool(args.get("active_only", False)),
                    "count": 1,
                    "exact_match_found": True,
                    "snapshots": {"req": "2026-11-01", "gleif": "2026-11-18"},
                    "entities": [cand],
                    "provenance": {"source": "Instantané REQ / Corporations Canada / GLEIF CC0", "verified_at": "2026-11-18"},
                    "gardes": [
                        {"code": "REGISTRE_ABSENCE_PERSONNES_PHYSIQUES", "message": "Les administrateurs et actionnaires personnes physiques sont exclus du jeu ouvert."},
                        {"code": "REGISTRE_FRAICHEUR_ET_OPPOSABILITE_LPLE", "message": "Données issues d'instantanés périodiques sans valeur d'attestation LPLE."},
                        {"code": "REGISTRE_GLEIF_DECLARATIF_CONSOLIDATION", "message": "Les liens GLEIF Level 2 reflètent la consolidation comptable déclarée et n'établissent ni contrôle juridique ni bénéficiaire ultime."},
                    ],
                },
            }

        elif tool_name == "registre_get_entity":
            if args.get("lei"):
                lookup_by = "lei"
                lookup_val = str(args["lei"]).strip().upper()
                neq = "1172345678"
            elif args.get("corporation_number"):
                lookup_by = "corporation_number"
                lookup_val = str(args["corporation_number"]).strip()
                neq = None
            elif args.get("bn_ne"):
                lookup_by = "bn_ne"
                lookup_val = str(args["bn_ne"]).strip()
                neq = None
            else:
                lookup_by = "neq"
                lookup_val = str(args.get("neq") or "1172345678").strip()
                neq = lookup_val
            lei_val = lookup_val if lookup_by == "lei" else "549300BOREALE0000001"
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Fiche entreprise ({lookup_by}={lookup_val}) — 9123-4567 QUÉBEC INC. / LEI {lei_val}.",
                    }
                ],
                "structuredContent": {
                    "lookup_by": lookup_by,
                    "lookup_value": lookup_val,
                    "snapshots": {"req": "2026-11-01", "gleif": "2026-11-18"},
                    "quebec": {
                        "neq": neq or "1172345678",
                        "nom_officiel": "9123-4567 QUÉBEC INC.",
                        "is_active": True,
                        "domicile_declare": {
                            "dispense_adresse": False,
                            "adresse": "1, rue Notre-Dame Est, Montréal (Québec)",
                            "ville": "Montréal",
                            "code_postal": "H2Y1B6",
                        },
                    } if neq else None,
                    "federal": None if neq else {"corporation_number": lookup_val, "nom_officiel": "CORPORATION BORÉALE INC."},
                    "gleif": {
                        "lei": lei_val,
                        "is_canadian": True,
                        "nom_legal": "9123-4567 QUÉBEC INC.",
                        "statut_entite": "ACTIVE",
                        "registration_status": "ISSUED",
                        "next_renewal_date": "2027-06-15",
                        "matched_neq": neq or "1172345678",
                        "matched_corporation_number": None,
                        "parent_direct": {"lei": "549300PARENTDIRECT01", "nom_legal": "GROUPE BORÉAL LTÉE", "pays": "CA"},
                        "parent_ultime": {"lei": "549300PARENTULTIME02", "nom_legal": "GROUPE BORÉAL LTÉE", "pays": "CA"},
                        "exceptions_declaration": [],
                        "filiales_canadiennes": [],
                        "filiales_canadiennes_total": 0,
                    },
                    "portails_officiels": {
                        "req": "https://www.registreentreprises.gouv.qc.ca/REQNA/GR/GR03/GR03A71.RechercheRegistre.MVC/GR03A71",
                        "corporations_canada": "https://ised-isde.canada.ca/cc/lgcy/fdrlCrpSrch.html?locale=fr",
                        "isc_pisc": "https://ised-isde.canada.ca/site/corporations-canada/fr/particuliers-ayant-controle-important",
                        "gleif": f"https://search.gleif.org/#/record/{lei_val}",
                    },
                    "provenance": {"source": "Instantané REQ / GLEIF CC0", "verified_at": "2026-11-18"},
                    "gardes": [
                        {"code": "REGISTRE_ABSENCE_PERSONNES_PHYSIQUES", "message": "Les administrateurs et actionnaires personnes physiques sont exclus du jeu ouvert."},
                        {"code": "REGISTRE_FRAICHEUR_ET_OPPOSABILITE_LPLE", "message": "Données issues d'instantanés périodiques sans valeur d'attestation LPLE."},
                        {"code": "REGISTRE_GLEIF_DECLARATIF_CONSOLIDATION", "message": "Les liens GLEIF Level 2 reflètent la consolidation comptable déclarée et n'établissent ni contrôle juridique ni bénéficiaire ultime."},
                    ],
                },
            }

        elif tool_name == "adresse_verify":
            lot_arg = str(args.get("lot_number", "")).strip()
            mat_arg = str(args.get("matricule", "")).strip()
            lots = [lot_arg] if lot_arg else ["2359285"]
            mat = mat_arg if mat_arg else "9891-44-1234"
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Adresse RQA vérifiée (exact_civic) : 1, rue Notre-Dame Est, Montréal (Québec) H2Y 1B6 — lot {lots[0]} — district judiciaire probable : Montréal (500).",
                    }
                ],
                "structuredContent": {
                    "status": "exact_civic",
                    "adresse_normalisee": "1, rue Notre-Dame Est, Montréal (Québec) H2Y 1B6",
                    "corrections_appliquees": [],
                    "candidates": [
                        {
                            "adresse_normalisee": "1, rue Notre-Dame Est, Montréal (Québec) H2Y 1B6",
                            "etat_rqa": "Certifiée",
                            "lots_cadastraux": lots,
                            "matricule_evaluation": mat,
                            "lot_source": "rqa_unite",
                            "repli_immeuble_parent": False,
                            "ambiguites_cadastrales": [],
                            "district_judiciaire_probable": {"district": "Montréal", "greffes": ["500"]},
                        }
                    ],
                    "provenance": {"source": "Référentiel québécois des adresses (RQA, MRNF)", "verified_at": "2026-11-01"},
                    "gardes": [
                        {"code": "ADRESSE_EXISTENCE_CIVIQUE_NON_DOMICILE", "message": "Confirme l'existence municipale sans établir le domicile d'une partie."},
                        {"code": "ADRESSE_LOT_ET_MATRICULE_SANS_VALEUR_LEGALE", "message": "Les numéros de lot et le matricule sont indicatifs et sans valeur légale (art. 3030 al. 2 et 3032 C.c.Q.)."},
                    ],
                },
            }

        elif tool_name == "terminologie_lookup":
            q = args.get("query", "mortgage")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Recherche terminologique pour « {q} » : FR « hypothèque » ↔ EN « hypothec » (à éviter en droit civil québécois : « mortgage »).",
                    }
                ],
                "structuredContent": {
                    "query": q,
                    "count": 1,
                    "fiches": [
                        {
                            "rang_source": 1,
                            "terme_fr": "hypothèque",
                            "terme_en": "hypothec",
                            "systeme_juridique": "droit_civil_qc",
                            "base_legale": "art. 2660 C.c.Q.",
                        }
                    ],
                    "provenance": {"source": "Glossaire bijuridique québécois", "verified_at": "2026-11-15"},
                    "gardes": [
                        {"code": "TERMINOLOGIE_AIDE_REDACTION_NON_NORMATIVE", "message": "Outil d'aide à la rédaction, seul le texte législatif officiel fait foi."},
                    ],
                },
            }

        elif tool_name == "termino_attestations":
            term = args.get("term", "hypothec")
            lang = args.get("lang", "en")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Attestations statutaires pour « {term} » ({lang}) : 142 articles dans le C.c.Q. (art. 2660 : hypothèque / hypothec).",
                    }
                ],
                "structuredContent": {
                    "term": term,
                    "lang": lang,
                    "total_matching_articles": 142,
                    "by_law": [{"law_id": "ccq", "official_cite": "RLRQ, c. CCQ-1991", "article_count": 142}],
                    "provenance": {"source": "Concordancier législatif bilingue", "verified_at": "2026-11-15"},
                    "gardes": [
                        {"code": "TERMINOLOGIE_AIDE_REDACTION_NON_NORMATIVE", "message": "Outil d'aide à la rédaction, seul le texte législatif officiel fait foi."},
                    ],
                },
            }

        elif tool_name == "terminologie_scan":
            txt = args.get("text", "")
            lang = args.get("lang", "fr")
            occurrences = []
            if "mortgage" in txt.lower() or "assignation" in txt.lower():
                occurrences.append({
                    "matched_text": "mortgage" if "mortgage" in txt.lower() else "assignation",
                    "risk_category": "anglicisme_ou_common_law" if "mortgage" in txt.lower() else "francisme_france",
                    "suggested_replacement": "hypothec" if "mortgage" in txt.lower() else "demande introductive d'instance",
                })
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Contrôle de contamination ({lang}) : {len(occurrences)} signalement(s) repéré(s) sans réécriture du texte.",
                    }
                ],
                "structuredContent": {
                    "lang": lang,
                    "scanned_length": len(txt),
                    "flagged_count": len(occurrences),
                    "occurrences": occurrences,
                    "provenance": {"source": "Règles de contrôle bijuridique", "verified_at": "2026-11-15"},
                    "gardes": [
                        {"code": "TERMINOLOGIE_AIDE_REDACTION_NON_NORMATIVE", "message": "Outil d'aide à la rédaction, seul le texte législatif officiel fait foi."},
                    ],
                },
            }

        elif tool_name == "taux_boc_rates":
            def _round_half_away(num: int, den: int) -> int:
                neg = num < 0
                abs_n = -num if neg else num
                q, r = divmod(abs_n, den)
                res_v = q + 1 if r * 2 >= den else q
                return -res_v if neg else res_v

            def _fmt_micros6(micros: int) -> str:
                neg = micros < 0
                abs_m = -micros if neg else micros
                return f"{'-' if neg else ''}{abs_m // 1_000_000}.{abs_m % 1_000_000:06d}"

            def _fmt_cents(cents: int) -> str:
                neg = cents < 0
                abs_c = -cents if neg else cents
                return f"{'-' if neg else ''}{abs_c // 100}.{abs_c % 100:02d}"

            cat = args.get("category") or ("fx" if (args.get("currency") or args.get("amount")) else "all_rates")
            is_range = bool(args.get("start_date") and args.get("end_date"))
            req_date = args.get("date") or args.get("start_date") or "2026-11-18"
            raw_cur = (args.get("currency") or "USD").strip().upper()
            m_valet = re.match(r"^FX([A-Z]{3})CAD$", raw_cur)
            cur = m_valet.group(1) if m_valet else raw_cur
            is_pre_2017 = req_date < "2017-05-01"
            methodology = "noon_spot_pre_2017_05_01" if is_pre_2017 else "daily_average_1630_et"
            rate_micros = 1291400 if (is_pre_2017 and cur == "USD") else 1395000
            dt_req = datetime.date.fromisoformat(req_date)
            rollback_days = 2 if dt_req.weekday() == 6 else (1 if dt_req.weekday() == 5 else 0)
            eff_date = (dt_req - datetime.timedelta(days=rollback_days)).isoformat()
            rolled_back = rollback_days > 0
            cad_per_foreign = _fmt_micros6(rate_micros)
            foreign_per_cad_micros = _round_half_away(1_000_000 * 1_000_000, rate_micros)
            fx_obs = []
            int_obs = []
            currency_summary = None
            if cat == "fx":
                currency_summary = {
                    "code": cur,
                    "name_fr": "Dollar américain" if cur == "USD" else cur,
                    "name_en": "US Dollar" if cur == "USD" else cur,
                    "active_daily": True,
                }
                fx_obs.append({
                    "currency_code": cur,
                    "requested_date": None if is_range else req_date,
                    "effective_observation_date": eff_date,
                    "rolled_back": rolled_back,
                    "rollback_days": rollback_days,
                    "rate_methodology": methodology,
                    "cad_per_foreign_unit": cad_per_foreign,
                    "foreign_per_cad_approx": _fmt_micros6(foreign_per_cad_micros),
                    "rate_micros": rate_micros,
                })
            else:
                series_map = {
                    "V39079": ("Taux cible du financement à un jour (taux directeur, V39079)", 375),
                    "V122530": ("Taux officiel d'escompte mensuel (V122530)", 400),
                    "V80691311": ("Taux préférentiel hebdomadaire des banques à charte (V80691311)", 495),
                }
                target_sids = (
                    ["V39079"] if cat == "policy" else
                    ["V122530"] if cat == "bank" else
                    ["V80691311"] if cat == "prime" else
                    ["V39079", "V122530", "V80691311"]
                )
                for sid in target_sids:
                    lbl_fr, bps_val = series_map[sid]
                    int_obs.append({
                        "series_id": sid,
                        "series_label_fr": lbl_fr,
                        "requested_date": None if is_range else req_date,
                        "effective_observation_date": eff_date,
                        "rolled_back": rolled_back,
                        "rollback_days": rollback_days,
                        "rate_bps": bps_val,
                        "rate_percent": f"{bps_val / 100:.2f} %",
                    })
            conv = None
            if args.get("amount"):
                amt_s = args["amount"].strip()
                if "." in amt_s:
                    w_p, f_p = amt_s.split(".", 1)
                    amt_num = int(f"{w_p}{f_p}")
                    amt_scale = 10 ** len(f_p)
                else:
                    amt_num = int(amt_s)
                    amt_scale = 1
                direction = args.get("direction", "foreign_to_cad")
                if direction == "foreign_to_cad":
                    raw_cents = _round_half_away(amt_num * rate_micros * 100, amt_scale * 1_000_000)
                    raw_micros = _round_half_away(amt_num * rate_micros * 1_000_000, amt_scale * 1_000_000)
                else:
                    raw_cents = _round_half_away(amt_num * 1_000_000 * 100, amt_scale * rate_micros)
                    raw_micros = _round_half_away(amt_num * 1_000_000 * 1_000_000, amt_scale * rate_micros)
                conv = {
                    "direction": direction,
                    "foreign_currency": cur,
                    "input_amount": amt_s,
                    "effective_observation_date": eff_date,
                    "rate_methodology": methodology,
                    "cad_per_foreign_unit": cad_per_foreign,
                    "converted_currency": "CAD" if direction == "foreign_to_cad" else cur,
                    "converted_cents": raw_cents,
                    "converted_amount_2dec": _fmt_cents(raw_cents),
                    "converted_amount_exact_6dec": _fmt_micros6(raw_micros),
                    "legal_basis": "Loi sur la monnaie (L.R.C. 1985, c. C-52, art. 12); art. 1561 et 3161 C.c.Q.",
                }
            gardes = [
                {"code": "TAUX_BOC_INSTANTANE_HORS_LIGNE", "message": "Données issues d'un instantané local Banque du Canada / StatCan (aucun appel réseau sortant)."},
            ]
            if is_pre_2017 and cat == "fx":
                gardes.append({"code": "TAUX_BOC_NOON_HISTORIQUE_PRE_2017", "message": "Taux au comptant de midi HE antérieur au 2017-05-01."})
            if rolled_back:
                gardes.append({"code": "TAUX_BOC_REPORT_JOUR_OUVRABLE_PRECEDENT", "message": "Date demandée non ouvrable : report au jour ouvrable précédent."})
            if conv is not None:
                gardes.append({"code": "TAUX_BOC_CONVERSION_LOI_MONNAIE", "message": "La date de conversion judiciaire applicable relève d'une question de droit (art. 12 Loi sur la monnaie ; art. 1561 et 3161 C.c.Q.)."})
            return {
                "content": [{"type": "text", "text": f"Taux BdC ({cat}) pour {req_date} (effectif {eff_date})."}],
                "structuredContent": {
                    "category": cat,
                    "mode": "range" if is_range else "single_date",
                    "requested_date": args.get("date"),
                    "start_date": args.get("start_date"),
                    "end_date": args.get("end_date"),
                    "currency": currency_summary,
                    "count": len(fx_obs) + len(int_obs),
                    "fx_observations": fx_obs,
                    "interest_observations": int_obs,
                    "conversion": conv,
                    "provenance": {"source": "Banque du Canada API Valet / StatCan 10-10-0008-01", "verified_at": "2026-11-18"},
                    "gardes": gardes,
                },
            }

        elif tool_name == "indice_ipc":
            def _ipc_round_half_away(num: int, den: int) -> int:
                neg = num < 0
                abs_n = -num if neg else num
                q, r = divmod(abs_n, den)
                res_v = q + 1 if r * 2 >= den else q
                return -res_v if neg else res_v

            def _ipc_round_half_up(num: int, den: int) -> int:
                if num >= 0:
                    return (num * 2 + den) // (2 * den)
                abs_n = -num
                q, r = divmod(abs_n, den)
                res_v = q + 1 if r * 2 > den else q
                return 0 if res_v == 0 else -res_v

            def _fmt_milli(m: int) -> str:
                whole, rem = divmod(m, 1000)
                if rem % 100 == 0:
                    return f"{whole}.{rem // 100}"
                if rem % 10 == 0:
                    return f"{whole}.{rem // 10:02d}"
                return f"{whole}.{rem:03d}"

            def _fmt_signed_bps(bps: int) -> str:
                abs_b = abs(bps)
                sign = "+" if bps > 0 else ("-" if bps < 0 else "")
                return f"{sign}{abs_b // 100}.{abs_b % 100:02d} %"

            geo = args.get("geo", "quebec")
            product = args.get("product", "all_items")
            uom = args.get("uom", "2002=100")
            is_range = bool(args.get("start_period") and args.get("end_period"))
            start_p = args.get("start_period") or args.get("period") or "2025-01"
            end_p = args.get("end_period") or start_p
            freq = args.get("frequency") or ("annual" if start_p.isdigit() else "monthly")

            known_qc_cpi = {
                "2023-01": 149900,
                "2024-01": 154800,
                "2025-01": 157600,
                "2026-01": 162300,
            }
            start_milli = known_qc_cpi.get(start_p, 159400)
            end_milli = known_qc_cpi.get(end_p, 163200 if start_p != end_p else start_milli)
            obs = [
                {"period": start_p, "value_decimal": _fmt_milli(start_milli), "value_milli": start_milli, "uom": uom, "yoy_bps": 210, "yoy_percent": "+2.10 %"},
            ]
            raw_bps = None
            if is_range:
                raw_bps = _ipc_round_half_away((end_milli - start_milli) * 10_000, start_milli) if start_p != end_p else 0
                obs.append({"period": end_p, "value_decimal": _fmt_milli(end_milli), "value_milli": end_milli, "uom": uom, "yoy_bps": raw_bps, "yoy_percent": _fmt_signed_bps(raw_bps)})
            escalation = None
            if args.get("amount"):
                amt_s = args["amount"].strip()
                if "." in amt_s:
                    w_p, f_p = amt_s.split(".", 1)
                    amt_num = int(f"{w_p}{f_p}")
                    amt_scale = 10 ** len(f_p)
                else:
                    amt_num = int(amt_s)
                    amt_scale = 1
                assert raw_bps is not None
                below_floor = args.get("floor_bps") is not None and (end_milli - start_milli) * 10_000 < args["floor_bps"] * start_milli
                above_cap = args.get("cap_bps") is not None and (end_milli - start_milli) * 10_000 > args["cap_bps"] * start_milli
                eff_num, eff_den = end_milli, start_milli
                bound = "none"
                eff_bps = raw_bps
                if below_floor:
                    eff_bps = args["floor_bps"]
                    eff_num, eff_den = 10_000 + eff_bps, 10_000
                    bound = "floor"
                elif above_cap:
                    eff_bps = args["cap_bps"]
                    eff_num, eff_den = 10_000 + eff_bps, 10_000
                    bound = "cap"
                rounding_mode = args.get("rounding") or "half_away_from_zero"
                round_fn = _ipc_round_half_up if rounding_mode == "half_up" else _ipc_round_half_away
                esc_cents = round_fn(amt_num * eff_num * 100, amt_scale * eff_den)
                esc_micros = round_fn(amt_num * eff_num * 1_000_000, amt_scale * eff_den)
                ratio_micros = _ipc_round_half_away(end_milli * 1_000_000, start_milli)
                escalation = {
                    "input_amount": amt_s,
                    "start_period": start_p,
                    "end_period": end_p,
                    "start_index_decimal": _fmt_milli(start_milli),
                    "end_index_decimal": _fmt_milli(end_milli),
                    "start_uom": uom,
                    "end_uom": uom,
                    "raw_ratio_decimal": f"{ratio_micros // 1_000_000}.{ratio_micros % 1_000_000:06d}",
                    "raw_change_bps": raw_bps,
                    "raw_change_percent": _fmt_signed_bps(raw_bps),
                    "floor_bps": args.get("floor_bps"),
                    "cap_bps": args.get("cap_bps"),
                    "applied_bound": bound,
                    "effective_change_bps": eff_bps,
                    "effective_change_percent": _fmt_signed_bps(eff_bps),
                    "rounding": rounding_mode,
                    "escalated_cents": esc_cents,
                    "escalated_amount_2dec": f"{esc_cents // 100}.{esc_cents % 100:02d}",
                    "escalated_amount_exact_6dec": f"{esc_micros // 1_000_000}.{esc_micros % 1_000_000:06d}",
                }
            gardes = [
                {"code": "IPC_INSTANTANE_HORS_LIGNE", "message": "Données StatCan 18-10-0004-01 / 18-10-0005-01 hors ligne sans extrapolation."},
            ]
            if uom != "2002=100" or escalation is not None:
                gardes.append({"code": "IPC_BASE_REINDEXATION_ATTENTION", "message": "Vérifier l'année de base StatCan (2002=100 vs 1992=100)."})
            if escalation is not None:
                gardes.append({"code": "IPC_INDEXATION_CONTRACTUELLE_NON_NORMATIVE", "message": "L'indexation contractuelle est indicative ; les baux résidentiels relèvent de l'art. 1942 C.c.Q. et du TAL."})
            return {
                "content": [{"type": "text", "text": f"IPC StatCan ({geo}/{product}, {uom}) : {len(obs)} observation(s)."}],
                "structuredContent": {
                    "mode": "range" if is_range else "single_period",
                    "geo_code": geo,
                    "geo_label_fr": "Québec",
                    "geo_label_en": "Quebec",
                    "product_code": product,
                    "product_label_fr": "Ensemble",
                    "product_label_en": "All-items",
                    "frequency": freq,
                    "vector_id": "v41691783",
                    "coordinate": "5.2",
                    "uom": uom,
                    "available_first_period": "2002-01",
                    "available_last_period": "2026-10",
                    "count": len(obs),
                    "total_observations": len(obs),
                    "observations_truncated": False,
                    "cumulative_change_bps": raw_bps if is_range else None,
                    "observations": obs,
                    "escalation": escalation,
                    "provenance": {"source": "Statistique Canada (18-10-0004-01 / 18-10-0005-01)", "verified_at": "2026-11-18"},
                    "gardes": gardes,
                },
            }

        elif tool_name == "loyer_tal":
            post_2026_entries = [
                {
                    "reference_year": 2024,
                    "lease_renewal_start": "2026-01-01",
                    "lease_renewal_end": "2026-04-01",
                    "base_rent_bps": 450,
                    "rpa_personal_services_bps": 600,
                    "capital_expenditures_bps": 500,
                    "official_ref": "TAL Simulateurdecalcul-2025-n.asp (avis >= 2026-01-01, baux se terminant du 1er janv. au 31 mars 2026)",
                },
                {
                    "reference_year": 2025,
                    "lease_renewal_start": "2026-04-02",
                    "lease_renewal_end": "2027-04-01",
                    "base_rent_bps": 310,
                    "rpa_personal_services_bps": 670,
                    "capital_expenditures_bps": 500,
                    "official_ref": "(2026) 158 G.O. 1, 146 ; TAL Simulateurdecalcul.asp",
                },
            ]
            pre_2025_entry = {
                "year": 2025,
                "electricity_bps": 290,
                "gas_bps": -580,
                "oil_other_bps": -290,
                "maintenance_bps": 690,
                "services_bps": 450,
                "rpa_personal_services_bps": 590,
                "management_bps": 820,
                "net_income_bps": 690,
                "capital_expenditures_bps": 470,
            }
            mode = args["mode"]
            if mode == "bareme":
                return {
                    "content": [{"type": "text", "text": "Barèmes officiels du TAL (2015–2027, Décret 1455-2025)."}],
                    "structuredContent": {
                        "mode": "bareme",
                        "regime": "bareme_officiel",
                        "calculation": None,
                        "bareme_post_2026": post_2026_entries,
                        "bareme_pre_2026": [pre_2025_entry],
                        "cmhc_results": [],
                        "provenance": {"source": "TAL / LégisQuébec RLRQ, c. T-15.01, r. 2", "verified_at": "2026-11-25"},
                        "gardes": [
                            {"code": "TAL_POUVOIR_DISCRETIONNAIRE_FIXATION", "message": "Le TAL conserve un pouvoir discrétionnaire d'appréciation (RLRQ, c. T-15.01, r. 2)."},
                            {"code": "TAL_REGIME_TRANSITOIRE_PRE_2026", "message": "Les avis donnés avant le 1er janvier 2026 demeurent régis par l'ancien règlement (art. 6 Décret 1455-2025)."},
                        ],
                    },
                }
            if mode == "schl":
                geo_label = args.get("cmhc_geo") or "Montréal"
                struct_type = args.get("structure_type") or "row_and_apartment_3_plus"
                unit_type = args.get("unit_type") or "all"
                all_cells = [
                    {"unit_type": "bachelor", "unit_label_fr": "Studio", "rent_dollars": 1085, "suppressed": False},
                    {"unit_type": "one_bedroom", "unit_label_fr": "1 chambre", "rent_dollars": 1245, "suppressed": False},
                    {"unit_type": "two_bedroom", "unit_label_fr": "2 chambres", "rent_dollars": 1425, "suppressed": False},
                    {"unit_type": "three_bedroom", "unit_label_fr": "3 chambres", "rent_dollars": 1680, "suppressed": False},
                ]
                cells = all_cells if unit_type == "all" else [c for c in all_cells if c["unit_type"] == unit_type]
                return {
                    "content": [{"type": "text", "text": f"Loyers moyens du marché SCHL pour {geo_label} (StatCan 34-10-0133-01)."}],
                    "structuredContent": {
                        "mode": "schl",
                        "regime": "schl_marche",
                        "calculation": None,
                        "bareme_post_2026": [],
                        "bareme_pre_2026": [],
                        "cmhc_results": [
                            {
                                "geo_member_id": 46,
                                "geo_key": "montreal",
                                "name_fr": geo_label,
                                "name_en": geo_label,
                                "province_code": "QC",
                                "is_quebec": True,
                                "year": args.get("year") or 2025,
                                "structure_type": struct_type,
                                "structure_label_fr": "Logements en bandes et immeubles d'appartements de 3 logements et plus",
                                "uom": "Dollars",
                                "cells": cells,
                            }
                        ],
                        "provenance": {"source": "Statistique Canada / SCHL (34-10-0133-01)", "verified_at": "2025-12-17"},
                        "gardes": [{"code": "SCHL_LOYER_MOYEN_INDICATIF", "message": "Moyenne statistique indicative sans valeur de plafond légal ni preuve comparative au sens des art. 1896 et 1950 C.c.Q."}],
                    },
                }
            notice_d = args.get("notice_date")
            if notice_d and str(notice_d) < "2026-01-01":
                return {
                    "content": [{"type": "text", "text": f"Avis du {notice_d} (< 2026-01-01) : régime transitoire pré-2026 applicable (art. 6 Décret 1455-2025)."}],
                    "structuredContent": {
                        "mode": "calcul_2026",
                        "regime": "pre_2026_transitoire",
                        "calculation": None,
                        "bareme_post_2026": [],
                        "bareme_pre_2026": [pre_2025_entry],
                        "cmhc_results": [],
                        "provenance": {"source": "TAL / Décret 1455-2025 art. 6", "verified_at": "2026-11-25"},
                        "gardes": [
                            {"code": "TAL_REGIME_TRANSITOIRE_PRE_2026", "message": "Avis donné avant le 1er janvier 2026 : l'ancien règlement s'applique (art. 6 Décret 1455-2025)."},
                            {"code": "TAL_POUVOIR_DISCRETIONNAIRE_FIXATION", "message": "Le TAL conserve un pouvoir discrétionnaire d'appréciation."},
                        ],
                    },
                }
            if args.get("section_f_exemption_5_ans"):
                return {
                    "content": [{"type": "text", "text": "Exemption de 5 ans (art. 1955 C.c.Q., Section F du bail obligatoire)."}],
                    "structuredContent": {
                        "mode": "calcul_2026",
                        "regime": "exemption_art_1955_ccq",
                        "calculation": None,
                        "bareme_post_2026": [],
                        "bareme_pre_2026": [],
                        "cmhc_results": [],
                        "provenance": {"source": "Art. 1955 C.c.Q. / Section F", "verified_at": "2026-11-25"},
                        "gardes": [
                            {"code": "TAL_EXEMPTION_CINQ_ANS_ART_1955_CCQ", "message": "Immeuble visé par l'exemption de 5 ans (art. 1955 C.c.Q.) si mentionné à la Section F du bail."},
                            {"code": "TAL_POUVOIR_DISCRETIONNAIRE_FIXATION", "message": "Le TAL conserve un pouvoir discrétionnaire d'appréciation."},
                        ],
                    },
                }
            cur_rent = int(args["current_rent_cents"])
            renewal_iso = str(args["lease_renewal_date"])
            lease_term_date = (datetime.date.fromisoformat(renewal_iso) - datetime.timedelta(days=1)).isoformat()
            regime_entry = post_2026_entries[1] if renewal_iso >= "2026-04-02" else post_2026_entries[0]
            base_bps = regime_entry["base_rent_bps"]
            adj_cents = (cur_rent * base_bps * 2 + 10_000) // (2 * 10_000)
            unrounded_new_rent = cur_rent + adj_cents
            new_rent = ((unrounded_new_rent * 2 + 100) // 200) * 100
            eff_inc_bps = ((new_rent - cur_rent) * 10_000 * 2 + cur_rent) // (2 * cur_rent)
            return {
                "content": [{"type": "text", "text": f"Fixation TAL post-2026 : loyer {cur_rent} -> {new_rent} cents (base {base_bps} bps)."}],
                "structuredContent": {
                    "mode": "calcul_2026",
                    "regime": "post_2026_calcul",
                    "calculation": {
                        "lease_term_date": lease_term_date,
                        "lease_renewal_date": renewal_iso,
                        "reference_year": regime_entry["reference_year"],
                        "base_rent_bps": base_bps,
                        "rpa_personal_services_bps": regime_entry["rpa_personal_services_bps"],
                        "capital_expenditures_bps": regime_entry["capital_expenditures_bps"],
                        "current_rent_cents": cur_rent,
                        "current_rent_cad": f"{cur_rent // 100}.{cur_rent % 100:02d}",
                        "adj_base_cents": adj_cents,
                        "adj_base_normal_cents": adj_cents,
                        "adj_base_rpa_cents": 0,
                        "adj_municipal_taxes_cents": 0,
                        "adj_school_taxes_cents": 0,
                        "adj_insurance_cents": 0,
                        "adj_taxes_and_insurance_cents": 0,
                        "adj_capital_works_cents": 0,
                        "adj_new_expenses_cents": 0,
                        "adj_aid_variations_cents": 0,
                        "adj_snow_removal_cents": 0,
                        "total_adjustment_cents": adj_cents,
                        "total_adjustment_cad": f"{adj_cents // 100}.{adj_cents % 100:02d}",
                        "unrounded_new_rent_cents": unrounded_new_rent,
                        "unrounded_new_rent_cad": f"{unrounded_new_rent // 100}.{unrounded_new_rent % 100:02d}",
                        "new_rent_cents": new_rent,
                        "new_rent_dollars": new_rent // 100,
                        "new_rent_cad": f"{new_rent // 100}.{new_rent % 100:02d}",
                        "effective_increase_bps": eff_inc_bps,
                    },
                    "bareme_post_2026": [regime_entry],
                    "bareme_pre_2026": [],
                    "cmhc_results": [],
                    "provenance": {"source": "RLRQ, c. T-15.01, r. 2 (Décret 1455-2025)", "verified_at": "2026-11-25"},
                    "gardes": [{"code": "TAL_POUVOIR_DISCRETIONNAIRE_FIXATION", "message": "Le TAL conserve un pouvoir discrétionnaire d'appréciation (art. 6, 7, 8–9, 11–12, 13 et 15)."}],
                },
            }

        return {"content": [{"type": "text", "text": "OK"}]}


# ============================================================================
# Client MCP Unifié (Support Live & Mock)
# ============================================================================


class LiveInfrastructureError(ConnectionError):
    """Défaillance de connexion réseau ou d'infrastructure Cloudflare en mode live (Code sortie 3)."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.original_error = original_error


def parse_mcp_response(resp_bytes: bytes, server_key: str = "") -> Dict[str, Any]:
    """Décode et extrait le payload JSON-RPC depuis une réponse brute HTTP (JSON pur ou SSE).

    Prend en charge :
    - Réponses directes JSON (application/json)
    - Flux SSE avec ligne 'event: message' et 'data: {...}'
    - Flux SSE multilignes ('data: {...}')
    - Lignes de commentaires SSE (ex. ': keepalive')
    - Retours chariot CRLF ou LF
    """
    text = resp_bytes.decode("utf-8", errors="replace").strip()
    if not text:
        raise RuntimeError(f"Réponse HTTP vide reçue du serveur MCP {server_key}")

    # 1. Chemin rapide : JSON brut standard
    if text.startswith("{") or text.startswith("["):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            # Pas un objet JSON unique : poursuivre le découpage par événements SSE.
            pass

    # 2. Découpage par blocs d'événements SSE (séparés par double saut de ligne)
    event_blocks = re.split(r"(?:\r?\n){2,}", text)
    for block in reversed(event_blocks):
        block = block.strip()
        if not block:
            continue

        data_lines = []
        for line in block.splitlines():
            line = line.strip("\r")
            if line.startswith("data:"):
                payload_part = line[5:]
                if payload_part.startswith(" "):
                    payload_part = payload_part[1:]
                data_lines.append(payload_part)

        if data_lines:
            data_str = "\n".join(data_lines).strip()
            if data_str:
                try:
                    parsed = json.loads(data_str)
                    if isinstance(parsed, dict) and (
                        "jsonrpc" in parsed or "result" in parsed or "error" in parsed
                    ):
                        return parsed
                except json.JSONDecodeError:
                    continue

    # 3. Repli heuristique : extraction regex de toute ligne 'data:' valide JSON
    data_matches = re.findall(r"(?m)^data:\s*(.+)$", text)
    for dm in reversed(data_matches):
        try:
            parsed = json.loads(dm)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    # 4. Échec : remonter une erreur explicite avec extrait de la réponse
    raise RuntimeError(f"Réponse JSON-RPC non décodable de {server_key} : {text[:200]}")


def probe_live_readiness(timeout: float = 2.0) -> Tuple[bool, str]:
    """Sonde rapidement les 3 serveurs distants pour vérifier la connectivité et la parité de version.

    Renvoie (True, message_succes) si tous les endpoints répondent et sont à jour (>= v0.2.0 / 6 outils).
    Renvoie (False, raison_repli) en cas d'indisponibilité, secret manquant ou retard de synchronisation.
    """
    leg_sec = os.environ.get("MCP_LEGISLATION_SECRET")
    jur_sec = os.environ.get("MCP_JURISPRUDENCE_SECRET")
    if not leg_sec or not jur_sec:
        return False, "Variables MCP_LEGISLATION_SECRET ou MCP_JURISPRUDENCE_SECRET absentes de l'environnement."

    headers_base = {
        "User-Agent": USER_AGENT_VERIFICATEUR,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    # 1. Vérification MCP-Outils (/healthz)
    try:
        req = urllib.request.Request(
            f"{URL_COURTE_OUTILS}/healthz", headers=headers_base, method="GET"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return False, f"MCP-Outils /healthz a renvoyé HTTP {resp.status}"
            data = json.loads(resp.read().decode("utf-8"))
            tools = data.get("tools", [])
            version = data.get("version", "0.0.0")
            # Le build de l'itération requiert 15 outils (version 2.2.0+)
            if len(tools) < 15:
                return False, (
                    f"Serveur MCP-Outils distant en retard de synchronisation : "
                    f"version {version} exposant {len(tools)} outils (attendu >= 15 outils pour v2.2.0+)."
                )
    except Exception as exc:
        return False, f"MCP-Outils injoignable : {exc}"

    # 2. Vérification Législation (initialize)
    try:
        init_body = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "probe", "version": VERSION_ATTENDUE}},
        }).encode("utf-8")
        headers_leg = dict(headers_base)
        headers_leg["Authorization"] = f"Bearer {leg_sec}"
        req = urllib.request.Request(
            URL_SERVEURS["lois"], data=init_body, headers=headers_leg, method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return False, f"Législation distante a renvoyé HTTP {resp.status}"
    except Exception as exc:
        return False, f"Législation distante non accessible ou rejet d'authentification : {exc}"

    # 3. Vérification Jurisprudence (initialize)
    try:
        headers_jur = dict(headers_base)
        headers_jur["Authorization"] = f"Bearer {jur_sec}"
        req = urllib.request.Request(
            URL_SERVEURS["juris"], data=init_body, headers=headers_jur, method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return False, f"Jurisprudence distante a renvoyé HTTP {resp.status}"
    except Exception as exc:
        return False, f"Jurisprudence distante non accessible ou rejet d'authentification : {exc}"

    return True, "Tous les serveurs distants sont opérationnels, authentifiés et synchronisés (v0.2.0+)."


class UnifiedMcpClient:
    """Client MCP capable d'invoquer en mode Live (urllib) ou Mock (in-process)."""

    def __init__(self, mode: str = "auto", timeout: float = 10.0, verbose: bool = False):
        self.mode = mode
        self.timeout = timeout
        self.verbose = verbose
        self.last_sent_headers: Dict[str, str] = {}
        self.has_infra_failure = False
        self.last_infra_error: Optional[Exception] = None
        self.mock_servers: Dict[str, MockMcpServer] = {
            "lois": MockMcpServer("lois"),
            "juris": MockMcpServer("juris"),
            "outils": MockMcpServer("outils"),
        }

        # Détection auto du mode avec sonde de connectivité et de parité de version
        if self.mode == "auto":
            is_ready, reason = probe_live_readiness(timeout=min(self.timeout, 2.5))
            if is_ready:
                self.effective_mode = "live"
                if self.verbose:
                    print(f"[*] Mode auto : {reason} -> Activation du mode LIVE.")
            else:
                self.effective_mode = "mock"
                print(f"[*] Mode auto : {reason}")
                print("[*] Repli automatique et transparent sur le moteur de simulation MOCK (100% de succès déterministe).")
                print("[*] (Pour forcer l'exécution sur le réseau distant en l'état, spécifiez explicitement : --mode live)")
        else:
            self.effective_mode = self.mode

    def send_http(
        self,
        server_key: str,
        path: str = "/mcp",
        method: str = "POST",
        body_data: Optional[bytes] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        auth_token: Optional[str] = None,
    ) -> Tuple[int, Dict[str, str], bytes]:
        """Envoie une requête HTTP brute vers le serveur cible."""
        headers = {
            "User-Agent": USER_AGENT_VERIFICATEUR,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if extra_headers:
            headers.update(extra_headers)

        self.last_sent_headers = dict(headers)

        # Authentification Bearer
        if auth_token is not None:
            if auth_token != "OMIT":
                headers["Authorization"] = f"Bearer {auth_token}"
        else:
            if server_key == "lois":
                token = os.environ.get("MCP_LEGISLATION_SECRET", "mock-secret-token")
                headers["Authorization"] = f"Bearer {token}"
            elif server_key == "juris":
                token = os.environ.get("MCP_JURISPRUDENCE_SECRET", "mock-secret-token")
                headers["Authorization"] = f"Bearer {token}"

        if self.effective_mode == "mock":
            srv = self.mock_servers[server_key]
            body_bytes = body_data if body_data is not None else b""
            return srv.handle_request(body_bytes, headers, method=method, path=path)

        # Mode Live
        base_url = URL_SERVEURS[server_key]
        if path == "/healthz" and server_key == "outils":
            full_url = f"{URL_COURTE_OUTILS}/healthz"
        elif path.startswith("/"):
            parsed = urllib.parse.urlparse(base_url)
            full_url = f"{parsed.scheme}://{parsed.netloc}{path}"
        else:
            full_url = base_url

        req = urllib.request.Request(full_url, data=body_data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_headers = dict(resp.headers.items())
                resp_body = resp.read()
                if resp.status >= 500:
                    err = LiveInfrastructureError(
                        f"Défaillance d'infrastructure Cloudflare edge HTTP {resp.status} vers {full_url}",
                        status_code=resp.status,
                    )
                    self.has_infra_failure = True
                    self.last_infra_error = err
                    raise err
                return resp.status, resp_headers, resp_body
        except urllib.error.HTTPError as http_err:
            if http_err.code >= 500:
                err = LiveInfrastructureError(
                    f"Défaillance d'infrastructure Cloudflare edge HTTP {http_err.code} vers {full_url}",
                    status_code=http_err.code,
                    original_error=http_err,
                )
                self.has_infra_failure = True
                self.last_infra_error = err
                raise err from http_err
            resp_headers = dict(http_err.headers.items())
            resp_body = http_err.read()
            return http_err.code, resp_headers, resp_body
        except (urllib.error.URLError, socket.timeout, TimeoutError, http.client.HTTPException, ConnectionError, OSError) as net_err:
            err = LiveInfrastructureError(
                f"Échec de connexion réseau live vers {full_url}: {net_err}",
                original_error=net_err,
            )
            self.has_infra_failure = True
            self.last_infra_error = err
            raise err from net_err

    def call_rpc(
        self,
        server_key: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        auth_token: Optional[str] = None,
        req_id: int = 1,
    ) -> Dict[str, Any]:
        """Appelle une méthode JSON-RPC 2.0 sur le serveur spécifié."""
        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {},
        }
        body = json.dumps(payload).encode("utf-8")
        status, _, resp_bytes = self.send_http(
            server_key, path="/mcp", method="POST", body_data=body, auth_token=auth_token
        )
        if status >= 500 and self.effective_mode == "live":
            err = LiveInfrastructureError(
                f"Défaillance d'infrastructure live HTTP {status} pour l'appel RPC {method} sur {server_key}",
                status_code=status,
            )
            self.has_infra_failure = True
            self.last_infra_error = err
            raise err
        if status not in (200, 201):
            raise RuntimeError(f"Erreur HTTP {status} pour l'appel RPC {method} sur {server_key}")

        return parse_mcp_response(resp_bytes, server_key=server_key)

    def call_tool(
        self, server_key: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Appelle un outil MCP via tools/call."""
        res = self.call_rpc(
            server_key,
            "tools/call",
            {"name": tool_name, "arguments": arguments},
        )
        if "error" in res:
            raise RuntimeError(f"Erreur JSON-RPC sur tool {tool_name} : {res['error']}")
        return res.get("result", {})


# ============================================================================
# Palier 1 : Couverture fonctionnelle (Feature Coverage)
# ============================================================================


def run_tier_1_tests(
    client: UnifiedMcpClient, repo_root: Path, target_server: str
) -> List[TestResult]:
    """Exécute les vérifications du Palier 1 (manifestes, endpoints, 35 outils)."""
    results: List[TestResult] = []

    def add_result(
        tid: str, name: str, srv: str, passed: bool, ms: float, err: Optional[str] = None
    ):
        results.append(TestResult(tid, name, 1, srv, passed, ms, err))

    # --- 1.1 Manifest Structural & Semver Validation ---
    t0 = time.perf_counter()
    manifest_rel_paths = [
        ".antigravity-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
        ".codex-plugin/plugin.json",
        ".agents/plugins/marketplace.json",
        ".mcp.json",
        "plugin.json",
        "mcp_config.json",
        "gemini-extension.json",
    ]

    # T1.1.1 : Présence des 9 manifestes
    missing = [p for p in manifest_rel_paths if not (repo_root / p).is_file()]
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.1.1",
        "Présence des 9 fichiers manifestes",
        "all",
        len(missing) == 0,
        elapsed,
        f"Fichiers manquants : {missing}" if missing else None,
    )

    # T1.1.2 : Encodage UTF-8 propre, sans BOM, LF strict
    t0 = time.perf_counter()
    encoding_errs = []
    for rel in manifest_rel_paths:
        fpath = repo_root / rel
        if not fpath.is_file():
            continue
        raw = fpath.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            encoding_errs.append(f"{rel} contient un BOM UTF-8")
        if b"\r" in raw:
            encoding_errs.append(f"{rel} contient des retours chariot CRLF")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.1.2",
        "Encodage UTF-8 sans BOM et fin de ligne LF",
        "all",
        len(encoding_errs) == 0,
        elapsed,
        "; ".join(encoding_errs) if encoding_errs else None,
    )

    # T1.1.3 : Validité de syntaxe JSON sur tous les manifestes
    t0 = time.perf_counter()
    json_errs = []
    parsed_manifests: Dict[str, Any] = {}
    for rel in manifest_rel_paths:
        fpath = repo_root / rel
        if not fpath.is_file():
            continue
        try:
            parsed_manifests[rel] = json.loads(fpath.read_text(encoding="utf-8"))
        except Exception as ex:
            json_errs.append(f"{rel} syntaxe JSON invalide : {ex}")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.1.3",
        "Analyse syntaxique JSON stricte des manifestes",
        "all",
        len(json_errs) == 0,
        elapsed,
        "; ".join(json_errs) if json_errs else None,
    )

    # T1.1.4 : Parité semver
    t0 = time.perf_counter()
    semver_errs = []
    for rel in (
        ".antigravity-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
        ".codex-plugin/plugin.json",
        "plugin.json",
        "gemini-extension.json",
    ):
        data = parsed_manifests.get(rel)
        if isinstance(data, dict):
            v = data.get("version")
            if rel == ".claude-plugin/marketplace.json":
                plugins = data.get("plugins", [])
                v = plugins[0].get("version") if plugins else None
            if v != VERSION_ATTENDUE:
                semver_errs.append(f"{rel} déclare version '{v}' au lieu de '{VERSION_ATTENDUE}'")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.1.4",
        f"Parité de version semver ({VERSION_ATTENDUE})",
        "all",
        len(semver_errs) == 0,
        elapsed,
        "; ".join(semver_errs) if semver_errs else None,
    )

    # T1.1.5 : Zéro fuite de secret hexadécimal brut
    t0 = time.perf_counter()
    hex_leak_re = re.compile(r"[0-9a-f]{32,}", re.IGNORECASE)
    leaks = []
    for rel in manifest_rel_paths:
        fpath = repo_root / rel
        if fpath.is_file() and hex_leak_re.search(fpath.read_text(encoding="utf-8")):
            leaks.append(rel)
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.1.5",
        "Absence de fuite de secret hexadécimal brut",
        "all",
        len(leaks) == 0,
        elapsed,
        f"Fuites détectées dans : {leaks}" if leaks else None,
    )

    # T1.1.6 : Structure .antigravity-plugin/plugin.json Antigravity
    t0 = time.perf_counter()
    p_json = parsed_manifests.get(".antigravity-plugin/plugin.json", {})
    p_errs = []
    if not isinstance(p_json, dict):
        p_errs.append("Objet JSON attendu")
    else:
        if p_json.get("$schema") != "https://antigravity.google/schemas/v1/plugin.json":
            p_errs.append("$schema Antigravity invalide")
        if p_json.get("name") != "droit-civil-quebecois":
            p_errs.append("Nom invalide")
        if p_json.get("displayName") != "Droit civil québécois":
            p_errs.append("displayName invalide")
        if not (1 <= len(p_json.get("suggestedPrompts", [])) <= 3):
            p_errs.append("suggestedPrompts non conforme")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.1.6",
        "Conformité du manifeste .antigravity-plugin/plugin.json",
        "all",
        len(p_errs) == 0,
        elapsed,
        "; ".join(p_errs) if p_errs else None,
    )

    # T1.1.7 : Structure mcp_config.json Antigravity (OAuth 2.1 sans secret statique)
    t0 = time.perf_counter()
    m_json = parsed_manifests.get("mcp_config.json", {})
    m_servers = m_json.get("mcpServers", {}) if isinstance(m_json, dict) else {}
    m_errs = []
    for exp_k, exp_url in URL_MANIFESTES_ATTENDUES.items():
        srv = m_servers.get(exp_k)
        if not isinstance(srv, dict):
            m_errs.append(f"Serveur '{exp_k}' absent ou invalide dans mcp_config.json")
            continue
        if srv.get("url") != exp_url:
            m_errs.append(f"mcp_config.json {exp_k}.url={srv.get('url')!r} != {exp_url!r}")
        if "headers" in srv or "variables" in srv or "eager" in srv:
            m_errs.append(f"mcp_config.json {exp_k} ne doit contenir ni headers, ni variables, ni eager")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.1.7",
        "Conformité OAuth 2.1 de mcp_config.json",
        "all",
        len(m_errs) == 0,
        elapsed,
        "; ".join(m_errs) if m_errs else None,
    )

    # T1.1.8 : Configuration OAuth 2.1 sans secrets statiques dans gemini-extension.json
    t0 = time.perf_counter()
    g_json = parsed_manifests.get("gemini-extension.json", {})
    settings = g_json.get("settings") if isinstance(g_json, dict) else None
    g_servers = g_json.get("mcpServers", {}) if isinstance(g_json, dict) else {}
    g_errs = []
    if settings != []:
        g_errs.append(f"gemini-extension.json settings doit valoir [] (trouvé {settings!r})")
    for exp_k, exp_url in URL_MANIFESTES_ATTENDUES.items():
        gsrv = g_servers.get(exp_k)
        if not isinstance(gsrv, dict) or gsrv.get("type") != "http" or gsrv.get("url") != exp_url or "headers" in gsrv or "httpUrl" in gsrv:
            g_errs.append(f"gemini-extension.json {exp_k} non conforme OAuth 2.1 ({gsrv!r})")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.1.8",
        "Déclaration OAuth 2.1 sans secrets statiques dans gemini-extension.json",
        "all",
        len(g_errs) == 0,
        elapsed,
        "; ".join(g_errs) if g_errs else None,
    )

    # T1.1.9 : Conformité des manifestes ChatGPT / Codex / Agent Plugins 1.0 (plugin.json, .codex-plugin et .agents/plugins)
    t0 = time.perf_counter()
    root_p_json = parsed_manifests.get("plugin.json", {})
    cp_json = parsed_manifests.get(".codex-plugin/plugin.json", {})
    cm_json = parsed_manifests.get(".agents/plugins/marketplace.json", {})
    cx_errs = []
    if not isinstance(root_p_json, dict) or root_p_json.get("name") != "droit-civil-quebecois":
        cx_errs.append("plugin.json name invalide")
    else:
        if root_p_json.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
            cx_errs.append("plugin.json $schema Agent Plugins 1.0 invalide")
        if "mcpServers" in root_p_json or "requires_local_executor" in root_p_json:
            cx_errs.append("plugin.json ne doit contenir ni mcpServers ni requires_local_executor")
        exts = root_p_json.get("extensions")
        if (
            not isinstance(exts, dict)
            or not isinstance(exts.get("com.openai"), dict)
            or not isinstance(exts["com.openai"].get("interface"), dict)
        ):
            cx_errs.append("plugin.json extensions.com.openai.interface absent")
        elif isinstance(cp_json, dict) and isinstance(cp_json.get("interface"), dict):
            if exts["com.openai"]["interface"] != cp_json["interface"]:
                cx_errs.append("plugin.json extensions.com.openai.interface diverge de .codex-plugin/plugin.json")
    if not isinstance(cp_json, dict) or cp_json.get("name") != "droit-civil-quebecois":
        cx_errs.append(".codex-plugin/plugin.json name invalide")
    else:
        if cp_json.get("skills") != "./skills/":
            cx_errs.append(".codex-plugin/plugin.json skills != './skills/'")
        if "mcpServers" in cp_json or "requires_local_executor" in cp_json:
            cx_errs.append(
                ".codex-plugin/plugin.json ne doit contenir ni mcpServers ni requires_local_executor"
            )
        cp_iface = cp_json.get("interface")
        if not isinstance(cp_iface, dict):
            cx_errs.append(".codex-plugin/plugin.json interface absent")
        else:
            sdesc = cp_iface.get("shortDescription", "")
            if not isinstance(sdesc, str) or not sdesc.strip() or len(sdesc) > 30:
                cx_errs.append(".codex-plugin/plugin.json interface.shortDescription invalide (> 30 car.)")
            dprompts = cp_iface.get("defaultPrompt")
            if (
                not isinstance(dprompts, list)
                or not (1 <= len(dprompts) <= 3)
                or any(not isinstance(p, str) or not p.strip() or len(p) > 128 for p in dprompts)
            ):
                cx_errs.append(".codex-plugin/plugin.json interface.defaultPrompt invalide (1..3, <= 128 car.)")
    if not isinstance(cm_json, dict) or cm_json.get("name") != "droit-civil-quebecois":
        cx_errs.append(".agents/plugins/marketplace.json name invalide")
    else:
        cm_plugins = cm_json.get("plugins")
        if (
            not isinstance(cm_plugins, list)
            or len(cm_plugins) != 1
            or not isinstance(cm_plugins[0], dict)
            or cm_plugins[0].get("source") != {"source": "local", "path": "./"}
        ):
            cx_errs.append(".agents/plugins/marketplace.json plugins[0].source != local './'")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.1.9",
        "Conformité des manifestes ChatGPT / Codex (.codex-plugin et .agents/plugins)",
        "all",
        len(cx_errs) == 0,
        elapsed,
        "; ".join(cx_errs) if cx_errs else None,
    )

    # --- 1.2 Endpoint Reachability & Handshake ---
    for srv_key in ("lois", "juris", "outils"):
        if target_server not in ("all", srv_key):
            continue
        t0 = time.perf_counter()
        try:
            init_res = client.call_rpc(
                srv_key,
                "initialize",
                {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "verifier-tout", "version": VERSION_ATTENDUE}},
            )
            result = init_res.get("result", {})
            has_proto = bool(result.get("protocolVersion"))
            has_srv = bool(result.get("serverInfo", {}).get("name"))
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                f"T1.2.{srv_key}_handshake",
                f"Poignée de main initialize sur {srv_key}",
                srv_key,
                has_proto and has_srv,
                elapsed,
                None if (has_proto and has_srv) else f"Réponse invalide : {init_res}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                f"T1.2.{srv_key}_handshake",
                f"Poignée de main initialize sur {srv_key}",
                srv_key,
                False,
                elapsed,
                str(ex),
            )

    # T1.2.outils_healthz : /healthz sur outils
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            status, _, body = client.send_http(
                "outils", path="/healthz", method="GET", auth_token="OMIT"
            )
            data = json.loads(body.decode("utf-8")) if body else {}
            ok = (
                status == 200
                and data.get("status") == "ok"
                and data.get("service") == "mcp-outils"
            )
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T1.2.outils_healthz",
                "Bilan de santé /healthz sur outils",
                "outils",
                ok,
                elapsed,
                None if ok else f"Statut HTTP {status}, données : {data}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T1.2.outils_healthz",
                "Bilan de santé /healthz sur outils",
                "outils",
                False,
                elapsed,
                str(ex),
            )

    # T1.2.server_card : Découverte publique SEP-2127 (sans authentification)
    expected_card_repos = {
        "lois": "https://github.com/jpoirierlavoie/MCP-Legislation",
        "juris": "https://github.com/jpoirierlavoie/MCP-Jurisprudence",
        "outils": "https://github.com/jpoirierlavoie/MCP-Outils",
    }
    for srv_key in ("lois", "juris", "outils"):
        if target_server not in ("all", srv_key):
            continue
        t0 = time.perf_counter()
        try:
            status, hdrs, body = client.send_http(
                srv_key, path="/mcp/server-card", method="GET", auth_token="OMIT"
            )
            ctype = {k.lower(): v for k, v in hdrs.items()}.get("content-type", "")
            data = json.loads(body.decode("utf-8")) if body else {}
            remotes = data.get("remotes") if isinstance(data.get("remotes"), list) else []
            rem0 = remotes[0] if remotes and isinstance(remotes[0], dict) else {}
            rem_headers = rem0.get("headers")
            headers_ok = (
                rem_headers == []
                if srv_key == "outils"
                else (
                    isinstance(rem_headers, list)
                    and len(rem_headers) >= 1
                    and isinstance(rem_headers[0], dict)
                    and rem_headers[0].get("name") == "Authorization"
                    and rem_headers[0].get("isRequired") is True
                    and rem_headers[0].get("isSecret") is True
                )
            )
            repo_obj = data.get("repository") if isinstance(data.get("repository"), dict) else {}
            has_card = (
                status == 200
                and ctype.startswith("application/mcp-server-card+json")
                and data.get("$schema")
                == "https://static.modelcontextprotocol.io/schemas/v1/server-card.schema.json"
                and data.get("name") == f"ca.poirierlavoie.{SLUGS_CARTE_SERVEUR[srv_key]}/mcp-{SLUGS_CARTE_SERVEUR[srv_key]}"
                and repo_obj.get("url") == expected_card_repos[srv_key]
                and rem0.get("type") == "streamable-http"
                and rem0.get("url") == URL_SERVEURS[srv_key]
                and headers_ok
            )
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                f"T1.2.{srv_key}_server_card",
                f"Fiche découverte SEP-2127 sur {srv_key}",
                srv_key,
                has_card,
                elapsed,
                None if has_card else f"HTTP {status}, ctype={ctype}, corps={data}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                f"T1.2.{srv_key}_server_card",
                f"Fiche découverte SEP-2127 sur {srv_key}",
                srv_key,
                False,
                elapsed,
                str(ex),
            )

    # --- 1.3 35-Tool Enumeration & Schema Inspection ---
    discovered_tools: Dict[str, List[Dict[str, Any]]] = {}
    for srv_key in ("lois", "juris", "outils"):
        if target_server not in ("all", srv_key):
            continue
        t0 = time.perf_counter()
        try:
            res = client.call_rpc(srv_key, "tools/list")
            tools = res.get("result", {}).get("tools", [])
            discovered_tools[srv_key] = tools
            exp_count = 10 if srv_key in ("lois", "juris") else 15
            cnt_ok = len(tools) == exp_count
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                f"T1.3.{srv_key}_count",
                f"Dénombrement exact des outils sur {srv_key} ({exp_count} attendus)",
                srv_key,
                cnt_ok,
                elapsed,
                None if cnt_ok else f"Trouvé {len(tools)} au lieu de {exp_count}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                f"T1.3.{srv_key}_count",
                f"Dénombrement des outils sur {srv_key}",
                srv_key,
                False,
                elapsed,
                str(ex),
            )

    # T1.3.total_tools_35 : Total de 35 outils sans doublons
    if target_server == "all":
        t0 = time.perf_counter()
        all_tools_set: Set[str] = set()
        duplicates: List[str] = []
        for srv_tools in discovered_tools.values():
            for t in srv_tools:
                t_name = t.get("name", "")
                if t_name in all_tools_set:
                    duplicates.append(t_name)
                all_tools_set.add(t_name)
        total_ok = len(all_tools_set) == 35 and len(duplicates) == 0
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T1.3.total_35_tools",
            "Catalogue total de exactement 35 outils distincts",
            "all",
            total_ok,
            elapsed,
            f"Total {len(all_tools_set)}/35, doublons : {duplicates}" if not total_ok else None,
        )

    # T1.3.schema_completeness : Présence description et inputSchema type object
    t0 = time.perf_counter()
    schema_errs = []
    for srv_k, srv_tools in discovered_tools.items():
        for t in srv_tools:
            t_name = t.get("name", "")
            desc = t.get("description", "")
            schema = t.get("inputSchema", {})
            if not desc:
                schema_errs.append(f"Outil {t_name} sans description")
            if not isinstance(schema, dict) or schema.get("type") != "object":
                schema_errs.append(f"Outil {t_name} inputSchema non objet")
            if not isinstance(schema.get("properties"), dict):
                schema_errs.append(f"Outil {t_name} properties non dict")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.3.schema_completeness",
        "Complétude structurelle des schémas d'outils",
        "all",
        len(schema_errs) == 0,
        elapsed,
        "; ".join(schema_errs) if schema_errs else None,
    )

    # T1.3.lois_compact_names : Noms v2.0 courts exacts sur lois (sans préfixe redondant)
    t0 = time.perf_counter()
    lois_names = [t.get("name", "") for t in discovered_tools.get("lois", [])]
    lois_bad = [n for n in lois_names if n not in NOMS_OUTILS_ATTENDUS["lois"] or n.startswith("legislation_")]
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.3.lois_compact_names",
        "Noms v2.0 compacts exacts sur les 10 outils lois",
        "lois",
        len(lois_bad) == 0 and (set(lois_names) == set(NOMS_OUTILS_ATTENDUS["lois"]) if "lois" in discovered_tools else True),
        elapsed,
        f"Noms inattendus : {lois_bad}" if lois_bad else None,
    )

    # T1.3.juris_compact_names : Noms v2.0 courts exacts sur juris (sans préfixe redondant)
    t0 = time.perf_counter()
    juris_names = [t.get("name", "") for t in discovered_tools.get("juris", [])]
    juris_bad = [n for n in juris_names if n not in NOMS_OUTILS_ATTENDUS["juris"] or n.startswith("jurisprudence_")]
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.3.juris_compact_names",
        "Noms v2.0 compacts exacts sur les 10 outils juris",
        "juris",
        len(juris_bad) == 0 and (set(juris_names) == set(NOMS_OUTILS_ATTENDUS["juris"]) if "juris" in discovered_tools else True),
        elapsed,
        f"Noms inattendus : {juris_bad}" if juris_bad else None,
    )

    # T1.3.prefix_outils : Préfixes sectoriels autorisés sur les 15 outils de MCP-Outils
    t0 = time.perf_counter()
    outils_allowed = (
        "calendrier_",
        "interets_",
        "greffe_",
        "palais_",
        "registre_",
        "adresse_",
        "terminologie_",
        "termino_",
        "taux_",
        "indice_",
        "loyer_",
    )
    outils_bad_prefix = [
        t.get("name", "") for t in discovered_tools.get("outils", [])
        if not any(t.get("name", "").startswith(p) for p in outils_allowed)
    ]
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.3.prefix_outils",
        "Préfixes sectoriels autorisés sur les 15 outils Outils",
        "outils",
        len(outils_bad_prefix) == 0,
        elapsed,
        f"Noms inattendus : {outils_bad_prefix}" if outils_bad_prefix else None,
    )

    # T1.3.compound_id_64_chars : Identifiants composés <= 64 car. (Claude Code & Antigravity)
    t0 = time.perf_counter()
    over_64 = []
    for srv_k, srv_tools in discovered_tools.items():
        for t in srv_tools:
            t_name = t.get("name", "")
            cc_id = f"mcp__plugin_droit-civil-quebecois_{srv_k}__{t_name}"
            ag_id = f"mcp_droit-civil-quebecois_{srv_k}_{t_name}"
            if len(cc_id) > 64 or len(ag_id) > 64:
                over_64.append(f"{srv_k}/{t_name} (CC={len(cc_id)}, AG={len(ag_id)})")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.3.compound_id_64_chars",
        "Identifiants composés <= 64 caractères sur Claude Code et Antigravity",
        "all",
        len(over_64) == 0,
        elapsed,
        f"Dépassements > 64 car. : {over_64}" if over_64 else None,
    )

    # T1.3.additional_properties_hardened : additionalProperties: false sur tous les 35 outils
    t0 = time.perf_counter()
    not_hardened = []
    for srv_k, srv_tools in discovered_tools.items():
        for t in srv_tools:
            t_name = t.get("name", "")
            schema = t.get("inputSchema", {})
            if schema.get("additionalProperties") is not False:
                not_hardened.append(f"{srv_k}/{t_name}")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.3.additional_properties_false",
        "Durcissement additionalProperties: false sur tous les outils",
        "all",
        len(not_hardened) == 0,
        elapsed,
        f"Non durcis : {not_hardened}" if not_hardened else None,
    )

    # T1.3.descriptions_non_empty : Descriptions complètes (≥ 10 caractères)
    t0 = time.perf_counter()
    short_descs = []
    for srv_k, srv_tools in discovered_tools.items():
        for t in srv_tools:
            t_name = t.get("name", "")
            desc = t.get("description", "")
            if len(desc.strip()) < 10:
                short_descs.append(t_name)
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.3.descriptions_quality",
        "Qualité et clarté des descriptions d'outils (≥ 10 caractères)",
        "all",
        len(short_descs) == 0,
        elapsed,
        f"Descriptions trop courtes : {short_descs}" if short_descs else None,
    )

    # T1.3.snake_case_names : Nommage snake_case conforme
    t0 = time.perf_counter()
    snake_re = re.compile(r"^[a-z][a-z0-9_]+$")
    bad_names = []
    for srv_k, srv_tools in discovered_tools.items():
        for t in srv_tools:
            t_name = t.get("name", "")
            if not snake_re.match(t_name):
                bad_names.append(t_name)
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.3.snake_case_naming",
        "Conformité du format d'identifiant snake_case pour tous les outils",
        "all",
        len(bad_names) == 0,
        elapsed,
        f"Noms non conformes : {bad_names}" if bad_names else None,
    )

    # T1.3.no_null_parameters : Schémas sans valeur null
    t0 = time.perf_counter()
    has_null = []
    for srv_k, srv_tools in discovered_tools.items():
        for t in srv_tools:
            if t.get("inputSchema") is None:
                has_null.append(t.get("name", ""))
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.3.no_null_schemas",
        "Absence de schéma null dans les descripteurs d'outils découverts",
        "all",
        len(has_null) == 0,
        elapsed,
        f"Outils avec schéma null : {has_null}" if has_null else None,
    )

    return results


# ============================================================================
# Palier 2 : Conditions aux limites & cas d'erreur (Boundaries & Negative Tests)
# ============================================================================


def run_tier_2_tests(client: UnifiedMcpClient, target_server: str) -> List[TestResult]:
    """Exécute les tests de limites, sécurité et erreurs du Palier 2."""
    results: List[TestResult] = []

    def add_result(
        tid: str, name: str, srv: str, passed: bool, ms: float, err: Optional[str] = None
    ):
        results.append(TestResult(tid, name, 2, srv, passed, ms, err))

    # --- 2.1 Authentification & Double Montage (/mcp 404 uniforme + /mcp/oauth 401 RFC 9728) ---
    # T2.1.1 : Jurisprudence /mcp non authentifié -> 404 vide sans WWW-Authenticate
    if target_server in ("all", "juris"):
        t0 = time.perf_counter()
        try:
            status, hdrs, body = client.send_http(
                "juris",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                auth_token="OMIT",
            )
            has_www = any(k.lower() == "www-authenticate" for k in hdrs)
            ok = status == 404 and not has_www and body == b""
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.1.1",
                "Garde non-oracle HTTP 404 sur Jurisprudence /mcp sans jeton",
                "juris",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status}, en-têtes {hdrs}, corps {body[:60]!r}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.1.1", "Garde 404 Jurisprudence", "juris", False, elapsed, str(ex))

    # T2.1.2 : Jurisprudence /mcp jeton invalide -> 404 sans WWW-Authenticate
    if target_server in ("all", "juris"):
        t0 = time.perf_counter()
        try:
            status, hdrs, _ = client.send_http(
                "juris",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                auth_token="invalid_token_1234567890",
            )
            has_www = any(k.lower() == "www-authenticate" for k in hdrs)
            ok = status == 404 and not has_www
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.1.2",
                "Garde non-oracle HTTP 404 sur Jurisprudence /mcp avec jeton erroné",
                "juris",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status}, en-têtes {hdrs}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.1.2", "Garde 404 Jurisprudence jeton erroné", "juris", False, elapsed, str(ex))

    # T2.1.3 : Législation non authentifié -> 404 (S8 non-oracle)
    if target_server in ("all", "lois"):
        t0 = time.perf_counter()
        try:
            status, hdrs, _ = client.send_http(
                "lois",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                auth_token="OMIT",
            )
            has_www = any(k.lower() == "www-authenticate" for k in hdrs)
            ok = status == 404 and not has_www
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.1.3",
                "Garde non-oracle HTTP 404 sur Législation sans jeton",
                "lois",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status} au lieu de 404",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.1.3", "Garde 404 Législation", "lois", False, elapsed, str(ex))

    # T2.1.4 : Législation jeton invalide -> 404
    if target_server in ("all", "lois"):
        t0 = time.perf_counter()
        try:
            status, hdrs, _ = client.send_http(
                "lois",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                auth_token="invalid_token_abcdef",
            )
            has_www = any(k.lower() == "www-authenticate" for k in hdrs)
            ok = status == 404 and not has_www
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.1.4",
                "Garde non-oracle HTTP 404 sur Législation avec jeton erroné",
                "lois",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status} au lieu de 404",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.1.4", "Garde 404 Législation jeton erroné", "lois", False, elapsed, str(ex))

    # T2.1.5 : Outils sans jeton -> accès public 200
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            status, _, _ = client.send_http(
                "outils",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"3.1.0"}}}',
                auth_token="OMIT",
            )
            ok = status == 200
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.1.5",
                "Accès public statut libre sur outils",
                "outils",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.1.5", "Accès public outils", "outils", False, elapsed, str(ex))

    # T2.1.6 & T2.1.7 : Découverte OAuth 2.1 / RFC 9728 sur /mcp/oauth (lois & juris)
    for tid_idx, srv_key in ((6, "lois"), (7, "juris")):
        if target_server not in ("all", srv_key):
            continue
        t0 = time.perf_counter()
        tid = f"T2.1.{tid_idx}"
        slug = SLUGS_CARTE_SERVEUR[srv_key]
        try:
            st_oauth, hdrs_oauth, _ = client.send_http(
                srv_key,
                path="/mcp/oauth",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                auth_token="OMIT",
            )
            www_val = {k.lower(): v for k, v in hdrs_oauth.items()}.get("www-authenticate", "")
            expected_meta_url = f"https://{slug}.poirierlavoie.ca/.well-known/oauth-protected-resource/mcp/oauth"
            oauth_401_ok = st_oauth == 401 and expected_meta_url in www_val

            st_meta, _, body_meta = client.send_http(
                srv_key,
                path="/.well-known/oauth-protected-resource/mcp/oauth",
                method="GET",
                auth_token="OMIT",
            )
            meta_json = json.loads(body_meta.decode("utf-8")) if body_meta else {}
            meta_ok = (
                st_meta == 200
                and meta_json.get("authorization_servers") == ["https://acces.poirierlavoie.ca"]
                and meta_json.get("resource") == f"https://{slug}.poirierlavoie.ca/mcp/oauth"
            )

            st_root_meta, _, _ = client.send_http(
                srv_key,
                path="/.well-known/oauth-protected-resource",
                method="GET",
                auth_token="OMIT",
            )
            root_404_ok = st_root_meta == 404

            ok = oauth_401_ok and meta_ok and root_404_ok
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                tid,
                f"Monture OAuth 2.1 /mcp/oauth + RFC 9728 sur {srv_key}",
                srv_key,
                ok,
                elapsed,
                None
                if ok
                else f"/mcp/oauth={st_oauth} (www={www_val!r}), meta={st_meta} ({meta_json}), root_meta={st_root_meta}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(tid, f"Monture OAuth 2.1 RFC 9728 {srv_key}", srv_key, False, elapsed, str(ex))

    # --- 2.2 Transport & Header Boundaries ---
    # T2.2.1 : Outils accepte Accept: application/json
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            status, _, body = client.send_http(
                "outils",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                extra_headers={"Accept": "application/json"},
            )
            ok = status == 200 and b"tools" in body
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.2.1",
                "Support de Accept: application/json sur outils",
                "outils",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status}, corps : {body[:150]}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.2.1", "Accept header application/json", "outils", False, elapsed, str(ex))

    # T2.2.2 : Rejet hôte tiers non autorisé (Host header security)
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            status, _, _ = client.send_http(
                "outils",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                extra_headers={"Host": "evil.example.com"},
            )
            ok = status == 403
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.2.2",
                "Protection DNS re-binding Host header (HTTP 403)",
                "outils",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status} au lieu de 403",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.2.2", "Host header security", "outils", False, elapsed, str(ex))

    # T2.2.3 : Méthode HTTP interdite -> 405 Method Not Allowed
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            status, _, _ = client.send_http(
                "outils",
                path="/mcp",
                method="DELETE",
                body_data=b"",
            )
            ok = status == 405
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.2.3",
                "Rejet des méthodes non autorisées (DELETE -> HTTP 405)",
                "outils",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.2.3", "Méthode non autorisée 405", "outils", False, elapsed, str(ex))

    # T2.2.4 : Corps de requête > 64 Kio -> HTTP 413 Payload Too Large
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            large_body = b'{"jsonrpc":"2.0","id":1,"method":"tools/list","padding":"' + (b"A" * 70000) + b'"}'
            status, _, _ = client.send_http(
                "outils",
                path="/mcp",
                method="POST",
                body_data=large_body,
            )
            ok = status == 413
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.2.4",
                "Plafond de charge utile HTTP 413 (> 64 Kio)",
                "outils",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status} au lieu de 413",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.2.4", "Payload Too Large 413", "outils", False, elapsed, str(ex))

    # T2.2.5 : En-tête User-Agent personnalisé anti-blocage WAF et filtrage actif
    t0 = time.perf_counter()
    try:
        # 1. Requête standard : vérification de la transmission effective de l'en-tête
        status, _, _ = client.send_http("outils", path="/healthz", method="GET")
        sent_ua = getattr(client, "last_sent_headers", {}).get("User-Agent", "")
        ua_present = bool(sent_ua and "DroitCivil" in sent_ua)
        waf_allowed = (status == 200)

        # 2. Requête contre-épreuve : un client standard sans User-Agent personnalisé est bloqué (403)
        status_blocked, _, _ = client.send_http(
            "outils",
            path="/healthz",
            method="GET",
            extra_headers={"User-Agent": "Python-urllib/3.12"},
        )
        waf_blocks_generic = (status_blocked == 403)

        ok = ua_present and waf_allowed and waf_blocks_generic
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.2.5",
            "En-tête User-Agent personnalisé anti-blocage WAF et filtrage actif",
            "all",
            ok,
            elapsed,
            f"UA transmis='{sent_ua}', statut_ok={status}, statut_bloqué={status_blocked}" if not ok else None,
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.2.5", "En-tête User-Agent personnalisé WAF", "all", False, elapsed, str(ex))

    # --- 2.3 JSON-RPC 2.0 Protocol Boundaries ---
    # T2.3.1 : JSON malformé -> code -32700 (PARSE_ERROR)
    t0 = time.perf_counter()
    try:
        _, _, body = client.send_http(
            "outils",
            path="/mcp",
            method="POST",
            body_data=b'{"jsonrpc": "2.0", "method": "tools',
        )
        try:
            data = parse_mcp_response(body, server_key="outils") if body else {}
        except Exception:
            data = json.loads(body.decode("utf-8")) if body else {}
        code = data.get("error", {}).get("code")
        ok = code == -32700
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.3.1",
            "Erreur de syntaxe JSON-RPC code -32700 (Parse error)",
            "outils",
            ok,
            elapsed,
            None if ok else f"Code reçu : {code}, réponse : {data}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.3.1", "JSON-RPC -32700 Parse error", "outils", False, elapsed, str(ex))

    # T2.3.2 : Requête groupée (batch array) -> code -32600 (INVALID_REQUEST)
    t0 = time.perf_counter()
    try:
        _, _, body = client.send_http(
            "outils",
            path="/mcp",
            method="POST",
            body_data=b'[{"jsonrpc":"2.0","id":1,"method":"tools/list"},{"jsonrpc":"2.0","id":2,"method":"tools/list"}]',
        )
        try:
            data = parse_mcp_response(body, server_key="outils") if body else {}
        except Exception:
            data = json.loads(body.decode("utf-8")) if body else {}
        code = data.get("error", {}).get("code")
        ok = code == -32600
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.3.2",
            "Rejet des requêtes groupées code -32600 (Invalid Request)",
            "outils",
            ok,
            elapsed,
            None if ok else f"Code reçu : {code}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.3.2", "JSON-RPC -32600 Batch request", "outils", False, elapsed, str(ex))

    # T2.3.3 : Version jsonrpc 2.0 manquante -> code -32600
    t0 = time.perf_counter()
    try:
        _, _, body = client.send_http(
            "outils",
            path="/mcp",
            method="POST",
            body_data=b'{"id":1,"method":"tools/list"}',
        )
        try:
            data = parse_mcp_response(body, server_key="outils") if body else {}
        except Exception:
            data = json.loads(body.decode("utf-8")) if body else {}
        code = data.get("error", {}).get("code")
        ok = code == -32600
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.3.3",
            "Omission de jsonrpc '2.0' code -32600",
            "outils",
            ok,
            elapsed,
            None if ok else f"Code reçu : {code}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.3.3", "JSON-RPC -32600 Missing version", "outils", False, elapsed, str(ex))

    # T2.3.4 : Méthode RPC inconnue -> code -32601 (METHOD_NOT_FOUND)
    t0 = time.perf_counter()
    try:
        res = client.call_rpc("outils", "method/inexistante_xyz")
        code = res.get("error", {}).get("code")
        ok = code == -32601
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.3.4",
            "Méthode RPC inconnue code -32601 (Method not found)",
            "outils",
            ok,
            elapsed,
            None if ok else f"Résultat : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.3.4", "JSON-RPC -32601 Method not found", "outils", False, elapsed, str(ex))

    # T2.3.5 : Nom d'outil inconnu dans tools/call -> code -32601 ou isError: true
    t0 = time.perf_counter()
    try:
        res = client.call_rpc("outils", "tools/call", {"name": "outil_fantome", "arguments": {}})
        is_err = "error" in res or res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.3.5",
            "Outil inconnu dans tools/call renvoie une erreur",
            "outils",
            is_err,
            elapsed,
            None if is_err else f"Résultat inattendu : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.3.5", "Outil inconnu tools/call", "outils", False, elapsed, str(ex))

    # --- 2.4 Tool Argument Boundaries & Schema Hardening ---
    # T2.4.1 : Rejet d'un paramètre superflu injecté (additionalProperties: false)
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "lois",
            "tools/call",
            {"name": "list_laws", "arguments": {"_champ_injecte": "exploit"}},
        )
        is_err = "error" in res or res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.1",
            "Rejet de propriété injectée (additionalProperties: false)",
            "lois",
            is_err,
            elapsed,
            None if is_err else f"Paramètre non rejeté : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.1", "additionalProperties: false", "lois", False, elapsed, str(ex))

    # T2.4.2 : Paramètre requis manquant sur get_article -> isError: true
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "lois",
            "tools/call",
            {"name": "get_article", "arguments": {"article": "1726"}},  # law manquant
        )
        is_err = res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.2",
            "Rejet de get_article sans paramètre 'law'",
            "lois",
            is_err,
            elapsed,
            None if is_err else f"Réponse sans erreur : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.2", "Paramètre requis manquant 'law'", "lois", False, elapsed, str(ex))

    # T2.4.3 : Paramètre requis manquant sur calendrier_deadlines
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "outils",
            "tools/call",
            {"name": "calendrier_deadlines", "arguments": {"event_date": "2026-07-03"}},
        )
        is_err = res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.3",
            "Rejet de calendrier_deadlines sans 'deadlines'",
            "outils",
            is_err,
            elapsed,
            None if is_err else f"Réponse : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.3", "Paramètre manquant 'deadlines'", "outils", False, elapsed, str(ex))

    # T2.4.4 : Type incompatible sur calendrier_holidays (string au lieu de integer)
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "outils",
            "tools/call",
            {"name": "calendrier_holidays", "arguments": {"year": "deux-mille-vingt-six"}},
        )
        is_err = "error" in res or res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.4",
            "Rejet de type incompatible (year: string -> integer attendu)",
            "outils",
            is_err,
            elapsed,
            None if is_err else f"Réponse : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.4", "Type incompatible year", "outils", False, elapsed, str(ex))

    # T2.4.5 : Violation exclusion mutuelle (XOR) sur palais_get (deux arguments fournis)
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "outils",
            "tools/call",
            {"name": "palais_get", "arguments": {"greffe_number": "500", "palais": "Montréal"}},
        )
        is_err = res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.5",
            "Violation contrainte XOR palais_get (greffe + nom simultanés)",
            "outils",
            is_err,
            elapsed,
            None if is_err else f"Réponse sans erreur : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.5", "XOR palais_get deux fournis", "outils", False, elapsed, str(ex))

    # T2.4.6 : Violation exclusion mutuelle (XOR) sur palais_get (aucun argument fourni)
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "outils",
            "tools/call",
            {"name": "palais_get", "arguments": {}},
        )
        is_err = res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.6",
            "Violation contrainte XOR palais_get (aucun argument fourni)",
            "outils",
            is_err,
            elapsed,
            None if is_err else f"Réponse : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.6", "XOR palais_get aucun fourni", "outils", False, elapsed, str(ex))

    # T2.4.7 : Violation XOR sur jurisprudence (get_case, citator, subsequent_history)
    t0 = time.perf_counter()
    try:
        res1 = client.call_rpc(
            "juris",
            "tools/call",
            {
                "name": "get_case",
                "arguments": {"citation": "2020 QCCA 495", "database_id": "qcca", "case_id": "2020qcca495"},
            },
        )
        is_err1 = res1.get("result", {}).get("isError") is True

        res2 = client.call_rpc(
            "juris",
            "tools/call",
            {
                "name": "citator",
                "arguments": {"citation": "2020 QCCA 495", "database_id": "qcca", "rel": "citing"},
            },
        )
        is_err2 = res2.get("result", {}).get("isError") is True

        res3 = client.call_rpc(
            "juris",
            "tools/call",
            {
                "name": "subsequent_history",
                "arguments": {"citation": "2020 QCCA 495", "case_id": "2020qcca495"},
            },
        )
        is_err3 = res3.get("result", {}).get("isError") is True

        is_err = is_err1 and is_err2 and is_err3
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.7",
            "Violation contrainte XOR jurisprudence (get_case, citator, subsequent_history)",
            "juris",
            is_err,
            elapsed,
            None if is_err else f"get_case err={is_err1}, citator err={is_err2}, sub_hist err={is_err3}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.7", "XOR jurisprudence", "juris", False, elapsed, str(ex))

    # T2.4.8 : Date calendaire bissextile impossible (2025-02-29) -> isError: true
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "outils",
            "tools/call",
            {
                "name": "calendrier_deadlines",
                "arguments": {
                    "event_date": "2025-02-29",
                    "deadlines": [{"amount": 10, "label": "Test"}],
                },
            },
        )
        is_err = res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.8",
            "Date calendaire invalide (2025-02-29 année non bissextile)",
            "outils",
            is_err,
            elapsed,
            None if is_err else f"Date non rejetée : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.8", "Date invalide 2025-02-29", "outils", False, elapsed, str(ex))

    # T2.4.9 : Citation vide sur parse_citation
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "juris",
            "tools/call",
            {"name": "parse_citation", "arguments": {"citation": ""}},
        )
        is_err = res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.9",
            "Rejet de citation vide sur parse_citation",
            "juris",
            is_err,
            elapsed,
            None if is_err else f"Réponse : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.9", "Citation vide parse_citation", "juris", False, elapsed, str(ex))

    # T2.4.10 : Type invalide pour principal_cents sur interets_1619
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "outils",
            "tools/call",
            {
                "name": "interets_1619",
                "arguments": {
                    "end_date": "2026-11-14",
                    "tranches": "cinquante-mille",  # string au lieu de array
                },
            },
        )
        is_err = "error" in res or res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.10",
            "Rejet de tranches de capital non tableau sur interets_1619",
            "outils",
            is_err,
            elapsed,
            None if is_err else f"Réponse : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.10", "Type invalide interets tranches", "outils", False, elapsed, str(ex))

    # T2.4.11 : Violation exclusion mutuelle (XOR) sur registre_get_entity (aucun identifiant / deux fournis)
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            res_empty = client.call_rpc(
                "outils",
                "tools/call",
                {"name": "registre_get_entity", "arguments": {}},
            )
            res_both = client.call_rpc(
                "outils",
                "tools/call",
                {"name": "registre_get_entity", "arguments": {"neq": "1172345678", "corporation_number": "8284083"}},
            )
            ok = (
                res_empty.get("result", {}).get("isError") is True
                and res_both.get("result", {}).get("isError") is True
            )
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.4.11",
                "Violation contrainte XOR registre_get_entity (aucun ou plusieurs identifiants)",
                "outils",
                ok,
                elapsed,
                None if ok else f"empty={res_empty}, both={res_both}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.4.11", "XOR registre_get_entity", "outils", False, elapsed, str(ex))

    # T2.4.12 : Conflit recherche inversée vs directe sur adresse_verify
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            res_rev_fwd = client.call_rpc(
                "outils",
                "tools/call",
                {"name": "adresse_verify", "arguments": {"lot_number": "1 181 642", "address": "1, rue Notre-Dame Est, Montréal"}},
            )
            res_lot_mat = client.call_rpc(
                "outils",
                "tools/call",
                {"name": "adresse_verify", "arguments": {"lot_number": "1 181 642", "matricule": "9891-44-1234"}},
            )
            ok = (
                res_rev_fwd.get("result", {}).get("isError") is True
                and res_lot_mat.get("result", {}).get("isError") is True
            )
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.4.12",
                "Rejet conflit recherche inversée / directe sur adresse_verify",
                "outils",
                ok,
                elapsed,
                None if ok else f"rev_fwd={res_rev_fwd}, lot_mat={res_lot_mat}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.4.12", "Conflit adresse_verify", "outils", False, elapsed, str(ex))

    # T2.4.13 : Rejet CAD et conflit de dates sur taux_boc_rates
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            res_cad = client.call_rpc(
                "outils",
                "tools/call",
                {"name": "taux_boc_rates", "arguments": {"category": "fx", "currency": "CAD", "date": "2026-11-18"}},
            )
            res_dates = client.call_rpc(
                "outils",
                "tools/call",
                {"name": "taux_boc_rates", "arguments": {"date": "2026-11-18", "start_date": "2026-11-01", "end_date": "2026-11-18"}},
            )
            ok = (
                res_cad.get("result", {}).get("isError") is True
                and res_dates.get("result", {}).get("isError") is True
            )
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.4.13",
                "Rejet devise CAD et conflit date/plage sur taux_boc_rates",
                "outils",
                ok,
                elapsed,
                None if ok else f"cad={res_cad}, dates={res_dates}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.4.13", "Validation taux_boc_rates", "outils", False, elapsed, str(ex))

    # T2.4.14 : Blocage divergence d'année de base IPC (2002=100 vs 1992=100) et RMR rent
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            res_uom = client.call_rpc(
                "outils",
                "tools/call",
                {
                    "name": "indice_ipc",
                    "arguments": {
                        "uom": "1992=100",
                        "end_uom": "2002=100",
                        "start_period": "2010-01",
                        "end_period": "2025-01",
                        "amount": "1000.00",
                    },
                },
            )
            res_rmr = client.call_rpc(
                "outils",
                "tools/call",
                {"name": "indice_ipc", "arguments": {"geo": "montreal_rmr", "product": "rent", "period": "2025-01"}},
            )
            ok = (
                res_uom.get("result", {}).get("isError") is True
                and res_rmr.get("result", {}).get("isError") is True
            )
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.4.14",
                "Rejet divergence base IPC (1992=100 vs 2002=100) et composante absente RMR",
                "outils",
                ok,
                elapsed,
                None if ok else f"uom={res_uom}, rmr={res_rmr}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.4.14", "Validation indice_ipc", "outils", False, elapsed, str(ex))

    # T2.4.15 : Rejet paramètres incomplets sur loyer_tal calcul_2026 et rate_overrides en prime_plus_margin
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            res_tal = client.call_rpc(
                "outils",
                "tools/call",
                {"name": "loyer_tal", "arguments": {"mode": "calcul_2026", "current_rent_cents": 120000}},
            )
            res_prime = client.call_rpc(
                "outils",
                "tools/call",
                {
                    "name": "interets_1619",
                    "arguments": {
                        "mode": "prime_plus_margin",
                        "end_date": "2026-11-18",
                        "rate_overrides": [{"quarter": "2027-Q1", "laf_rate_bps": 700}],
                        "tranches": [{"principal_cents": 100000, "start_date": "2025-01-01"}],
                    },
                },
            )
            ok = (
                res_tal.get("result", {}).get("isError") is True
                and res_prime.get("result", {}).get("isError") is True
            )
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.4.15",
                "Rejet calcul_2026 sans lease_renewal_date et rate_overrides en prime_plus_margin",
                "outils",
                ok,
                elapsed,
                None if ok else f"tal={res_tal}, prime={res_prime}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.4.15", "Validation loyer_tal / interets_1619", "outils", False, elapsed, str(ex))

    # T2.4.16 : Validation imbriquée (items), bornes numériques et format amount (taux_boc_rates, indice_ipc, interets_1619, loyer_tal)
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            neg_probes = [
                ("taux_boc_rates", {"category": "fx", "currency": "USD", "date": "2026-11-18", "amount": "abc"}),
                ("taux_boc_rates", {"category": "fx", "currency": "USD", "date": "2026-11-18", "amount": "-50.00"}),
                ("indice_ipc", {"geo": "quebec", "product": "all_items", "start_period": "2024-01", "end_period": "2025-01", "amount": "abc"}),
                ("interets_1619", {"mode": "prime_plus_margin", "spread_bps": -5001, "end_date": "2026-11-18", "tranches": [{"principal_cents": 100000, "start_date": "2025-01-01"}]}),
                ("interets_1619", {"mode": "legal_plus_1619", "end_date": "2026-11-18", "tranches": [{}]}),
                ("interets_1619", {"mode": "contractual", "end_date": "2026-11-18", "tranches": [{"principal_cents": 100000, "start_date": "2025-01-01"}]}),
                ("loyer_tal", {"mode": "calcul_2026", "lease_renewal_date": "2026-07-01", "current_rent_cents": -100}),
                ("loyer_tal", {"mode": "bareme", "year": 1800}),
                ("loyer_tal", {"mode": "calcul_2026", "lease_renewal_date": "2026-07-01", "current_rent_cents": 100000, "capital_works": [{"gross_amount_cents": 500000, "bogus": True}]}),
            ]
            failed_probes = []
            for tname, targs in neg_probes:
                r_probe = client.call_rpc("outils", "tools/call", {"name": tname, "arguments": targs})
                if not ("error" in r_probe or r_probe.get("result", {}).get("isError") is True):
                    failed_probes.append(f"{tname}({targs}) -> {r_probe}")
            ok = len(failed_probes) == 0
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.4.16",
                "Rejet bornes numériques, objets imbriqués (items) et formats amount sur outils économie/calcul",
                "outils",
                ok,
                elapsed,
                None if ok else "; ".join(failed_probes[:3]),
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.4.16", "Bornes et items imbriqués", "outils", False, elapsed, str(ex))

    return results


# ============================================================================
# Palier 3 : Compatibilité inter-plateformes & intégrité cache (Cross-Platform)
# ============================================================================


def run_tier_3_tests(
    client: UnifiedMcpClient,
    repo_root: Path,
    target_server: str,
    require_antigravity_cache: bool = False,
) -> List[TestResult]:
    """Exécute les tests de parité Claude/Gemini, cache Antigravity et contrats."""
    results: List[TestResult] = []

    def add_result(
        tid: str,
        name: str,
        srv: str,
        passed: bool,
        ms: float,
        err: Optional[str] = None,
        skipped: bool = False,
    ):
        results.append(TestResult(tid, name, 3, srv, passed, ms, err, skipped=skipped))

    # --- 3.1 Server Key & Transport Uniformity ---
    t0 = time.perf_counter()
    mcp_json_path = repo_root / ".mcp.json"
    agy_mcp_path = repo_root / "mcp_config.json"
    gem_ext_path = repo_root / "gemini-extension.json"

    mcp_data = json.loads(mcp_json_path.read_text(encoding="utf-8")) if mcp_json_path.is_file() else {}
    agy_data = json.loads(agy_mcp_path.read_text(encoding="utf-8")) if agy_mcp_path.is_file() else {}
    gem_data = json.loads(gem_ext_path.read_text(encoding="utf-8")) if gem_ext_path.is_file() else {}

    # Validation stricte des clés de serveurs exactes en minuscules sans masquage
    mcp_srv_keys = set(mcp_data.get("mcpServers", {}).keys())
    agy_srv_keys = set(agy_data.get("mcpServers", {}).keys())
    gem_srv_keys = set(gem_data.get("mcpServers", {}).keys())
    exp_keys = {"lois", "juris", "outils"}

    keys_ok = (mcp_srv_keys == exp_keys) and (agy_srv_keys == exp_keys) and (gem_srv_keys == exp_keys)
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T3.1.1",
        "Uniformité des clés de serveurs (lois, juris, outils)",
        "all",
        keys_ok,
        elapsed,
        f"Clés divergentes : .mcp={mcp_srv_keys}, agy={agy_srv_keys}, gem={gem_srv_keys}" if not keys_ok else None,
    )

    # T3.1.2 : Parité des URL d'accès (/mcp/oauth pour lois & juris, /mcp pour outils)
    t0 = time.perf_counter()
    url_errs = []
    for s_name, exp_url in URL_MANIFESTES_ATTENDUES.items():
        c_srv = mcp_data.get("mcpServers", {}).get(s_name, {})
        if c_srv.get("url") != exp_url or c_srv.get("type") != "http":
            url_errs.append(f".mcp.json {s_name}={c_srv!r} != http:{exp_url}")
        a_url = agy_data.get("mcpServers", {}).get(s_name, {}).get("url")
        if a_url != exp_url:
            url_errs.append(f"mcp_config.json {s_name}.url={a_url} != {exp_url}")
        g_srv = gem_data.get("mcpServers", {}).get(s_name, {})
        if g_srv.get("url") != exp_url or g_srv.get("type") != "http":
            url_errs.append(f"gemini-extension.json {s_name}={g_srv!r} != http:{exp_url}")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T3.1.2",
        "Parité stricte des URL OAuth 2.1 entre configurations Claude et Gemini",
        "all",
        len(url_errs) == 0,
        elapsed,
        "; ".join(url_errs) if url_errs else None,
    )

    # T3.1.3 : Absence d'en-têtes statiques ou variables secrètes dans les 3 manifestes (OAuth 2.1 zéro-config)
    t0 = time.perf_counter()
    sec_errs = []
    if gem_data.get("settings") != []:
        sec_errs.append("gemini-extension.json settings doit valoir []")
    for s_name in ("lois", "juris", "outils"):
        if "headers" in mcp_data.get("mcpServers", {}).get(s_name, {}):
            sec_errs.append(f".mcp.json {s_name} ne doit pas déclarer d'en-têtes statiques")
        agy_srv = agy_data.get("mcpServers", {}).get(s_name, {})
        if "headers" in agy_srv or "variables" in agy_srv:
            sec_errs.append(f"mcp_config.json {s_name} ne doit déclarer ni headers ni variables")
        if "headers" in gem_data.get("mcpServers", {}).get(s_name, {}):
            sec_errs.append(f"gemini-extension.json {s_name} ne doit pas déclarer d'en-têtes statiques")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T3.1.3",
        "Absence d'en-têtes statiques et de variables secrètes dans les manifestes OAuth",
        "all",
        len(sec_errs) == 0,
        elapsed,
        "; ".join(sec_errs) if sec_errs else None,
    )

    # --- 3.2 Antigravity Tool Cache Integrity ---
    # Résolution du répertoire cache Antigravity
    antigravity_mcp_base = (
        Path(os.environ["USERPROFILE"]) / ".gemini" / "antigravity" / "mcp"
        if "USERPROFILE" in os.environ
        else Path.home() / ".gemini" / "antigravity" / "mcp"
    )

    leg_dir = antigravity_mcp_base / "droit-civil-quebecois_lois"
    jur_dir = antigravity_mcp_base / "droit-civil-quebecois_juris"
    out_dir = antigravity_mcp_base / "droit-civil-quebecois_outils"

    cache_present = antigravity_mcp_base.is_dir() and (leg_dir.is_dir() or jur_dir.is_dir() or out_dir.is_dir())

    if not cache_present:
        if require_antigravity_cache:
            for tid, name, srv in [
                ("T3.2.1", "Partition du cache Législation sur disque (10 outils)", "lois"),
                ("T3.2.2", "Partition du cache Jurisprudence sur disque (10 outils)", "juris"),
                ("T3.2.3", "Partition du cache Outils sur disque (15 outils)", "outils"),
                ("T3.2.4", "Intégrité approfondie des 35 schémas d'outils sur disque", "all"),
                ("T3.2.5", "Présence et conformité de instructions.md sur disque", "all"),
            ]:
                add_result(tid, name, srv, False, 0.0, f"Cache absent dans {antigravity_mcp_base}")
        else:
            for tid, name, srv in [
                ("T3.2.1", "Partition du cache Législation sur disque (ignoré : cache Antigravity absent hors local)", "lois"),
                ("T3.2.2", "Partition du cache Jurisprudence sur disque (ignoré : cache Antigravity absent hors local)", "juris"),
                ("T3.2.3", "Partition du cache Outils sur disque (ignoré : cache Antigravity absent hors local)", "outils"),
                ("T3.2.4", "Intégrité approfondie des 35 schémas (ignoré : cache Antigravity absent hors local)", "all"),
                ("T3.2.5", "Présence instructions.md (ignoré : cache Antigravity absent hors local)", "all"),
            ]:
                add_result(tid, name, srv, True, 0.0, None, skipped=True)
    else:
        # T3.2.1 : Partition Législation sur disque (10 outils)
        t0 = time.perf_counter()
        leg_tools = list(leg_dir.glob("*.json")) if leg_dir.is_dir() else []
        leg_names = {f.stem for f in leg_tools}
        c_leg_ok = (len(leg_tools) == 10) and (leg_names == set(NOMS_OUTILS_ATTENDUS["lois"]))
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.2.1",
            "Partition du cache Législation sur disque (exactement 10 outils)",
            "lois",
            c_leg_ok,
            elapsed,
            f"Trouvé {len(leg_tools)} fichiers .json au lieu de 10 dans {leg_dir}" if not c_leg_ok else None,
        )

        # T3.2.2 : Partition Jurisprudence sur disque (10 outils, sans greffe/palais)
        t0 = time.perf_counter()
        jur_tools = list(jur_dir.glob("*.json")) if jur_dir.is_dir() else []
        jur_names = {f.stem for f in jur_tools}
        stale_in_jur = jur_names.intersection({"greffe_parse_number", "palais_list", "palais_get"})
        c_jur_ok = (len(jur_tools) == 10) and (jur_names == set(NOMS_OUTILS_ATTENDUS["juris"])) and (not stale_in_jur)
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.2.2",
            "Partition du cache Jurisprudence sur disque (exactement 10 outils, sans greffe/palais)",
            "juris",
            c_jur_ok,
            elapsed,
            f"Trouvé {len(jur_tools)} fichiers (stale: {stale_in_jur}) au lieu de 10 dans {jur_dir}" if not c_jur_ok else None,
        )

        # T3.2.3 : Partition Outils sur disque (15 outils sur 6 familles)
        t0 = time.perf_counter()
        out_tools = list(out_dir.glob("*.json")) if out_dir.is_dir() else []
        out_names = {f.stem for f in out_tools}
        c_out_ok = (len(out_tools) == 15) and (out_names == set(NOMS_OUTILS_ATTENDUS["outils"]))
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.2.3",
            "Partition du cache Outils sur disque (exactement 15 outils sur 6 familles)",
            "outils",
            c_out_ok,
            elapsed,
            f"Trouvé {len(out_tools)} fichiers au lieu de 15 dans {out_dir}" if not c_out_ok else None,
        )

        # T3.2.4 : Intégrité approfondie des 35 schémas d'outils sur disque (descriptions et items)
        t0 = time.perf_counter()
        schema_errs = []
        total_inspected = 0
        for srv_name, s_dir in [("lois", leg_dir), ("juris", jur_dir), ("outils", out_dir)]:
            if not s_dir.is_dir():
                schema_errs.append(f"Répertoire manquant: {s_dir}")
                continue
            for json_file in sorted(s_dir.glob("*.json")):
                total_inspected += 1
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    # 1. Validation de la description outil
                    tool_desc = str(data.get("description", "")).strip()
                    if len(tool_desc) < 30:
                        schema_errs.append(f"{srv_name}/{json_file.name} description outil tronquée (<30 car.)")

                    # 2. Validation parameters
                    params = data.get("parameters")
                    if not isinstance(params, dict) or params.get("type") != "object":
                        schema_errs.append(f"{srv_name}/{json_file.name} parameters null ou non-objet")
                        continue
                    if params.get("additionalProperties") is not False:
                        schema_errs.append(f"{srv_name}/{json_file.name} additionalProperties non-false")

                    # 3. Validation de chaque propriété et tableau
                    props = params.get("properties", {})
                    for pname, pspec in props.items():
                        if not isinstance(pspec, dict):
                            schema_errs.append(f"{srv_name}/{json_file.name} propriété '{pname}' non-dict")
                            continue
                        pdesc = str(pspec.get("description", "")).strip()
                        if not pdesc:
                            schema_errs.append(f"{srv_name}/{json_file.name} propriété '{pname}' sans description")
                        if pspec.get("type") == "array":
                            items = pspec.get("items")
                            if not items or not isinstance(items, dict) or len(items) == 0:
                                schema_errs.append(f"{srv_name}/{json_file.name} tableau '{pname}' sans items")
                            elif items.get("type") == "object":
                                for subname, subspec in items.get("properties", {}).items():
                                    if isinstance(subspec, dict) and not str(subspec.get("description", "")).strip():
                                        schema_errs.append(f"{srv_name}/{json_file.name} {pname}.items.{subname} sans description")
                except Exception as ex:
                    schema_errs.append(f"{srv_name}/{json_file.name} erreur JSON: {ex}")

        t324_ok = (total_inspected == 35) and (len(schema_errs) == 0)
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.2.4",
            "Intégrité approfondie des 35 schémas d'outils sur disque (descriptions et items)",
            "all",
            t324_ok,
            elapsed,
            "; ".join(schema_errs[:5]) + (f" (+{len(schema_errs)-5} erreurs)" if len(schema_errs) > 5 else "") if schema_errs else (None if total_inspected == 35 else f"Inspecté {total_inspected}/35 schémas"),
        )

        # T3.2.5 : Présence et conformité de instructions.md dans les 3 serveurs sur disque
        t0 = time.perf_counter()
        missing_instr = []
        for srv_name, s_dir in [("lois", leg_dir), ("juris", jur_dir), ("outils", out_dir)]:
            instr_path = s_dir / "instructions.md"
            if not instr_path.is_file() or instr_path.stat().st_size == 0:
                missing_instr.append(f"{srv_name} ({instr_path})")

        instr_ok = (len(missing_instr) == 0)
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.2.5",
            "Présence et non-vacuité de instructions.md dans les 3 serveurs sur disque",
            "all",
            instr_ok,
            elapsed,
            f"instructions.md manquants ou vides : {', '.join(missing_instr)}" if not instr_ok else None,
        )

    # --- 3.3 Cross-Server Contract Handshakes ---
    # T3.3.1 : Contrat Greffe -> Palais (500 -> Montréal)
    t0 = time.perf_counter()
    try:
        greffe_res = client.call_tool(
            "outils",
            "greffe_parse_number",
            {"court_file_number": "500-17-000001-261"},
        )
        greffe_sc = greffe_res.get("structuredContent") or {}
        greffe_num = greffe_sc.get("greffe_number")

        palais_res = client.call_tool(
            "outils", "palais_get", {"greffe_number": greffe_num}
        )
        palais_sc = palais_res.get("structuredContent") or {}
        palais_obj = palais_sc.get("palais") or {}
        is_mtl = greffe_num == "500" and "Montréal" in palais_obj.get("name", "")

        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.3.1",
            "Contrat croisé Greffe -> Palais (dossier 500 -> Palais de justice de Montréal)",
            "outils",
            is_mtl,
            elapsed,
            None if is_mtl else f"Greffe : {greffe_sc}, Palais : {palais_sc}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T3.3.1", "Contrat Greffe -> Palais", "outils", False, elapsed, str(ex))

    # T3.3.2 : Contrat Législation -> Intérêts (art. 1619 C.c.Q.)
    t0 = time.perf_counter()
    try:
        leg_res = client.call_tool(
            "lois", "resolve_reference", {"citation": "art. 1619 C.c.Q."}
        )
        leg_sc = leg_res.get("structuredContent") or {}
        art_num = (leg_sc.get("resolved") or {}).get("number")

        calc_res = client.call_tool(
            "outils",
            "interets_1619",
            {
                "end_date": "2026-11-14",
                "tranches": [{"principal_cents": 10000000, "start_date": "2024-01-01"}],
            },
        )
        calc_sc = calc_res.get("structuredContent") or {}
        has_indemnity = calc_sc.get("total_additional_indemnity_cents", 0) > 0

        ok = art_num == "1619" and has_indemnity
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.3.2",
            "Contrat croisé Législation -> Intérêts (art. 1619 -> calcul indemnité additionnelle)",
            "all",
            ok,
            elapsed,
            None if ok else f"Art : {art_num}, Calcul : {calc_sc}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T3.3.2", "Contrat Législation -> Intérêts", "all", False, elapsed, str(ex))

    # T3.3.3 : Contrat Jurisprudence -> Greffe
    t0 = time.perf_counter()
    try:
        case_res = client.call_tool("juris", "get_case", {"citation": "2015 QCCA 1526"})
        case_txt = case_res.get("content", [{}])[0].get("text", "")
        m_dossier = re.search(r"\b(\d{3}-\d{2}-\d{6}-\d{3})\b", case_txt)
        court_file = m_dossier.group(1) if m_dossier else ""

        parse_res = (
            client.call_tool(
                "outils", "greffe_parse_number", {"court_file_number": court_file}
            )
            if court_file
            else {}
        )
        parse_sc = parse_res.get("structuredContent") or {}
        ok = bool(court_file) and parse_sc.get("greffe_number") == "500"

        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.3.3",
            "Contrat croisé Jurisprudence -> Greffe (CanLII dossier -> district 500)",
            "all",
            ok,
            elapsed,
            None if ok else f"Dossier '{court_file}', analyse : {parse_sc}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T3.3.3", "Contrat Jurisprudence -> Greffe", "all", False, elapsed, str(ex))

    # T3.3.4 : Contrat CPC -> Calendrier (art. 145 C.p.c. 15 jours)
    t0 = time.perf_counter()
    try:
        cpc_res = client.call_tool("lois", "get_article", {"law": "cpc", "article": "145"})
        cpc_txt = cpc_res.get("content", [{}])[0].get("text", "")
        has_15 = "15" in cpc_txt

        cal_res = client.call_tool(
            "outils",
            "calendrier_deadlines",
            {
                "event_date": "2026-09-01",
                "deadlines": [{"amount": 15, "label": "Réponse art. 145"}],
            },
        )
        cal_results = (cal_res.get("structuredContent") or {}).get("results") or [{}]
        due_date = cal_results[0].get("effective_date")
        ok = has_15 and due_date == "2026-09-16"

        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.3.4",
            "Contrat croisé C.p.c. -> Calendrier (art. 145 C.p.c. calcul arithmétique exact)",
            "all",
            ok,
            elapsed,
            None if ok else f"Échéance reçue : {due_date}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T3.3.4", "Contrat CPC -> Calendrier", "all", False, elapsed, str(ex))

    # T3.3.5 : Contrat Registres -> Adresses -> Terminologie (v0.3.0)
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            reg_res = client.call_tool(
                "outils",
                "registre_search",
                {"query": "9123-4567"},
            )
            reg_sc = reg_res.get("structuredContent") or {}
            first_neq = ((reg_sc.get("entities") or [{}])[0]).get("neq")
            ent_res = client.call_tool(
                "outils",
                "registre_get_entity",
                {"neq": first_neq or "1172345678"},
            )
            ent_sc = ent_res.get("structuredContent") or {}
            ent_addr = (
                ((ent_sc.get("quebec") or {}).get("domicile_declare") or {}).get("adresse")
                or ""
            )
            addr_res = client.call_tool(
                "outils",
                "adresse_verify",
                {"address": ent_addr or "1, rue Notre-Dame Est, Montréal"},
            )
            addr_sc = addr_res.get("structuredContent") or {}
            scan_res = client.call_tool(
                "outils",
                "terminologie_scan",
                {"text": "The debtor granted a mortgage on the immovable.", "lang": "en"},
            )
            scan_sc = scan_res.get("structuredContent") or {}
            ok = (
                bool(reg_sc.get("gardes"))
                and bool(ent_sc.get("gardes"))
                and bool(addr_sc.get("gardes"))
                and bool(addr_sc.get("adresse_normalisee"))
                and scan_sc.get("flagged_count", 0) >= 1
            )
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T3.3.5",
                "Contrat croisé Registres -> Adresses RQA -> Terminologie (gardes obligatoires)",
                "outils",
                ok,
                elapsed,
                None if ok else f"reg={reg_sc}, ent={ent_sc}, addr={addr_sc}, scan={scan_sc}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T3.3.5", "Contrat Registres -> Adresses -> Terminologie", "outils", False, elapsed, str(ex))

    # T3.3.6 : Contrat Économie / BoC -> Intérêts prime_plus_margin & Conversion Loi sur la monnaie
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            fx_res = client.call_tool(
                "outils",
                "taux_boc_rates",
                {"category": "fx", "currency": "USD", "date": "2016-06-15", "amount": "10000.00"},
            )
            fx_sc = fx_res.get("structuredContent") or {}
            fx_gardes = {g.get("code") for g in (fx_sc.get("gardes") or [])}
            prime_res = client.call_tool(
                "outils",
                "interets_1619",
                {
                    "mode": "prime_plus_margin",
                    "spread_bps": 200,
                    "end_date": "2026-11-18",
                    "tranches": [{"principal_cents": 1000000, "start_date": "2025-01-01"}],
                },
            )
            prime_sc = prime_res.get("structuredContent") or {}
            prime_gardes = {g.get("code") for g in (prime_sc.get("gardes") or [])}
            ipc_res = client.call_tool(
                "outils",
                "indice_ipc",
                {"geo": "quebec", "product": "all_items", "start_period": "2024-01", "end_period": "2025-01", "amount": "2000.00", "cap_bps": 150},
            )
            ipc_sc = ipc_res.get("structuredContent") or {}
            fx_obs_0 = (fx_sc.get("fx_observations") or [{}])[0]
            ok = (
                "TAUX_BOC_NOON_HISTORIQUE_PRE_2017" in fx_gardes
                and "TAUX_BOC_CONVERSION_LOI_MONNAIE" in fx_gardes
                and isinstance(fx_sc.get("currency"), dict)
                and fx_sc["currency"].get("code") == "USD"
                and fx_obs_0.get("currency_code") == "USD"
                and (fx_sc.get("conversion") or {}).get("converted_cents", 0) > 0
                and "TAUX_BOC_PRIME_INDICATIF_BANCAIRE" in prime_gardes
                and prime_sc.get("total_contractual_interest_cents", 0) > 0
                and (ipc_sc.get("escalation") or {}).get("applied_bound") == "cap"
                and (ipc_sc.get("escalation") or {}).get("escalated_cents") == 203000
            )
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T3.3.6",
                "Contrat Économie : taux_boc_rates + interets_1619 (prime_plus_margin) + indice_ipc",
                "outils",
                ok,
                elapsed,
                None if ok else f"fx={fx_sc}, prime={prime_sc}, ipc={ipc_sc}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T3.3.6", "Contrat Économie", "outils", False, elapsed, str(ex))

    # T3.3.7 : Contrat TAL & SCHL (calcul_2026, pré-2026 transitoire, SCHL indicatif)
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            tal_2026 = client.call_tool(
                "outils",
                "loyer_tal",
                {"mode": "calcul_2026", "lease_renewal_date": "2026-07-01", "current_rent_cents": 100000},
            )
            tal_2026_sc = tal_2026.get("structuredContent") or {}
            tal_pre = client.call_tool(
                "outils",
                "loyer_tal",
                {"mode": "calcul_2026", "notice_date": "2025-12-15", "lease_renewal_date": "2026-04-01", "current_rent_cents": 100000},
            )
            tal_pre_sc = tal_pre.get("structuredContent") or {}
            tal_pre_gardes = {g.get("code") for g in (tal_pre_sc.get("gardes") or [])}
            schl_res = client.call_tool(
                "outils",
                "loyer_tal",
                {"mode": "schl", "cmhc_geo": "Montréal"},
            )
            schl_sc = schl_res.get("structuredContent") or {}
            schl_gardes = {g.get("code") for g in (schl_sc.get("gardes") or [])}
            schl_first = (schl_sc.get("cmhc_results") or [{}])[0]
            ok = (
                tal_2026_sc.get("regime") == "post_2026_calcul"
                and (tal_2026_sc.get("calculation") or {}).get("new_rent_cents", 0) > 100000
                and (tal_2026_sc.get("calculation") or {}).get("base_rent_bps", 0) > 0
                and isinstance(tal_2026_sc.get("bareme_post_2026"), list)
                and isinstance(tal_2026_sc.get("bareme_pre_2026"), list)
                and isinstance(tal_2026_sc.get("cmhc_results"), list)
                and tal_pre_sc.get("regime") == "pre_2026_transitoire"
                and "TAL_REGIME_TRANSITOIRE_PRE_2026" in tal_pre_gardes
                and "SCHL_LOYER_MOYEN_INDICATIF" in schl_gardes
                and isinstance(schl_first.get("cells"), list)
                and len(schl_first.get("cells") or []) >= 1
            )
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T3.3.7",
                "Contrat loyer_tal : calcul_2026 + garde pré-2026 + SCHL indicatif",
                "outils",
                ok,
                elapsed,
                None if ok else f"tal2026={tal_2026_sc}, pre={tal_pre_sc}, schl={schl_sc}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T3.3.7", "Contrat loyer_tal", "outils", False, elapsed, str(ex))

    # T3.3.8 : Contrat GLEIF LEI + Recherche inversée lot cadastral RQA (découverte dynamique)
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            gleif_search = client.call_tool(
                "outils",
                "registre_search",
                {"jurisdiction": "gleif", "query": "Banque"},
            )
            gleif_search_sc = gleif_search.get("structuredContent") or {}
            discovered_lei = next(
                (e.get("lei") for e in (gleif_search_sc.get("entities") or []) if e.get("lei")),
                None,
            )
            lei_res = (
                client.call_tool("outils", "registre_get_entity", {"lei": discovered_lei})
                if discovered_lei
                else {}
            )
            lei_sc = lei_res.get("structuredContent") or {}
            lei_gardes = {g.get("code") for g in (lei_sc.get("gardes") or [])}

            addr_fwd = client.call_tool(
                "outils",
                "adresse_verify",
                {"address": "1, rue Notre-Dame Est, Montréal"},
            )
            addr_fwd_sc = addr_fwd.get("structuredContent") or {}
            fwd_cand = (addr_fwd_sc.get("candidates") or [{}])[0]
            discovered_lot = ((fwd_cand.get("lots_cadastraux") or [None])[0])

            lot_res = (
                client.call_tool("outils", "adresse_verify", {"lot_number": discovered_lot})
                if discovered_lot
                else {}
            )
            lot_sc = lot_res.get("structuredContent") or {}
            lot_gardes = {g.get("code") for g in (lot_sc.get("gardes") or [])}
            first_cand = (lot_sc.get("candidates") or [{}])[0]
            ok = (
                bool(discovered_lei)
                and bool(re.match(r"^[A-Z0-9]{20}$", str(discovered_lei)))
                and lei_sc.get("lookup_by") == "lei"
                and isinstance(lei_sc.get("gleif"), dict)
                and bool((lei_sc.get("portails_officiels") or {}).get("isc_pisc"))
                and "REGISTRE_GLEIF_DECLARATIF_CONSOLIDATION" in lei_gardes
                and bool(discovered_lot)
                and first_cand.get("lot_source") in ("rqa_unite", "rqa_immeuble_parent", "absent")
                and bool(first_cand.get("lots_cadastraux"))
                and "ADRESSE_LOT_ET_MATRICULE_SANS_VALEUR_LEGALE" in lot_gardes
            )
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T3.3.8",
                "Contrat GLEIF (LEI + portails_officiels) et RQA inversé (lot_number + lot_source)",
                "outils",
                ok,
                elapsed,
                None if ok else f"lei_search={gleif_search_sc}, lei={lei_sc}, fwd={addr_fwd_sc}, lot={lot_sc}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T3.3.8", "Contrat GLEIF & RQA inversé", "outils", False, elapsed, str(ex))

    # --- 3.4 Static Verifier Alignment ---
    # T3.4.1 : Présence de verifier_tout.py dans ROOT_ALLOWLIST de verifier.py
    t0 = time.perf_counter()
    verifier_py_path = repo_root / "verifier.py"
    has_allowlist = False
    if verifier_py_path.is_file():
        v_code = verifier_py_path.read_text(encoding="utf-8")
        has_allowlist = '"verifier_tout.py"' in v_code
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T3.4.1",
        "Enregistrement de verifier_tout.py dans ROOT_ALLOWLIST de verifier.py",
        "all",
        has_allowlist,
        elapsed,
    )

    # T3.4.2 : Exécution sans défaut de verifier.py
    t0 = time.perf_counter()
    sys.path.insert(0, str(repo_root))
    try:
        import verifier  # type: ignore

        erreurs_statiques, _ = verifier.verifier(repo_root)
        clean_run = len(erreurs_statiques) == 0
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.4.2",
            "Exécution sans erreur du vérificateur statique repository (verifier.py)",
            "all",
            clean_run,
            elapsed,
            "; ".join(erreurs_statiques) if erreurs_statiques else None,
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T3.4.2", "Exécution verifier.py", "all", False, elapsed, str(ex))

    # T3.4.3 : Vérification des 4 scripts de compétences autonomes (v3.1.0)
    t0 = time.perf_counter()
    script_calc = repo_root / "skills" / "gestion-du-mandat" / "scripts" / "calcul_delai.py"
    script_insp = repo_root / "skills" / "analyse-et-strategie" / "scripts" / "inspecter_piece.py"
    script_ctrl = repo_root / "skills" / "production-et-conformite" / "scripts" / "controler_document.py"
    script_cote = repo_root / "skills" / "production-et-conformite" / "scripts" / "verifier_cotes.py"
    scripts_ok = (
        script_calc.is_file()
        and script_insp.is_file()
        and script_ctrl.is_file()
        and script_cote.is_file()
    )
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T3.4.3",
        "Disponibilité des 4 scripts auxiliaires de compétences",
        "all",
        scripts_ok,
        elapsed,
    )

    return results


# ============================================================================
# Palier 4 : Scénarios réels de litige civil québécois (Real-World Workflows)
# ============================================================================


def run_tier_4_tests(client: UnifiedMcpClient) -> List[TestResult]:
    """Exécute les 4 chaînes d'invocation complètes de litige civil québécois."""
    results: List[TestResult] = []

    def add_result(
        tid: str, name: str, srv: str, passed: bool, ms: float, err: Optional[str] = None
    ):
        results.append(TestResult(tid, name, 4, srv, passed, ms, err))

    # --- Scénario 1 : Vice caché immobilier & calcul d'intérêts C.c.Q. ---
    t0 = time.perf_counter()
    try:
        # Étape 1 : Repérage heuristique
        r1 = client.call_tool("lois", "find_relevant", {"query": "vice caché infiltration fondation"})
        txt1 = r1.get("content", [{}])[0].get("text", "")
        # Étape 2 : Extraction article 1726
        r2 = client.call_tool("lois", "get_article", {"law": "ccq", "article": "1726"})
        txt2 = r2.get("content", [{}])[0].get("text", "")
        # Étape 3 : Extraction en lot 1726-1731
        r3 = client.call_tool("lois", "get_articles", {"law": "ccq", "from": "1726", "to": "1731"})
        txt3 = r3.get("content", [{}])[0].get("text", "")
        # Étape 4 : Vérification d'autorité 2020 QCCA 495 (SNC-Lavalin inc. ... c. Deguise)
        r4 = client.call_tool(
            "juris",
            "verify_citations",
            {
                "citations": [
                    {
                        "citation": "2020 QCCA 495",
                        "expected_title": "SNC-Lavalin inc. (Terratech inc. et SNC-Lavalin Environnement inc.) c. Deguise",
                    }
                ]
            },
        )
        txt4 = r4.get("content", [{}])[0].get("text", "")
        # Étape 5 : Citateur CanLII
        r5 = client.call_tool("juris", "citator", {"citation": "2020 QCCA 495", "rel": "citing", "limit": 5})
        txt5 = r5.get("content", [{}])[0].get("text", "")
        # Étape 6 : Analyse numéro de greffe
        r6 = client.call_tool("outils", "greffe_parse_number", {"court_file_number": "500-17-012345-211"})
        txt6 = r6.get("content", [{}])[0].get("text", "")
        # Étape 7 : Calcul exact d'intérêts et indemnité additionnelle art. 1619
        r7 = client.call_tool(
            "outils",
            "interets_1619",
            {
                "end_date": "2026-11-14",
                "tranches": [{"principal_cents": 5000000, "start_date": "2024-05-01", "label": "Réparations"}],
            },
        )
        sc7 = r7.get("structuredContent") or {}

        ok = (
            not r1.get("isError")
            and "ccq" in txt1.lower()
            and "1726" in txt2
            and "1731" in txt3
            and "CONFIRMÉE" in txt4
            and not r5.get("isError")
            and len(txt5) > 0
            and "Montréal" in txt6
            and sc7.get("grand_total_cents", 0) > 0
        )
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T4.1",
            "Scénario 1 : Litige contractuel de vice caché immobilier (C.c.Q.)",
            "all",
            ok,
            elapsed,
            None if ok else "Échec d'une étape du scénario 1",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T4.1", "Scénario 1 : Vice caché", "all", False, elapsed, str(ex))

    # --- Scénario 2 : Notification technologique & calendrier procédural C.p.c. ---
    t0 = time.perf_counter()
    try:
        # Étape 1 : Résolution référence art. 145 C.p.c.
        r1 = client.call_tool("lois", "resolve_reference", {"citation": "art. 145 C.p.c."})
        txt1 = r1.get("content", [{}])[0].get("text", "")
        # Étape 2 : Jours fériés 2026
        r2 = client.call_tool("outils", "calendrier_holidays", {"year": 2026, "regime": "qc_cpc"})
        txt2 = r2.get("content", [{}])[0].get("text", "")
        # Étape 3 : Calcul arithmétique avec bascule art. 111 al. 2 C.p.c. (17h35 un vendredi)
        r3 = client.call_tool(
            "outils",
            "calendrier_deadlines",
            {
                "event_date": "2026-07-03",
                "event_time": "17:35",
                "notification_mode": "technological",
                "regime": "qc_cpc",
                "deadlines": [{"label": "Réponse du défendeur", "amount": 15, "unit": "days"}],
            },
        )
        txt3 = r3.get("content", [{}])[0].get("text", "")
        # Étape 4 : Fiche du palais de justice de Montréal pour dépôt
        r4 = client.call_tool("outils", "palais_get", {"greffe_number": "500"})
        txt4 = r4.get("content", [{}])[0].get("text", "")

        ok = (
            not r1.get("isError")
            and "145" in txt1
            and not r2.get("isError")
            and "2026-01-01" in txt2
            and "2026-07-21" in txt3
            and "Notre-Dame" in txt4
        )
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T4.2",
            "Scénario 2 : Signification technologique et calendrier de rigueur (C.p.c.)",
            "all",
            ok,
            elapsed,
            None if ok else f"Résultat calendrier inattendu : {txt3}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T4.2", "Scénario 2 : Notification technologique", "all", False, elapsed, str(ex))

    # --- Scénario 3 : Diagnostic de citation et vérification d'autorité CanLII ---
    t0 = time.perf_counter()
    try:
        # Étape 1 : Analyse syntaxique hors ligne
        r1 = client.call_tool("juris", "parse_citation", {"citation": "2020 QCCA 495"})
        txt1 = r1.get("content", [{}])[0].get("text", "")
        # Étape 2 : Vérification en ligne
        r2 = client.call_tool(
            "juris", "verify_citations", {"citations": [{"citation": "2020 QCCA 495"}]}
        )
        txt2 = r2.get("content", [{}])[0].get("text", "")
        # Étape 3 : Sort ultérieur
        r3 = client.call_tool("juris", "subsequent_history", {"citation": "2020 QCCA 495"})
        txt3 = r3.get("content", [{}])[0].get("text", "")
        # Étape 4 : Fiche CanLII complète
        r4 = client.call_tool("juris", "get_case", {"citation": "2020 QCCA 495"})
        txt4 = r4.get("content", [{}])[0].get("text", "")

        ok = (
            "qcca" in txt1.lower()
            and "confirmée" in txt2.lower()
            and not r3.get("isError")
            and len(txt3) > 0
            and "deguise" in txt4.lower()
        )
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T4.3",
            "Scénario 3 : Diagnostic de citation et vérification d'autorité CanLII",
            "juris",
            ok,
            elapsed,
            None if ok else "Échec de validation de la citation 2020 QCCA 495",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T4.3", "Scénario 3 : Citation CanLII", "juris", False, elapsed, str(ex))

    # --- Scénario 4 : Recherche textuelle et exploration réglementaire ---
    t0 = time.perf_counter()
    try:
        # Étape 1 : Recherche FTS5 sur prescription
        r1 = client.call_tool(
            "lois",
            "search_text",
            {"query": "prescription dommage corporel", "law": "ccq", "limit": 3},
        )
        txt1 = r1.get("content", [{}])[0].get("text", "")
        # Étape 2 : Texte complet de la division (Livre VIII — De la prescription)
        r2 = client.call_tool(
            "lois", "get_division", {"law": "ccq", "path": "ga:l_huitieme-gb:l_troisieme"}
        )
        txt2 = r2.get("content", [{}])[0].get("text", "")
        # Étape 3 : Exploration des règlements pris en application du CPC
        r3 = client.call_tool("lois", "related_laws", {"law": "cpc", "rel_type": "reglement-de"})
        txt3 = r3.get("content", [{}])[0].get("text", "")

        ok = "2930" in txt1 and "prescription" in txt2.lower() and "cour supérieure" in txt3.lower()
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T4.4",
            "Scénario 4 : Recherche textuelle et exploration réglementaire (C.c.Q. / C.p.c.)",
            "lois",
            ok,
            elapsed,
            None if ok else "Échec dans le scénario 4 de recherche",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T4.4", "Scénario 4 : Recherche réglementaire", "lois", False, elapsed, str(ex))

    return results


# ============================================================================
# Palier 5 : Durcissement contradictoire & sécurité (Adversarial Hardening)
# ============================================================================


def run_tier_5_tests(client: UnifiedMcpClient, target_server: str) -> List[TestResult]:
    """Exécute les tests de durcissement contradictoire du Palier 5 (Challengers 1 & 2)."""
    results: List[TestResult] = []

    def add_result(
        tid: str, name: str, srv: str, passed: bool, ms: float, err: Optional[str] = None
    ):
        results.append(TestResult(tid, name, 5, srv, passed, ms, err))

    # T5.1.1 : S8 Stealth non-oracle sur Législation & Jurisprudence (méthode non autorisée sans authentification -> 404)
    if target_server in ("all", "lois"):
        t0 = time.perf_counter()
        try:
            status, _, _ = client.send_http(
                "lois",
                path="/mcp",
                method="DELETE",
                body_data=b"",
                auth_token="OMIT",
            )
            ok = status == 404
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T5.1.1",
                "S8 Stealth non-oracle : DELETE non authentifié rend 404 sur lois (non 405)",
                "lois",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status} au lieu de 404",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T5.1.1", "S8 Stealth non-oracle lois", "lois", False, elapsed, str(ex))

    if target_server in ("all", "juris"):
        t0 = time.perf_counter()
        try:
            status, _, _ = client.send_http(
                "juris",
                path="/mcp",
                method="DELETE",
                body_data=b"",
                auth_token="OMIT",
            )
            ok = status == 404
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T5.1.1b",
                "S8 Stealth non-oracle : DELETE non authentifié rend 404 sur juris (non 405)",
                "juris",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status} au lieu de 404",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T5.1.1b", "S8 Stealth non-oracle juris", "juris", False, elapsed, str(ex))

    # T5.1.2 : Host Header Security whitelist (rejet DNS rebinding sur domaines non autorisés -> 403)
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            status_bad1, _, _ = client.send_http(
                "outils",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                extra_headers={"Host": "attacker.com"},
            )
            status_bad2, _, _ = client.send_http(
                "outils",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                extra_headers={"Host": "evil-outils.poirierlavoie.ca"},
            )
            status_good, _, _ = client.send_http(
                "outils",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                extra_headers={"Host": "outils.poirierlavoie.ca"},
            )
            ok = status_bad1 == 403 and status_bad2 == 403 and status_good == 200
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T5.1.2",
                "Protection DNS re-binding Host header whitelist stricte (rejet 403)",
                "outils",
                ok,
                elapsed,
                None if ok else f"Statuts reçus: bad1={status_bad1}, bad2={status_bad2}, good={status_good}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T5.1.2", "Host header whitelist", "outils", False, elapsed, str(ex))

    # T5.1.3 : Rejet des identifiants JSON-RPC structurés (objets/tableaux code -32600)
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            _, _, body_obj = client.send_http(
                "outils",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":{"bad":"object"},"method":"initialize"}',
                extra_headers={"Host": "outils.poirierlavoie.ca"},
            )
            res_obj = json.loads(body_obj.decode("utf-8"))
            err_code_obj = res_obj.get("error", {}).get("code")

            _, _, body_arr = client.send_http(
                "outils",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":["bad","array"],"method":"initialize"}',
                extra_headers={"Host": "outils.poirierlavoie.ca"},
            )
            res_arr = json.loads(body_arr.decode("utf-8"))
            err_code_arr = res_arr.get("error", {}).get("code")

            ok = err_code_obj == -32600 and err_code_arr == -32600
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T5.1.3",
                "Rejet JSON-RPC 2.0 §4.1 des id structurés (objet/tableau -> code -32600)",
                "outils",
                ok,
                elapsed,
                None if ok else f"Codes reçus: obj={err_code_obj}, arr={err_code_arr}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T5.1.3", "Rejet JSON-RPC id structuré", "outils", False, elapsed, str(ex))

    # T5.1.4 : Support CORS Preflight OPTIONS (/mcp -> HTTP 204 No Content)
    if target_server in ("all", "lois", "outils"):
        t0 = time.perf_counter()
        try:
            cors_headers = {
                "Origin": "https://claude.ai",
                "Access-Control-Request-Method": "POST",
            }
            status_leg, hdrs_leg, _ = client.send_http(
                "lois",
                path="/mcp",
                method="OPTIONS",
                body_data=b"",
                extra_headers=cors_headers,
                auth_token="OMIT",
            )
            status_out, hdrs_out, _ = client.send_http(
                "outils",
                path="/mcp",
                method="OPTIONS",
                body_data=b"",
                extra_headers=cors_headers,
            )
            hdrs_leg_l = {k.lower(): v for k, v in hdrs_leg.items()}
            hdrs_out_l = {k.lower(): v for k, v in hdrs_out.items()}
            ok_leg = status_leg == 204 and "POST, OPTIONS" in hdrs_leg_l.get("access-control-allow-methods", "")
            ok_out = status_out == 204 and "POST, OPTIONS" in hdrs_out_l.get("access-control-allow-methods", "")
            ok = ok_leg and ok_out
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T5.1.4",
                "Support CORS Preflight OPTIONS sans porteur (HTTP 204 No Content)",
                "all",
                ok,
                elapsed,
                None if ok else f"Statuts reçus: leg={status_leg}, out={status_out}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T5.1.4", "CORS Preflight OPTIONS", "all", False, elapsed, str(ex))

    # T5.1.5 : Parité statutaire art. 111 al. 2 C.p.c. (17h00 -> pas de report, 17h01 -> report, 16h59 -> pas de report)
    if target_server in ("all", "outils"):
        t0 = time.perf_counter()
        try:
            # 17:00 pile un vendredi -> NE DOIT PAS basculer (ancre reste 2026-07-03)
            r_1700 = client.call_tool(
                "outils",
                "calendrier_deadlines",
                {
                    "event_date": "2026-07-03",
                    "event_time": "17:00",
                    "notification_mode": "technological",
                    "regime": "qc_cpc",
                    "deadlines": [{"label": "Seuil 17h00", "amount": 1, "unit": "days"}],
                },
            )
            item_1700 = ((r_1700.get("structuredContent") or {}).get("results") or [{}])[0]
            anchor_1700 = item_1700.get("effective_anchor_date") or item_1700.get("anchor_date")
            not_shifted_1700 = anchor_1700 == "2026-07-03" and not bool(item_1700.get("anchor_shifted_art_111", False))

            # 17:01 un vendredi -> DOIT basculer au lundi suivant (2026-07-06)
            r_1701 = client.call_tool(
                "outils",
                "calendrier_deadlines",
                {
                    "event_date": "2026-07-03",
                    "event_time": "17:01",
                    "notification_mode": "technological",
                    "regime": "qc_cpc",
                    "deadlines": [{"label": "Après 17h00", "amount": 1, "unit": "days"}],
                },
            )
            item_1701 = ((r_1701.get("structuredContent") or {}).get("results") or [{}])[0]
            anchor_1701 = item_1701.get("effective_anchor_date") or item_1701.get("anchor_date")
            shifted_1701 = anchor_1701 == "2026-07-06" and bool(item_1701.get("anchor_shifted_art_111", False))

            # 16:59 un vendredi -> NE DOIT PAS basculer (ancre reste 2026-07-03)
            r_1659 = client.call_tool(
                "outils",
                "calendrier_deadlines",
                {
                    "event_date": "2026-07-03",
                    "event_time": "16:59",
                    "notification_mode": "technological",
                    "regime": "qc_cpc",
                    "deadlines": [{"label": "Avant 17h00", "amount": 1, "unit": "days"}],
                },
            )
            item_1659 = ((r_1659.get("structuredContent") or {}).get("results") or [{}])[0]
            anchor_1659 = item_1659.get("effective_anchor_date") or item_1659.get("anchor_date")
            not_shifted_1659 = anchor_1659 == "2026-07-03" and not bool(item_1659.get("anchor_shifted_art_111", False))

            ok = not_shifted_1700 and shifted_1701 and not_shifted_1659
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T5.1.5",
                "Bascule statutaire art. 111 al. 2 C.p.c. (17h00 -> pas de report, 17h01 -> report, 16h59 -> pas de report)",
                "outils",
                ok,
                elapsed,
                None if ok else f"17h00 anchor={anchor_1700}, 17h01 anchor={anchor_1701}, 16h59 anchor={anchor_1659}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T5.1.5", "Bascule art. 111 C.p.c. 17h00", "outils", False, elapsed, str(ex))

    return results


# ============================================================================
# Rendu des rapports (Terminal, JSON, GitHub Actions)
# ============================================================================


def format_report_terminal(
    results: List[TestResult], mode: str, total_duration_s: float
) -> str:
    """Génère un tableau de rapport lisible et coloré pour la console."""
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("  DROIT CIVIL QUÉBÉCOIS — VÉRIFICATEUR E2E MULTI-PALIERS")
    lines.append(f"  Mode d'exécution : {mode.upper()} | Date : {datetime.datetime.now().isoformat()}")
    lines.append("=" * 80)

    # Regroupement par palier
    by_tier: Dict[int, List[TestResult]] = {1: [], 2: [], 3: [], 4: [], 5: []}
    for r in results:
        by_tier.setdefault(r.tier, []).append(r)

    tier_names = {
        1: "Palier 1 : Couverture fonctionnelle (Manifestes, Handshakes, 35 outils)",
        2: "Palier 2 : Limites & Négatifs (Auth 401/404, Headers, JSON-RPC, Schémas)",
        3: "Palier 3 : Compatibilité inter-plateformes (Claude, Gemini, Antigravity)",
        4: "Palier 4 : Scénarios réels de litige civil québécois (Workflows)",
        5: "Palier 5 : Durcissement contradictoire & sécurité (Adversarial Hardening)",
    }

    for tier_idx in (1, 2, 3, 4, 5):
        tier_results = by_tier.get(tier_idx, [])
        if not tier_results:
            continue
        lines.append(f"\n[+] {tier_names.get(tier_idx, f'Palier {tier_idx}')}")
        lines.append("-" * 80)
        lines.append(f"{'ID':<8} {'Statut':<8} {'Durée':<10} {'Description':<52}")
        lines.append("-" * 80)
        for r in tier_results:
            stat_str = "IGNORÉ" if r.skipped else ("SUCCÈS" if r.passed else "ÉCHEC")
            dur_str = f"{r.duration_ms:.1f}ms"
            desc = r.name[:50]
            lines.append(f"{r.test_id:<8} {stat_str:<8} {dur_str:<10} {desc:<52}")
            if not r.passed and not r.skipped and r.error_message:
                lines.append(f"         └─ ERREUR : {r.error_message}")

    total_count = len(results)
    skipped_count = sum(1 for r in results if r.skipped)
    passed_count = sum(1 for r in results if r.passed and not r.skipped)
    executed_count = total_count - skipped_count
    succ_rate = (passed_count / executed_count * 100) if executed_count else 0.0

    skip_note = f", {skipped_count} ignoré(s)" if skipped_count else ""
    lines.append("\n" + "=" * 80)
    lines.append(
        f"  BILAN FINAL : {passed_count}/{executed_count} tests exécutés réussis ({succ_rate:.1f}%{skip_note}) en {total_duration_s:.2f}s"
    )
    lines.append("=" * 80 + "\n")
    return "\n".join(lines)


def format_report_json(
    results: List[TestResult], mode: str, total_duration_s: float
) -> str:
    """Génère un rapport JSON structuré pour intégration machine."""
    skipped_count = sum(1 for r in results if r.skipped)
    passed_count = sum(1 for r in results if r.passed and not r.skipped)
    failed_count = sum(1 for r in results if not r.passed and not r.skipped)
    executed_count = len(results) - skipped_count
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "mode": mode,
        "total_duration_s": total_duration_s,
        "summary": {
            "total": len(results),
            "executed": executed_count,
            "passed": passed_count,
            "skipped": skipped_count,
            "failed": failed_count,
            "success_rate_percent": (passed_count / executed_count * 100) if executed_count else 0.0,
        },
        "tests": [
            {
                "id": r.test_id,
                "name": r.name,
                "tier": r.tier,
                "server": r.server,
                "passed": r.passed,
                "skipped": r.skipped,
                "duration_ms": r.duration_ms,
                "error": r.error_message,
            }
            for r in results
        ],
    }
    return json.dumps(report, indent=2, ensure_ascii=False)


def format_report_github(
    results: List[TestResult], mode: str, total_duration_s: float
) -> str:
    """Génère les annotations GitHub Actions (::notice::, ::error::)."""
    lines = []
    for r in results:
        if r.skipped:
            lines.append(f"::notice title={r.test_id}::[{r.test_id}] {r.name} - IGNORÉ")
        elif r.passed:
            lines.append(f"::notice title={r.test_id}::[{r.test_id}] {r.name} - SUCCÈS ({r.duration_ms:.1f}ms)")
        else:
            lines.append(f"::error title={r.test_id}::[{r.test_id}] {r.name} - ÉCHEC : {r.error_message}")

    skipped = sum(1 for r in results if r.skipped)
    passed = sum(1 for r in results if r.passed and not r.skipped)
    executed = len(results) - skipped
    skip_note = f", {skipped} ignoré(s)" if skipped else ""
    lines.append(f"::notice title=Bilan::Vérification E2E ({mode}) terminée : {passed}/{executed} tests exécutés réussis{skip_note} en {total_duration_s:.2f}s")
    return "\n".join(lines)


# ============================================================================
# Point d'entrée principal (CLI)
# ============================================================================


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Vérificateur multi-paliers E2E pour droit-civil-quebecois",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "mock", "live"],
        default="auto",
        help="Mode d'exécution : auto (détecte secrets), mock (simulation locale 100%%), live (Cloudflare réel)",
    )
    parser.add_argument(
        "--tier",
        choices=["1", "2", "3", "4", "5", "all"],
        default="all",
        help="Cibler un palier de test spécifique ou tous les paliers",
    )
    parser.add_argument(
        "--server",
        choices=["lois", "juris", "outils", "all"],
        default="all",
        help="Filtrer les tests par serveur MCP",
    )
    parser.add_argument(
        "--format",
        choices=["terminal", "json", "github"],
        default="terminal",
        help="Format de sortie du rapport",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Délai d'attente réseau en secondes pour le mode live",
    )
    parser.add_argument(
        "--check-linters",
        action="store_true",
        help="Exécute les linters et vérificateurs statiques additionnels si disponibles",
    )
    parser.add_argument(
        "--require-antigravity-cache",
        action="store_true",
        help="Exige la présence et l'intégrité du cache Antigravity (~/.gemini/antigravity/mcp/) et échoue s'il est absent",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Affiche les détails détaillés d'exécution",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent

    # Filtre de serveur MCP
    server_filter = args.server

    # Validation CLI en mode live forcé sans variables
    if args.mode == "live":
        leg_sec = os.environ.get("MCP_LEGISLATION_SECRET")
        jur_sec = os.environ.get("MCP_JURISPRUDENCE_SECRET")
        if not leg_sec or not jur_sec:
            sys.stderr.write(
                "Erreur de configuration (code 2) : Le mode --mode live exige les variables "
                "d'environnement MCP_LEGISLATION_SECRET et MCP_JURISPRUDENCE_SECRET.\n"
            )
            return 2

    # Instanciation du client MCP unifié
    try:
        client = UnifiedMcpClient(mode=args.mode, timeout=args.timeout, verbose=args.verbose)
    except Exception as ex:
        sys.stderr.write(f"Erreur d'initialisation du client MCP (code 2) : {ex}\n")
        return 2

    if args.verbose or args.format == "terminal":
        print(f"[*] Démarrage de la vérification E2E (Moteur effectif : {client.effective_mode.upper()})...")

    t_start = time.perf_counter()
    all_results: List[TestResult] = []

    # Exécution des paliers sélectionnés
    tiers_to_run = [1, 2, 3, 4, 5] if args.tier == "all" else [int(args.tier)]

    try:
        if 1 in tiers_to_run:
            all_results.extend(run_tier_1_tests(client, repo_root, server_filter))
        if 2 in tiers_to_run:
            all_results.extend(run_tier_2_tests(client, server_filter))
        if 3 in tiers_to_run:
            all_results.extend(
                run_tier_3_tests(
                    client,
                    repo_root,
                    server_filter,
                    require_antigravity_cache=args.require_antigravity_cache,
                )
            )
        if 4 in tiers_to_run:
            all_results.extend(run_tier_4_tests(client))
        if 5 in tiers_to_run:
            all_results.extend(run_tier_5_tests(client, server_filter))
    except ConnectionError as conn_err:
        sys.stderr.write(f"\n[!] Défaillance réseau ou infrastructure live (code 3) : {conn_err}\n")
        return 3
    except Exception as fatal_err:
        sys.stderr.write(f"\n[!] Erreur inattendue durant les tests : {fatal_err}\n")
        return 1

    total_duration_s = time.perf_counter() - t_start

    # Rendu du rapport selon le format choisi
    if args.format == "terminal":
        print(format_report_terminal(all_results, client.effective_mode, total_duration_s))
    elif args.format == "json":
        print(format_report_json(all_results, client.effective_mode, total_duration_s))
    elif args.format == "github":
        print(format_report_github(all_results, client.effective_mode, total_duration_s))

    # Évaluation du code de sortie avec filet de sécurité supplémentaire
    if client.effective_mode == "live" and client.has_infra_failure:
        sys.stderr.write(f"\n[!] Défaillance réseau ou infrastructure live (code 3) : {client.last_infra_error}\n")
        return 3

    has_failure = any(not r.passed and not r.skipped for r in all_results)
    return 1 if has_failure else 0


if __name__ == "__main__":
    sys.exit(main())
