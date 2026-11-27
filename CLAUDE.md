# droit-civil-quebecois — Architecture, principes et consignes de travail

Directives de développement, architecture multi-dépôts à trois couches et règles anti-dérive pour le greffon **Droit civil québécois** (`droit-civil-quebecois`, `v3.4.0`). Ce document gouverne de façon identique OpenAI Codex, Claude Code et Google Antigravity / Gemini CLI (`AGENTS.md`, `CLAUDE.md` et `GEMINI.md` doivent rester identiques octet pour octet et sous **24 000 octets** UTF-8 LF).

> **Portée en session finale :** `gemini-extension.json` fixe `"contextFileName": []`, Antigravity ignore les fichiers `AGENTS.md`/`GEMINI.md` à la racine d'un greffon (seul `rules/` est chargé) et l'archive universelle ChatGPT exclut `AGENTS.md`, `CLAUDE.md` et `GEMINI.md`. Ces instructions ne s'appliquent qu'aux agents qui modifient ce dépôt.

---

## 1. Architecture v3.4.0 multi-dépôts et topologie (10 compétences + 6 personas)

`droit-civil-quebecois` est le greffon cadre multiplateforme (Claude Code, Claude Desktop, `claude.ai` / Claude Research, ChatGPT Web/Desktop *(hors ChatGPT Deep Research)*, OpenAI Codex, API OpenAI Responses, Google Antigravity, Gemini CLI, Gemini App / Vertex AI, Gemini API Deep Research) orchestrant **10 compétences** (5 orchestrateurs de phase + 5 services transversaux), **60 feuilles de référence**, **6 personas sans contexte (`agents/`)** et **4 scripts Python stdlib** au-dessus de **3 serveurs MCP spécialisés** (`lois`, `juris`, `outils` — 37 outils), d'un **portail d'accès et serveur OAuth 2.1 dédié** (`MCP-Acces`), d'une base D1 partagée (`DB_IDENTITE` / `mcp-identite`) et d'un socle partagé (`MCP-Socle`) :

- **Greffon cadre (`droit-civil-quebecois`) :** 5 orchestrateurs `phase-*`, 5 services transversaux, 60 feuilles, 6 personas `agents/*.md`, 4 scripts stdlib.
- **Connecteurs MCP :**
  - `lois` (`MCP-Legislation`) : D1 + Vectorize + Workers AI (`hybride_permis`) — `/mcp/oauth` (OAuth 2.1) et `/mcp` (Bearer / `404`), aucune clé CanLII requise ; repli autonome sans `DB_IDENTITE`.
  - `juris` (`MCP-Jurisprudence`) : D1 cache CanLII + BYOK CanLII strict sans `fetched_at` — `/mcp/oauth` (OAuth 2.1) et `/mcp` (`404`) ; repli autonome sans `DB_IDENTITE`.
  - `outils` (`MCP-Outils`) : Barreau via `acces.poirierlavoie.ca` (aucune clé CanLII requise), 4 D1 lecture seule (`DB_TERMINOLOGIE`, `DB_REGISTRES`, `DB_ADRESSES`, `DB_ECONOMIE`; 15 outils sur 6 familles), zéro journalisation, OAuth 2.1 `/mcp/oauth` + `/mcp` (`404`) ; repli autonome sans `DB_IDENTITE` ni liste fermée d'hôtes HTTP (`*.workers.dev`).
- **Socle & Identité :** `MCP-Socle` (transport 2026, auth, OAuth 2.1, coffre, gouverne) et `MCP-Acces` (`https://acces.poirierlavoie.ca` — admission Barreau, coffre AES-GCM, portail `/moi`, serveur OAuth PKCE, D1 partagée `mcp-identite`).

### Cartographie des 10 compétences, 60 feuilles, 6 personas (`agents/`) et 4 scripts (`skills/`)

Conception **Découverte progressive à 3 niveaux** + **Calibration de rigueur à 3 paliers** (Palier 1 *Triage*, Palier 2 *Dossier*, Palier 3 *Tribunal / dépôt complet*), dédiée au litige civil et commercial québécois (**hors droit familial et droit criminel**).

#### A. Cinq orchestrateurs de phase (`PHASE_SKILLS` — listes de contrôle, portes et enchaînements uniquement, aucune règle de fond)

1. **`skills/phase-ouverture-dossier`** (`0` feuille) — Conflit, identification/mandat, réception/tri des pièces, triage d'urgence, recherche préliminaire, note stratégique, mise en demeure ou suite.
2. **`skills/phase-introduction-reponse`** (`3` feuilles) — `references/branche-demandeur.md`, `branche-defendeur.md`, `branche-urgence.md`.
3. **`skills/phase-interrogatoires-instruction`** (`0` feuille) — Communication de preuve, plan d'interrogatoire, tenue, extraction de transcription, engagements/objections (`5 j` sur art. 228 al. 2), expertise, modifications (`206–208`).
4. **`skills/phase-preparation-audience`** (`1` feuille) — Mise en état, CRA/conférence préparatoire, témoins, cahiers, plan d'argumentation, admissions, contrôle complet de production ; `references/branche-audience-interlocutoire.md`.
5. **`skills/phase-jugement-et-suites`** (`0` feuille) — Réception du jugement, analyse des erreurs/norme, délai d'appel/permission/rétractation, rapport au client, recours/exécution, frais/intérêts, clôture du dossier.

#### B. Cinq compétences de service (`SERVICE_SKILLS`)

1. **`skills/recherche-juridique`** (`6` feuilles) — `grille-prealables.md` et `recherche-*.md` (`legislative`, `jurisprudentielle`, `doctrinale`, `precedents-internes`, `livrables`).
2. **`skills/analyse-et-strategie`** (`13` feuilles, `1` script) — `piece-reception-et-qualification.md`, `preuve-*.md` (`5`), `produit-*.md` (`7`, dont `produit-contre-epreuve-banc.md`) ; script `scripts/inspecter_piece.py` (inspection locale `.docx`/`.xlsx`/`.eml`/`.pdf`/images/médias + `--journal` + `--extraire-texte`, zéro réseau).
3. **`skills/redaction-juridique`** (`25` feuilles) — Socle (`fondamentaux-actes.md`, `anti-contamination-bilingue.md`), `acte-*.md` (`12`), `arg-*.md` (`4`), `corr-*.md` (`3`), `contrat-*.md` (`4`).
4. **`skills/production-et-conformite`** (`7` feuilles, `2` scripts) — `controle-*.md` (`4`), `cahier-*.md` (`3`) ; scripts `scripts/controler_document.py` (vérification + bon de travail Word/PDF) et `scripts/verifier_cotes.py` (continuité des cotes et concordance).
5. **`skills/gestion-du-mandat`** (`5` feuilles, `1` script) — `conformite-*.md` (`ouverture-conflits-mandat`, `radar-deontologique`, `facturation-fideicommis`, `echeanciers-cpc`, `quantum-interets-frais`) ; script `scripts/calcul_delai.py` (repli local déterministe du calendrier C.p.c., zéro réseau).

#### C. Six personas sans contexte (`agents/*.md` — Banc de contre-épreuve)

- `avocat-analyste.md` (*lecture à froid*, `CONTRE_EPREUVE`, zéro MCP) · `avocat-adverse.md` (*avocat adverse*, `lois`/`outils`) · `verificateur-dossier.md` (*concordance 1:1, citations & aveux `2852 C.c.Q.`*, `lois`/`outils`) · `avocat-conseil.md` (*angles procéduraux & règlement*, `lois`/`outils`) · `parajuriste-inventaire.md` (*tranches `LOT_PIECES`*, zéro MCP) · `coordonnateur-revue.md` (*coordonnateur parallèle → `etat-dossier/banc/`*, zéro MCP). **`juris` strictement réservé à l'Éléphant** (protection quota CanLII BYOK).

---

## 2. Contrats d'architecture, gabarits et règles de graphe

### Règles de graphe (vérifiées par `verifier.py`)

1. **Phases → services uniquement**, soit par **activation** (`Type = livrable`, nom de compétence cible uniquement, jamais `../<cible>/SKILL.md`), soit par **lecture directe d'une feuille** (`Type = référence`).
2. **Services → feuilles voisines d'autres services** (`../<service>/references/<feuille>.md` avec repli autonome via `lois`), **jamais** vers une compétence `phase-` et **jamais** vers un autre `SKILL.md`.
3. **Phase → phase :** suggestion en texte brut de la phase suivante uniquement ; `../phase-*` est interdit.
4. **Feuilles terminales (« impasses ») :** toute feuille sous `references/` contient zéro lien relatif `../`.

### Noyau de sécurité canonique v3 (`SAFETY-KERNEL`)

Les **10** `SKILL.md` partagent au bit près le même bloc `<!-- SAFETY-KERNEL:START -->...<!-- SAFETY-KERNEL:END -->` (5 garde-fous : Confidentialité stricte, Sources primaires obligatoires avec redirection vers `acces.poirierlavoie.ca/moi` sur `401`/`403`/`404`/`429`/`[CLEF_ABSENTE]`/`[CLEF_REFUSEE]`/`QUOTA_EPUISE`/hors ligne, Étanchéité bijuridique, Protection et déclencheurs déontologiques, **Perception et précédents**). Ce bloc reste en tête de chaque `SKILL.md` afin de survivre à la compaction de contexte et correspond au préambule Deep Research dans `README.md`. Crochets normalisés : `[À CONFIRMER]`, `[DATE À CONFIRMER]`, `[À COMPLÉTER]`, `[À VÉRIFIER VIA LOIS]`, `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`.

### Gabarit 1 — Orchestrateur (`phase-*/SKILL.md`)

- En-tête YAML (`name`, `description <= 450` car., incluant `En anglais` et `Ne pas utiliser pour`).
- Titre `# <Phase>` + `SAFETY-KERNEL` v3.
- Sections obligatoires dans l'ordre :
  1. `## Entrées requises` *(ce que l'avocat doit fournir ; sinon `[À CONFIRMER]`)*
  2. `## État de la phase` *(créer ou relire `etat-dossier/<phase>.md` ; bloc Markdown en ligne sur surface sans disque inscriptible)*
  3. `## Parcours` *(étapes numérotées `### Étape n — <nom>`, chacune avec Objectif · Livrable · Porte)*
  4. `## Enchaînements` *(tableau vérifiable — interdit dans les services)*
  5. `## Branches` *(ex. demandeur / défendeur / urgence ; 0 à 3 feuilles `references/branche-*.md`, listes de contrôle sans règles de fond)*
  6. `## Contrôle de sortie de phase` *(conditions de passage à la phase suivante)*

### Format de la table `## Enchaînements`

```markdown
| Étape | Type | Cible | Feuille | Palier | Condition |
|---|---|---|---|---|---|
| 3 | livrable | redaction-juridique | acte-demande-introductive | 3 | après Étape 2 franchie |
| 1 | référence | recherche-juridique | grille-prealables | — | toujours |
```

- `Type` ∈ `{livrable, référence}` ; `Cible` ∈ `SERVICE_SKILLS` ; `Feuille` = identifiant sans `.md` existant dans `skills/<Cible>/references/<Feuille>.md` ; `Palier` ∈ `{1, 2, 3, —}` (obligatoire `1|2|3` lorsque `Type = livrable`).

### Suivi d'état de phase (`etat-dossier/<phase>.md`)

- **Emplacement :** `etat-dossier/<phase>.md` dans le répertoire du dossier client lorsque le disque est inscriptible (Claude Code, Codex, Antigravity, Gemini CLI). Sur surfaces sans disque inscriptible (`claude.ai`, ChatGPT, Gemini App `/mcp/oauth`, Deep Research), produire directement un **bloc d'état Markdown en ligne** complet à sauvegarder sans prétendre avoir écrit sur disque.
- **En-tête :** `phase`, `branche`, `date`, `palier`, `dernière mise à jour`.
- **Corps :** tableau `| Étape | Statut (À faire / En cours / Franchie / Bloquée) | Livrable | Porte | Notes |`.
- **Règles :** relu au début de chaque tour de la phase ; jamais copié hors du dossier ; faits étiquetés `Établi`, `Rapporté`, `Déduit` ou `[À CONFIRMER]`.

### Gabarit 2 — Service (`<service>/SKILL.md`)

- En-tête YAML (`name`, `description <= 750` car., incluant `En anglais` et `Ne pas utiliser pour`, zéro mention `phase-`).
- Titre `# <Service>` + `SAFETY-KERNEL` v3.
- `## Paliers de rigueur` + **catalogue des feuilles** (`| Intention | references/<id>.md | Connecteurs |`) + règle de chargement (socle commun + 1 ou 2 feuilles max) + `## Contrôle avant remise`. Aucune section `## Enchaînements`.

### Gabarit 3 — Feuilles par famille (préfixes et titres `##` exigés)

| Préfixe | Famille | Titres `##` obligatoires |
|---|---|---|
| `acte-` | Acte de procédure | `Vecteur législatif` · `Conditions et préalables` · `Forum et compétence` · `Structure obligatoire` · `Pièces jointes et formalités` · `Particularités et pièges` · `Conclusions types` · `Délais (renvoi)` |
| `arg-` | Argumentation | `Destinataire et format` · `Structure` · `Discipline de citation` · `Pièges` · `Contrôle` |
| `corr-` / `contrat-` | Correspondance / contrat | `Objet et destinataire` · `Mentions obligatoires` · `Structure` · `Clauses ou formules à proscrire` · `Contrôle` |
| `preuve-` / `piece-` | Analyse probante | `Qualification` · `Authentification et intégrité` · `Recevabilité` · `Force probante` · `Protection` · `Ce que la pièce ne prouve pas` |
| `produit-` | Produit interne | `Finalité` · `Gabarit` · `Statut des faits` · `Mise à jour` |
| `recherche-` | Méthode de recherche | `Sources et outils` · `Séquence` · `Statuts de lecture` · `Modes d'échec` |
| `controle-` / `cahier-` | Production & conformité | `Règles applicables` · `Contrôles automatisés` · `Contrôles humains` · `Bon de travail` |
| `conformite-` | Gestion du mandat | `Déclencheurs` · `Vecteur` · `Obligations` · `Silences et paires confondables` |

*(Exceptions nommées sans préfixe de famille : `fondamentaux-actes.md`, `anti-contamination-bilingue.md`, `grille-prealables.md`, ainsi que `branche-*.md` dans les orchestrateurs de phase.)*

### Règles transversales de fond (`v3.4.0`)

- **Auto-connexion OAuth 2.1 unifiée par défaut, clé CanLII facultative sur `/demande`, portée `"tous"` et zéro-log :** les 3 manifestes MCP (`.mcp.json`, `mcp_config.json`, `gemini-extension.json`) pointent tous trois par défaut vers `/mcp/oauth` sans secret ni variable statique (flux OAuth 2.1 PKCE `S256` + inscription dynamique RFC 7591 sans état `/oauth/register` via `acces.poirierlavoie.ca`, portée universelle `"tous"` avec rétrocompatibilité `"les_deux"`, quota `local` relevé à `3 000/j` `actif` / `300/j` `limite`), tandis que `.codex-plugin/plugin.json`, `plugin.json` et `scripts/empaqueter_plugin_chatgpt.py` omettent `mcpServers` afin d'éviter le badge *Desktop only* sur ChatGPT Web, et que `/mcp` (`Bearer` / `?key=`, refus uniforme `404`) demeure actif pour les CLI/CI sans navigateur, l'API OpenAI Responses et l'API Gemini Deep Research *(ChatGPT Deep Research exclu)*. La clé API CanLII est facultative à l'admission (`/demande`) et requise uniquement sur `juris` (`X-Clef-CanLII` ou `DB_IDENTITE.coffre_clef`), jamais sur `lois` ni `outils`. Zéro écriture dans `search_log`/`api_usage`, `observability.enabled = false`. Chaque dépôt de connecteur embarque ses schémas/migrations et bascule en mode autonome sans `DB_IDENTITE` grâce au repli par secret statique.
- **Quarantaine par domaine et corpus élargi (`lois`, `134` textes, `50` matières) :** `list_laws`, `find_relevant` et `search_text` (sans `law`) ciblent par défaut le domaine `'core'` *(incluant Vague 1 constitutionnelle et ajouts `core` Vague 2)* avec radar `other_domains` et filtres optionnels `domains` (`core`, `cours-federales`, `financier`, `construction-immobilier`, `municipal-environnement`, `travail`, `penal` — incluant `ca-c-46`, `ca-c-38.8`, `ca-y-1.5` —, `propriete-intellectuelle`, `all`), `jurisdiction` (`qc`|`ca`) et `forum` (`get_article`/`get_articles`/`resolve_reference`/`related_laws` ouverts corpus entier ; LIR exclue) ; inclut directives QCCS/QCCQ (`fonction='directive'`, `unit='paragraphe'`, `par.`/`dir.`, `fr`-only ; aucun recueil unifié QCCA au-delà de `c-25.01-r.0.2.01`) et règlements/orientations AMF (`v-1.1-r.*`, `amf-ig-*`, `fonction='orientation'`).
- **Aucune décharge statutaire figée :** privilégier les vecteurs `lois.get_articles`, paires confondables et silences ; ne jamais copier le texte intégral d'articles ni coder de seuils réglementaires en dur dans les scripts.
- **Production et dégradation nuage (`production-et-conformite` & `analyse-et-strategie`) :** vérifier et rapporter par scripts Python stdlib, puis émettre un **bon de travail** précis. Lorsque les scripts `.py` locaux (`controler_document.py`, `verifier_cotes.py`, `inspecter_piece.py`) ne peuvent pas s'exécuter (`claude.ai`, ChatGPT sans Python local, Gemini App `/mcp/oauth`, Deep Research), **divulguer explicitement** que les contrôles octets/XML/PDF/cotes ont été omis et les inscrire en tête du **bon de travail** manuel.
- **Banc de contre-épreuve (`produit-contre-epreuve-banc.md` & `agents/*.md`) :** pare-feu par liste blanche (`etat-dossier/banc/`), extraction `--extraire-texte`, accès MCP hybride (`juris` Éléphant uniquement), porte de triage obligatoire (`FORTIFIER`, `DÉSAMORCER`, `CIBLE D'INSTRUCTION`, `RISQUE ASSUMÉ`) sans modification directe de `.docx`/`.pdf`, et repli nuage honnête par **Paquet Contre-épreuve (Nouvel onglet vierge)** sans simulation dans un fil partagé.
- **Précédents internes (`recherche-precedents-internes.md`) :** uniquement fournis par l'avocat, dé-identifiés obligatoirement, savoir-faire et structure uniquement, alerte de conflit, actes publics/jugements classés au-dessus des notes internes.
- **Honnêteté perceptuelle (`preuve-directe.md`) :** n'analyser un média (audio, vidéo, image) que s'il a été effectivement perçu ; sinon exiger transcription ou captures et étiqueter « support secondaire » ; transcription IA = aide de travail uniquement ; empreinte SHA-256 + métadonnées à la réception (`inspecter_piece.py --journal`, ou bloc en ligne `[SHA-256 : À CALCULER LOCALEMENT]` en nuage).

---

## 3. Évaluation d'impact obligatoire avant clôture (4 axes)

**Aucune tâche touchant `droit-civil-quebecois` n'est terminée tant que son impact n'a pas été évalué, répercuté et explicitement rapporté sur chacun des quatre axes :**

| # | Axe d'impact | Éléments à inspecter |
|---|---|---|
| 1 | **Compétences (`skills/`), sous-agents (`agents/`), scripts et `evals/`** | `skills/*/SKILL.md`, `references/`, `scripts/`, `agents/*.md`, `evals/scenarios.json`, `evals/executer_evals.py`, `evals/test_verifier.py`, `verifier.py`, `verifier_tout.py` |
| 2 | **`README.md`, gouvernance, sécurité, licence et 9 manifestes** | `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `LICENSE` (`Apache-2.0`), `NOTICE`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.antigravity-plugin/plugin.json`, `plugin.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `mcp_config.json`, `gemini-extension.json`, `.mcp.json` |
| 3 | **Pages publiques HTML (`GET /`) et fiches `/mcp/server-card` des serveurs MCP** | `src/site.ts` / `site.i18n.ts` / `server-card` / `/.well-known/oauth-protected-resource/mcp/oauth` dans `MCP-Legislation`, `MCP-Jurisprudence`, `MCP-Outils` et `MCP-Acces` |
| 4 | **Impacts inter-dépôts (`Cross-repository`)** | **`MCP-Socle`**, **`MCP-Acces`**, **`MCP-Legislation`**, **`MCP-Jurisprudence`** et **`MCP-Outils`** (identité `mcp-identite`, BYOK, OAuth 2.1 `/mcp/oauth`, 37 outils, synchronisation Antigravity / Gemini CLI) |

---

## 4. Invariants structurels, budgets et sécurité (`verifier.py`)

Toute modification doit passer `python verifier.py` (sortie strictement muette, code `0`) :

1. **Inventaire strict (`ROOT_ALLOWLIST`, `EVALS_ALLOWLIST`) :** aucun fichier orphelin (incluant `CONTRIBUTING.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`) ; parité octet pour octet entre `AGENTS.md`, `CLAUDE.md` et `GEMINI.md` (`< 24 000` octets) ; liens Markdown/images relatifs valides dans les documentations racine ; syntaxe `ast.parse` sur tous les `.py` et encodage UTF-8 sans BOM + LF uniquement sur **tous** les fichiers du dépôt, y compris `LICENSE` et `NOTICE`.
2. **Parité exacte des 9 manifestes, `evals/scenarios.json` et licence (`3.4.0`) :** `name` = `droit-civil-quebecois`, `displayName` = `Droit civil québécois`, licence = `Apache-2.0` (`LICENSE`) + `NOTICE`, semver identique partout (`3.4.0`, incluant `evals/scenarios.json`) : `.antigravity-plugin/plugin.json` (`$schema` Antigravity v1, `description <= 160` car.), `plugin.json` racine (Portable Agent Plugins 1.0 + `extensions.com.openai.interface` identique à `.codex-plugin/plugin.json`), `.claude-plugin/plugin.json` (`icon`), `.claude-plugin/marketplace.json` (`$schema`), `.codex-plugin/plugin.json` (`shortDescription <= 30`, `defaultPrompt <= 128`), `.agents/plugins/marketplace.json`, `gemini-extension.json` (`"contextFileName": []`, `"settings": []`), `mcp_config.json`, `.mcp.json`.
3. **Serveurs MCP OAuth-first et plafond `<= 64` caractères :** `lois`, `juris` et `outils` (`/mcp/oauth` sans `headers`, `variables` ni `eager`), 37 outils (`10 lois`, `12 juris`, `15 outils` sur 6 familles incluant `economie`), longueur composée `<= 64` car. (max 62 Claude Code, 53 Antigravity, 55 OpenAI `plugin:skill`) ; `plugin.json`, `.codex-plugin/plugin.json` et `scripts/empaqueter_plugin_chatgpt.py` omettent `mcpServers` et `requires_local_executor` pour la compatibilité ChatGPT Web + Desktop. `synchroniser_plugin_gemini.py` et `empaqueter_plugin_chatgpt.py` embarquent `agents/`.
4. **Budgets et structure des compétences (`skills/`) et personas (`agents/`) :**
   - Descriptions YAML : `<= 450` car. (phases et `agents/*.md`), `<= 750` car. (services), `<= 1 024` car. absolu, **somme totale des compétences `<= 6 000` car.**, incluant `En anglais` (et `Ne pas utiliser pour` pour `SKILL.md`), sans `<`/`>`.
   - `SKILL.md` et `agents/*.md` : `<= 16 384` octets (`16 KB`), ouverture par `# ` ; corps `SKILL.md <= 2 200` mots et parité SHA-256 du `SAFETY-KERNEL` v3 sur les 10 `SKILL.md` ; `agents/*.md` inclut `donnée brute` et `etat-dossier`, sans `../`, `phase-*` ni `skills/...`, et chaque persona est référencé dans `produit-contre-epreuve-banc.md`.
   - Feuilles `references/*.md` : `<= 24 576` octets (`24 KB`), zéro `../`, titres conformes à la famille.
   - Plafond par chargement : `SKILL.md` + ses 2 plus grandes feuilles `<= 65 536` octets (`64 KB`).
   - Fichiers par compétence : `<= 100`.
5. **Marqueurs de rédaction et mode publication (`--release`) :** `[FICHE À RÉDIGER]` et `[NON VALIDÉ PAR LA PRATIQUE]` autorisés hors mode publication ; **interdits** avec `python verifier.py --release` (qui exige aussi la couverture complète des scénarios `evals/`).
6. **Isolation DMS et anti-dérive (`BANNED_PATTERNS`, `RETIRED_*`) :** interdiction absolue de tout nom d'outil de gestionnaire de dossiers (`get_dossier`, `create_note`, etc.), codes DMS fermés, mentions de l'ancienne application, identifiants retirés (`v1`/`v2`, anciens outils/dépôts), `$ARGUMENTS`, `${CLAUDE_...}`, `mcp__`, `qclaw_`, `canlii_`.

---

## 5. Commandes de synchronisation et de vérification

```powershell
# 1. Contrôles statiques (muet, sortie 0) et mode publication (--release)
python verifier.py
python verifier.py --stats
python verifier.py --release

# 2. Suite d'évaluation comportementale, scripts locaux et tests du vérificateur
python evals/executer_evals.py --auto-test
python -m unittest evals/test_verifier.py

# 3. Suite E2E multi-paliers (simulation locale ou réseau réel)
python verifier_tout.py --mode mock
# python verifier_tout.py --mode live --require-antigravity-cache

# 4. Déploiement local Antigravity / Gemini CLI
python scripts/synchroniser_plugin_gemini.py --apply
python scripts/regenerer_cache_mcp.py --apply   # (mainteneur uniquement — nécessite les 3 dépôts MCP frères)

# 5. Empaquetage universel ChatGPT (Web + Desktop)
python scripts/empaqueter_plugin_chatgpt.py --apply
```
