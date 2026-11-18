# droit-civil-quebecois — Architecture, principes et consignes de travail

Directives de développement, architecture multi-dépôts et règles anti-dérive pour le greffon **Droit civil québécois** (`droit-civil-quebecois`, `v2.1.0`, anciennement `pratique-civile-quebecoise`). Ce document gouverne de façon identique Claude et Google Antigravity / Gemini CLI (`CLAUDE.md` et `GEMINI.md` doivent rester identiques octet pour octet et sous **24 000 octets** UTF-8 LF).

> **Note Gemini CLI (`gemini-extension.json`) :** La racine déclare `"contextFileName": []` afin que `GEMINI.md` ne soit **jamais** injecté comme contexte système dans les sessions d'usage juridique normal des utilisateurs finaux. Il s'applique exclusivement aux agents qui modifient ce dépôt.

---

## 1. Rôle dans le cadre global multi-dépôts

`droit-civil-quebecois` est le greffon cadre multiplateforme (Claude Code, Claude Desktop, `claude.ai` / Claude Research, Google Antigravity, Gemini CLI, Gemini App / Vertex AI, Gemini API Deep Research) orchestrant **5 compétences** à découverte progressive au-dessus de **3 serveurs MCP spécialisés** (`lois`, `juris`, `outils`), d'un **portail d'accès et serveur OAuth 2.1 dédié** (`MCP-Acces`), d'une base D1 partagée (`DB_IDENTITE` / `mcp-identite`) et d'un socle partagé :

```
             ┌────────────────────────────────────────────────────────┐
             │      droit-civil-quebecois (Plugin Cadre v2.1.0)       │
             │  5 routeurs SKILL.md · 17 feuilles · 2 scripts stdlib  │
             └──────┬───────────────────────┬──────────────────┬──────┘
                    │ /mcp (404)            │ /mcp (404)       │ /mcp (public)
                    │ /mcp/oauth (401 OAuth)│ /mcp/oauth (401) │
                    ▼                       ▼                  ▼
         ┌─────────────────────┐ ┌─────────────────────┐ ┌──────────────────────────┐
         │   MCP-Legislation   │ │  MCP-Jurisprudence  │ │        MCP-Outils        │
         │  D1 + Vectorize +   │ │  D1 cache CanLII    │ │   Public, 3 D1 lecture   │
         │  Workers AI +       │ │  BYOK CanLII strict │ │   seule, zéro secret,    │
         │  hybride_permis     │ │  sans fetched_at    │ │   zéro journalisation    │
         └──────────┬──────────┘ └──────────┬──────────┘ └──────────────────────────┘
                    │                       │
                    ├───────────┬───────────┴────┐
                    │           ▼ (dev `#v0.8.0`) ▼ (D1 partagée `mcp-identite`)
                    │  ┌──────────────────┐  ┌──────────────────────────────────────┐
                    │  │    MCP-Socle     │  │              MCP-Acces               │
                    │  │ Transport 2026   │  │     https://acces.poirierlavoie.ca   │
                    └──│ Auth · OAuth 2.1 │◄─┤ Admission Barreau · Coffre AES-GCM · │
                       │ Coffre · Gouverne│  │ Portail /moi · Serveur OAuth PKCE    │
                       └──────────────────┘  └──────────────────────────────────────┘
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

### Règles transversales de fond (`v2.1.0`)

- **Noyau de sécurité canonique (`SAFETY-KERNEL`) :** Les 5 `SKILL.md` partagent au bit près le même bloc `<!-- SAFETY-KERNEL:START -->...<!-- SAFETY-KERNEL:END -->` (contrôle SHA-256 dans `verifier.py`), couvrant la confidentialité (recherche web et champs de recherche libre `query` sans noms ni faits identifiants), le repérage des connecteurs par outils signatures/alias et chargement des outils différés avant arrêt sur le volet touché (`401`, `404`, `429`, `[CLEF_ABSENTE]`, `[CLEF_REFUSEE]`, `QUOTA_EPUISE`, hors ligne — redirection vers `acces.poirierlavoie.ca/moi`), l'étanchéité bijuridique et la présomption `CONFIDENTIEL`. Les crochets normalisés sont `[À CONFIRMER]`, `[DATE À CONFIRMER]`, `[À COMPLÉTER]`, `[À VÉRIFIER VIA LOIS]` et `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`.
- **Feuilles terminales (« impasses ») :** Une compétence ne renvoie jamais vers un autre `SKILL.md`. Seuls les routeurs `SKILL.md` peuvent pointer vers une feuille voisine précise (`../<compétence>/references/<feuille>.md`) avec repli autonome via `lois` ; les feuilles sous `references/` ne contiennent aucun lien relatif `../`.
- **BYOK CanLII, double montage et zéro-log :** `/mcp` retourne uniformément `404` à corps vide sur `lois` et `juris`, tandis que `/mcp/oauth` retourne `401` RFC 9728 PKCE `S256` via `acces.poirierlavoie.ca`. Sur `juris`, chaque titulaire utilise sa clé API CanLII personnelle (en-tête `X-Clef-CanLII` ou coffre `DB_IDENTITE.coffre_clef`) vérifiée avant toute lecture du cache partagé, sans retombée opérateur. Aucune écriture d'exécution dans `search_log`/`api_usage`, et `observability.enabled = false`.
- **Aucune décharge statutaire figée :** Jamais de copie intégrale d'articles du C.c.Q. ou du C.p.c. dans les feuilles ; privilégier les lots d'identifiants d'articles à charger via `lois.get_articles`, les paires confondables et les silences législatifs.
- **Palier 3 et lecture CanLII :** Tout arrêt dont le texte intégral officiel (PDF ou document complet CanLII/SOQUIJ/CAIJ) n'a pas été lu en session utilise explicitement le marqueur `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`. Par défaut, `redaction-juridique` produit le livrable complet prêt au dépôt, tout en offrant un mode explicite *« bloc de contenu seul »*.

---

## 2. Évaluation d'impact obligatoire avant clôture (4 axes)

**Aucune tâche touchant `droit-civil-quebecois` n'est terminée tant que son impact n'a pas été évalué, répercuté et explicitement rapporté sur chacun des quatre axes ci-dessous** (« non touché » doit être vérifié et énoncé, jamais passé sous silence) :

| # | Axe d'impact | Éléments à inspecter | Ce qui impose une action |
|---|---|---|---|
| 1 | **Compétences (`skills/`), scripts et `evals/`** | `skills/*/SKILL.md`, `references/`, `scripts/`, `evals/scenarios.json`, `evals/executer_evals.py`, `verifier.py`, `verifier_tout.py` | Toute évolution d'outil MCP, de palier de rigueur, de mode d'échec/BYOK, de contrat de confidentialité ou de scénario d'évaluation |
| 2 | **`README.md`, sécurité, licence et manifestes** | `README.md`, `SECURITY.md`, `LICENSE` (`CC-BY-NC-SA-4.0` + autorisation de pratique professionnelle), `CLAUDE.md`, `GEMINI.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `plugin.json`, `mcp_config.json`, `gemini-extension.json`, `.mcp.json` | Tout changement de version (parité semver stricte), de licence (`EXPECTED_LICENSE` + mentions d'autorisation), de secrets (`MCP_LEGISLATION_SECRET`, `MCP_JURISPRUDENCE_SECRET`), de liste d'outils ou de politique de confidentialité |
| 3 | **Pages publiques HTML (`GET /`) et fiches `/mcp/server-card` des serveurs MCP liés** | `src/site.ts` (+ `src/site.i18n.ts` / `catalogue.json`), `/mcp/server-card` et `/.well-known/oauth-protected-resource/mcp/oauth` dans `MCP-Legislation`, `MCP-Jurisprudence`, `MCP-Outils` et `MCP-Acces` | Ce greffon ne sert pas de page HTTP propre ; toutefois, tout changement touchant les URL de connexion, la description du greffon, les noms d'outils ou la posture de confidentialité/licence doit être confronté aux **pages publiques HTML (`GET /`)**, aux **`/mcp/server-card`** et aux **`README.md`** des serveurs MCP |
| 4 | **Impacts inter-dépôts (`Cross-repository`)** | **`MCP-Socle`**, **`MCP-Acces`**, **`MCP-Legislation`**, **`MCP-Jurisprudence`** et **`MCP-Outils`** (identité D1 `mcp-identite`, BYOK, OAuth 2.1 `/mcp/oauth`, synchronisation locale Antigravity / Gemini CLI) | Vérifier l'alignement réel et l'ordre de déploiement inter-dépôts (Phases 1 -> 5 ci-dessous) |

### Coordination multi-dépôts (Phases 1 à 5)

- **Phase 1 (`MCP-Socle` `#v0.8.0` — livrée localement) :** Primitives d'identité `DB_IDENTITE`, coffre `HKDF-SHA256` + `AES-256-GCM`, OAuth 2.1 PKCE `S256` / RFC 9728 / CIMD, quarantaine IP Deep Research (`G32`) et purges Loi 25 (`G16`, `G18`).
- **Phase 2 (`MCP-Acces` `v1.0.0` — livrée localement) :** Portail `acces.poirierlavoie.ca` (`/demande`, `/moi`, `/exploitant`), migrations D1 `mcp-identite`, courriel `SendEmail`, serveur OAuth 2.1 et documents publics (`/cgu`, `/confidentialite`, `/attestation`, `/conformite`, `/gouverne`).
- **Phase 3 (`MCP-Legislation` & `MCP-Jurisprudence` — livrée localement) :** Passage à `@poirierlavoie/mcp-socle#v0.8.0`, liaison `DB_IDENTITE`, double montage `/mcp` (`404` uniforme) + `/mcp/oauth` (`401` RFC 9728), BYOK CanLII strict (`G8`, `G38`), `hybride_permis`, retrait de `search_log`, désactivation d'`observability` (`G37`) et limiteurs Deep Research (`1011..1025`).
- **Phase 4 (`droit-civil-quebecois` `v2.1.0` & `MCP-Outils`) :** Alignement des manifestes, `SAFETY-KERNEL`, `strategie-sources.md`, `LICENSE` (autorisation complémentaire de pratique professionnelle), `README.md`, `SECURITY.md`, guides Deep Research et `verifier_tout.py`.
- **Phase 5 (Bascule distante & postes locaux) :** Pousser `MCP-Socle#v0.8.0` puis remplacer `"file:../MCP-Socle"` par `"github:jpoirierlavoie/MCP-Socle#v0.8.0"` dans `MCP-Acces`, `MCP-Legislation` et `MCP-Jurisprudence` ; provisionner D1 `mcp-identite` (`enam`), déployer `MCP-Acces` puis Phase 3a, créer le compte exploitant #1, exécuter `python verifier_tout.py --mode live`, retirer les secrets hérités en Phase 3b et synchroniser Antigravity (`python scripts/synchroniser_plugin_gemini.py --apply`).

---

## 3. Invariants structurels, budget 64 car. et sécurité (`verifier.py`)

Toute modification doit passer `python verifier.py` (sortie strictement muette, code `0`) :

1. **Inventaire strict (`ROOT_ALLOWLIST`, `EVALS_ALLOWLIST`) :** Aucun fichier orphelin à la racine ni sous `skills/`. Tout nouveau fichier racine doit être justifié et inscrit dans `ROOT_ALLOWLIST` (`verifier.py`).
2. **Parité exacte des manifestes et licence (`2.1.0`) :**
   - `name` / slug = `droit-civil-quebecois` ; `displayName` = `Droit civil québécois` ; dépôt = `https://github.com/jpoirierlavoie/droit-civil-quebecois`.
   - Version semver identique partout : `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (`metadata.version` et `plugins[0].version`), `plugin.json`, `gemini-extension.json`, `verifier_tout.py`.
   - Licence SPDX = `CC-BY-NC-SA-4.0` dans `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `LICENSE` et `verifier.py`, accompagnée de l'**Autorisation complémentaire de pratique professionnelle du droit** (*Companion Professional Legal Practice Grant*) dans `LICENSE`.
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
6. **Encodage :** UTF-8 sans BOM et fins de ligne LF (`\n`) sur **tous** les fichiers du dépôt, y compris `LICENSE`.

---

## 4. Commandes de synchronisation et de vérification

```powershell
# 1. Contrôles statiques (muet, sortie 0) et bilan de taille
python verifier.py
python verifier.py --stats

# 2. Scénarios d'évaluation locaux et tests déterministes des 2 scripts
python evals/executer_evals.py --auto-test

# 3. Suite E2E multi-paliers (simulation locale ou réseau réel après Phase 5)
python verifier_tout.py --mode mock
# python verifier_tout.py --mode live

# 4. Déploiement local Antigravity / Gemini CLI (après bascule Phase 5)
python scripts/synchroniser_plugin_gemini.py --apply
# python scripts/regenerer_cache_mcp.py --apply   # optionnel depuis les dépôts locaux
```
