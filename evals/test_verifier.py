#!/usr/bin/env python3
"""Tests unitaires sur fixtures pour verifier.py (architecture v3.0.0).

Bibliothèque standard Python uniquement. Exécutable directement ou via
`python evals/executer_evals.py --auto-test`.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import verifier  # noqa: E402

KERNEL_V3 = """<!-- SAFETY-KERNEL:START -->
## Garde-fous impératifs

1. **Confidentialité stricte :** Ne jamais inclure de noms de clients dans une requête `query`.
2. **Sources primaires obligatoires :** Lire `lois` (`get_article`), `juris` (`verify_citations`), `outils` (`calendrier_deadlines`). En cas d'échec (`401`, `404`, `429`, `[CLEF_ABSENTE]`, `[CLEF_REFUSEE]`, `QUOTA_EPUISE`, hors ligne), s'arrêter sur le volet touché et diriger vers `acces.poirierlavoie.ca/moi`.
3. **Étanchéité bijuridique :** Écarter tout droit étranger.
4. **Protection et déclencheurs déontologiques :** Présumer `CONFIDENTIEL`.
5. **Perception et précédents :** Ne jamais décrire un média non perçu dans la session (support secondaire). Précédents dé-identifiés fournis par l'avocat.
<!-- SAFETY-KERNEL:END -->"""


def _write_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def _build_valid_v3_fixture(root: Path) -> None:
    """Construit un dépôt minimal 100 % conforme aux règles v3.0.0."""
    for rel in sorted(verifier.ROOT_ALLOWLIST | verifier.EVALS_ALLOWLIST):
        target = root / rel
        if rel in (".claude-plugin/plugin.json",):
            _write_lf(
                target,
                json.dumps(
                    {
                        "name": verifier.EXPECTED_PLUGIN_NAME,
                        "version": "3.0.0",
                        "license": verifier.EXPECTED_LICENSE,
                        "homepage": verifier.EXPECTED_REPO_URL,
                        "repository": verifier.EXPECTED_REPO_URL,
                    }
                )
                + "\n",
            )
        elif rel == ".claude-plugin/marketplace.json":
            _write_lf(
                target,
                json.dumps(
                    {
                        "name": verifier.EXPECTED_PLUGIN_NAME,
                        "metadata": {"version": "3.0.0"},
                        "plugins": [
                            {
                                "name": verifier.EXPECTED_PLUGIN_NAME,
                                "version": "3.0.0",
                                "license": verifier.EXPECTED_LICENSE,
                                "homepage": verifier.EXPECTED_REPO_URL,
                                "repository": verifier.EXPECTED_REPO_URL,
                                "source": "./",
                            }
                        ],
                    }
                )
                + "\n",
            )
        elif rel == "plugin.json":
            _write_lf(
                target,
                json.dumps(
                    {
                        "name": verifier.EXPECTED_PLUGIN_NAME,
                        "displayName": verifier.EXPECTED_DISPLAY_NAME,
                        "version": "3.0.0",
                        "description": "Plugin v3",
                        "logo": "assets/logo.svg",
                        "suggestedPrompts": ["Test 1"],
                        "author": {"name": "Test"},
                        "homepage": verifier.EXPECTED_REPO_URL,
                        "repository": verifier.EXPECTED_REPO_URL,
                    }
                )
                + "\n",
            )
        elif rel == "mcp_config.json":
            _write_lf(
                target,
                json.dumps(
                    {
                        "mcpServers": {
                            "lois": {
                                "url": verifier.EXPECTED_LEGISLATION_URL,
                                "headers": {"Authorization": verifier.EXPECTED_LEGISLATION_AUTH},
                                "variables": [
                                    {
                                        "name": "MCP_LEGISLATION_SECRET",
                                        "title": "Secret",
                                        "description": "Token",
                                    }
                                ],
                            },
                            "juris": {
                                "url": verifier.EXPECTED_JURISPRUDENCE_URL,
                                "headers": {"Authorization": verifier.EXPECTED_JURISPRUDENCE_AUTH},
                                "variables": [
                                    {
                                        "name": "MCP_JURISPRUDENCE_SECRET",
                                        "title": "Secret",
                                        "description": "Token",
                                    }
                                ],
                            },
                            "outils": {"url": verifier.EXPECTED_OUTILS_URL},
                        }
                    }
                )
                + "\n",
            )
        elif rel == "gemini-extension.json":
            _write_lf(
                target,
                json.dumps(
                    {
                        "name": verifier.EXPECTED_PLUGIN_NAME,
                        "version": "3.0.0",
                        "contextFileName": [],
                        "settings": [
                            {
                                "name": "L",
                                "description": "D",
                                "envVar": "MCP_LEGISLATION_SECRET",
                                "sensitive": True,
                            },
                            {
                                "name": "J",
                                "description": "D",
                                "envVar": "MCP_JURISPRUDENCE_SECRET",
                                "sensitive": True,
                            },
                        ],
                        "mcpServers": {
                            "lois": {
                                "httpUrl": verifier.EXPECTED_LEGISLATION_URL,
                                "headers": {"Authorization": verifier.EXPECTED_LEGISLATION_AUTH},
                            },
                            "juris": {
                                "httpUrl": verifier.EXPECTED_JURISPRUDENCE_URL,
                                "headers": {"Authorization": verifier.EXPECTED_JURISPRUDENCE_AUTH},
                            },
                            "outils": {"httpUrl": verifier.EXPECTED_OUTILS_URL},
                        },
                    }
                )
                + "\n",
            )
        elif rel == ".mcp.json":
            _write_lf(target, json.dumps({"mcpServers": verifier.EXPECTED_MCP_SERVERS}) + "\n")
        elif rel in ("CLAUDE.md", "GEMINI.md"):
            _write_lf(target, "# Contrat v3\n")
        elif rel == "LICENSE":
            _write_lf(
                target,
                f"SPDX: {verifier.EXPECTED_LICENSE}\n"
                "AUTORISATION COMPLÉMENTAIRE DE PRATIQUE PROFESSIONNELLE DU DROIT\n"
                "COMPANION PROFESSIONAL LEGAL PRACTICE GRANT\n",
            )
        elif rel == "evals/scenarios.json":
            continue
        elif rel.endswith(".py"):
            _write_lf(target, "# stub\n")
        else:
            _write_lf(target, "ok\n")

    service_leaves = {
        "recherche-juridique": "recherche-legislative.md",
        "analyse-et-strategie": "preuve-directe.md",
        "redaction-juridique": "acte-demande-introductive.md",
        "production-et-conformite": "controle-acte-de-procedure.md",
        "gestion-du-mandat": "conformite-echeanciers-cpc.md",
    }

    for svc, leaf_file in service_leaves.items():
        headings = verifier._required_headings_for_leaf(leaf_file) or ()
        leaf_body = f"# {leaf_file}\n\n" + "\n\n".join(f"## {h}\n\nContenu." for h in headings) + "\n"
        _write_lf(root / "skills" / svc / "references" / leaf_file, leaf_body)
        router = (
            "---\n"
            f"name: {svc}\n"
            "description: >-\n"
            "  Service de test. En anglais — test service. Ne pas utiliser pour hors champ.\n"
            "---\n\n"
            f"# {svc}\n\n"
            f"{KERNEL_V3}\n\n"
            "## Paliers de rigueur\n\nPalier 2.\n\n"
            "## Catalogue\n\n"
            f"| Intention | references/{leaf_file} | lois |\n\n"
            "## Contrôle avant remise\n\nOK.\n"
        )
        _write_lf(root / "skills" / svc / "SKILL.md", router)

    for ph in sorted(verifier.PHASE_SKILLS):
        phase_router = (
            "---\n"
            f"name: {ph}\n"
            "description: >-\n"
            "  Phase de test. En anglais — test phase. Ne pas utiliser pour hors champ.\n"
            "---\n\n"
            f"# {ph}\n\n"
            f"{KERNEL_V3}\n\n"
            "## Entrées requises\n\nMandat.\n\n"
            "## État de la phase\n\netat-dossier.\n\n"
            "## Parcours\n\n### Étape 1 — Contrôle\n- Porte.\n\n"
            "## Enchaînements\n\n"
            "| Étape | Type | Cible | Feuille | Palier | Condition |\n"
            "|---|---|---|---|---|---|\n"
            "| 1 | référence | recherche-juridique | recherche-legislative | — | toujours |\n"
            "| 2 | livrable | redaction-juridique | acte-demande-introductive | 3 | après étape 1 |\n\n"
            "## Branches\n\nStandard.\n\n"
            "## Contrôle de sortie de phase\n\nOK.\n"
        )
        _write_lf(root / "skills" / ph / "SKILL.md", phase_router)

    scenarios = []
    idx = 1
    for ph in sorted(verifier.PHASE_SKILLS):
        for kind in ("parcours", "porte", "branche"):
            scenarios.append(
                {
                    "id": f"PH-{idx}",
                    "competence": ph,
                    "palier": 2,
                    "titre": f"{ph} {kind}",
                    "prompt": "Test phase",
                    "criteres": ["Critère"],
                    "doit_contenir": ["ok"],
                    "ne_doit_pas_contenir": [],
                    "feuilles_attendues": [],
                    "enchainement_attendu": ["recherche-juridique:recherche-legislative"],
                    "declencheur_negatif": False,
                }
            )
            idx += 1
        scenarios.append(
            {
                "id": f"NEG-{idx}",
                "competence": ph,
                "palier": 1,
                "titre": f"{ph} hors champ",
                "prompt": "Droit criminel",
                "criteres": ["Refuser hors champ"],
                "doit_contenir": ["hors champ"],
                "ne_doit_pas_contenir": [],
                "feuilles_attendues": [],
                "enchainement_attendu": [],
                "declencheur_negatif": True,
            }
        )
        idx += 1

    for svc, leaf_file in sorted(service_leaves.items()):
        stem = leaf_file[:-3]
        for k in range(2):
            scenarios.append(
                {
                    "id": f"SVC-{idx}-{k}",
                    "competence": svc,
                    "palier": 2,
                    "titre": f"{svc} {k}",
                    "prompt": "Test service",
                    "criteres": ["Critère"],
                    "doit_contenir": ["ok"],
                    "ne_doit_pas_contenir": [],
                    "feuilles_attendues": [stem],
                    "enchainement_attendu": [],
                    "declencheur_negatif": False,
                }
            )
            idx += 1
        scenarios.append(
            {
                "id": f"NEG-{idx}",
                "competence": svc,
                "palier": 1,
                "titre": f"{svc} hors champ",
                "prompt": "Droit familial",
                "criteres": ["Refuser hors champ"],
                "doit_contenir": ["hors champ"],
                "ne_doit_pas_contenir": [],
                "feuilles_attendues": [],
                "enchainement_attendu": [],
                "declencheur_negatif": True,
            }
        )
        idx += 1

    _write_lf(
        root / "evals" / "scenarios.json",
        json.dumps({"version": "3.0.0", "scenarios": scenarios}, ensure_ascii=False, indent=2) + "\n",
    )


class VerifierV3Tests(unittest.TestCase):
    def test_valid_fixture_passes_normal_and_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_valid_v3_fixture(root)
            errs, stats = verifier.verifier(root, release_mode=False)
            self.assertEqual(errs, [])
            self.assertEqual(stats["release_markers_count"], 0)
            errs_rel, _ = verifier.verifier(root, release_mode=True)
            self.assertEqual(errs_rel, [])

    def test_release_markers_allowed_on_branch_but_blocked_in_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_valid_v3_fixture(root)
            leaf = root / "skills" / "redaction-juridique" / "references" / "acte-demande-introductive.md"
            leaf.write_bytes((leaf.read_text(encoding="utf-8") + "\n[FICHE À RÉDIGER]\n").encode("utf-8"))
            errs_branch, stats = verifier.verifier(root, release_mode=False)
            self.assertEqual(errs_branch, [])
            self.assertEqual(stats["release_markers_count"], 1)
            errs_rel, _ = verifier.verifier(root, release_mode=True)
            self.assertTrue(any("[FICHE À RÉDIGER]" in e for e in errs_rel))

    def test_description_budgets_and_total_cap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_valid_v3_fixture(root)
            p_skill = root / "skills" / "phase-ouverture-dossier" / "SKILL.md"
            txt = p_skill.read_text(encoding="utf-8")
            long_desc = "Phase test " + ("x" * 420) + ". En anglais — x. Ne pas utiliser pour y."
            txt = txt.replace(
                "  Phase de test. En anglais — test phase. Ne pas utiliser pour hors champ.",
                f"  {long_desc}",
            )
            _write_lf(p_skill, txt)
            errs, _ = verifier.verifier(root)
            self.assertTrue(any("450 caractères" in e for e in errs))

    def test_enchainements_rules_and_service_forbiddance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_valid_v3_fixture(root)
            p_skill = root / "skills" / "phase-ouverture-dossier" / "SKILL.md"
            bad_txt = p_skill.read_text(encoding="utf-8").replace(
                "| 2 | livrable | redaction-juridique | acte-demande-introductive | 3 | après étape 1 |",
                "| 2 | livrable | redaction-juridique | feuille-inexistante.md | — | après étape 1 |",
            )
            _write_lf(p_skill, bad_txt)
            errs, _ = verifier.verifier(root)
            self.assertTrue(any("Feuille invalide" in e for e in errs))
            self.assertTrue(any("exige un Palier 1, 2 ou 3" in e for e in errs))

            svc_skill = root / "skills" / "recherche-juridique" / "SKILL.md"
            _write_lf(
                svc_skill,
                svc_skill.read_text(encoding="utf-8") + "\n## Enchaînements\n\nInterdit.\n",
            )
            errs2, _ = verifier.verifier(root)
            self.assertTrue(any("## Enchaînements" in e and "interdite" in e for e in errs2))

    def test_graph_isolation_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_valid_v3_fixture(root)
            svc_leaf = root / "skills" / "recherche-juridique" / "references" / "recherche-legislative.md"
            _write_lf(
                svc_leaf,
                svc_leaf.read_text(encoding="utf-8") + "\nVoir phase-ouverture-dossier et ../autre.md\n",
            )
            errs, _ = verifier.verifier(root)
            self.assertTrue(any("phase-*" in e for e in errs))
            self.assertTrue(any("lien relatif '../' interdit" in e for e in errs))

    def test_sheet_template_headings_and_prefix_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_valid_v3_fixture(root)
            leaf = root / "skills" / "analyse-et-strategie" / "references" / "preuve-directe.md"
            _write_lf(leaf, "# Preuve directe\n\n## Qualification\n\nSeule section.\n")
            errs, _ = verifier.verifier(root)
            self.assertTrue(any("titres obligatoires manquants" in e for e in errs))

    def test_kernel_parity_across_ten_skills_and_guard_five(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_valid_v3_fixture(root)
            p_skill = root / "skills" / "phase-jugement-et-suites" / "SKILL.md"
            _write_lf(
                p_skill,
                p_skill.read_text(encoding="utf-8").replace("5. **Perception et précédents", "5. **Autre"),
            )
            errs, _ = verifier.verifier(root)
            self.assertTrue(any("10 SKILL.md" in e for e in errs))
            self.assertTrue(any("Perception et précédents" in e for e in errs))

    def test_per_load_cap_and_leaf_byte_cap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_valid_v3_fixture(root)
            leaf = root / "skills" / "gestion-du-mandat" / "references" / "conformite-echeanciers-cpc.md"
            _write_lf(leaf, leaf.read_text(encoding="utf-8") + ("a" * 26000) + "\n")
            errs, _ = verifier.verifier(root)
            self.assertTrue(any("24576" in e for e in errs))

    def test_banned_dms_patterns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_valid_v3_fixture(root)
            leaf = root / "skills" / "gestion-du-mandat" / "references" / "conformite-echeanciers-cpc.md"
            bad_tool = "get_" + "dossier"
            _write_lf(leaf, leaf.read_text(encoding="utf-8") + f"\nAppeler {bad_tool}.\n")
            errs, _ = verifier.verifier(root)
            self.assertTrue(any("gestionnaire de dossiers" in e for e in errs))

    def test_phase_section_order_and_branch_enchainement_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_valid_v3_fixture(root)
            p_skill = root / "skills" / "phase-introduction-reponse" / "SKILL.md"
            txt = p_skill.read_text(encoding="utf-8")
            swapped = txt.replace(
                "## Entrées requises\n\nMandat.\n\n## État de la phase\n\netat-dossier.\n\n",
                "## État de la phase\n\netat-dossier.\n\n## Entrées requises\n\nMandat.\n\n",
            ).replace("## Branches\n\nStandard.", "## Branches\n\n* `references/branche-test.md`")
            _write_lf(p_skill, swapped)
            _write_lf(
                root / "skills" / "phase-introduction-reponse" / "references" / "branche-test.md",
                "# Branche\n\nConsulter `preuve-directe`.\n",
            )
            errs, _ = verifier.verifier(root)
            self.assertTrue(any("ordre des sections obligatoires invalide" in e for e in errs))
            self.assertTrue(any("preuve-directe" in e and "Enchaînements" in e for e in errs))

    def test_missing_script_in_leaf_and_negative_trigger_not_counting_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_valid_v3_fixture(root)
            leaf = root / "skills" / "analyse-et-strategie" / "references" / "preuve-directe.md"
            _write_lf(leaf, leaf.read_text(encoding="utf-8") + "\nExécuter `scripts/inexistant.py`.\n")
            sc_path = root / "evals" / "scenarios.json"
            sc_data = json.loads(sc_path.read_text(encoding="utf-8"))
            sc_data["scenarios"] = [
                sc for sc in sc_data["scenarios"]
                if not (sc["competence"] == "analyse-et-strategie" and not sc["declencheur_negatif"])
            ]
            for sc in sc_data["scenarios"]:
                if sc["competence"] == "analyse-et-strategie" and sc["declencheur_negatif"]:
                    sc["feuilles_attendues"] = ["preuve-directe"]
                    sc["enchainement_attendu"] = ["analyse-et-strategie:preuve-directe"]
            _write_lf(sc_path, json.dumps(sc_data, ensure_ascii=False, indent=2) + "\n")
            errs_norm, _ = verifier.verifier(root, release_mode=False)
            self.assertTrue(any("script local introuvable" in e for e in errs_norm))
            errs_rel, _ = verifier.verifier(root, release_mode=True)
            self.assertTrue(any("analyse-et-strategie/references/preuve-directe.md (0 trouvé(s))" in e for e in errs_rel))

    def test_license_markers_lf_and_kernel_rule_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_valid_v3_fixture(root)
            (root / "LICENSE").write_bytes(b"CC-BY-NC-SA-4.0\r\n")
            errs, _ = verifier.verifier(root)
            self.assertTrue(any("LICENSE : fins de ligne CR/CRLF" in e for e in errs))
            self.assertTrue(any("AUTORISATION COMPLÉMENTAIRE" in e for e in errs))
            self.assertTrue(any("COMPANION PROFESSIONAL" in e for e in errs))

            p_skill = root / "skills" / "recherche-juridique" / "SKILL.md"
            _write_lf(
                p_skill,
                p_skill.read_text(encoding="utf-8").replace("acces.poirierlavoie.ca/moi", "reconnecter"),
            )
            errs2, _ = verifier.verifier(root)
            self.assertTrue(any("acces.poirierlavoie.ca/moi" in e for e in errs2))


if __name__ == "__main__":
    unittest.main()
