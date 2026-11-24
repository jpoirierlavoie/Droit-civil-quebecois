# Journal des modifications / Changelog

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et [Semantic Versioning](https://semver.org/).

## [Non publié]

### Ajouté
- Manifeste dédié Antigravity `.antigravity-plugin/plugin.json` (`https://antigravity.google/schemas/v1/plugin.json`) et alignement de `plugin.json` racine sur le standard portable **Agent Plugins 1.0** (`https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`).
- Fichier d'instructions unifié [`AGENTS.md`](AGENTS.md) synchronisé octet pour octet avec [`CLAUDE.md`](CLAUDE.md) et [`GEMINI.md`](GEMINI.md) (condensés sous `20 Ko` UTF-8 LF).
- Fichiers communautaires open source : [`CONTRIBUTING.md`](CONTRIBUTING.md), [`CHANGELOG.md`](CHANGELOG.md) et [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
- Validation de l'archive ChatGPT dans `.github/workflows/verify.yml` et publication automatisée de `dist/droit-civil-quebecois-chatgpt-universal.zip` + `.sha256` dans `.github/workflows/release.yml`.

### Modifié
- Mise à jour de `scripts/synchroniser_plugin_gemini.py` (promotion de `.antigravity-plugin/plugin.json` vers `plugin.json`, `Path.home()` multiplateforme, variable `DCQ_PLUGIN_SRC_DIR`), `scripts/empaqueter_plugin_chatgpt.py` (liste d'exclusion élargie et contrôle de parité avec `plugin.json` racine) et `scripts/regenerer_cache_mcp.py`.
- Nettoyage des gabarits `.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/bug_report.yml`, `.github/workflows/dependabot-auto-merge.yml`, ainsi que de `README.md`, `SECURITY.md`, `verifier.py`, `verifier_tout.py` (lecture dynamique de la version du manifeste) et `evals/test_verifier.py`.

---

## [3.1.0] — 2026-11-22

### Ajouté
- Auto-connexion **OAuth 2.1 PKCE `S256`** sans configuration préalable (`/mcp/oauth` par défaut dans `.mcp.json`, `mcp_config.json` et `gemini-extension.json`, `"settings": []` sur Gemini CLI) avec repli documenté sur `/mcp` (`Bearer` / `?key=`) et `acces.poirierlavoie.ca/moi`.
- Compatibilité universelle ChatGPT Web & Desktop (`.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `scripts/empaqueter_plugin_chatgpt.py`), OpenAI Codex et API OpenAI Responses.
- Licence **Apache-2.0** (`LICENSE`) assortie du fichier d'attribution et de non-revendication [`NOTICE`](NOTICE).
- Migration de `gemini-extension.json` vers `type: "http"` + `url` et dimensionnement intrinsèque `256x256` pour `assets/logo.svg`.

---

## [3.0.1] — 2026-11-19

### Corrigé
- Remédiation d'audit et de tests de résistance (`calcul_delai.py`, `verifier_cotes.py`, `inspecter_piece.py`, réessai `403` sur requêtes libres `query`, élimination du dernier `except` nu).

---

## [3.0.0] — 2026-11-19

### Modifié
- Architecture v3.0.0 : **10 compétences** (5 orchestrateurs de phase `phase-*` + 5 compétences de service), **59 feuilles de référence**, **4 scripts Python stdlib**, noyau `SAFETY-KERNEL` v3 (incluant honnêteté perceptuelle et isolement des pièces non fiables), suivi `etat-dossier/` avec dégradation nuage, suite `evals/` à 77 scénarios, et prise en charge du corpus PDF Vague 1 (`110` textes dont directives QCCS/QCCQ et orientations AMF).

---

## [2.1.0] — 2026-11-18

### Ajouté
- Intégration de `MCP-Acces` (`acces.poirierlavoie.ca`), clé API CanLII personnelle obligatoire (**BYOK strict**), OAuth 2.1 et préambule Deep Research (`Claude Research` & `Gemini Deep Research`).

---

## [2.0.2] — 2026-11-16

### Corrigé
- Corrections des délais d'assignation et de présentation dans les fiches de procédure.

---

## [2.0.1] — 2026-11-16

### Amélioré
- Optimisation des descriptions YAML de compétences pour le déclenchement multi-modèles.

---

## [2.0.0] — 2026-11-16

### Modifié
- Refonte complète du greffon en architecture modulaire à 10 compétences et validation statique dédiée.

---

## [1.5.0] — 2026-11-15

### Ajouté
- Gouvernance GitHub (workflows `CodeQL`, `Scorecard`, `Trivy`, `Release`, `Vérification`, gabarits d'issues et `SECURITY.md`).
