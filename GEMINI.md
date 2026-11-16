# droit-civil-quebecois — Architecture, principes et consignes de travail

Directives de développement, architecture à trois couches et règles anti-dérive pour le greffon **Droit civil québécois** (`droit-civil-quebecois`, `v2.0.1`, anciennement `pratique-civile-quebecoise`). Ce document gouverne de façon identique Claude et Google Antigravity / Gemini CLI (`CLAUDE.md` et `GEMINI.md` doivent rester identiques octet pour octet et sous **24 000 octets** UTF-8 LF).

> **Note Gemini CLI (`gemini-extension.json`) :** La racine déclare `"contextFileName": []` afin que `GEMINI.md` ne soit **jamais** injecté comme contexte système dans les sessions d'usage juridique normal des utilisateurs finaux. Il s'applique exclusivement aux agents qui modifient ce dépôt.

---

## 1. Rôle dans le cadre global à trois couches

`droit-civil-quebecois` est le greffon cadre multiplateforme (Claude Code, Claude Desktop, claude.ai, Google Antigravity, Gemini CLI) orchestrant **5 compétences** à découverte progressive au-dessus de **3 serveurs MCP spécialisés** (`lois`, `juris`, `outils`) et d'un socle de transport partagé :

```
             ┌────────────────────────────────────────────────────────┐
             │      droit-civil-quebecois (Plugin Cadre v2.0.1)       │
             │  5 routeurs SKILL.md · 17 feuilles · 2 scripts stdlib  │
             └──────┬───────────────────────┬──────────────────┬──────┘
                    │                       │                  │
        (serveur `lois`, 10 outils)  (serveur `juris`, 10)  (serveur `outils`, 12)
                    │                       │                  │
                    ▼                       ▼                  ▼
         ┌─────────────────────┐ ┌─────────────────────┐ ┌──────────────────────────┐
         │   MCP-Legislation   │ │  MCP-Jurisprudence  │ │        MCP-Outils        │
         │  (Worker Cloudflare │ │ (Worker Cloudflare  │ │    (Worker Cloudflare    │
         │  D1 + Vectorize +   │ │  D1 cache CanLII    │ │   public, D1 lecture     │
         │    Workers AI)      │ │  authentifié Bearer │ │   seule, zéro secret)    │
         └──────────┬──────────┘ └──────────┬──────────┘ └──────────────────────────┘
                    │                       │
                    └───────────┬───────────┘
                                ▼ (dépendance de dev `#v0.7.0`, zéro runtime dep)
                 ┌─────────────────────────────┐
                 │          MCP-Socle          │
                 │  Transport JSON-RPC 2.0     │
                 │  Streamable HTTP sans état  │
                 │  Auth SHA-256 temps constant│
                 │  Zéro concept juridique     │
                 └─────────────────────────────┘
```

### Cartographie des 5 compétences, 17 feuilles terminales et 2 scripts (`skills/`)

Conception **Découverte progressive à 3 niveaux** (*3-Tier Progressive Discovery*) + **Calibration de rigueur à 3 paliers** (Palier 1 *Triage*, Palier 2 *Dossier*, Palier 3 *Tribunal / dépôt complet*) :

1. **`skills/recherche-juridique`**
   - Feuilles (`3`) : `grille-prealables.md`, `strategie-sources.md`, `doctrine-et-livrables.md`
2. **`skills/analyse-juridique`**
   - Feuilles (`4`) : `remue-meninges-et-strategie.md`, `tri-mentions-et-chronologie.md`, `preuve-et-protection.md`, `interrogatoire-prealable.md`
   - Script (`1`) : `scripts/inspecter_piece.py` (inspection locale de pièces, zéro réseau)
3. **`skills/redaction-juridique`**
   - Feuilles (`4`) : `actes-de-procedure.md`, `argumentation-appel-et-sources.md`, `correspondance-et-contrats.md`, `anti-contamination-bilingue.md`
4. **`skills/administration-litige`**
   - Feuilles (`3`) : `echeanciers-cpc.md`, `bordereaux-concordance-et-endos.md`, `tableaux-quantum-et-frais.md`
   - Script (`1`) : `scripts/calcul_delai.py` (repli local déterministe du calendrier C.p.c., zéro réseau)
5. **`skills/deontologie-et-pratique`**
   - Feuilles (`3`) : `radar-deontologique.md`, `identification-conflits-et-mandat.md`, `facturation-temps-et-fideicommis.md`

### Règles transversales de fond (`v2.0.1`)

- **Noyau de sécurité canonique (`SAFETY-KERNEL`) :** Les 5 `SKILL.md` partagent au bit près le même bloc `<!-- SAFETY-KERNEL:START -->...<!-- SAFETY-KERNEL:END -->` (contrôle SHA-256 dans `verifier.py`), couvrant la confidentialité (recherche web et champs de recherche libre `query` sans noms ni faits identifiants), le repérage des connecteurs par outils signatures/alias et chargement des outils différés avant arrêt sur le volet touché (*fail-closed*), l'étanchéité bijuridique et la présomption `CONFIDENTIEL`. Les crochets normalisés sont `[À CONFIRMER]`, `[DATE À CONFIRMER]`, `[À COMPLÉTER]`, `[À VÉRIFIER VIA LOIS]` et `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`.
- **Feuilles terminales (« impasses ») :** Une compétence ne renvoie jamais vers un autre `SKILL.md`. Seuls les routeurs `SKILL.md` peuvent pointer vers une feuille voisine précise (`../<compétence>/references/<feuille>.md`) avec repli autonome via `lois` ; les feuilles sous `references/` ne contiennent aucun lien relatif `../`.
- **Aucune décharge statutaire figée :** Jamais de copie intégrale d'articles du C.c.Q. ou du C.p.c. dans les feuilles ; privilégier les lots d'identifiants d'articles à charger via `lois.get_articles`, les paires confondables et les silences législatifs.
- **Palier 3 et lecture CanLII :** Tout arrêt dont le texte intégral officiel (PDF ou document complet CanLII/SOQUIJ/CAIJ) n'a pas été lu en session utilise explicitement le marqueur `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`. Par défaut, `redaction-juridique` produit le livrable complet prêt au dépôt, tout en offrant un mode explicite *« bloc de contenu seul »*.

---

## 2. Évaluation d'impact obligatoire avant clôture (4 axes)

**Aucune tâche touchant `droit-civil-quebecois` n'est terminée tant que son impact n'a pas été évalué, répercuté et explicitement rapporté sur chacun des quatre axes ci-dessous** (« non touché » doit être vérifié et énoncé, jamais passé sous silence) :

| # | Axe d'impact | Éléments à inspecter | Ce qui impose une action |
|---|---|---|---|
| 1 | **Compétences (`skills/`), scripts et `evals/`** | `skills/*/SKILL.md`, `references/`, `scripts/`, `evals/scenarios.json`, `evals/executer_evals.py`, `verifier.py` | Toute évolution d'outil MCP, de palier de rigueur, de feuillage, de contrat de confidentialité ou de scénario d'évaluation |
| 2 | **`README.md`, sécurité, licence et manifestes** | `README.md`, `SECURITY.md`, `LICENSE` (`CC-BY-NC-SA-4.0`), `CLAUDE.md`, `GEMINI.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `plugin.json`, `mcp_config.json`, `gemini-extension.json`, `.mcp.json` | Tout changement de version (parité semver stricte), de licence (`EXPECTED_LICENSE`), de secrets (`MCP_LEGISLATION_SECRET`, `MCP_JURISPRUDENCE_SECRET`), de liste d'outils ou de politique de confidentialité |
| 3 | **Pages publiques HTML (`GET /`) et fiches `/mcp/server-card` des serveurs MCP liés** | `src/site.ts` (+ `src/site.i18n.ts` / `catalogue.json`) et `/mcp/server-card` dans `MCP-Legislation`, `MCP-Jurisprudence` et `MCP-Outils` | Ce greffon ne sert pas de page HTTP propre ; toutefois, tout changement touchant les URL de connexion, la description du greffon, les noms d'outils ou la posture de confidentialité/licence doit être confronté aux **pages publiques HTML (`GET /`)**, aux **`/mcp/server-card`** et aux **`README.md`** des trois serveurs MCP |
| 4 | **Impacts inter-dépôts (`Cross-repository`)** | **`MCP-Legislation`**, **`MCP-Jurisprudence`**, **`MCP-Outils`** et **`MCP-Socle`** (renommage exact des 32 outils, serveurs `lois`/`juris`/`outils`, porteurs Bearer, synchronisation locale Antigravity / Gemini CLI) | Vérifier l'alignement réel et l'ordre de déploiement inter-dépôts (Phases 1 -> 2 -> 3 ci-dessous) |

### Coordination multi-dépôts (Phases 1 à 3)

- **Phase 1 (ce dépôt, branche `v2.0`) :** Refonte complète des compétences, feuilles, manifestes (`droit-civil-quebecois` v2.0.0, clés `lois`/`juris`/`outils`, 32 noms d'outils courts), `verifier.py`, `evals/`, `verifier_tout.py --mode mock`, documentation et scripts de synchronisation. Ne pas exécuter `--apply` contre `~/.gemini/` avant le déploiement des serveurs Phase 2.
- **Phase 2 (Workers Cloudflare aval) :** Mettre à jour et déployer `MCP-Legislation` (10 outils sans préfixe `legislation_`), `MCP-Jurisprudence` (10 outils sans préfixe `jurisprudence_`) et `MCP-Outils` (7 outils raccourcis : `calendrier_holidays`, `calendrier_deadlines`, `interets_1619`, `greffe_parse_number`, `registre_search`, `termino_attestations`, `terminologie_scan`), ainsi que leurs tests, `README.md` et pages publiques HTML/`server-card`.
- **Phase 3 (Publication & postes locaux) :** Exécuter `python verifier_tout.py --mode live`, fusionner `v2.0` -> `main`, synchroniser Antigravity (`python scripts/synchroniser_plugin_gemini.py --apply`), puis désinstaller l'ancien greffon `pratique-civile-quebecoise` sous Claude Code et Gemini CLI.

---

## 3. Invariants structurels, budget 64 car. et sécurité (`verifier.py`)

Toute modification doit passer `python verifier.py` (sortie strictement muette, code `0`) :

1. **Inventaire strict (`ROOT_ALLOWLIST`, `EVALS_ALLOWLIST`) :** Aucun fichier orphelin à la racine ni sous `skills/`. Tout nouveau fichier racine doit être justifié et inscrit dans `ROOT_ALLOWLIST` (`verifier.py`).
2. **Parité exacte des manifestes et licence (`2.0.1`) :**
   - `name` / slug = `droit-civil-quebecois` ; `displayName` = `Droit civil québécois` ; dépôt = `https://github.com/jpoirierlavoie/droit-civil-quebecois`.
   - Version semver identique partout : `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (`metadata.version` et `plugins[0].version`), `plugin.json`, `gemini-extension.json`, `verifier_tout.py`.
   - Licence SPDX = `CC-BY-NC-SA-4.0` dans `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `LICENSE` et `verifier.py`.
   - Clés strictes dans `plugin.json` (`ANTIGRAVITY_PLUGIN_KEYS`), `"contextFileName": []` dans `gemini-extension.json`.
3. **Configuration MCP, secrets et plafond `<= 64` caractères :**
   - `.mcp.json`, `mcp_config.json` et `gemini-extension.json` déclarent exactement les clés `lois`, `juris` et `outils` (`https://legislation.poirierlavoie.ca/mcp`, `https://jurisprudence.poirierlavoie.ca/mcp`, `https://outils.poirierlavoie.ca/mcp`).
   - `MCP_LEGISLATION_SECRET` et `MCP_JURISPRUDENCE_SECRET` référencés uniquement par variable d'environnement ; `sensitive: true` sous Gemini CLI ; aucune clé `eager` dans `mcp_config.json`.
   - **Plafond d'identifiant composé `<= 64` caractères vérifié sur les 32 outils :**
     - Claude Code : `mcp__plugin_droit-civil-quebecois_<srv>__<tool>` -> max **62 car.** (`outils` + `calendrier_deadlines` ou `termino_attestations`).
     - Google Antigravity : `mcp_droit-civil-quebecois_<srv>_<tool>` -> max **52 car.** (zéro troncature / zéro `parameters: null`).
4. **Budgets et structure des compétences (`skills/`) :**
   - En-tête YAML contenant uniquement `name` et `description` (`<= 850` car., sans `<`/`>`, incluant `En anglais` et `Ne pas utiliser pour`).
   - Corps `SKILL.md <= 1 000` mots ; ouverture par `# ` ; parité SHA-256 exacte du bloc `SAFETY-KERNEL` sur les 5 `SKILL.md` ; correspondance 1:1 exacte avec `references/*.md` et `scripts/*.py` locaux ; interdiction de `../<autre>/SKILL.md`.
   - Chaque feuille `references/*.md` : `<= 1 500` mots et `<= 12 288` octets, zéro lien relatif `../`.
   - Total `skills/**/*.md <= 143 360` octets (`140 KB`).
5. **Purge `v1` et isolation DMS (`BANNED_PATTERNS`, `RETIRED_V1_*`, `LEGACY_PLUGIN_ALLOW_MIGRATION`) :**
   - Interdiction absolue de tout nom d'outil de gestionnaire de dossiers (`get_dossier`, `create_note`, `create_task`, etc.), des codes DMS fermés hérités (`PROC_DEM_INTRO`, `CAB_MEMO`, etc.), des mentions de l'ancienne application, des variables `$ARGUMENTS` / `${CLAUDE_...}`, des préfixes d'outils `mcp__`, `qclaw_`, `canlii_`, des anciens noms de compétences (`analyse-documentaire`, `calendrier-procedural`, `deontologie-professionnelle`) et des 27 anciens noms d'outils `v1`.
   - `"pratique-civile-quebecoise"` est strictement limité à `LEGACY_PLUGIN_ALLOW_MIGRATION` (`verifier.py`, `README.md`, `CLAUDE.md`, `GEMINI.md`, `scripts/synchroniser_plugin_gemini.py`, `scripts/regenerer_cache_mcp.py`).
6. **Encodage :** UTF-8 sans BOM et fins de ligne LF (`\n`) sur tous les fichiers (sauf `LICENSE`).

---

## 4. Commandes de synchronisation et de vérification

```powershell
# 1. Contrôles statiques (muet, sortie 0) et bilan de taille
python verifier.py
python verifier.py --stats

# 2. Scénarios d'évaluation locaux et tests déterministes des 2 scripts
python evals/executer_evals.py --auto-test

# 3. Suite E2E multi-paliers (simulation locale ou réseau réel après Phase 2)
python verifier_tout.py --mode mock
# python verifier_tout.py --mode live

# 4. Déploiement local Antigravity / Gemini CLI (après déploiement Phase 2)
python scripts/synchroniser_plugin_gemini.py --apply
# python scripts/regenerer_cache_mcp.py --apply   # optionnel depuis les dépôts locaux
```
