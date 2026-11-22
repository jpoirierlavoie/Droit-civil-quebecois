# droit-civil-quebecois — Architecture, principes et consignes de travail

Directives de développement, architecture multi-dépôts à trois couches et règles anti-dérive pour le greffon **Droit civil québécois** (`droit-civil-quebecois`, `v3.1.0`). Ce document gouverne de façon identique Claude et Google Antigravity / Gemini CLI (`CLAUDE.md` et `GEMINI.md` doivent rester identiques octet pour octet et sous **24 000 octets** UTF-8 LF).

> **Note Gemini CLI (`gemini-extension.json`) :** La racine déclare `"contextFileName": []` afin que `GEMINI.md` ne soit **jamais** injecté comme contexte système dans les sessions d'usage juridique normal des utilisateurs finaux. Il s'applique exclusivement aux agents qui modifient ce dépôt.

---

## 1. Architecture v3.1.0 multi-dépôts et topologie (10 compétences)

`droit-civil-quebecois` est le greffon cadre multiplateforme (Claude Code, Claude Desktop, `claude.ai` / Claude Research, ChatGPT Web/Desktop *(hors ChatGPT Deep Research)*, OpenAI Codex, API OpenAI Responses, Google Antigravity, Gemini CLI, Gemini App / Vertex AI, Gemini API Deep Research) orchestrant **10 compétences** (5 orchestrateurs de phase + 5 services transversaux), **59 feuilles de référence** et **4 scripts Python stdlib** au-dessus de **3 serveurs MCP spécialisés** (`lois`, `juris`, `outils` — 32 outils), d'un **portail d'accès et serveur OAuth 2.1 dédié** (`MCP-Acces`), d'une base D1 partagée (`DB_IDENTITE` / `mcp-identite`) et d'un socle partagé :

```
             ┌────────────────────────────────────────────────────────┐
             │      droit-civil-quebecois (Plugin Cadre v3.1.0)       │
             │   5 orchestrateurs phase-* · 5 services · 59 feuilles  │
             │              4 scripts Python stdlib                   │
             └──────┬───────────────────────┬──────────────────┬──────┘
                    │ /mcp/oauth (OAuth 2.1)│ /mcp/oauth       │ /mcp (public)
                    │ /mcp (Bearer / 404)   │ /mcp (404)       │
                    ▼                       ▼                  ▼
         ┌─────────────────────┐ ┌─────────────────────┐ ┌──────────────────────────┐
         │   MCP-Legislation   │ │  MCP-Jurisprudence  │ │        MCP-Outils        │
         │  D1 + Vectorize +   │ │  D1 cache CanLII    │ │   Public, 3 D1 lecture   │
         │  Workers AI +       │ │  BYOK CanLII strict │ │   seule, zéro secret,    │
         │  hybride_permis     │ │  sans fetched_at    │ │   zéro journalisation    │
         └──────────┬──────────┘ └──────────┬──────────┘ └──────────────────────────┘
                    │                       │
                    ├───────────┬───────────┴────┐
                    │           ▼ (MCP-Socle)    ▼ (D1 partagée `mcp-identite`)
                    │  ┌──────────────────┐  ┌──────────────────────────────────────┐
                    │  │    MCP-Socle     │  │              MCP-Acces               │
                    │  │ Transport 2026   │  │     https://acces.poirierlavoie.ca   │
                    └──│ Auth · OAuth 2.1 │◄─┤ Admission Barreau · Coffre AES-GCM · │
                       │ Coffre · Gouverne│  │ Portail /moi · Serveur OAuth PKCE    │
                       └──────────────────┘  └──────────────────────────────────────┘
```

### Cartographie des 10 compétences, 59 feuilles et 4 scripts (`skills/`)

Conception **Découverte progressive à 3 niveaux** + **Calibration de rigueur à 3 paliers** (Palier 1 *Triage*, Palier 2 *Dossier*, Palier 3 *Tribunal / dépôt complet*), dédiée au litige civil et commercial québécois (**hors droit familial et droit criminel**).

#### A. Cinq orchestrateurs de phase (`PHASE_SKILLS` — listes de contrôle, portes et enchaînements uniquement, aucune règle de fond)

1. **`skills/phase-ouverture-dossier`** (`0` feuille) — Conflit, identification/mandat, réception/tri des pièces, triage d'urgence, recherche préliminaire, note stratégique, mise en demeure ou suite.
2. **`skills/phase-introduction-reponse`** (`3` feuilles de branche) — `references/branche-demandeur.md`, `references/branche-defendeur.md`, `references/branche-urgence.md`.
3. **`skills/phase-interrogatoires-instruction`** (`0` feuille) — Communication de preuve, plan d'interrogatoire, tenue, extraction de transcription, engagements/objections (`5 j` sur art. 228 al. 2), expertise, modifications (`206–208`).
4. **`skills/phase-preparation-audience`** (`1` feuille de branche) — Mise en état, CRA/conférence préparatoire, témoins, cahiers, plan d'argumentation, admissions, contrôle complet de production ; `references/branche-audience-interlocutoire.md`.
5. **`skills/phase-jugement-et-suites`** (`0` feuille) — Réception du jugement, analyse des erreurs/norme, délai d'appel/permission/rétractation, rapport au client, recours/exécution, frais/intérêts, clôture du dossier.

#### B. Cinq compétences de service (`SERVICE_SKILLS`)

1. **`skills/recherche-juridique`** (`6` feuilles)
   - `grille-prealables.md`, `recherche-legislative.md`, `recherche-jurisprudentielle.md`, `recherche-doctrinale.md`, `recherche-precedents-internes.md`, `recherche-livrables.md`.
2. **`skills/analyse-et-strategie`** (`12` feuilles, `1` script)
   - `piece-reception-et-qualification.md`, `preuve-directe.md`, `preuve-indirecte.md`, `preuve-documents-judiciaires.md`, `preuve-recevabilite-force-probante.md`, `preuve-privilege-confidentialite-caviardage.md`, `produit-theorie-de-la-cause.md`, `produit-note-et-memo.md`, `produit-matrice-allegations.md`, `produit-fiche-preuve-et-temoins.md`, `produit-chronologie.md`, `produit-interrogatoire.md`.
   - Script : `scripts/inspecter_piece.py` (inspection locale .docx/.xlsx/.eml/.pdf/images/médias + `--journal` journal de garde, zéro réseau).
3. **`skills/redaction-juridique`** (`25` feuilles)
   - Socle : `fondamentaux-actes.md`, `anti-contamination-bilingue.md`.
   - Actes (`12`) : `acte-demande-introductive.md`, `acte-defense-et-expose-sommaire.md`, `acte-demandes-cours-instance.md`, `acte-moyens-preliminaires.md`, `acte-reconvention-intervention-garantie.md`, `acte-injonction.md`, `acte-saisie-avant-jugement.md`, `acte-mesures-provisionnelles-autres.md`, `acte-pourvoi-controle-judiciaire.md`, `acte-appel-declaration-permission.md`, `acte-retractation-jugement.md`, `acte-execution-et-oppositions.md`.
   - Argumentation (`4`) : `arg-plan-argumentation.md`, `arg-argumentation-ecrite.md`, `arg-memoire-et-expose-appel.md`, `arg-citations.md`.
   - Correspondance & contrats (`7`) : `corr-mise-en-demeure.md`, `corr-confrere-et-tribunal.md`, `corr-client.md`, `contrat-protocole-instance.md`, `contrat-ententes-judiciaires.md`, `contrat-transaction-quittance.md`, `contrat-civil-commercial.md`.
4. **`skills/production-et-conformite`** (`7` feuilles, `2` scripts)
   - `controle-acte-de-procedure.md`, `controle-correspondance.md`, `controle-pdf-et-metadonnees.md`, `cahier-des-sources.md`, `cahier-des-pieces-et-bordereaux.md`, `cahier-des-procedures.md`, `controle-endos-depot-signification.md`.
   - Scripts : `scripts/controler_document.py` (vérification + bon de travail Word/PDF), `scripts/verifier_cotes.py` (continuité des cotes et concordance).
5. **`skills/gestion-du-mandat`** (`5` feuilles, `1` script)
   - `conformite-ouverture-conflits-mandat.md`, `conformite-radar-deontologique.md`, `conformite-facturation-fideicommis.md`, `conformite-echeanciers-cpc.md`, `conformite-quantum-interets-frais.md`.
   - Script : `scripts/calcul_delai.py` (repli local déterministe du calendrier C.p.c., zéro réseau).

---

## 2. Contrats d'architecture, gabarits et règles de graphe

### Règles de graphe (vérifiées par `verifier.py`)

1. **Phases → services uniquement**, soit par **activation** (`Type = livrable`, nom de compétence cible uniquement, jamais `../<cible>/SKILL.md`), soit par **lecture directe d'une feuille** (`Type = référence`).
2. **Services → feuilles voisines d'autres services** (`../<service>/references/<feuille>.md` avec repli autonome via `lois`), **jamais** vers une compétence `phase-` et **jamais** vers un autre `SKILL.md`.
3. **Phase → phase :** suggestion en texte brut de la phase suivante uniquement ; `../phase-*` est interdit.
4. **Feuilles terminales (« impasses ») :** toute feuille sous `references/` contient zéro lien relatif `../`.

### Noyau de sécurité canonique v3 (`SAFETY-KERNEL`)

Les **10** `SKILL.md` partagent au bit près le même bloc `<!-- SAFETY-KERNEL:START -->...<!-- SAFETY-KERNEL:END -->` (5 garde-fous : Confidentialité stricte, Sources primaires obligatoires avec redirection vers `acces.poirierlavoie.ca/moi` sur `401`/`404`/`429`/`[CLEF_ABSENTE]`/`[CLEF_REFUSEE]`/`QUOTA_EPUISE`/hors ligne, Étanchéité bijuridique, Protection et déclencheurs déontologiques, **Perception et précédents**). Ce bloc reste en tête de chaque `SKILL.md` afin de survivre à la compaction de contexte et correspond au préambule Deep Research dans `README.md`. Crochets normalisés : `[À CONFIRMER]`, `[DATE À CONFIRMER]`, `[À COMPLÉTER]`, `[À VÉRIFIER VIA LOIS]`, `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`.

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

### Règles transversales de fond (`v3.1.0`)

- **Auto-connexion OAuth 2.1 par défaut, BYOK CanLII et zéro-log :** les 3 manifestes MCP (`.mcp.json`, `mcp_config.json`, `gemini-extension.json`) pointent par défaut vers `/mcp/oauth` sans secret ni variable statique (flux OAuth 2.1 PKCE `S256` + inscription dynamique RFC 7591 sans état `/oauth/register` via `acces.poirierlavoie.ca`), tandis que `.codex-plugin/plugin.json` et `scripts/empaqueter_plugin_chatgpt.py` omettent `mcpServers` afin d'éviter le badge *Desktop only* sur ChatGPT Web, et que `/mcp` (`Bearer` / `?key=`, refus uniforme `404`) demeure actif pour les CLI/CI sans navigateur, l'API OpenAI Responses et l'API Gemini Deep Research *(ChatGPT Deep Research exclu)*. Sur `juris`, chaque titulaire utilise sa clé API CanLII personnelle (`X-Clef-CanLII` ou `DB_IDENTITE.coffre_clef`) vérifiée avant toute lecture du cache partagé. Zéro écriture dans `search_log`/`api_usage`, `observability.enabled = false`.
- **Corpus PDF Vague 1 (`lois`, `110` textes) :** inclut les directives QCCS/QCCQ (`fonction='directive'`, `unit='paragraphe'`, `par.`/`dir.`, `fr`-only ; `QCCA` absent de la Vague 1) et les règlements/orientations AMF (`v-1.1-r.*`, `amf-ig-*`, `fonction='orientation'`), reliés par `rel_type='preseance-sur'|'interprete'` et `articles.links` (`kind='annexe'`, `ps:*`).
- **Aucune décharge statutaire figée :** privilégier les vecteurs `lois.get_articles`, paires confondables et silences ; ne jamais copier le texte intégral d'articles ni coder de seuils réglementaires en dur dans les scripts.
- **Production et dégradation nuage (`production-et-conformite` & `analyse-et-strategie`) :** vérifier et rapporter par scripts Python stdlib, puis émettre un **bon de travail** précis. Lorsque les scripts `.py` locaux (`controler_document.py`, `verifier_cotes.py`, `inspecter_piece.py`) ne peuvent pas s'exécuter (`claude.ai`, ChatGPT sans Python local, Gemini App `/mcp/oauth`, Deep Research), **divulguer explicitement** que les contrôles octets/XML/PDF/cotes ont été omis et les inscrire en tête du **bon de travail** manuel.
- **Précédents internes (`recherche-precedents-internes.md`) :** uniquement fournis par l'avocat, dé-identifiés obligatoirement, savoir-faire et structure uniquement, alerte de conflit, actes publics/jugements classés au-dessus des notes internes.
- **Honnêteté perceptuelle (`preuve-directe.md`) :** n'analyser un média (audio, vidéo, image) que s'il a été effectivement perçu ; sinon exiger transcription ou captures et étiqueter « support secondaire » ; transcription IA = aide de travail uniquement ; empreinte SHA-256 + métadonnées à la réception (`inspecter_piece.py --journal`, ou bloc en ligne `[SHA-256 : À CALCULER LOCALEMENT]` en nuage).

---

## 3. Évaluation d'impact obligatoire avant clôture (4 axes)

**Aucune tâche touchant `droit-civil-quebecois` n'est terminée tant que son impact n'a pas été évalué, répercuté et explicitement rapporté sur chacun des quatre axes :**

| # | Axe d'impact | Éléments à inspecter |
|---|---|---|
| 1 | **Compétences (`skills/`), scripts et `evals/`** | `skills/*/SKILL.md`, `references/`, `scripts/`, `evals/scenarios.json`, `evals/executer_evals.py`, `evals/test_verifier.py`, `verifier.py`, `verifier_tout.py` |
| 2 | **`README.md`, sécurité, licence et manifestes** | `README.md`, `SECURITY.md`, `LICENSE` (`Apache-2.0`), `NOTICE`, `CLAUDE.md`, `GEMINI.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `plugin.json`, `mcp_config.json`, `gemini-extension.json`, `.mcp.json` |
| 3 | **Pages publiques HTML (`GET /`) et fiches `/mcp/server-card` des serveurs MCP** | `src/site.ts` / `site.i18n.ts` / `server-card` / `/.well-known/oauth-protected-resource/mcp/oauth` dans `MCP-Legislation`, `MCP-Jurisprudence`, `MCP-Outils` et `MCP-Acces` |
| 4 | **Impacts inter-dépôts (`Cross-repository`)** | **`MCP-Socle`**, **`MCP-Acces`**, **`MCP-Legislation`**, **`MCP-Jurisprudence`** et **`MCP-Outils`** (identité `mcp-identite`, BYOK, OAuth 2.1 `/mcp/oauth`, 32 outils, synchronisation Antigravity / Gemini CLI) |

---

## 4. Invariants structurels, budgets et sécurité (`verifier.py`)

Toute modification doit passer `python verifier.py` (sortie strictement muette, code `0`) :

1. **Inventaire strict (`ROOT_ALLOWLIST`, `EVALS_ALLOWLIST`) :** aucun fichier orphelin ; encodage UTF-8 sans BOM et LF uniquement sur **tous** les fichiers du dépôt, y compris `LICENSE` et `NOTICE`.
2. **Parité exacte des manifestes et licence (`3.1.0`) :** `name` = `droit-civil-quebecois`, `displayName` = `Droit civil québécois`, licence = `Apache-2.0` (`LICENSE`) accompagnée de `NOTICE` (reconnaissance des sources officielles et non-revendication), semver identique partout (`3.1.0`, dont `.codex-plugin/plugin.json` avec `shortDescription <= 30` car., `defaultPrompt <= 128` car., et `.agents/plugins/marketplace.json`), `"contextFileName": []` et `"settings": []` dans `gemini-extension.json`.
3. **Serveurs MCP OAuth-first et plafond `<= 64` caractères :** `lois`, `juris` (`/mcp/oauth` sans `headers`, `variables` ni `eager`) et `outils` (`/mcp`), 32 outils inchangés, longueur composée `<= 64` car. (max 62 Claude Code, 52 Antigravity, 55 OpenAI `plugin:skill`) ; `.codex-plugin/plugin.json` et `scripts/empaqueter_plugin_chatgpt.py` omettent `mcpServers` et `requires_local_executor` pour la compatibilité ChatGPT Web + Desktop.
4. **Budgets et structure des compétences (`skills/`) :**
   - Descriptions YAML : `<= 450` car. (phases), `<= 750` car. (services), `<= 1 024` car. absolu, **somme totale du greffon `<= 6 000` car.**, incluant `En anglais` et `Ne pas utiliser pour`, sans `<`/`>`.
   - `SKILL.md` : corps `<= 2 200` mots et `<= 16 384` octets (`16 KB`), ouverture par `# `, parité SHA-256 du `SAFETY-KERNEL` v3 (règle 2 `acces.poirierlavoie.ca/moi` + `403`, règle 5 `Perception et précédents` + `donnée brute`) sur les 10 `SKILL.md`, correspondance 1:1 avec `references/*.md` et `scripts/*.py`.
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
# python verifier.py --release

# 2. Suite d'évaluation comportementale, scripts locaux et tests du vérificateur
python evals/executer_evals.py --auto-test
python -m unittest evals/test_verifier.py

# 3. Suite E2E multi-paliers (simulation locale ou réseau réel)
python verifier_tout.py --mode mock
# python verifier_tout.py --mode live --require-antigravity-cache

# 4. Déploiement local Antigravity / Gemini CLI
python scripts/synchroniser_plugin_gemini.py --apply
python scripts/regenerer_cache_mcp.py --apply

# 5. Empaquetage universel ChatGPT (Web + Desktop)
python scripts/empaqueter_plugin_chatgpt.py --apply
```
