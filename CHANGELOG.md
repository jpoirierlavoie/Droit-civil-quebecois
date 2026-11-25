# Journal des modifications / Changelog

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et [Semantic Versioning](https://semver.org/).

## [3.2.0] — 2026-11-25

### Ajouté
- **Première passe complète des 16 fiches `[FICHE À RÉDIGER]`** dans `analyse-et-strategie` (`preuve-directe.md`, `preuve-indirecte.md`, `preuve-documents-judiciaires.md`, `produit-fiche-preuve-et-temoins.md`), `production-et-conformite` (`cahier-des-procedures.md`) et `redaction-juridique` (`acte-demandes-cours-instance.md`, `acte-execution-et-oppositions.md`, `acte-injonction.md`, `acte-mesures-provisionnelles-autres.md`, `acte-moyens-preliminaires.md`, `acte-pourvoi-controle-judiciaire.md`, `acte-reconvention-intervention-garantie.md`, `acte-retractation-jugement.md`, `acte-saisie-avant-jugement.md`, `arg-argumentation-ecrite.md`, `contrat-ententes-judiciaires.md`), passées à `[NON VALIDÉ PAR LA PRATIQUE]` avec vecteurs législatifs et renvois `outils` actualisés.
- **Couverture complète de la suite `evals/scenarios.json` (`79` → `118` scénarios) :** ajout de `39` scénarios (`AS-05` à `AS-17`, `DP-03`, `PC-10`, `RJ-09` à `RJ-12`, `RD-25` à `RD-44`) couvrant l'ensemble des feuilles de référence restantes sans collision d'identifiants avec `PC-09` et `RJ-08`.

### Corrigé
- Renvoi exact à l'`art. 41 al. 3 C.p.c.` dans `skills/redaction-juridique/references/contrat-civil-commercial.md` (clause d'élection de for dans un contrat d'adhésion ou de consommation).

---

## [3.1.1] — 2026-11-25

### Ajouté
- Synchronisation complète avec **`MCP-Outils` `v2.2.0`** (`15` outils sur `outils` sur `6` familles : `taux_boc_rates`, `indice_ipc`, `loyer_tal`, hiérarchies GLEIF L1/L2/REPEX, lots RQA et `prime_plus_margin` sur `interets_1619`).
- Synchronisation complète avec **`MCP-Jurisprudence` `v2.3.0`** (`12` outils sur `juris`, portant le catalogue total du greffon à **`37` outils MCP** sous le plafond strict `<= 64` caractères) : ajout de `list_exempt_cases` (`58` car. sous Claude Code) et `check_exempt_cases` (`59` car. sous Claude Code ; contrôle automatique de dispense de reproduction et règles procédurales sur les `27` listes compilées, `QCCA`/`QCCS`/`QCCQ`/`TAT`/`TDP`/`TP`/`TMF`/`CF`/`COMC`) dans `production-et-conformite` (`SKILL.md`, `cahier-des-sources.md`), `phase-preparation-audience`, `recherche-juridique`, `redaction-juridique`, `evals/scenarios.json` (`PC-09`), `verifier.py`, `verifier_tout.py` et `scripts/regenerer_cache_mcp.py`.
- Alignement de `recherche-juridique` (`references/recherche-legislative.md`, `references/grille-prealables.md`, `SKILL.md`), de `verifier_tout.py` (`MockMcpServer` + `T4.4`) et de la suite `evals/` (`RJ-08`, précision QCCA sur `RJ-06`, `PC-09`, 79 scénarios) sur la **quarantaine à 8 domaines** (`core` par défaut, `cours-federales`, `financier`, `construction-immobilier`, `municipal-environnement`, `travail`, `penal`, `propriete-intellectuelle`, paramètres `domains`, `jurisdiction`, `forum`, radar `other_domains` et note marginale fédérale pondérée) de `MCP-Legislation`.

### Modifié
- Remplacement de `assets/logo.svg` par une fleur de lys royale bleue (`#003DA5`) originale publiée sous licence `Apache-2.0`, et mise à jour correspondante de [`NOTICE`](NOTICE) et [`README.md`](README.md).
- Polissage des manifestes : `"authentication": "ON_USE"` dans `.agents/plugins/marketplace.json`, description v3 à `37` outils dans `gemini-extension.json`, confirmation documentée de la préséance multi-outils de `.antigravity-plugin/plugin.json` sur `plugin.json` racine et mise à niveau semver `3.1.1` sur l'ensemble des manifestes et `evals/scenarios.json`.

---

## [3.1.0] — 2026-11-24

### Ajouté
- Auto-connexion **OAuth 2.1 PKCE `S256`** sans configuration préalable (`/mcp/oauth` par défaut dans `.mcp.json`, `mcp_config.json` et `gemini-extension.json`, `"settings": []` sur Gemini CLI) avec repli documenté sur `/mcp` (`Bearer` / `?key=`) et `acces.poirierlavoie.ca/moi`.
- Compatibilité universelle ChatGPT Web & Desktop (`.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `scripts/empaqueter_plugin_chatgpt.py`), OpenAI Codex et API OpenAI Responses.
- Manifeste dédié Antigravity `.antigravity-plugin/plugin.json` (`https://antigravity.google/schemas/v1/plugin.json`) et alignement du manifeste racine `plugin.json` sur le standard portable **Agent Plugins 1.0** (`https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`).
- Licence **Apache-2.0** (`LICENSE`) assortie du fichier d'attribution et de non-revendication [`NOTICE`](NOTICE) (incluant la réserve de propriété du Barreau du Québec sur le symbole du membre `assets/logo.svg`).
- Fichiers de gouvernance et documentation open source : [`AGENTS.md`](AGENTS.md) (synchronisé octet pour octet avec [`CLAUDE.md`](CLAUDE.md) et [`GEMINI.md`](GEMINI.md) sous `20 Ko`), [`CONTRIBUTING.md`](CONTRIBUTING.md), [`CHANGELOG.md`](CHANGELOG.md) et [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
- Validation CI de l'archive ChatGPT dans `.github/workflows/verify.yml` et publication automatisée de `dist/droit-civil-quebecois-chatgpt-universal.zip` (reproductible, permissions Unix `0755`/`0644`) et `.sha256` dans `.github/workflows/release.yml`.

### Modifié
- Mise à jour de `assets/logo.svg` vers le symbole vectoriel du membre du Barreau du Québec (et ajout de `icon` dans `.claude-plugin/plugin.json` et `$schema` dans `.claude-plugin/marketplace.json`), plus migration de `gemini-extension.json` vers `type: "http"` + `url`.
- Mise à jour de `scripts/synchroniser_plugin_gemini.py` (promotion `.antigravity-plugin/plugin.json` -> `plugin.json`, `Path.home()`, `DCQ_PLUGIN_SRC_DIR`), `scripts/empaqueter_plugin_chatgpt.py` (archive déterministe, liste d'exclusion élargie et parité `plugin.json`), `scripts/regenerer_cache_mcp.py`, `README.md`, `SECURITY.md`, des gabarits `.github/` et des suites `verifier.py` (parité `evals/scenarios.json`, syntaxe de tous les `.py`, liens Markdown), `verifier_tout.py` et `evals/test_verifier.py`.

### Sécurité
- Durcissement des scripts stdlib locaux (`inspecter_piece.py`, `controler_document.py`, `verifier_cotes.py`) contre les bombes de décompression (`zlib`, flux PDF `/ObjStm`, chunks PNG `zTXt`/`iTXt`, `word/document.xml` et plafond de taille de fichier).
- Permissions exécutables `100755` appliquées dans Git sur les scripts Python et délais/annulation de concurrence ajoutés aux flux CI (`verify.yml`, `codeql.yml`, `trivy.yml`).

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
