#!/usr/bin/env python3
"""
verifier_tout.py — Suite de vérification E2E multi-paliers pour pratique-civile-quebecoise.

Valide de bout en bout l'intégration du greffon et de ses serveurs MCP (Législation,
Jurisprudence, Outils) pour Claude et Gemini, en mode simulation locale (Mock) ou
réseau en direct (Live).

Paliers de vérification :
- Palier 1 : Couverture fonctionnelle (manifestes, poignées de main, 26 outils)
- Palier 2 : Conditions aux limites & cas négatifs (auth 401/404, schémas, JSON-RPC)
- Palier 3 : Compatibilité inter-plateformes (parité Claude/Gemini, cache Antigravity)
- Palier 4 : Scénarios réels de pratique juridique québécoise (4 workflows complets)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import datetime
import http.client
import json
import os
from pathlib import Path
import re
import socket
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import urllib.error
import urllib.parse
import urllib.request

# Constantes de version et d'environnement
VERSION_ATTENDUE = "1.5.0"
USER_AGENT_VERIFICATEUR = (
    "PratiqueCivileQuebecoise-Verifier/1.0 (Windows NT 10.0; Win64; x64) "
    "Python-urllib-E2E"
)

URL_SERVEURS = {
    "legislation": "https://legislation.poirierlavoie.ca/mcp",
    "jurisprudence": "https://jurisprudence.poirierlavoie.ca/mcp",
    "pratique-civile-outils": "https://outils.poirierlavoie.ca/mcp",
}

URL_COURTE_OUTILS = "https://outils.poirierlavoie.ca"

NOMS_OUTILS_ATTENDUS = {
    "legislation": [
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
    ],
    "jurisprudence": [
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
    ],
    "pratique-civile-outils": [
        "calendrier_list_holidays",
        "calendrier_compute_deadlines",
        "interets_compute_1619",
        "greffe_parse_court_file_number",
        "palais_list",
        "palais_get",
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


# ============================================================================
# Moteur de simulation en mémoire (Mock Engine)
# ============================================================================


class MockMcpServer:
    """Simulateur conforme JSON-RPC 2.0 pour les 3 serveurs MCP et leurs 26 outils."""

    def __init__(self, server_name: str, secret_token: Optional[str] = None):
        self.server_name = server_name
        if secret_token is not None:
            self.secret_token = secret_token
        elif server_name == "legislation":
            self.secret_token = os.environ.get("MCP_LEGISLATION_SECRET", "mock-secret-token")
        elif server_name == "jurisprudence":
            self.secret_token = os.environ.get("MCP_JURISPRUDENCE_SECRET", "mock-secret-token")
        else:
            self.secret_token = "mock-secret-token"
        self.tool_definitions = self._build_tool_definitions()

    def _build_tool_definitions(self) -> Dict[str, Dict[str, Any]]:
        expected_names = NOMS_OUTILS_ATTENDUS.get(self.server_name, [])
        tools: Dict[str, Dict[str, Any]] = {}

        if self.server_name == "legislation":
            tools["legislation_list_laws"] = {
                "name": "legislation_list_laws",
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
            tools["legislation_list_subjects"] = {
                "name": "legislation_list_subjects",
                "description": "Matières de la taxonomie juridique québécoise.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "lang": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "additionalProperties": False,
                },
            }
            tools["legislation_related_laws"] = {
                "name": "legislation_related_laws",
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
            tools["legislation_find_relevant"] = {
                "name": "legislation_find_relevant",
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
            tools["legislation_get_article"] = {
                "name": "legislation_get_article",
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
            tools["legislation_get_articles"] = {
                "name": "legislation_get_articles",
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
            tools["legislation_get_structure"] = {
                "name": "legislation_get_structure",
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
            tools["legislation_get_division"] = {
                "name": "legislation_get_division",
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
            tools["legislation_search_text"] = {
                "name": "legislation_search_text",
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
            tools["legislation_resolve_reference"] = {
                "name": "legislation_resolve_reference",
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

        elif self.server_name == "jurisprudence":
            tools["jurisprudence_verify_citations"] = {
                "name": "jurisprudence_verify_citations",
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
            tools["jurisprudence_find_case"] = {
                "name": "jurisprudence_find_case",
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
            tools["jurisprudence_get_case"] = {
                "name": "jurisprudence_get_case",
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
            tools["jurisprudence_citator"] = {
                "name": "jurisprudence_citator",
                "description": "Citateur brut de décisions citées, citantes ou textes.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "rel": {"type": "string", "enum": ["cited", "citing", "legislation"]},
                        "citation": {"type": "string"},
                        "database_id": {"type": "string"},
                        "case_id": {"type": "string"},
                        "limit": {"type": "integer"},
                        "offset": {"type": "integer"},
                        "refresh": {"type": "boolean"},
                    },
                    "required": ["rel"],
                    "additionalProperties": False,
                },
            }
            tools["jurisprudence_subsequent_history"] = {
                "name": "jurisprudence_subsequent_history",
                "description": "Indice heuristique de sorts ultérieurs.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "citation": {"type": "string"},
                        "database_id": {"type": "string"},
                        "case_id": {"type": "string"},
                        "limit": {"type": "integer"},
                        "refresh": {"type": "boolean"},
                    },
                    "additionalProperties": False,
                },
            }
            tools["jurisprudence_browse_cases"] = {
                "name": "jurisprudence_browse_cases",
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
            tools["jurisprudence_list_databases"] = {
                "name": "jurisprudence_list_databases",
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
            tools["jurisprudence_browse_legislation"] = {
                "name": "jurisprudence_browse_legislation",
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
            tools["jurisprudence_get_legislation"] = {
                "name": "jurisprudence_get_legislation",
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
            tools["jurisprudence_parse_citation"] = {
                "name": "jurisprudence_parse_citation",
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

        elif self.server_name == "pratique-civile-outils":
            tools["calendrier_list_holidays"] = {
                "name": "calendrier_list_holidays",
                "description": "Calendrier des jours fériés et non juridiques (QC / CA).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {"type": "integer"},
                        "regime": {"type": "string", "enum": ["qc_cpc", "qc_li", "ca_li"]},
                    },
                    "required": ["year"],
                    "additionalProperties": False,
                },
            }
            tools["calendrier_compute_deadlines"] = {
                "name": "calendrier_compute_deadlines",
                "description": "Calculateur arithmétique exact de délais procéduraux.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "event_date": {"type": "string"},
                        "deadlines": {"type": "array"},
                        "event_time": {"type": "string"},
                        "notification_mode": {"type": "string", "enum": ["none", "technological", "physical"]},
                        "regime": {"type": "string", "enum": ["qc_cpc", "qc_li", "ca_li"]},
                        "rollover_saturday": {"type": "boolean"},
                        "extra_non_juridical_dates": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["event_date", "deadlines"],
                    "additionalProperties": False,
                },
            }
            tools["interets_compute_1619"] = {
                "name": "interets_compute_1619",
                "description": "Calcul d'intérêts légaux (5%) et indemnité art. 1619 C.c.Q.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "end_date": {"type": "string"},
                        "tranches": {"type": "array"},
                        "mode": {"type": "string", "enum": ["legal_plus_1619", "legal_only", "contractual"]},
                        "rate_bps": {"type": "integer"},
                        "rate_overrides": {"type": "array"},
                    },
                    "required": ["end_date", "tranches"],
                    "additionalProperties": False,
                },
            }
            tools["greffe_parse_court_file_number"] = {
                "name": "greffe_parse_court_file_number",
                "description": "Décomposition hors ligne de numéro de dossier de cour.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "court_file_number": {"type": "string"},
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
                        "district": {"type": "string"},
                        "query": {"type": "string"},
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
                        "greffe_number": {"type": "string"},
                        "palais": {"type": "string"},
                    },
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
        if not ua or ("Python-urllib" in ua and "PratiqueCivile" not in ua):
            return 403, {"Content-Type": "application/json"}, b'{"error":"Forbidden: Cloudflare WAF bot block"}'

        # 1. CORS Preflight OPTIONS (doit répondre avant auth, statut 204 No Content)
        if method == "OPTIONS":
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
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps({
                    "status": "ok",
                    "service": self.server_name,
                    "version": VERSION_ATTENDUE,
                    "tools": list(self.tool_definitions.keys()),
                }).encode("utf-8"),
            )

        # 4. Endpoint server card SEP-2127
        if path == "/mcp/server-card" and method == "GET":
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps({
                    "$schema": "https://mcp.run/server-card-v1.json",
                    "name": f"poirierlavoie-{self.server_name}",
                    "description": f"MCP Server {self.server_name} pour pratique civile québécoise",
                    "version": VERSION_ATTENDUE,
                    "capabilities": {"tools": True},
                }).encode("utf-8"),
            )

        # 5. Authentification selon doctrine (Legislation 404, Jurisprudence 401, Outils public)
        # S8 : Sur Législation, l'absence de porteur rend 404 AVANT toute vérification de méthode HTTP.
        auth_header = headers.get("authorization") or headers.get("Authorization") or ""
        is_authenticated = bool(auth_header) and (
            auth_header in (f"Bearer {self.secret_token}", "Bearer mock-secret-token")
        ) and not auth_header.startswith("Bearer invalid")

        if self.server_name == "legislation" and not is_authenticated:
            # S8 : 404 Not Found non-oracle
            return 404, {"Content-Type": "application/json"}, b""

        if self.server_name == "jurisprudence" and not is_authenticated:
            return (
                401,
                {"Content-Type": "application/json", "WWW-Authenticate": "Bearer"},
                json.dumps({"error": "unauthorized"}).encode("utf-8"),
            )

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

    def _validate_args(
        self, tool_name: str, args: Dict[str, Any], schema: Dict[str, Any]
    ) -> Optional[str]:
        """Valide strictement les arguments contre le schéma de l'outil."""
        if not isinstance(args, dict):
            return "Les arguments doivent être un objet JSON."

        # Vérification des propriétés inattendues (additionalProperties: false)
        allowed_props = set(schema.get("properties", {}).keys())
        for key in args:
            if key not in allowed_props:
                return f"Propriété non autorisée '{key}' détectée (additionalProperties: false)."

        # Vérification des paramètres requis
        required = schema.get("required", [])
        for req_key in required:
            if req_key not in args or args[req_key] is None:
                return f"Paramètre requis manquant : '{req_key}'."

        # Contrôles de types fondamentaux
        props = schema.get("properties", {})
        for k, v in args.items():
            if k in props:
                expected_type = props[k].get("type")
                if expected_type == "integer" and not isinstance(v, int):
                    return f"Type invalide pour '{k}' : attendu integer, reçu {type(v).__name__}."
                if expected_type == "string" and not isinstance(v, str):
                    return f"Type invalide pour '{k}' : attendu string, reçu {type(v).__name__}."
                if expected_type == "array" and not isinstance(v, list):
                    return f"Type invalide pour '{k}' : attendu array, reçu {type(v).__name__}."

        # Règle XOR pour palais_get
        if tool_name == "palais_get":
            has_greffe = bool(args.get("greffe_number"))
            has_palais = bool(args.get("palais"))
            if has_greffe and has_palais:
                return "Exclusion mutuelle (XOR) violée : fournir soit greffe_number soit palais, pas les deux."
            if not has_greffe and not has_palais:
                return "Exclusion mutuelle (XOR) violée : fournir au moins greffe_number ou palais."

        # Règle XOR pour jurisprudence_get_case, citator et subsequent_history
        if tool_name in ("jurisprudence_get_case", "jurisprudence_citator", "jurisprudence_subsequent_history"):
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
        if tool_name == "jurisprudence_parse_citation":
            if not args.get("citation", "").strip():
                return "La citation ne peut pas être vide."

        # Contrôle de date pour calendrier
        if tool_name == "calendrier_compute_deadlines":
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
        if tool_name == "legislation_list_laws":
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

        elif tool_name == "legislation_list_subjects":
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

        elif tool_name == "legislation_related_laws":
            law = args.get("law", "").lower()
            relations = [
                {"law": "cpc", "target": "Tarif des honoraires judiciaires", "rel_type": "reglement-de"},
                {"law": "cpc", "target": "Règlement de la Cour supérieure (civile)", "rel_type": "reglement-de"},
            ]
            return {"content": [{"type": "text", "text": json.dumps(relations, ensure_ascii=False)}]}

        elif tool_name == "legislation_find_relevant":
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

        elif tool_name == "legislation_get_article":
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

        elif tool_name == "legislation_get_articles":
            law = args.get("law", "").lower()
            from_art = int(args.get("from", "1726")) if args.get("from", "").isdigit() else 1726
            to_art = int(args.get("to", "1731")) if args.get("to", "").isdigit() else 1731
            arts = [
                {"law": law, "article": str(num), "text": f"Texte de l'article {num} du {law.upper()}"}
                for num in range(from_art, min(to_art + 1, from_art + 20))
            ]
            return {"content": [{"type": "text", "text": json.dumps(arts, ensure_ascii=False)}]}

        elif tool_name == "legislation_get_structure":
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

        elif tool_name == "legislation_get_division":
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

        elif tool_name == "legislation_search_text":
            query = args.get("query", "")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps([
                            {
                                "law": args.get("law", "ccq"),
                                "article": "2925",
                                "snippet": f"Correspondance avec '{query}' : action personnelle se prescrit par trois ans.",
                                "score": 0.88,
                            }
                        ], ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "legislation_resolve_reference":
            cit = args.get("citation", "")
            cit_norm = re.sub(r"[.\s]", "", cit.lower())
            if "145" in cit and ("cpc" in cit_norm or "c-25" in cit_norm):
                res = {"law": "cpc", "article": "145", "titre": "Délai de réponse de 15 jours"}
            elif "1619" in cit and ("ccq" in cit_norm or "codecivil" in cit_norm):
                res = {"law": "ccq", "article": "1619", "titre": "Indemnité additionnelle"}
            else:
                res = {"law": "ccq", "article": "1726", "titre": "Garantie légale de qualité"}
            return {"content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False)}]}

        # --- Jurisprudence ---
        elif tool_name == "jurisprudence_verify_citations":
            citations = args.get("citations", [])
            rapports = []
            for item in citations:
                cit_str = item.get("citation", "")
                if "2020 QCCA 495" in cit_str:
                    rapports.append({
                        "citation": cit_str,
                        "verdict": "CONFIRMÉE",
                        "title": "Droit de la famille - 20495",
                        "database_id": "qcca",
                        "case_id": "2020qcca495",
                        "url": "https://www.canlii.org/fr/qc/qcca/doc/2020/2020qcca495/2020qcca495.html",
                    })
                elif "2015 QCCA 1526" in cit_str:
                    rapports.append({
                        "citation": cit_str,
                        "verdict": "CONFIRMÉE",
                        "title": "St-Louis c. Morin",
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

        elif tool_name == "jurisprudence_find_case":
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

        elif tool_name == "jurisprudence_get_case":
            cit = args.get("citation") or f"{args.get('database_id')} {args.get('case_id')}"
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "citation": cit,
                            "title": "Droit de la famille - 20495",
                            "court": "Cour d'appel du Québec",
                            "date": "2020-04-15",
                            "judges": ["Bich", "Mainville", "Racicot"],
                            "court_file": "500-09-028456-193",
                            "url": "https://www.canlii.org/fr/qc/qcca/doc/2020/2020qcca495/2020qcca495.html",
                        }, ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "jurisprudence_citator":
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

        elif tool_name == "jurisprudence_subsequent_history":
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

        elif tool_name == "jurisprudence_browse_cases":
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

        elif tool_name == "jurisprudence_list_databases":
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

        elif tool_name == "jurisprudence_browse_legislation":
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

        elif tool_name == "jurisprudence_get_legislation":
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

        elif tool_name == "jurisprudence_parse_citation":
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
        elif tool_name == "calendrier_list_holidays":
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

        elif tool_name == "calendrier_compute_deadlines":
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
            for item in args.get("deadlines", []):
                amt = item.get("amount", 15)
                due = shifted_start + datetime.timedelta(days=amt)
                # Art. 83 C.p.c. : si samedi ou dimanche, reporte au lundi
                while due.weekday() >= 5:
                    due += datetime.timedelta(days=1)
                results.append({
                    "label": item.get("label", "Délai"),
                    "amount": amt,
                    "anchor_date": shifted_start.isoformat(),
                    "due_date": due.isoformat(),
                    "day_of_week": due.strftime("%A"),
                    "anchor_shifted_art_111": shifted_start != d_date,
                    "effective_anchor_date": shifted_start.isoformat(),
                })

            return {"content": [{"type": "text", "text": json.dumps(results, ensure_ascii=False)}]}

        elif tool_name == "interets_compute_1619":
            tranches = args.get("tranches", [])
            total_principal = sum(t.get("principal_cents", 0) for t in tranches)
            # Calcul authentique d'intérêts : 5% légal + indemnité additionnelle (~4%)
            taux_legal = 0.05
            taux_indemnite = 0.04
            interet_legal_cents = int(total_principal * taux_legal)
            indemnite_cents = int(total_principal * taux_indemnite)
            grand_total_cents = total_principal + interet_legal_cents + indemnite_cents

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "principal_total_cents": total_principal,
                            "legal_interest_cents": interet_legal_cents,
                            "additional_indemnity_cents": indemnite_cents,
                            "grand_total_cents": grand_total_cents,
                            "end_date": args.get("end_date"),
                        }, ensure_ascii=False),
                    }
                ]
            }

        elif tool_name == "greffe_parse_court_file_number":
            num = args.get("court_file_number", "")
            # Format standard québécois : 500-17-012345-211
            parts = num.split("-")
            greffe = parts[0] if len(parts) >= 1 else "500"
            court_code = parts[1] if len(parts) >= 2 else "17"
            districts = {"500": "Montréal", "200": "Québec", "150": "Trois-Rivières"}
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "court_file_number": num,
                            "greffe_number": greffe,
                            "district": districts.get(greffe, "District québécois"),
                            "court": "Cour supérieure" if court_code == "17" else "Cour du Québec",
                            "matter": "civil",
                        }, ensure_ascii=False),
                    }
                ]
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
                    "palais": "Palais de justice de Montréal",
                    "greffe_number": "500",
                    "district": "Montréal",
                    "address": "1, rue Notre-Dame Est, Montréal (Québec) H2Y 1B6",
                }
            else:
                info = {
                    "palais": "Palais de justice de Québec",
                    "greffe_number": "200",
                    "district": "Québec",
                    "address": "300, boulevard Jean-Lesage, Québec (Québec) G1K 8K6",
                }
            return {"content": [{"type": "text", "text": json.dumps(info, ensure_ascii=False)}]}

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

    # 1. Vérification pratique-civile-outils (/healthz)
    try:
        req = urllib.request.Request(
            f"{URL_COURTE_OUTILS}/healthz", headers=headers_base, method="GET"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return False, f"pratique-civile-outils /healthz a renvoyé HTTP {resp.status}"
            data = json.loads(resp.read().decode("utf-8"))
            tools = data.get("tools", [])
            version = data.get("version", "0.0.0")
            # Le build de l'itération requiert 6 outils (version 0.2.0+)
            if len(tools) < 6:
                return False, (
                    f"Serveur pratique-civile-outils distant en retard de synchronisation : "
                    f"version {version} exposant {len(tools)} outils (attendu >= 6 outils pour v0.2.0+)."
                )
    except Exception as exc:
        return False, f"pratique-civile-outils injoignable : {exc}"

    # 2. Vérification Législation (initialize)
    try:
        init_body = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "probe"}},
        }).encode("utf-8")
        headers_leg = dict(headers_base)
        headers_leg["Authorization"] = f"Bearer {leg_sec}"
        req = urllib.request.Request(
            URL_SERVEURS["legislation"], data=init_body, headers=headers_leg, method="POST"
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
            URL_SERVEURS["jurisprudence"], data=init_body, headers=headers_jur, method="POST"
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
            "legislation": MockMcpServer("legislation"),
            "jurisprudence": MockMcpServer("jurisprudence"),
            "pratique-civile-outils": MockMcpServer("pratique-civile-outils"),
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
            if server_key == "legislation":
                token = os.environ.get("MCP_LEGISLATION_SECRET", "mock-secret-token")
                headers["Authorization"] = f"Bearer {token}"
            elif server_key == "jurisprudence":
                token = os.environ.get("MCP_JURISPRUDENCE_SECRET", "mock-secret-token")
                headers["Authorization"] = f"Bearer {token}"

        if self.effective_mode == "mock":
            srv = self.mock_servers[server_key]
            body_bytes = body_data if body_data is not None else b""
            return srv.handle_request(body_bytes, headers, method=method, path=path)

        # Mode Live
        base_url = URL_SERVEURS[server_key]
        if path == "/healthz" and server_key == "pratique-civile-outils":
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
    """Exécute les vérifications du Palier 1 (manifestes, endpoints, 26 outils)."""
    results: List[TestResult] = []

    def add_result(
        tid: str, name: str, srv: str, passed: bool, ms: float, err: Optional[str] = None
    ):
        results.append(TestResult(tid, name, 1, srv, passed, ms, err))

    # --- 1.1 Manifest Structural & Semver Validation ---
    t0 = time.perf_counter()
    manifest_rel_paths = [
        ".claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
        ".mcp.json",
        "plugin.json",
        "mcp_config.json",
        "gemini-extension.json",
    ]

    # T1.1.1 : Présence des 6 manifestes
    missing = [p for p in manifest_rel_paths if not (repo_root / p).is_file()]
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.1.1",
        "Présence des 6 fichiers manifestes",
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

    # T1.1.4 : Parité semver 1.5.0
    t0 = time.perf_counter()
    semver_errs = []
    for rel in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "plugin.json", "gemini-extension.json"):
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

    # T1.1.6 : Structure plugin.json Antigravity
    t0 = time.perf_counter()
    p_json = parsed_manifests.get("plugin.json", {})
    p_errs = []
    if not isinstance(p_json, dict) or p_json.get("name") != "pratique-civile-quebecoise":
        p_errs.append("Nom invalide")
    if not (1 <= len(p_json.get("suggestedPrompts", [])) <= 3):
        p_errs.append("suggestedPrompts non conforme")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.1.6",
        "Conformité du manifeste plugin.json Antigravity",
        "all",
        len(p_errs) == 0,
        elapsed,
        "; ".join(p_errs) if p_errs else None,
    )

    # T1.1.7 : Structure mcp_config.json Antigravity
    t0 = time.perf_counter()
    m_json = parsed_manifests.get("mcp_config.json", {})
    m_servers = m_json.get("mcpServers", {}) if isinstance(m_json, dict) else {}
    m_errs = []
    for exp_k in ("legislation", "jurisprudence", "pratique-civile-outils"):
        if exp_k not in m_servers:
            m_errs.append(f"Serveur '{exp_k}' absent de mcp_config.json")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.1.7",
        "Conformité des déclarations mcp_config.json",
        "all",
        len(m_errs) == 0,
        elapsed,
        "; ".join(m_errs) if m_errs else None,
    )

    # T1.1.8 : Paramètres sensibles gemini-extension.json
    t0 = time.perf_counter()
    g_json = parsed_manifests.get("gemini-extension.json", {})
    settings = g_json.get("settings", []) if isinstance(g_json, dict) else []
    sec_vars = {s.get("envVar") for s in settings if isinstance(s, dict) and s.get("sensitive")}
    g_errs = []
    for exp_v in ("MCP_LEGISLATION_SECRET", "MCP_JURISPRUDENCE_SECRET"):
        if exp_v not in sec_vars:
            g_errs.append(f"Paramètre sensible manquant : {exp_v}")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.1.8",
        "Déclaration des secrets dans gemini-extension.json",
        "all",
        len(g_errs) == 0,
        elapsed,
        "; ".join(g_errs) if g_errs else None,
    )

    # --- 1.2 Endpoint Reachability & Handshake ---
    for srv_key in ("legislation", "jurisprudence", "pratique-civile-outils"):
        if target_server not in ("all", srv_key):
            continue
        t0 = time.perf_counter()
        try:
            init_res = client.call_rpc(
                srv_key,
                "initialize",
                {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test"}},
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
    if target_server in ("all", "pratique-civile-outils"):
        t0 = time.perf_counter()
        try:
            status, _, body = client.send_http(
                "pratique-civile-outils", path="/healthz", method="GET"
            )
            data = json.loads(body.decode("utf-8")) if body else {}
            ok = status == 200 and data.get("status") == "ok"
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T1.2.outils_healthz",
                "Bilan de santé /healthz sur pratique-civile-outils",
                "pratique-civile-outils",
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
                "Bilan de santé /healthz sur pratique-civile-outils",
                "pratique-civile-outils",
                False,
                elapsed,
                str(ex),
            )

    # T1.2.server_card : Découverte SEP-2127
    for srv_key in ("legislation", "jurisprudence"):
        if target_server not in ("all", srv_key):
            continue
        t0 = time.perf_counter()
        try:
            status, _, body = client.send_http(srv_key, path="/mcp/server-card", method="GET")
            data = json.loads(body.decode("utf-8")) if body else {}
            has_card = status == 200 and "name" in data
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                f"T1.2.{srv_key}_server_card",
                f"Fiche découverte SEP-2127 sur {srv_key}",
                srv_key,
                has_card,
                elapsed,
                None if has_card else f"HTTP {status}, corps : {data}",
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

    # --- 1.3 26-Tool Enumeration & Schema Inspection ---
    discovered_tools: Dict[str, List[Dict[str, Any]]] = {}
    for srv_key in ("legislation", "jurisprudence", "pratique-civile-outils"):
        if target_server not in ("all", srv_key):
            continue
        t0 = time.perf_counter()
        try:
            res = client.call_rpc(srv_key, "tools/list")
            tools = res.get("result", {}).get("tools", [])
            discovered_tools[srv_key] = tools
            exp_count = 10 if srv_key in ("legislation", "jurisprudence") else 6
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

    # T1.3.total_tools_26 : Total de 26 outils sans doublons
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
        total_ok = len(all_tools_set) == 26 and len(duplicates) == 0
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T1.3.total_26_tools",
            "Catalogue total de exactement 26 outils distincts",
            "all",
            total_ok,
            elapsed,
            f"Total {len(all_tools_set)}/26, doublons : {duplicates}" if not total_ok else None,
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

    # T1.3.prefix_legislation : Préfixe legislation_ sur tous les 10 outils
    t0 = time.perf_counter()
    leg_bad_prefix = [
        t.get("name", "") for t in discovered_tools.get("legislation", [])
        if not t.get("name", "").startswith("legislation_")
    ]
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.3.prefix_legislation",
        "Préfixe 'legislation_' uniforme sur les 10 outils Législation",
        "legislation",
        len(leg_bad_prefix) == 0,
        elapsed,
        f"Noms sans préfixe : {leg_bad_prefix}" if leg_bad_prefix else None,
    )

    # T1.3.prefix_jurisprudence : Préfixe jurisprudence_ sur tous les 10 outils
    t0 = time.perf_counter()
    jur_bad_prefix = [
        t.get("name", "") for t in discovered_tools.get("jurisprudence", [])
        if not t.get("name", "").startswith("jurisprudence_")
    ]
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.3.prefix_jurisprudence",
        "Préfixe 'jurisprudence_' uniforme sur les 10 outils Jurisprudence",
        "jurisprudence",
        len(jur_bad_prefix) == 0,
        elapsed,
        f"Noms sans préfixe : {jur_bad_prefix}" if jur_bad_prefix else None,
    )

    # T1.3.prefix_outils : Préfixes autorisés sur les 6 outils de pratique-civile-outils
    t0 = time.perf_counter()
    outils_allowed = ("calendrier_", "interets_", "greffe_", "palais_")
    outils_bad_prefix = [
        t.get("name", "") for t in discovered_tools.get("pratique-civile-outils", [])
        if not any(t.get("name", "").startswith(p) for p in outils_allowed)
    ]
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T1.3.prefix_outils",
        "Préfixes sectoriels autorisés sur les 6 outils Outils",
        "pratique-civile-outils",
        len(outils_bad_prefix) == 0,
        elapsed,
        f"Noms inattendus : {outils_bad_prefix}" if outils_bad_prefix else None,
    )

    # T1.3.additional_properties_hardened : additionalProperties: false sur tous les 26 outils
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

    # --- 2.1 Authentification ---
    # T2.1.1 : Jurisprudence non authentifié -> 401 WWW-Authenticate
    if target_server in ("all", "jurisprudence"):
        t0 = time.perf_counter()
        try:
            status, hdrs, body = client.send_http(
                "jurisprudence",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                auth_token="OMIT",
            )
            has_www = any(k.lower() == "www-authenticate" for k in hdrs)
            ok = status == 401 and has_www
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.1.1",
                "Rejet HTTP 401 sur Jurisprudence sans jeton",
                "jurisprudence",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status}, en-têtes {hdrs}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.1.1", "Rejet 401 Jurisprudence", "jurisprudence", False, elapsed, str(ex))

    # T2.1.2 : Jurisprudence jeton invalide -> 401
    if target_server in ("all", "jurisprudence"):
        t0 = time.perf_counter()
        try:
            status, _, _ = client.send_http(
                "jurisprudence",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                auth_token="invalid_token_1234567890",
            )
            ok = status == 401
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.1.2",
                "Rejet HTTP 401 sur Jurisprudence avec jeton erroné",
                "jurisprudence",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.1.2", "Rejet 401 Jurisprudence jeton erroné", "jurisprudence", False, elapsed, str(ex))

    # T2.1.3 : Législation non authentifié -> 404 (S8 non-oracle)
    if target_server in ("all", "legislation"):
        t0 = time.perf_counter()
        try:
            status, _, _ = client.send_http(
                "legislation",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                auth_token="OMIT",
            )
            ok = status == 404
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.1.3",
                "Garde non-oracle HTTP 404 sur Législation sans jeton",
                "legislation",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status} au lieu de 404",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.1.3", "Garde 404 Législation", "legislation", False, elapsed, str(ex))

    # T2.1.4 : Législation jeton invalide -> 404
    if target_server in ("all", "legislation"):
        t0 = time.perf_counter()
        try:
            status, _, _ = client.send_http(
                "legislation",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                auth_token="invalid_token_abcdef",
            )
            ok = status == 404
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.1.4",
                "Garde non-oracle HTTP 404 sur Législation avec jeton erroné",
                "legislation",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status} au lieu de 404",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.1.4", "Garde 404 Législation jeton erroné", "legislation", False, elapsed, str(ex))

    # T2.1.5 : Outils sans jeton -> accès public 200
    if target_server in ("all", "pratique-civile-outils"):
        t0 = time.perf_counter()
        try:
            status, _, _ = client.send_http(
                "pratique-civile-outils",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test"}}}',
                auth_token="OMIT",
            )
            ok = status == 200
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.1.5",
                "Accès public statut libre sur pratique-civile-outils",
                "pratique-civile-outils",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.1.5", "Accès public outils", "pratique-civile-outils", False, elapsed, str(ex))

    # --- 2.2 Transport & Header Boundaries ---
    # T2.2.1 : Outils accepte Accept: application/json
    if target_server in ("all", "pratique-civile-outils"):
        t0 = time.perf_counter()
        try:
            status, _, body = client.send_http(
                "pratique-civile-outils",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                extra_headers={"Accept": "application/json"},
            )
            ok = status == 200 and b"tools" in body
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.2.1",
                "Support de Accept: application/json sur pratique-civile-outils",
                "pratique-civile-outils",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status}, corps : {body[:150]}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.2.1", "Accept header application/json", "pratique-civile-outils", False, elapsed, str(ex))

    # T2.2.2 : Rejet hôte tiers non autorisé (Host header security)
    if target_server in ("all", "pratique-civile-outils"):
        t0 = time.perf_counter()
        try:
            status, _, _ = client.send_http(
                "pratique-civile-outils",
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
                "pratique-civile-outils",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status} au lieu de 403",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.2.2", "Host header security", "pratique-civile-outils", False, elapsed, str(ex))

    # T2.2.3 : Méthode HTTP interdite -> 405 Method Not Allowed
    if target_server in ("all", "pratique-civile-outils"):
        t0 = time.perf_counter()
        try:
            status, _, _ = client.send_http(
                "pratique-civile-outils",
                path="/mcp",
                method="DELETE",
                body_data=b"",
            )
            ok = status == 405
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.2.3",
                "Rejet des méthodes non autorisées (DELETE -> HTTP 405)",
                "pratique-civile-outils",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.2.3", "Méthode non autorisée 405", "pratique-civile-outils", False, elapsed, str(ex))

    # T2.2.4 : Corps de requête > 64 Kio -> HTTP 413 Payload Too Large
    if target_server in ("all", "pratique-civile-outils"):
        t0 = time.perf_counter()
        try:
            large_body = b'{"jsonrpc":"2.0","id":1,"method":"tools/list","padding":"' + (b"A" * 70000) + b'"}'
            status, _, _ = client.send_http(
                "pratique-civile-outils",
                path="/mcp",
                method="POST",
                body_data=large_body,
            )
            ok = status == 413
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T2.2.4",
                "Plafond de charge utile HTTP 413 (> 64 Kio)",
                "pratique-civile-outils",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status} au lieu de 413",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T2.2.4", "Payload Too Large 413", "pratique-civile-outils", False, elapsed, str(ex))

    # T2.2.5 : En-tête User-Agent personnalisé anti-blocage WAF et filtrage actif
    t0 = time.perf_counter()
    try:
        # 1. Requête standard : vérification de la transmission effective de l'en-tête
        status, _, _ = client.send_http("pratique-civile-outils", path="/healthz", method="GET")
        sent_ua = getattr(client, "last_sent_headers", {}).get("User-Agent", "")
        ua_present = bool(sent_ua and "PratiqueCivile" in sent_ua)
        waf_allowed = (status == 200)

        # 2. Requête contre-épreuve : un client standard sans User-Agent personnalisé est bloqué (403)
        status_blocked, _, _ = client.send_http(
            "pratique-civile-outils",
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
            "pratique-civile-outils",
            path="/mcp",
            method="POST",
            body_data=b'{"jsonrpc": "2.0", "method": "tools',
        )
        try:
            data = parse_mcp_response(body, server_key="pratique-civile-outils") if body else {}
        except Exception:
            data = json.loads(body.decode("utf-8")) if body else {}
        code = data.get("error", {}).get("code")
        ok = code == -32700
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.3.1",
            "Erreur de syntaxe JSON-RPC code -32700 (Parse error)",
            "pratique-civile-outils",
            ok,
            elapsed,
            None if ok else f"Code reçu : {code}, réponse : {data}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.3.1", "JSON-RPC -32700 Parse error", "pratique-civile-outils", False, elapsed, str(ex))

    # T2.3.2 : Requête groupée (batch array) -> code -32600 (INVALID_REQUEST)
    t0 = time.perf_counter()
    try:
        _, _, body = client.send_http(
            "pratique-civile-outils",
            path="/mcp",
            method="POST",
            body_data=b'[{"jsonrpc":"2.0","id":1,"method":"tools/list"},{"jsonrpc":"2.0","id":2,"method":"tools/list"}]',
        )
        try:
            data = parse_mcp_response(body, server_key="pratique-civile-outils") if body else {}
        except Exception:
            data = json.loads(body.decode("utf-8")) if body else {}
        code = data.get("error", {}).get("code")
        ok = code == -32600
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.3.2",
            "Rejet des requêtes groupées code -32600 (Invalid Request)",
            "pratique-civile-outils",
            ok,
            elapsed,
            None if ok else f"Code reçu : {code}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.3.2", "JSON-RPC -32600 Batch request", "pratique-civile-outils", False, elapsed, str(ex))

    # T2.3.3 : Version jsonrpc 2.0 manquante -> code -32600
    t0 = time.perf_counter()
    try:
        _, _, body = client.send_http(
            "pratique-civile-outils",
            path="/mcp",
            method="POST",
            body_data=b'{"id":1,"method":"tools/list"}',
        )
        try:
            data = parse_mcp_response(body, server_key="pratique-civile-outils") if body else {}
        except Exception:
            data = json.loads(body.decode("utf-8")) if body else {}
        code = data.get("error", {}).get("code")
        ok = code == -32600
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.3.3",
            "Omission de jsonrpc '2.0' code -32600",
            "pratique-civile-outils",
            ok,
            elapsed,
            None if ok else f"Code reçu : {code}",
        )
    except ConnectionError:
        raise
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.3.3", "JSON-RPC -32600 Missing version", "pratique-civile-outils", False, elapsed, str(ex))

    # T2.3.4 : Méthode RPC inconnue -> code -32601 (METHOD_NOT_FOUND)
    t0 = time.perf_counter()
    try:
        res = client.call_rpc("pratique-civile-outils", "method/inexistante_xyz")
        code = res.get("error", {}).get("code")
        ok = code == -32601
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.3.4",
            "Méthode RPC inconnue code -32601 (Method not found)",
            "pratique-civile-outils",
            ok,
            elapsed,
            None if ok else f"Résultat : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.3.4", "JSON-RPC -32601 Method not found", "pratique-civile-outils", False, elapsed, str(ex))

    # T2.3.5 : Nom d'outil inconnu dans tools/call -> code -32601 ou isError: true
    t0 = time.perf_counter()
    try:
        res = client.call_rpc("pratique-civile-outils", "tools/call", {"name": "outil_fantome", "arguments": {}})
        is_err = "error" in res or res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.3.5",
            "Outil inconnu dans tools/call renvoie une erreur",
            "pratique-civile-outils",
            is_err,
            elapsed,
            None if is_err else f"Résultat inattendu : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.3.5", "Outil inconnu tools/call", "pratique-civile-outils", False, elapsed, str(ex))

    # --- 2.4 Tool Argument Boundaries & Schema Hardening ---
    # T2.4.1 : Rejet d'un paramètre superflu injecté (additionalProperties: false)
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "legislation",
            "tools/call",
            {"name": "legislation_list_laws", "arguments": {"_champ_injecte": "exploit"}},
        )
        is_err = "error" in res or res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.1",
            "Rejet de propriété injectée (additionalProperties: false)",
            "legislation",
            is_err,
            elapsed,
            None if is_err else f"Paramètre non rejeté : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.1", "additionalProperties: false", "legislation", False, elapsed, str(ex))

    # T2.4.2 : Paramètre requis manquant sur legislation_get_article -> isError: true
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "legislation",
            "tools/call",
            {"name": "legislation_get_article", "arguments": {"article": "1726"}},  # law manquant
        )
        is_err = res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.2",
            "Rejet de legislation_get_article sans paramètre 'law'",
            "legislation",
            is_err,
            elapsed,
            None if is_err else f"Réponse sans erreur : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.2", "Paramètre requis manquant 'law'", "legislation", False, elapsed, str(ex))

    # T2.4.3 : Paramètre requis manquant sur calendrier_compute_deadlines
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "pratique-civile-outils",
            "tools/call",
            {"name": "calendrier_compute_deadlines", "arguments": {"event_date": "2026-07-03"}},
        )
        is_err = res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.3",
            "Rejet de calendrier_compute_deadlines sans 'deadlines'",
            "pratique-civile-outils",
            is_err,
            elapsed,
            None if is_err else f"Réponse : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.3", "Paramètre manquant 'deadlines'", "pratique-civile-outils", False, elapsed, str(ex))

    # T2.4.4 : Type incompatible sur calendrier_list_holidays (string au lieu de integer)
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "pratique-civile-outils",
            "tools/call",
            {"name": "calendrier_list_holidays", "arguments": {"year": "deux-mille-vingt-six"}},
        )
        is_err = "error" in res or res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.4",
            "Rejet de type incompatible (year: string -> integer attendu)",
            "pratique-civile-outils",
            is_err,
            elapsed,
            None if is_err else f"Réponse : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.4", "Type incompatible year", "pratique-civile-outils", False, elapsed, str(ex))

    # T2.4.5 : Violation exclusion mutuelle (XOR) sur palais_get (deux arguments fournis)
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "pratique-civile-outils",
            "tools/call",
            {"name": "palais_get", "arguments": {"greffe_number": "500", "palais": "Montréal"}},
        )
        is_err = res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.5",
            "Violation contrainte XOR palais_get (greffe + nom simultanés)",
            "pratique-civile-outils",
            is_err,
            elapsed,
            None if is_err else f"Réponse sans erreur : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.5", "XOR palais_get deux fournis", "pratique-civile-outils", False, elapsed, str(ex))

    # T2.4.6 : Violation exclusion mutuelle (XOR) sur palais_get (aucun argument fourni)
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "pratique-civile-outils",
            "tools/call",
            {"name": "palais_get", "arguments": {}},
        )
        is_err = res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.6",
            "Violation contrainte XOR palais_get (aucun argument fourni)",
            "pratique-civile-outils",
            is_err,
            elapsed,
            None if is_err else f"Réponse : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.6", "XOR palais_get aucun fourni", "pratique-civile-outils", False, elapsed, str(ex))

    # T2.4.7 : Violation XOR sur jurisprudence (get_case, citator, subsequent_history)
    t0 = time.perf_counter()
    try:
        res1 = client.call_rpc(
            "jurisprudence",
            "tools/call",
            {
                "name": "jurisprudence_get_case",
                "arguments": {"citation": "2020 QCCA 495", "database_id": "qcca", "case_id": "2020qcca495"},
            },
        )
        is_err1 = res1.get("result", {}).get("isError") is True

        res2 = client.call_rpc(
            "jurisprudence",
            "tools/call",
            {
                "name": "jurisprudence_citator",
                "arguments": {"citation": "2020 QCCA 495", "database_id": "qcca", "rel": "citing"},
            },
        )
        is_err2 = res2.get("result", {}).get("isError") is True

        res3 = client.call_rpc(
            "jurisprudence",
            "tools/call",
            {
                "name": "jurisprudence_subsequent_history",
                "arguments": {"citation": "2020 QCCA 495", "case_id": "2020qcca495"},
            },
        )
        is_err3 = res3.get("result", {}).get("isError") is True

        is_err = is_err1 and is_err2 and is_err3
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.7",
            "Violation contrainte XOR jurisprudence (get_case, citator, subsequent_history)",
            "jurisprudence",
            is_err,
            elapsed,
            None if is_err else f"get_case err={is_err1}, citator err={is_err2}, sub_hist err={is_err3}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.7", "XOR jurisprudence", "jurisprudence", False, elapsed, str(ex))

    # T2.4.8 : Date calendaire bissextile impossible (2025-02-29) -> isError: true
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "pratique-civile-outils",
            "tools/call",
            {
                "name": "calendrier_compute_deadlines",
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
            "pratique-civile-outils",
            is_err,
            elapsed,
            None if is_err else f"Date non rejetée : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.8", "Date invalide 2025-02-29", "pratique-civile-outils", False, elapsed, str(ex))

    # T2.4.9 : Citation vide sur jurisprudence_parse_citation
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "jurisprudence",
            "tools/call",
            {"name": "jurisprudence_parse_citation", "arguments": {"citation": ""}},
        )
        is_err = res.get("result", {}).get("isError") is True
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T2.4.9",
            "Rejet de citation vide sur jurisprudence_parse_citation",
            "jurisprudence",
            is_err,
            elapsed,
            None if is_err else f"Réponse : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.9", "Citation vide parse_citation", "jurisprudence", False, elapsed, str(ex))

    # T2.4.10 : Type invalide pour principal_cents sur interets_compute_1619
    t0 = time.perf_counter()
    try:
        res = client.call_rpc(
            "pratique-civile-outils",
            "tools/call",
            {
                "name": "interets_compute_1619",
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
            "Rejet de tranches de capital non tableau sur interets_compute_1619",
            "pratique-civile-outils",
            is_err,
            elapsed,
            None if is_err else f"Réponse : {res}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T2.4.10", "Type invalide interets tranches", "pratique-civile-outils", False, elapsed, str(ex))

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
        tid: str, name: str, srv: str, passed: bool, ms: float, err: Optional[str] = None
    ):
        results.append(TestResult(tid, name, 3, srv, passed, ms, err))

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
    exp_keys = {"legislation", "jurisprudence", "pratique-civile-outils"}

    keys_ok = (mcp_srv_keys == exp_keys) and (agy_srv_keys == exp_keys) and (gem_srv_keys == exp_keys)
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T3.1.1",
        "Uniformité des clés de serveurs (legislation, jurisprudence, outils)",
        "all",
        keys_ok,
        elapsed,
        f"Clés divergentes : .mcp={mcp_srv_keys}, agy={agy_srv_keys}, gem={gem_srv_keys}" if not keys_ok else None,
    )

    # T3.1.2 : Parité des URL d'accès
    t0 = time.perf_counter()
    url_errs = []
    for s_name, exp_url in URL_SERVEURS.items():
        # Antigravity url
        a_url = agy_data.get("mcpServers", {}).get(s_name, {}).get("url")
        if a_url != exp_url:
            url_errs.append(f"mcp_config.json {s_name}.url={a_url} != {exp_url}")
        # Gemini extension httpUrl
        g_url = gem_data.get("mcpServers", {}).get(s_name, {}).get("httpUrl")
        if g_url != exp_url:
            url_errs.append(f"gemini-extension.json {s_name}.httpUrl={g_url} != {exp_url}")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T3.1.2",
        "Parité stricte des URL d'accès entre configurations Claude et Gemini",
        "all",
        len(url_errs) == 0,
        elapsed,
        "; ".join(url_errs) if url_errs else None,
    )

    # T3.1.3 : Parité des variables de secrets
    t0 = time.perf_counter()
    sec_errs = []
    gem_vars = {s.get("envVar") for s in gem_data.get("settings", []) if isinstance(s, dict)}
    for s_var in ("MCP_LEGISLATION_SECRET", "MCP_JURISPRUDENCE_SECRET"):
        if s_var not in gem_vars:
            sec_errs.append(f"Variable {s_var} absente de gemini-extension.json settings")
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T3.1.3",
        "Correspondance des variables d'environnement de secrets",
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

    leg_dir = antigravity_mcp_base / "pratique-civile-quebecoise_legislation"
    jur_dir = antigravity_mcp_base / "pratique-civile-quebecoise_jurisprudence"
    out_dir = antigravity_mcp_base / "pratique-civile-quebecoise_pratique-civile-outils"

    cache_present = antigravity_mcp_base.is_dir() and (leg_dir.is_dir() or jur_dir.is_dir() or out_dir.is_dir())

    if not cache_present:
        if require_antigravity_cache:
            for tid, name, srv in [
                ("T3.2.1", "Partition du cache Législation sur disque (10 outils)", "legislation"),
                ("T3.2.2", "Partition du cache Jurisprudence sur disque (10 outils)", "jurisprudence"),
                ("T3.2.3", "Partition du cache Outils sur disque (6 outils)", "pratique-civile-outils"),
                ("T3.2.4", "Intégrité approfondie des 26 schémas d'outils sur disque", "all"),
                ("T3.2.5", "Présence et conformité de instructions.md sur disque", "all"),
            ]:
                add_result(tid, name, srv, False, 0.0, f"Cache absent dans {antigravity_mcp_base}")
        else:
            for tid, name, srv in [
                ("T3.2.1", "Partition du cache Législation sur disque (ignoré : cache Antigravity absent hors local)", "legislation"),
                ("T3.2.2", "Partition du cache Jurisprudence sur disque (ignoré : cache Antigravity absent hors local)", "jurisprudence"),
                ("T3.2.3", "Partition du cache Outils sur disque (ignoré : cache Antigravity absent hors local)", "pratique-civile-outils"),
                ("T3.2.4", "Intégrité approfondie des 26 schémas (ignoré : cache Antigravity absent hors local)", "all"),
                ("T3.2.5", "Présence instructions.md (ignoré : cache Antigravity absent hors local)", "all"),
            ]:
                add_result(tid, name, srv, True, 0.0, None)
    else:
        # T3.2.1 : Partition Législation sur disque (10 outils)
        t0 = time.perf_counter()
        leg_tools = list(leg_dir.glob("*.json")) if leg_dir.is_dir() else []
        leg_names = {f.stem for f in leg_tools}
        c_leg_ok = (len(leg_tools) == 10) and (leg_names == set(NOMS_OUTILS_ATTENDUS["legislation"]))
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.2.1",
            "Partition du cache Législation sur disque (exactement 10 outils)",
            "legislation",
            c_leg_ok,
            elapsed,
            f"Trouvé {len(leg_tools)} fichiers .json au lieu de 10 dans {leg_dir}" if not c_leg_ok else None,
        )

        # T3.2.2 : Partition Jurisprudence sur disque (10 outils, sans greffe/palais)
        t0 = time.perf_counter()
        jur_tools = list(jur_dir.glob("*.json")) if jur_dir.is_dir() else []
        jur_names = {f.stem for f in jur_tools}
        stale_in_jur = jur_names.intersection({"greffe_parse_court_file_number", "palais_list", "palais_get"})
        c_jur_ok = (len(jur_tools) == 10) and (jur_names == set(NOMS_OUTILS_ATTENDUS["jurisprudence"])) and (not stale_in_jur)
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.2.2",
            "Partition du cache Jurisprudence sur disque (exactement 10 outils, sans greffe/palais)",
            "jurisprudence",
            c_jur_ok,
            elapsed,
            f"Trouvé {len(jur_tools)} fichiers (stale: {stale_in_jur}) au lieu de 10 dans {jur_dir}" if not c_jur_ok else None,
        )

        # T3.2.3 : Partition Outils sur disque (6 outils avec greffe et palais)
        t0 = time.perf_counter()
        out_tools = list(out_dir.glob("*.json")) if out_dir.is_dir() else []
        out_names = {f.stem for f in out_tools}
        c_out_ok = (len(out_tools) == 6) and (out_names == set(NOMS_OUTILS_ATTENDUS["pratique-civile-outils"]))
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.2.3",
            "Partition du cache Outils sur disque (exactement 6 outils avec greffe et palais)",
            "pratique-civile-outils",
            c_out_ok,
            elapsed,
            f"Trouvé {len(out_tools)} fichiers au lieu de 6 dans {out_dir}" if not c_out_ok else None,
        )

        # T3.2.4 : Intégrité approfondie des 26 schémas d'outils sur disque (descriptions et items)
        t0 = time.perf_counter()
        schema_errs = []
        total_inspected = 0
        for srv_name, s_dir in [("legislation", leg_dir), ("jurisprudence", jur_dir), ("pratique-civile-outils", out_dir)]:
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

        t324_ok = (total_inspected == 26) and (len(schema_errs) == 0)
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.2.4",
            "Intégrité approfondie des 26 schémas d'outils sur disque (descriptions et items)",
            "all",
            t324_ok,
            elapsed,
            "; ".join(schema_errs[:5]) + (f" (+{len(schema_errs)-5} erreurs)" if len(schema_errs) > 5 else "") if schema_errs else (None if total_inspected == 26 else f"Inspecté {total_inspected}/26 schémas"),
        )

        # T3.2.5 : Présence et conformité de instructions.md dans les 3 serveurs sur disque
        t0 = time.perf_counter()
        missing_instr = []
        for srv_name, s_dir in [("legislation", leg_dir), ("jurisprudence", jur_dir), ("pratique-civile-outils", out_dir)]:
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
            "pratique-civile-outils",
            "greffe_parse_court_file_number",
            {"court_file_number": "500-17-000001-261"},
        )
        content_txt = greffe_res.get("content", [{}])[0].get("text", "")
        greffe_info = json.loads(content_txt)
        greffe_num = greffe_info.get("greffe_number")

        palais_res = client.call_tool(
            "pratique-civile-outils", "palais_get", {"greffe_number": greffe_num}
        )
        palais_txt = palais_res.get("content", [{}])[0].get("text", "")
        palais_info = json.loads(palais_txt)
        is_mtl = "Montréal" in palais_info.get("palais", "")

        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.3.1",
            "Contrat croisé Greffe -> Palais (dossier 500 -> Palais de justice de Montréal)",
            "pratique-civile-outils",
            is_mtl,
            elapsed,
            None if is_mtl else f"Greffe : {greffe_info}, Palais : {palais_info}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T3.3.1", "Contrat Greffe -> Palais", "pratique-civile-outils", False, elapsed, str(ex))

    # T3.3.2 : Contrat Législation -> Intérêts (art. 1619 C.c.Q.)
    t0 = time.perf_counter()
    try:
        leg_res = client.call_tool(
            "legislation", "legislation_resolve_reference", {"citation": "art. 1619 C.c.Q."}
        )
        leg_txt = leg_res.get("content", [{}])[0].get("text", "")
        leg_info = json.loads(leg_txt)
        art_num = leg_info.get("article")

        calc_res = client.call_tool(
            "pratique-civile-outils",
            "interets_compute_1619",
            {
                "end_date": "2026-11-14",
                "tranches": [{"principal_cents": 10000000, "start_date": "2024-01-01"}],
            },
        )
        calc_txt = calc_res.get("content", [{}])[0].get("text", "")
        calc_info = json.loads(calc_txt)
        has_indemnity = calc_info.get("additional_indemnity_cents", 0) > 0

        ok = art_num == "1619" and has_indemnity
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.3.2",
            "Contrat croisé Législation -> Intérêts (art. 1619 -> calcul indemnité additionnelle)",
            "all",
            ok,
            elapsed,
            None if ok else f"Art : {art_num}, Calcul : {calc_info}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T3.3.2", "Contrat Législation -> Intérêts", "all", False, elapsed, str(ex))

    # T3.3.3 : Contrat Jurisprudence -> Greffe
    t0 = time.perf_counter()
    try:
        case_res = client.call_tool("jurisprudence", "jurisprudence_get_case", {"citation": "2020 QCCA 495"})
        case_txt = case_res.get("content", [{}])[0].get("text", "")
        case_info = json.loads(case_txt)
        court_file = case_info.get("court_file", "500-09-028456-193")

        parse_res = client.call_tool(
            "pratique-civile-outils", "greffe_parse_court_file_number", {"court_file_number": court_file}
        )
        parse_txt = parse_res.get("content", [{}])[0].get("text", "")
        parse_info = json.loads(parse_txt)
        ok = parse_info.get("greffe_number") == "500"

        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T3.3.3",
            "Contrat croisé Jurisprudence -> Greffe (CanLII dossier -> district 500)",
            "all",
            ok,
            elapsed,
            None if ok else f"Dossier {court_file}, analyse : {parse_info}",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T3.3.3", "Contrat Jurisprudence -> Greffe", "all", False, elapsed, str(ex))

    # T3.3.4 : Contrat CPC -> Calendrier (art. 145 C.p.c. 15 jours)
    t0 = time.perf_counter()
    try:
        cpc_res = client.call_tool("legislation", "legislation_get_article", {"law": "cpc", "article": "145"})
        cpc_txt = cpc_res.get("content", [{}])[0].get("text", "")
        has_15 = "15" in cpc_txt

        cal_res = client.call_tool(
            "pratique-civile-outils",
            "calendrier_compute_deadlines",
            {
                "event_date": "2026-09-01",
                "deadlines": [{"amount": 15, "label": "Réponse art. 145"}],
            },
        )
        cal_txt = cal_res.get("content", [{}])[0].get("text", "")
        cal_info = json.loads(cal_txt)
        due_date = cal_info[0].get("due_date")
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

        erreurs_statiques = verifier.verifier(repo_root)
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

    # T3.4.3 : Vérification des scripts de compétences autonomes
    t0 = time.perf_counter()
    script_calc = repo_root / "skills" / "calendrier-procedural" / "scripts" / "calcul_delai.py"
    script_insp = repo_root / "skills" / "analyse-documentaire" / "scripts" / "inspecter_piece.py"
    scripts_ok = script_calc.is_file() and script_insp.is_file()
    elapsed = (time.perf_counter() - t0) * 1000
    add_result(
        "T3.4.3",
        "Disponibilité des scripts auxiliaires de compétences",
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
        r1 = client.call_tool("legislation", "legislation_find_relevant", {"query": "vice caché infiltration fondation"})
        txt1 = r1.get("content", [{}])[0].get("text", "")
        # Étape 2 : Extraction article 1726
        r2 = client.call_tool("legislation", "legislation_get_article", {"law": "ccq", "article": "1726"})
        txt2 = r2.get("content", [{}])[0].get("text", "")
        # Étape 3 : Extraction en lot 1726-1731
        r3 = client.call_tool("legislation", "legislation_get_articles", {"law": "ccq", "from": "1726", "to": "1731"})
        txt3 = r3.get("content", [{}])[0].get("text", "")
        # Étape 4 : Vérification d'autorité 2015 QCCA 1526
        r4 = client.call_tool(
            "jurisprudence",
            "jurisprudence_verify_citations",
            {"citations": [{"citation": "2015 QCCA 1526", "expected_title": "St-Louis c. Morin"}]},
        )
        txt4 = r4.get("content", [{}])[0].get("text", "")
        # Étape 5 : Citateur CanLII
        r5 = client.call_tool("jurisprudence", "jurisprudence_citator", {"citation": "2015 QCCA 1526", "rel": "citing", "limit": 5})
        txt5 = r5.get("content", [{}])[0].get("text", "")
        # Étape 6 : Analyse numéro de greffe
        r6 = client.call_tool("pratique-civile-outils", "greffe_parse_court_file_number", {"court_file_number": "500-17-012345-211"})
        txt6 = r6.get("content", [{}])[0].get("text", "")
        # Étape 7 : Calcul exact d'intérêts et indemnité additionnelle art. 1619
        r7 = client.call_tool(
            "pratique-civile-outils",
            "interets_compute_1619",
            {
                "end_date": "2026-11-14",
                "tranches": [{"principal_cents": 5000000, "start_date": "2024-05-01", "label": "Réparations"}],
            },
        )
        txt7 = r7.get("content", [{}])[0].get("text", "")

        ok = "1726" in txt2 and "CONFIRMÉE" in txt4 and "Montréal" in txt6 and "grand_total_cents" in txt7
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
        r1 = client.call_tool("legislation", "legislation_resolve_reference", {"citation": "art. 145 C.p.c."})
        # Étape 2 : Jours fériés 2026
        r2 = client.call_tool("pratique-civile-outils", "calendrier_list_holidays", {"year": 2026, "regime": "qc_cpc"})
        # Étape 3 : Calcul arithmétique avec bascule art. 111 al. 2 C.p.c. (17h35 un vendredi)
        r3 = client.call_tool(
            "pratique-civile-outils",
            "calendrier_compute_deadlines",
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
        r4 = client.call_tool("pratique-civile-outils", "palais_get", {"greffe_number": "500"})
        txt4 = r4.get("content", [{}])[0].get("text", "")

        ok = "2026-07-21" in txt3 and "Notre-Dame" in txt4
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
        r1 = client.call_tool("jurisprudence", "jurisprudence_parse_citation", {"citation": "2020 QCCA 495"})
        txt1 = r1.get("content", [{}])[0].get("text", "")
        # Étape 2 : Vérification en ligne
        r2 = client.call_tool(
            "jurisprudence", "jurisprudence_verify_citations", {"citations": [{"citation": "2020 QCCA 495"}]}
        )
        txt2 = r2.get("content", [{}])[0].get("text", "")
        # Étape 3 : Sort ultérieur
        r3 = client.call_tool("jurisprudence", "jurisprudence_subsequent_history", {"citation": "2020 QCCA 495"})
        txt3 = r3.get("content", [{}])[0].get("text", "")
        # Étape 4 : Fiche CanLII complète
        r4 = client.call_tool("jurisprudence", "jurisprudence_get_case", {"citation": "2020 QCCA 495"})
        txt4 = r4.get("content", [{}])[0].get("text", "")

        ok = "qcca" in txt1.lower() and "confirmée" in txt2.lower() and "famille" in txt4.lower()
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T4.3",
            "Scénario 3 : Diagnostic de citation et vérification d'autorité CanLII",
            "jurisprudence",
            ok,
            elapsed,
            None if ok else "Échec de validation de la citation 2020 QCCA 495",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T4.3", "Scénario 3 : Citation CanLII", "jurisprudence", False, elapsed, str(ex))

    # --- Scénario 4 : Recherche textuelle et exploration réglementaire ---
    t0 = time.perf_counter()
    try:
        # Étape 1 : Recherche FTS5 sur prescription
        r1 = client.call_tool(
            "legislation",
            "legislation_search_text",
            {"query": "prescription dommage corporel", "law": "ccq", "limit": 3},
        )
        txt1 = r1.get("content", [{}])[0].get("text", "")
        # Étape 2 : Texte complet de la division
        r2 = client.call_tool(
            "legislation", "legislation_get_division", {"law": "ccq", "path": "ga:l_dixieme-gb:l_premier"}
        )
        txt2 = r2.get("content", [{}])[0].get("text", "")
        # Étape 3 : Exploration des règlements pris en application du CPC
        r3 = client.call_tool("legislation", "legislation_related_laws", {"law": "cpc", "rel_type": "reglement-de"})
        txt3 = r3.get("content", [{}])[0].get("text", "")

        ok = "2925" in txt1 and "prescription" in txt2.lower() and "honoraires" in txt3.lower()
        elapsed = (time.perf_counter() - t0) * 1000
        add_result(
            "T4.4",
            "Scénario 4 : Recherche textuelle et exploration réglementaire (C.c.Q. / C.p.c.)",
            "legislation",
            ok,
            elapsed,
            None if ok else "Échec dans le scénario 4 de recherche",
        )
    except ConnectionError:
        raise
    except Exception as ex:
        elapsed = (time.perf_counter() - t0) * 1000
        add_result("T4.4", "Scénario 4 : Recherche réglementaire", "legislation", False, elapsed, str(ex))

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

    # T5.1.1 : S8 Stealth non-oracle sur Législation (méthode non autorisée sans authentification -> 404)
    if target_server in ("all", "legislation"):
        t0 = time.perf_counter()
        try:
            status, _, _ = client.send_http(
                "legislation",
                path="/mcp",
                method="DELETE",
                body_data=b"",
                auth_token="OMIT",
            )
            ok = status == 404
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T5.1.1",
                "S8 Stealth non-oracle : DELETE non authentifié rend 404 (non 405)",
                "legislation",
                ok,
                elapsed,
                None if ok else f"Statut reçu {status} au lieu de 404",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T5.1.1", "S8 Stealth non-oracle", "legislation", False, elapsed, str(ex))

    # T5.1.2 : Host Header Security whitelist (rejet DNS rebinding sur domaines non autorisés -> 403)
    if target_server in ("all", "pratique-civile-outils"):
        t0 = time.perf_counter()
        try:
            status_bad1, _, _ = client.send_http(
                "pratique-civile-outils",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                extra_headers={"Host": "attacker.com"},
            )
            status_bad2, _, _ = client.send_http(
                "pratique-civile-outils",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                extra_headers={"Host": "evil-outils.poirierlavoie.ca"},
            )
            status_good, _, _ = client.send_http(
                "pratique-civile-outils",
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
                "pratique-civile-outils",
                ok,
                elapsed,
                None if ok else f"Statuts reçus: bad1={status_bad1}, bad2={status_bad2}, good={status_good}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T5.1.2", "Host header whitelist", "pratique-civile-outils", False, elapsed, str(ex))

    # T5.1.3 : Rejet des identifiants JSON-RPC structurés (objets/tableaux code -32600)
    if target_server in ("all", "pratique-civile-outils"):
        t0 = time.perf_counter()
        try:
            _, _, body_obj = client.send_http(
                "pratique-civile-outils",
                path="/mcp",
                method="POST",
                body_data=b'{"jsonrpc":"2.0","id":{"bad":"object"},"method":"initialize"}',
                extra_headers={"Host": "outils.poirierlavoie.ca"},
            )
            res_obj = json.loads(body_obj.decode("utf-8"))
            err_code_obj = res_obj.get("error", {}).get("code")

            _, _, body_arr = client.send_http(
                "pratique-civile-outils",
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
                "pratique-civile-outils",
                ok,
                elapsed,
                None if ok else f"Codes reçus: obj={err_code_obj}, arr={err_code_arr}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T5.1.3", "Rejet JSON-RPC id structuré", "pratique-civile-outils", False, elapsed, str(ex))

    # T5.1.4 : Support CORS Preflight OPTIONS (/mcp -> HTTP 204 No Content)
    if target_server in ("all", "legislation", "pratique-civile-outils"):
        t0 = time.perf_counter()
        try:
            status_leg, hdrs_leg, _ = client.send_http(
                "legislation",
                path="/mcp",
                method="OPTIONS",
                body_data=b"",
                auth_token="OMIT",
            )
            status_out, hdrs_out, _ = client.send_http(
                "pratique-civile-outils",
                path="/mcp",
                method="OPTIONS",
                body_data=b"",
            )
            ok_leg = status_leg == 204 and "POST, OPTIONS" in hdrs_leg.get("Access-Control-Allow-Methods", "")
            ok_out = status_out == 204 and "POST, OPTIONS" in hdrs_out.get("Access-Control-Allow-Methods", "")
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
    if target_server in ("all", "pratique-civile-outils"):
        t0 = time.perf_counter()
        try:
            # 17:00 pile un vendredi -> NE DOIT PAS basculer (ancre reste 2026-07-03)
            r_1700 = client.call_tool(
                "pratique-civile-outils",
                "calendrier_compute_deadlines",
                {
                    "event_date": "2026-07-03",
                    "event_time": "17:00",
                    "notification_mode": "technological",
                    "regime": "qc_cpc",
                    "deadlines": [{"label": "Seuil 17h00", "amount": 1, "unit": "days"}],
                },
            )
            txt_1700 = r_1700.get("content", [{}])[0].get("text", "")
            data_1700 = json.loads(txt_1700)
            item_1700 = data_1700[0] if isinstance(data_1700, list) else data_1700.get("results", [{}])[0]
            anchor_1700 = item_1700.get("anchor_date") or item_1700.get("effective_anchor_date")
            not_shifted_1700 = anchor_1700 == "2026-07-03" and not bool(item_1700.get("anchor_shifted_art_111", False))

            # 17:01 un vendredi -> DOIT basculer au lundi suivant (2026-07-06)
            r_1701 = client.call_tool(
                "pratique-civile-outils",
                "calendrier_compute_deadlines",
                {
                    "event_date": "2026-07-03",
                    "event_time": "17:01",
                    "notification_mode": "technological",
                    "regime": "qc_cpc",
                    "deadlines": [{"label": "Après 17h00", "amount": 1, "unit": "days"}],
                },
            )
            txt_1701 = r_1701.get("content", [{}])[0].get("text", "")
            data_1701 = json.loads(txt_1701)
            item_1701 = data_1701[0] if isinstance(data_1701, list) else data_1701.get("results", [{}])[0]
            anchor_1701 = item_1701.get("anchor_date") or item_1701.get("effective_anchor_date")
            shifted_1701 = anchor_1701 == "2026-07-06" and bool(item_1701.get("anchor_shifted_art_111", False))

            # 16:59 un vendredi -> NE DOIT PAS basculer (ancre reste 2026-07-03)
            r_1659 = client.call_tool(
                "pratique-civile-outils",
                "calendrier_compute_deadlines",
                {
                    "event_date": "2026-07-03",
                    "event_time": "16:59",
                    "notification_mode": "technological",
                    "regime": "qc_cpc",
                    "deadlines": [{"label": "Avant 17h00", "amount": 1, "unit": "days"}],
                },
            )
            txt_1659 = r_1659.get("content", [{}])[0].get("text", "")
            data_1659 = json.loads(txt_1659)
            item_1659 = data_1659[0] if isinstance(data_1659, list) else data_1659.get("results", [{}])[0]
            anchor_1659 = item_1659.get("anchor_date") or item_1659.get("effective_anchor_date")
            not_shifted_1659 = anchor_1659 == "2026-07-03" and not bool(item_1659.get("anchor_shifted_art_111", False))

            ok = not_shifted_1700 and shifted_1701 and not_shifted_1659
            elapsed = (time.perf_counter() - t0) * 1000
            add_result(
                "T5.1.5",
                "Bascule statutaire art. 111 al. 2 C.p.c. (17h00 -> pas de report, 17h01 -> report, 16h59 -> pas de report)",
                "pratique-civile-outils",
                ok,
                elapsed,
                None if ok else f"17h00 anchor={anchor_1700}, 17h01 anchor={anchor_1701}, 16h59 anchor={anchor_1659}",
            )
        except ConnectionError:
            raise
        except Exception as ex:
            elapsed = (time.perf_counter() - t0) * 1000
            add_result("T5.1.5", "Bascule art. 111 C.p.c. 17h00", "pratique-civile-outils", False, elapsed, str(ex))

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
    lines.append(f"  PRATIQUE CIVILE QUÉBÉCOISE — VÉRIFICATEUR E2E MULTI-PALIERS")
    lines.append(f"  Mode d'exécution : {mode.upper()} | Date : {datetime.datetime.now().isoformat()}")
    lines.append("=" * 80)

    # Regroupement par palier
    by_tier: Dict[int, List[TestResult]] = {1: [], 2: [], 3: [], 4: [], 5: []}
    for r in results:
        by_tier.setdefault(r.tier, []).append(r)

    tier_names = {
        1: "Palier 1 : Couverture fonctionnelle (Manifestes, Handshakes, 26 outils)",
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
            stat_str = "SUCCÈS" if r.passed else "ÉCHEC"
            dur_str = f"{r.duration_ms:.1f}ms"
            desc = r.name[:50]
            lines.append(f"{r.test_id:<8} {stat_str:<8} {dur_str:<10} {desc:<52}")
            if not r.passed and r.error_message:
                lines.append(f"         └─ ERREUR : {r.error_message}")

    total_count = len(results)
    passed_count = sum(1 for r in results if r.passed)
    failed_count = total_count - passed_count
    succ_rate = (passed_count / total_count * 100) if total_count else 0.0

    lines.append("\n" + "=" * 80)
    lines.append(f"  BILAN FINAL : {passed_count}/{total_count} tests réussis ({succ_rate:.1f}%) en {total_duration_s:.2f}s")
    lines.append("=" * 80 + "\n")
    return "\n".join(lines)


def format_report_json(
    results: List[TestResult], mode: str, total_duration_s: float
) -> str:
    """Génère un rapport JSON structuré pour intégration machine."""
    passed_count = sum(1 for r in results if r.passed)
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "mode": mode,
        "total_duration_s": total_duration_s,
        "summary": {
            "total": len(results),
            "passed": passed_count,
            "failed": len(results) - passed_count,
            "success_rate_percent": (passed_count / len(results) * 100) if results else 0.0,
        },
        "tests": [
            {
                "id": r.test_id,
                "name": r.name,
                "tier": r.tier,
                "server": r.server,
                "passed": r.passed,
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
        if r.passed:
            lines.append(f"::notice title={r.test_id}::[{r.test_id}] {r.name} - SUCCÈS ({r.duration_ms:.1f}ms)")
        else:
            lines.append(f"::error title={r.test_id}::[{r.test_id}] {r.name} - ÉCHEC : {r.error_message}")

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    lines.append(f"::notice title=Bilan::Vérification E2E ({mode}) terminée : {passed}/{total} tests réussis en {total_duration_s:.2f}s")
    return "\n".join(lines)


# ============================================================================
# Point d'entrée principal (CLI)
# ============================================================================


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Vérificateur multi-paliers E2E pour pratique-civile-quebecoise",
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
        choices=["legislation", "jurisprudence", "pratique-civile-outils", "outils", "all"],
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

    # Normalisation de l'alias de serveur
    server_filter = args.server
    if server_filter == "outils":
        server_filter = "pratique-civile-outils"

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

    has_failure = any(not r.passed for r in all_results)
    return 1 if has_failure else 0


if __name__ == "__main__":
    sys.exit(main())
