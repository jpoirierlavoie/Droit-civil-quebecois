# pratique-civile-quebecoise — Architecture, principes et consignes de travail

Directives de développement, architecture du cadre global et règles anti-dérive pour le greffon **Pratique civile québécoise** (`v1.6.1`). Ce document s'applique de façon identique à Claude et à Google Antigravity / Gemini CLI (`CLAUDE.md` et `GEMINI.md` sont identiques octet pour octet et restent sous 24 000 octets UTF-8).

> **Note sur Gemini CLI (`gemini-extension.json`) :** La racine déclare `"contextFileName": []` afin que `GEMINI.md` ne soit **jamais** injecté comme contexte système dans les sessions d'usage juridique normal des utilisateurs finaux. Il gouverne exclusivement les agents qui modifient ce dépôt.

---

## 1. Rôle dans le cadre global à trois couches

`pratique-civile-quebecoise` est le greffon cadre multiplateforme (Claude Code, Claude Desktop, claude.ai, Google Antigravity, Gemini CLI) orchestrant cinq compétences de litige civil québécois au-dessus de trois serveurs MCP complémentaires et d'un socle d'infrastructure partagé :

```
             ┌────────────────────────────────────────────────────────┐
             │       pratique-civile-quebecoise (Plugin Cadre)        │
             │   5 compétences : recherche-juridique, analyse-doc,     │
             │  calendrier-proc, redaction-juridique, déontologie     │
             └──────┬───────────────────────┬──────────────────┬──────┘
                    │                       │                  │
   (10 outils `legislation_*`)    (10 outils `jurisprudence_*`) (12 outils `calendrier_*`, `interets_*`,
                    │                       │            `greffe_*`, `palais_*`, `registre_*`,
                    │                       │            `adresse_*`, `terminologie_*`)
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

### Cartographie des cinq compétences (`skills/`)
1. **`skills/recherche-juridique`** : Consomme les 10 outils `legislation_*`, les 10 outils `jurisprudence_*` (dont `jurisprudence_citator` avec `en` dans le chemin, et `jurisprudence_parse_citation` hors ligne), ainsi que `interets_compute_1619`, `greffe_parse_court_file_number`, `palais_list`, `palais_get`, `registre_search_entities`, `registre_get_entity`, `adresse_verify`, `terminologie_lookup` et `terminologie_attestations`.
2. **`skills/calendrier-procedural`** : Consomme `calendrier_compute_deadlines` et `calendrier_list_holidays` avec repli local déterministe `skills/calendrier-procedural/scripts/calcul_delai.py`. Ne nomme aucun outil `legislation_*` ni `jurisprudence_*`.
3. **`skills/redaction-juridique`** : Consomme `legislation_get_article` (dont `lang="en"` pour purger les anglicismes de common law), `legislation_search_text`, `calendrier_compute_deadlines`, `interets_compute_1619`, `registre_search_entities`, `registre_get_entity`, `adresse_verify`, `terminologie_lookup`, `terminologie_attestations` et `terminologie_scan_text`.
4. **`skills/analyse-documentaire`** : Ne nomme **aucun** outil MCP directement ; exprime les besoins abstraits du contrat d'information et les quatre régimes de protection (`0` à `3`).
5. **`skills/deontologie-professionnelle`** : Ne nomme **aucun** outil MCP directement ; signale les obligations professionnelles au texte.

---

## 2. ⛔ Évaluation d'impact obligatoire avant clôture (intra-dépôt, `README.md`, pages publiques HTML aval et inter-dépôts)

**Aucune tâche touchant `pratique-civile-quebecoise` n'est terminée tant que son impact n'a pas été évalué, répercuté et explicitement rapporté sur chacun des quatre axes ci-dessous** (« non touché » doit être vérifié et énoncé, jamais passé sous silence) :

| # | Axe d'impact | Éléments à inspecter | Ce qui impose une action |
|---|---|---|---|
| 1 | **Compétences (`skills/`), scripts et `evals/`** | `skills/*/SKILL.md`, `references/`, `scripts/`, `evals/scenarios.json`, `evals/executer_evals.py`, `verifier.py` | Toute évolution d'outil MCP, de flux juridique, de contrat d'information ou de scénario d'évaluation |
| 2 | **`README.md`, sécurité, licence et manifestes** | `README.md`, `SECURITY.md`, `LICENSE` (`CC-BY-NC-SA-4.0`), `CLAUDE.md`, `GEMINI.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `plugin.json`, `mcp_config.json`, `gemini-extension.json`, `.mcp.json` | Tout changement de version (parité semver stricte), de licence (`EXPECTED_LICENSE`), d'authentification (`MCP_LEGISLATION_SECRET`, `MCP_JURISPRUDENCE_SECRET`), de liste d'outils ou de politique de confidentialité |
| 3 | **Pages publiques HTML (`GET /`) et fiches `/mcp/server-card` des serveurs MCP liés** | `src/site.ts` (+ `src/site.i18n.ts` / `catalogue.json`) et `/mcp/server-card` dans `MCP-Legislation`, `MCP-Jurisprudence` et `MCP-Outils` | Ce greffon ne sert pas de page HTTP propre ; toutefois, tout changement touchant les URL de connexion, la description du greffon, la forme des secrets ou la posture de confidentialité/licence doit être confronté aux **pages publiques HTML (`GET /`)** et aux **`README.md`** des trois serveurs MCP afin d'éviter toute contradiction entre ce que le plugin configure et ce que les pages HTML documentent |
| 4 | **Impacts inter-dépôts (`Cross-repository`)** | **`MCP-Legislation`**, **`MCP-Jurisprudence`**, **`MCP-Outils`** et **`MCP-Socle`** (noms exacts des 32 outils, schémas, porteurs Bearer/`?key=`, sécurité/privilège, synchronisation du cache Antigravity et du répertoire d'installation Gemini) | Vérifier l'alignement réel sur les serveurs cibles et leurs suites de tests |

---

## 3. Invariants structurels et règles de sécurité (`verifier.py`)

Toute modification doit continuer à passer `python verifier.py` sans affaiblir aucun contrôle :

1. **Inventaire strict (`ROOT_ALLOWLIST`, `EVALS_ALLOWLIST`)** : Aucun fichier orphelin à la racine ni sous `skills/`. Tout nouveau fichier racine autorisé doit être justifié et inscrit dans `ROOT_ALLOWLIST` (`verifier.py`).
2. **Parité exacte des manifestes et licence** :
   - Version semver identique partout (`1.6.1`) : `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `plugin.json`, `gemini-extension.json`, `verifier_tout.py`.
   - Licence SPDX identique : `CC-BY-NC-SA-4.0` dans `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `LICENSE` et `verifier.py` (`EXPECTED_LICENSE`). Ne jamais ajouter de clé non reconnue dans `plugin.json` (`ANTIGRAVITY_PLUGIN_KEYS`).
   - `"contextFileName": []` dans `gemini-extension.json` reste vide.
3. **Configuration MCP et hygiène des secrets** :
   - `.mcp.json`, `mcp_config.json` et `gemini-extension.json` doivent déclarer exactement `legislation`, `jurisprudence` et `outils` (`https://legislation.poirierlavoie.ca/mcp`, `https://jurisprudence.poirierlavoie.ca/mcp`, `https://outils.poirierlavoie.ca/mcp`).
   - `MCP_LEGISLATION_SECRET` et `MCP_JURISPRUDENCE_SECRET` référencés uniquement par variable d'environnement ; `sensitive: true` sous Gemini CLI ; aucune propriété `eager` dans `mcp_config.json`.
   - **Zéro fuite** : aucun secret hexadécimal (`≥ 32` car.), aucun chemin personnel local, aucun identifiant de dépôt retiré (`RETIRED_REPO_SLUGS` dans `verifier.py`).
4. **Architecture des compétences (`skills/*/SKILL.md`)** :
   - En-tête YAML contenant uniquement `name` et `description` (`≤ 1 024` car., sans `<`/`>`, incluant `En anglais` et `Ne pas utiliser pour`).
   - Corps `< 3 000` mots ; ossature en 7 invariants (`# `, intro, `## Le principe qui gouverne` / `## La règle asymétrique`, `## La méthode` avant `## Ce qu'il faut du dossier`, puis le triptyque `## Le périmètre`, `## Contrôle avant remise`, `## Fichiers de référence [et outillage local]`).
   - Références exactes 1:1 avec `references/` et `scripts/`.
5. **Isolation du contrat d'information** : Aucun nom d'outil de gestionnaire de dossiers (`BANNED_PATTERNS` dans `verifier.py`), aucune variable `$ARGUMENTS` ou `${CLAUDE_...}`, et seuls les préfixes autorisés (`legislation`, `jurisprudence`, `greffe`, `palais`, `calendrier`, `interets`, `registre`, `adresse`, `terminologie`) sont permis pour les appels d'outils cités.
6. **Encodage** : UTF-8 sans BOM et fins de ligne LF (`\n`) sur tous les fichiers.

---

## 4. Commandes de synchronisation et de vérification

```powershell
# 1. Resynchroniser le répertoire d'extension Antigravity / Gemini AVANT le cache MCP
#    (modifier mcp_config.json déclenche l'observateur d'Antigravity, qui écrase avec
#    parameters: null les outils dont l'identifiant composé dépasse 64 caractères)
python scripts/synchroniser_plugin_gemini.py --apply
python scripts/regenerer_cache_mcp.py --apply
# gemini.cmd extensions update pratique-civile-quebecoise   # si installé dans Gemini CLI

# 2. Contrôles statiques et scénarios d'évaluation locaux
python verifier.py
python evals/executer_evals.py --auto-test

# 3. Suite multi-paliers inter-serveurs (simulation locale ou réseau en direct)
python verifier_tout.py --mode mock
# python verifier_tout.py --mode live
```
