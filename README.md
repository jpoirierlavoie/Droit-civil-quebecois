# Pratique civile québécoise

Cinq compétences pour le litige civil et commercial québécois : **établir le droit**, **écrire**,
**qualifier les documents**, **dater**, **se rappeler ce qu'on doit**. Elles se répondent et ne se
recoupent pas.

| Compétence | Répond à | Produit |
|---|---|---|
| `recherche-juridique` | Quelle est la règle? | La fiche, la note de recherche, la vérification de citations |
| `redaction-juridique` | Comment l'écrire? | Le bloc de contenu d'un acte, d'une lettre, d'une note |
| `analyse-documentaire` | Qu'est-ce que ce document, et que vaut-il? | Le registre de tri, la fiche de pièce, le bordereau, la chronologie |
| `calendrier-procedural` | Quand? | Le calendrier daté de l'instance, chaque délai qualifié |
| `deontologie-professionnelle` | Qu'est-ce que je dois, ici? | L'obligation nommée au texte, signalée sans qu'on la demande |

Aucune compétence ne dépend d'un gestionnaire de dossiers. Le plugin `pallas-athena` fournit celui du
cabinet; un autre connecteur, ou aucun, laisse les cinq compétences pleinement opérantes. Les connecteurs
(sources de droit et calcul déterministe) sont déclarés ici : voir `.mcp.json`, `mcp_config.json` et
`gemini-extension.json`.

---

## Le partage des rôles

`recherche-juridique` **établit ce qui peut être affirmé**. Aucune proposition de droit n'est
avancée ailleurs sans être passée par elle ou par une source que l'utilisateur fournit.

`redaction-juridique` **consomme ce travail et le convertit en texte**. Elle ne construit pas le
fondement; elle le présuppose et signale quand il manque.

`analyse-documentaire` **dit ce qu'un document est, qui peut le voir et ce qu'il prouve**. Elle
alimente les autres — une pièce qualifiée devient une allégation soutenue, un jugement authentifié
devient une autorité, une chronologie fournit ses ancrages au calendrier.

`calendrier-procedural` **dit le jour**. Depuis une date d'ancrage, il déroule la chaîne des délais
du Code de procédure civile, compte selon l'art. 83 et qualifie selon l'art. 84. Il ne touche pas à
la prescription, qui est du droit substantiel et reste à la recherche.

`deontologie-professionnelle` **rappelle l'obligation, au texte, sans qu'on la demande**. Elle est
le second regard du praticien seul : chaque autre compétence porte, en fin de contrôle, une ligne
qui lui renvoie ce qu'elle a aperçu. Elle rappelle; elle n'atteste rien, ne lit l'état d'aucune
vérification et ne dépend d'aucun système de suivi — elle est la seule des cinq à ne porter aucun
besoin du contrat d'information.

Trois disciplines circulent d'une compétence à l'autre et portent le même nom partout :
- le **statut de lecture** d'une autorité (`recherche-juridique`) — citée, résumée, rapportée, lue;
- le **statut du fait** (`redaction-juridique`) — établi, rapporté, administratif, absent;
- le **régime de protection** d'un document (`analyse-documentaire`) — niveaux 0 à 3.

Une autorité, un fait ou un document transmis d'une compétence à l'autre voyage **avec son
statut**, jamais nu.

---

## Le contrat d'information

Les compétences disent **quels renseignements il leur faut**; elles ne disent jamais **par quel
appel les obtenir**. C'est la règle qui les garde indépendantes du logiciel.

Chaque compétence porte une section « Ce qu'il faut du dossier » rédigée dans un vocabulaire
commun de douze besoins :

| Besoin | Ce qu'il recouvre |
|---|---|
| **FICHE** | Qualification du recours, forum, rôle du client, délai inscrit et sa nature |
| **PARTIES** | Désignations exactes, forme juridique, qualité, coordonnées |
| **THÉORIE** | La théorie de la cause telle que l'avocat l'a arrêtée |
| **NOTES** | Ce qui a déjà été écrit au dossier sur la question |
| **INVENTAIRE** | Quels documents le dossier contient, sous quelle catégorie |
| **TEXTE** | Le texte d'un document donné |
| **ÉCHÉANCES** | Protocole, audiences, tâches, portrait de prescription |
| **CORRESPONDANCE** | Les échanges — courriels, lettres, pièces jointes |
| **CALCUL** | Le calcul d'un délai de procédure ou d'intérêts légaux — servi par le connecteur « pratique-civile-outils » (`calendrier_*`, `interets_compute_1619`), à défaut par `scripts/calcul_delai.py` pour les délais |
| **GREFFE** | La décomposition d'un numéro de dossier de cour et les palais de justice — servis par le connecteur « pratique-civile-outils » (`greffe_*`, `palais_*`) |
| **VOCABULAIRE** | Les codes qu'un système accepte en écriture |
| **INSCRIPTION** | Verser un résultat au dossier |

**L'appui factuel se cherche dans un ordre de préférence**, le même partout : le gestionnaire de
dossiers s'il y en a un de connecté; à défaut, l'avocat, interrogé sur les éléments précis qui
manquent; à défaut encore, la réponse en droit, hypothèses énoncées et crochets apparents. La
compétence dit toujours lequel des trois a servi, et ne bascule jamais en silence sur la mémoire
pour combler.

---

## Architecture des serveurs MCP

Le framework s'appuie sur quatre briques MCP complémentaires :

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Plugin Pratique Civile                          │
│     (Claude Code, Claude Desktop, claude.ai, Antigravity, Gemini CLI)  │
└───────┬────────────────────────┬───────────────────────────────┬───────┘
        │                        │                               │
┌───────▼────────────────┐┌──────▼───────────────────────┐┌──────▼───────────────────────┐
│     MCP-Legislation    ││   MCP-Jurisprudence          ││ pratique-civile-outils       │
│  Lois du Québec & Can. ││   Vérification CanLII        ││ Calcul déterministe & greffe │
│  (10 outils, D1/Vect.) ││   (10 outils, D1/CanLII)     ││ (6 outils, public sans état) │
└───────┬────────────────┘└──────┬───────────────────────┘└──────────────────────────────┘
        │                        │
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │  MCP-Socle-Juridique   │
        │ Bibliothèque partagée  │
        │ (SEP-2127, Bearer,     │
        │  JSON-RPC 2.0 router)  │
        └────────────────────────┘
```

1. **`MCP-Legislation`** (`https://legislation.poirierlavoie.ca/mcp`) : 10 outils en lecture seule sur le corpus législatif et réglementaire consolidé du Québec (LégisQuébec) et fédéral (Justice Canada). Recherche hybride (lexicale FTS5 et sémantique Vectorize).
2. **`MCP-Jurisprudence`** (`https://jurisprudence.poirierlavoie.ca/mcp`) : 10 outils de vérification déterministe et de consultation de citations contre l'API et la collection CanLII (métadonnées officielles, 6 verdicts d'intégrité).
3. **`pratique-civile-outils`** (`https://outils.poirierlavoie.ca/mcp`) : 6 outils de calcul déterministe arithmétique et d'annuaire judiciaire québécois (délais procéduraux art. 83 C.p.c., intérêts légaux art. 1619 C.c.Q., numéros de greffe et palais de justice MJQ). Point d'accès public, sans état, sans secret, acceptant à la fois `application/json` et `text/event-stream`.
4. **`MCP-Socle-Juridique`** (`@poirierlavoie/socle-juridique`) : bibliothèque de protocole partagée garantissant la conformité SEP-2127, le routage JSON-RPC 2.0 sans état, la vérification constante des jetons Bearer (`timingSafeEqual` sur empreintes SHA-256) et l'étanchéité CORS/DNS rebinding.

---

## Répertoire exhaustif des 26 outils MCP

### 1. Législation (10 outils — `https://legislation.poirierlavoie.ca/mcp`)
| Outil | Catégorie | Entrées principales | Sorties & Rôle |
|---|---|---|---|
| `legislation_find_relevant` | Découverte | `query`, `lang`, `limit` | Repérage heuristique déterministe de lois et chapitres pertinents (4 signaux). |
| `legislation_list_laws` | Découverte | `fonction`, `forum`, `subject`, `lang` | Carte intégrale du corpus, dates de consolidation et plan des grands codes. |
| `legislation_list_subjects` | Découverte | `lang` | Matières de la taxonomie du droit québécois (droit privé et spécialisé). |
| `legislation_related_laws` | Graphe | `law`, `rel_type`, `direction`, `lang` | Graphe d'interconnexion (lois habilitantes, règlements, relations curées). |
| `legislation_get_article` | Extraction | `law`, `article`, `lang` | Texte officiel verbatim d'un article, historique, fil d'Ariane et statut. |
| `legislation_get_articles` | Extraction | `law`, `from`, `to`, `numbers`, `lang` | Textes officiels en lot par plage continue ou liste de numéros. |
| `legislation_get_structure` | Structure | `law`, `depth`, `root_path`, `lang` | Arborescence d'une loi (Livres, Titres, Chapitres, Sections) sans texte. |
| `legislation_get_division` | Extraction | `law`, `path`, `include_text`, `lang` | Texte officiel d'une division complète avec ses sous-divisions et articles. |
| `legislation_search_text` | Recherche | `query`, `law`, `lang`, `limit` | Recherche plein texte hybride (lexicale + sémantique) avec replis étiquetés. |
| `legislation_resolve_reference` | Résolution | `citation`, `lang` | Résolution d'une citation informelle vers l'article officiel correspondant. |

### 2. Jurisprudence (10 outils — `https://jurisprudence.poirierlavoie.ca/mcp`)
| Outil | Catégorie | Entrées principales | Sorties & Rôle |
|---|---|---|---|
| `jurisprudence_verify_citations` | Vérification | `citations` (max 25), `lang`, `refresh` | Vérification déterministe contre CanLII sous 6 verdicts (CONFIRMÉE, etc.). |
| `jurisprudence_find_case` | Recherche | `title`, `database_id`, `year_from`, `year_to` | Retrouve une décision par les parties ou fragment d'intitulé. |
| `jurisprudence_get_case` | Consultation | `citation` OU (`database_id` + `case_id`) | Fiche CanLII complète d'une décision (métadonnées et hyperlien). |
| `jurisprudence_citator` | Citateur | `rel` (`cited`/`citing`/`legislation`), réf | Citateur brut sur la collection CanLII. |
| `jurisprudence_subsequent_history` | Heuristique | `citation` OU (`database_id` + `case_id`) | Indice heuristique d'historique en juridiction supérieure. |
| `jurisprudence_browse_cases` | Répertoire | `database_id`, filtres de dates | Liste chronologique des décisions récentes d'un tribunal. |
| `jurisprudence_list_databases` | Répertoire | `kind`, `jurisdiction`, `query` | Répertoire officiel des bases CanLII (tribunaux ou corpus législatifs). |
| `jurisprudence_browse_legislation` | CanLII Légis | `database_id`, `query`, `limit` | Liste des lois et règlements d'une base législative CanLII. |
| `jurisprudence_get_legislation` | CanLII Légis | `database_id`, `legislation_id` | Fiche CanLII d'une loi consolidée (dates de version de CanLII). |
| `jurisprudence_parse_citation` | Hors ligne | `citation` | Analyse syntaxique pure hors ligne d'une citation canadienne. |

### 3. Pratique civile outils (6 outils — `https://outils.poirierlavoie.ca/mcp`)
| Outil | Catégorie | Entrées principales | Sorties & Rôle |
|---|---|---|---|
| `calendrier_list_holidays` | Calcul | `year` (1970..2100), `regime` | Jours fériés et non juridiques (C.p.c., L.I. Québec, L.I. fédérale). |
| `calendrier_compute_deadlines` | Calcul | `event_date`, `deadlines` (1..25), `regime` | Calcul arithmétique déterministe de délais civils (art. 83 C.p.c.). |
| `interets_compute_1619` | Calcul | `end_date`, `tranches`, `mode` | Intérêts légaux (5 %) et indemnité additionnelle art. 1619 C.c.Q. (art. 28 L.A.F.). |
| `greffe_parse_court_file_number` | Annuaire | `court_file_number` | Décomposition d'un numéro de dossier de cour (palais, district, tribunal). |
| `palais_list` | Annuaire | `district`, `type`, `query` | Répertoire des palais de justice et points de service du Québec (MJQ). |
| `palais_get` | Annuaire | `greffe_number` (3 chiffres) OU `palais` | Fiche détaillée d'un lieu de justice (adresses municipale et postale). |

---

## Modèle de sécurité et d'authentification

1. **Variables d'environnement clientes vs secrets Cloudflare** :
   - Côté client (Claude Code, Claude Desktop, Antigravity, Gemini CLI), les variables sont nommées :
     - `MCP_LEGISLATION_SECRET` (transmis en en-tête `Authorization: Bearer ...`)
     - `MCP_JURISPRUDENCE_SECRET` (transmis en en-tête `Authorization: Bearer ...`)
   - Côté serveurs Cloudflare Workers :
     - Worker Législation lit `env.MCP_TOKEN` (ou `env.MCP_TOKEN_VEILLE`).
     - Worker Jurisprudence lit `env.MCP_SHARED_SECRET`.
2. **Comparaison à temps constant** :
   - La bibliothèque `@poirierlavoie/socle-juridique` hache le jeton présenté et le secret attendu en SHA-256 avant d'exécuter `crypto.subtle.timingSafeEqual`. Aucune fuite de préfixe ni de longueur n'est possible.
3. **Forme des refus** :
   - `MCP-Legislation` refuse en **HTTP 404** (corps vide), empêchant les clients MCP d'entrer dans une boucle de découverte OAuth destructrice.
   - `MCP-Jurisprudence` refuse en **HTTP 401** avec en-tête `WWW-Authenticate: Bearer`.
   - `pratique-civile-outils` est **public et sans état** (aucun secret ni jeton requis).
4. **Erreurs d'arguments** :
   - Tout échec de validation de schéma ou d'argument d'outil répond un résultat applicatif `{ content: [...], isError: true }` et jamais une faute JSON-RPC `-32602`. L'agent LLM peut ainsi lire l'erreur et auto-corriger son appel.

---

## Installation et configuration multi-plateformes

### 1. Claude Code CLI

#### Méthode 1 : Ligne de commande `claude mcp add`
```bash
# Connecteur Législation
claude mcp add --transport http legislation https://legislation.poirierlavoie.ca/mcp --header "Authorization: Bearer ${MCP_LEGISLATION_SECRET}"

# Connecteur Jurisprudence
claude mcp add --transport http jurisprudence https://jurisprudence.poirierlavoie.ca/mcp --header "Authorization: Bearer ${MCP_JURISPRUDENCE_SECRET}"

# Connecteur Outils (public)
claude mcp add --transport http pratique-civile-outils https://outils.poirierlavoie.ca/mcp
```

#### Méthode 2 : Fichier `.mcp.json` dans le projet
Créer `.mcp.json` à la racine de votre projet :
```json
{
  "mcpServers": {
    "legislation": {
      "type": "http",
      "url": "https://legislation.poirierlavoie.ca/mcp",
      "headers": {
        "Authorization": "Bearer ${MCP_LEGISLATION_SECRET}"
      }
    },
    "jurisprudence": {
      "type": "http",
      "url": "https://jurisprudence.poirierlavoie.ca/mcp",
      "headers": {
        "Authorization": "Bearer ${MCP_JURISPRUDENCE_SECRET}"
      }
    },
    "pratique-civile-outils": {
      "type": "http",
      "url": "https://outils.poirierlavoie.ca/mcp"
    }
  }
}
```

Installer ensuite le catalogue de compétences :
```bash
/plugin marketplace add jpoirierlavoie/pratique-civile-quebecoise
/plugin install pratique-civile-quebecoise@pratique-civile-quebecoise
```

---

### 2. Claude Desktop (`claude_desktop_config.json`)

Emplacement du fichier :
- **macOS** : `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows** : `%APPDATA%\Claude\claude_desktop_config.json`

Ajouter dans la section `mcpServers` :
```json
{
  "mcpServers": {
    "legislation": {
      "url": "https://legislation.poirierlavoie.ca/mcp",
      "headers": {
        "Authorization": "Bearer VOTRE_SECRET_LEGISLATION"
      }
    },
    "jurisprudence": {
      "url": "https://jurisprudence.poirierlavoie.ca/mcp",
      "headers": {
        "Authorization": "Bearer VOTRE_SECRET_JURISPRUDENCE"
      }
    },
    "pratique-civile-outils": {
      "url": "https://outils.poirierlavoie.ca/mcp"
    }
  }
}
```

*Remarque : si votre version de Claude Desktop requiert un pont stdio local, employer `npx -y mcp-remote <URL> --header "Authorization: Bearer <SECRET>"`.*

---

### 3. Claude.ai (Navigateur Web)

Dans l'interface web `claude.ai` :
1. Accéder à *Paramètres de l'organisation → Connecteurs / Intégrations*.
2. Ajouter les connecteurs distants :
   - **Legislation** : `https://legislation.poirierlavoie.ca/mcp?key=<VOTRE_SECRET_LEGISLATION>` (ou en-tête `Authorization: Bearer <VOTRE_SECRET_LEGISLATION>`).
   - **Jurisprudence** : `https://jurisprudence.poirierlavoie.ca/mcp?key=<VOTRE_SECRET_JURISPRUDENCE>` (ou en-tête `Authorization: Bearer <VOTRE_SECRET_JURISPRUDENCE>`).
   - **pratique-civile-outils** : `https://outils.poirierlavoie.ca/mcp` (sans secret).

---

### 4. Google Antigravity

1. Installer le plugin :
   ```bash
   agy plugin install https://github.com/jpoirierlavoie/pratique-civile-quebecoise.git
   ```
   ou cloner le dossier dans `~/.gemini/config/plugins/pratique-civile-quebecoise`.
2. Le fichier `mcp_config.json` à la racine câble automatiquement les 3 serveurs :
   - Définir `MCP_LEGISLATION_SECRET` et `MCP_JURISPRUDENCE_SECRET` dans les variables de plugin Antigravity.
   - Les schémas d'outils sont mis en cache dans `~/.gemini/antigravity/mcp/`.

---

### 5. Gemini CLI

1. Installer l'extension :
   ```bash
   gemini extensions install https://github.com/jpoirierlavoie/pratique-civile-quebecoise
   ```
2. Le fichier `gemini-extension.json` invite à saisir de façon masquée (`sensitive: true`) les secrets `MCP_LEGISLATION_SECRET` et `MCP_JURISPRUDENCE_SECRET` et active `pratique-civile-outils` sans secret requis.

---

## Contrôle qualité et vérification

Exécuter la suite de contrôles depuis la racine du dépôt :

```bash
# 1. Contrôle statique des invariants et des manifestes
python verifier.py

# 2. Exécution des scénarios d'évaluation et tests unitaires locaux
python evals/executer_evals.py --auto-test

# 3. Vérification de bout en bout multi-serveurs (M3)
python verifier_tout.py
```
