# Droit civil québécois (`v2.1.0`)

Greffon multiplateforme (Claude Code, Claude Desktop, `claude.ai` / Claude Research, Google Antigravity, Gemini CLI, Gemini App / Vertex AI et Gemini API Deep Research) regroupant **5 compétences de pratique juridique québécoise**, **17 feuilles de référence ciblées**, **2 scripts Python locaux** et **3 connecteurs MCP spécialisés** (`lois`, `juris`, `outils` — 32 outils officiels) adossés au portail d'accès [`MCP-Acces`](https://github.com/jpoirierlavoie/MCP-Acces) (`acces.poirierlavoie.ca`) pour le litige et le conseil en droit civil et commercial québécois.

---

## Philosophie de conception (`v2.1.0`)

La version `2.1.0` (`droit-civil-quebecois`) prolonge l'architecture `v2.0` à trois couches vers l'ouverture encadrée aux membres du Barreau du Québec et la prise en charge native des modes **Deep Research** :

1. **Découverte progressive à 3 niveaux (*3-Tier Progressive Discovery*) :**
   - **Niveau 1 — En-têtes et routeurs (`SKILL.md`) :** 5 descriptions YAML compactes (`<= 850` car.) et 5 routeurs synthétiques (`<= 1 000` mots) partageant un noyau de garde-fous canonique (`SAFETY-KERNEL`, identique au bit près par empreinte SHA-256).
   - **Niveau 2 — Feuilles terminales (« impasses ») :** 17 fiches ciblées (`<= 1 500` mots et `<= 12 Kio` chacune) chargées à la demande selon l'intention précise, sans renvois en chaîne infinis.
   - **Niveau 3 — Outillage déterministe local et connecteurs MCP :** 2 scripts Python utilisant uniquement la bibliothèque standard (`inspecter_piece.py`, `calcul_delai.py`) et 32 outils MCP distants à schémas durcis.
2. **Calibration de rigueur à 3 paliers :**
   - **Palier 1 — Triage / Question ponctuelle :** orientation rapide sur règle vérifiée, sans surproduction documentaire.
   - **Palier 2 — Travail de dossier / Analyse :** stratégie, remue-méninges, tri de preuve, matrices de concordance et plans d'argumentation.
   - **Palier 3 — Acte ou état prêt au dépôt / Cour :** procédure complète par défaut (en-tête de cour, avis d'assignation, corps allégué, conclusions, avis de présentation, endos de cour) — avec mode explicite *« bloc de contenu seul à copier-coller »* lorsque demandé.
3. **Sources primaires obligatoires (*fail-closed*) :** les connecteurs `lois`, `juris` et `outils` sont requis pour énoncer un article, un seuil indexé, un délai calculé ou une décision authentifiée. Si un connecteur requis échoue (`401`, `404`, `429`, `[CLEF_ABSENTE]`, `[CLEF_REFUSEE]`, `QUOTA_EPUISE`, hors ligne) sans repli local prévu par la compétence, l'agent s'arrête sur le volet touché, nomme le connecteur et demande à l'avocat de rétablir l'accès (`acces.poirierlavoie.ca/moi`) ou de fournir le texte officiel. Au Palier 3, toute décision non lue intégralement en PDF CanLII utilise explicitement le marqueur de complétion `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`.
4. **Budget d'identifiants natif (`<= 64` caractères) :** tous les identifiants composés respectent nativement la limite stricte de 64 caractères sans tronquer les schémas JSON (maximum **62/64** sous Claude Code, **52/64** sous Google Antigravity).

---

## Les 5 compétences, 17 feuilles et 2 scripts (`skills/`)

| Compétence | Rôle principal | Feuilles (`references/`) et scripts locaux (`scripts/`) |
|---|---|---|
| **`recherche-juridique`** | Droit applicable, prescriptions, préalables procéduraux, jurisprudence et doctrine | `grille-prealables.md`, `strategie-sources.md`, `doctrine-et-livrables.md` |
| **`analyse-juridique`** | Stratégie, remue-méninges, qualification de pièces, privilège/confidentialité, chronologies, préparation d'interrogatoire | `remue-meninges-et-strategie.md`, `tri-mentions-et-chronologie.md`, `preuve-et-protection.md`, `interrogatoire-prealable.md`, `scripts/inspecter_piece.py` |
| **`redaction-juridique`** | Actes de procédure complets, mémoires/exposés en appel, mises en demeure, transactions, contrats, purge d'anglicismes | `actes-de-procedure.md`, `argumentation-appel-et-sources.md`, `correspondance-et-contrats.md`, `anti-contamination-bilingue.md` |
| **`administration-litige`** | Délais et calendrier C.p.c., bordereaux de pièces (`145`, `174`, `247`, `250`), concordance, endos, tableaux de quantum/intérêts (`1619 C.c.Q.`), état des frais (`339–344`) | `echeanciers-cpc.md`, `bordereaux-concordance-et-endos.md`, `tableaux-quantum-et-frais.md`, `scripts/calcul_delai.py` |
| **`deontologie-et-pratique`** | Conflits d'intérêts, identification du client, mandat/honoraires, fidéicommis, facturation, rapports avec la partie adverse et le tribunal | `radar-deontologique.md`, `identification-conflits-et-mandat.md`, `facturation-temps-et-fideicommis.md` |

---

## Les 3 connecteurs MCP et les 32 outils

| Clé serveur | Montages HTTP | Authentification et politique | Dépôt serveur |
|---|---|---|---|
| **`lois`** | Direct : `https://legislation.poirierlavoie.ca/mcp`<br>OAuth : `https://legislation.poirierlavoie.ca/mcp/oauth` | `/mcp` : `Authorization: Bearer ${MCP_LEGISLATION_SECRET}` (refus uniforme `404`)<br>`/mcp/oauth` : **OAuth 2.1 PKCE `S256`** via `acces.poirierlavoie.ca` (`401` RFC 9728) | [MCP-Legislation](https://github.com/jpoirierlavoie/MCP-Legislation) |
| **`juris`** | Direct : `https://jurisprudence.poirierlavoie.ca/mcp`<br>OAuth : `https://jurisprudence.poirierlavoie.ca/mcp/oauth` | `/mcp` : `Authorization: Bearer ${MCP_JURISPRUDENCE_SECRET}` (refus uniforme `404`)<br>`/mcp/oauth` : **OAuth 2.1 PKCE `S256`** via `acces.poirierlavoie.ca` (`401` RFC 9728)<br>**BYOK CanLII strict :** clé API CanLII personnelle requise (coffre chiffré ou `X-Clef-CanLII`) | [MCP-Jurisprudence](https://github.com/jpoirierlavoie/MCP-Jurisprudence) |
| **`outils`** | Public : `https://outils.poirierlavoie.ca/mcp` | Accès public libre (sans secret, lecture seule D1) | [MCP-Outils](https://github.com/jpoirierlavoie/MCP-Outils) |

> Les deux serveurs authentifiés (`lois` et `juris`) sont configurés par variables d'environnement uniquement (`MCP_LEGISLATION_SECRET` et `MCP_JURISPRUDENCE_SECRET`). Un seul jeton individuel de portée `les_deux` (43 car.) peut alimenter les deux variables. Aucun secret n'est stocké dans le dépôt.

### Catalogue exact des 32 outils (`v2.1.0`)

| Serveur (`lois`, 10 outils) | Serveur (`juris`, 10 outils) | Serveur (`outils`, 12 outils) |
|---|---|---|
| `list_laws` | `verify_citations` | `calendrier_holidays` |
| `list_subjects` | `find_case` | `calendrier_deadlines` |
| `related_laws` | `get_case` | `interets_1619` |
| `find_relevant` | `citator` | `greffe_parse_number` |
| `get_article` | `subsequent_history` | `palais_list` |
| `get_articles` | `browse_cases` | `palais_get` |
| `get_structure` | `list_databases` | `registre_search` |
| `get_division` | `browse_legislation` | `registre_get_entity` |
| `search_text` | `get_legislation` | `adresse_verify` |
| `resolve_reference` | `parse_citation` | `terminologie_lookup` |
| — | — | `termino_attestations` |
| — | — | `terminologie_scan` |

---

## Admission, clé API CanLII personnelle (BYOK) et jetons (`acces.poirierlavoie.ca`)

L'accès aux serveurs authentifiés (`lois` et `juris`) est réservé aux **membres actifs en règle du Barreau du Québec**, gérés via le portail [`https://acces.poirierlavoie.ca`](https://acces.poirierlavoie.ca) ([`MCP-Acces`](https://github.com/jpoirierlavoie/MCP-Acces)) :

1. **Demande d'admission (`/demande`) :**
   - Soumettre votre numéro de membre du Barreau du Québec, votre adresse courriel professionnelle et votre **clé API CanLII personnelle** (vérifiée en direct contre l'API CanLII dès l'admission).
   - Confirmer la propriété du courriel via le lien reçu de `noreply@acces.poirierlavoie.ca`, puis attendre la validation manuelle au *Bottin des avocats*.
   - La clé CanLII est scellée par chiffrement d'enveloppe (`HKDF-SHA256` + `AES-256-GCM`) dans le coffre `coffre_clef` ; à défaut de clé active au coffre (ou d'en-tête `X-Clef-CanLII`), les 9 outils CanLII de `juris` retournent `[CLEF_ABSENTE]` / `[CLEF_REFUSEE]` avant toute lecture du cache partagé.
2. **Espace libre-service titulaire (`/moi`) :**
   - **Jeton individuel (`les_deux`, `legislation` ou `jurisprudence`) :** jeton CSPRNG de 256 bits (`43` car. `base64url`), affiché une seule fois et stocké en condensé `SHA-256`. Un jeton `les_deux` peut être collé à la fois dans `MCP_LEGISLATION_SECRET` et `MCP_JURISPRUDENCE_SECRET`.
   - **Rotation / révocation :** remplacement ou révocation immédiate des jetons et de la clé API CanLII (support de transition sans coupure).
   - **Préférence `hybride_permis` (S19) :** activation ou désactivation en un clic du moteur vectoriel `Workers AI` dans `lois.search_text` (exécution 100 % lexicale FTS5 sur D1 lorsque désactivée).
   - **Droits Loi 25 :** exportation JSON et suppression intégrale en cascade du compte.
3. **Gouvernance publique :** [`/cgu`](https://acces.poirierlavoie.ca/cgu), [`/confidentialite`](https://acces.poirierlavoie.ca/confidentialite), [`/attestation`](https://acces.poirierlavoie.ca/attestation), [`/conformite`](https://acces.poirierlavoie.ca/conformite) et [`/gouverne`](https://acces.poirierlavoie.ca/gouverne).

---

## Installation par plateforme

### 1. Claude Code

Définir votre jeton individuel dans l'environnement utilisateur (un jeton `les_deux` suffit pour les deux variables), puis installer depuis la place de marché du dépôt :

```bash
export MCP_LEGISLATION_SECRET="<votre-jeton-titulaire>"
export MCP_JURISPRUDENCE_SECRET="<votre-jeton-titulaire>"
```

```text
/plugin marketplace add jpoirierlavoie/droit-civil-quebecois
/plugin install droit-civil-quebecois@droit-civil-quebecois
```

### 2. Claude Desktop & `claude.ai` (connecteurs personnalisés)

Deux modes sont pris en charge :
- **Recommandé (OAuth 2.1 PKCE `S256`) :** ajouter les connecteurs **`lois`** (`https://legislation.poirierlavoie.ca/mcp/oauth`), **`juris`** (`https://jurisprudence.poirierlavoie.ca/mcp/oauth`) et **`outils`** (`https://outils.poirierlavoie.ca/mcp`), puis compléter la connexion sur `acces.poirierlavoie.ca`.
- **Direct par paramètre de requête (`?key=`) :** saisir `https://legislation.poirierlavoie.ca/mcp?key=<votre-jeton>` et `https://jurisprudence.poirierlavoie.ca/mcp?key=<votre-jeton>` **dès la création du connecteur, avant toute première sonde** (sinon `claude.ai` reçoit un `404` et bascule sur la découverte OAuth). Importer les compétences `skills/` dans l'espace de travail pour activer le noyau `SAFETY-KERNEL`.

### 3. Google Antigravity

Synchroniser le greffon vers `~/.gemini/config/plugins/droit-civil-quebecois` et configurer `MCP_LEGISLATION_SECRET` / `MCP_JURISPRUDENCE_SECRET` dans le gestionnaire de greffons (identifiants nativement `<= 64` car., max 52 sous Antigravity) :

```powershell
python scripts/synchroniser_plugin_gemini.py --apply
python scripts/regenerer_cache_mcp.py --apply   # optionnel : reconstruit le cache depuis les dépôts locaux
```

### 4. Gemini CLI

```bash
gemini extensions install https://github.com/jpoirierlavoie/droit-civil-quebecois
```

`gemini-extension.json` déclare `sensitive: true` sur `MCP_LEGISLATION_SECRET` et `MCP_JURISPRUDENCE_SECRET` et fixe `"contextFileName": []` afin que les consignes de développement (`GEMINI.md`) n'alourdissent jamais le contexte juridique de l'avocat.

### 5. Gemini App (`gemini.google.com`) & Vertex AI Gemini Enterprise

Brancher les montages OAuth 2.1 **`https://legislation.poirierlavoie.ca/mcp/oauth`**, **`https://jurisprudence.poirierlavoie.ca/mcp/oauth`** (flux OAuth 2.1 + PKCE `S256` et RFC 9728 via `acces.poirierlavoie.ca`), et **`https://outils.poirierlavoie.ca/mcp`** (public, sans authentification).

---

## Modes Deep Research (`Claude Research` & `Gemini Deep Research`)

Les 32 outils des trois serveurs (`lois`, `juris`, `outils`) sont compatibles nativement sans façade supplémentaire avec **Claude Research** et **Gemini Deep Research** (`deep-research-preview-04-2026`, `deep-research-max-preview-04-2026`), avec limiteurs d'arête dédiés aux rafales multi-agents (`300/min` `lois`, `180/min` `juris`) et quotas journaliers UTC (`1 500` `local`, `200` `sortant`, `150` `semantique`) :

- **Claude Research (`claude.ai`) :** activer les 3 connecteurs (OAuth sur `/mcp/oauth` ou `?key=` sur `/mcp` + `outils`), régler les outils en lecture seule sur *Always allow*, charger `skills/`, puis **anonymiser strictement toute question** avant de lancer la boucle (la recherche web ouverte est active par défaut).
- **Gemini API Deep Research (`google-genai` / `gemini-api` CLI) :** déclarer les 3 serveurs en `"type": "mcp_server"` sur `/mcp` avec `"Authorization": "Bearer ..."` pour `lois` et `juris` (plus `outils` sans en-tête). Comme `background=True` exige `store=True`, **ne soumettre que des questions juridiques anonymisées** et **préfixer la requête** avec le préambule `SAFETY-KERNEL` ci-dessous (les fichiers `skills/` n'étant pas chargés automatiquement dans l'agent API) :

```text
CONTRAINTES IMPÉRATIVES (DROIT CIVIL QUÉBÉCOIS — PALIER 2/3) :
1. Confidentialité : Requête entièrement anonymisée ; n'inclure aucun nom de partie, numéro de dossier ni fait identifiant dans aucune recherche web ni requête `query`.
2. Sources primaires obligatoires : Ne citer aucun article de loi sans l'avoir lu via le serveur `lois` (`get_article` / `get_articles`) en relevant sa date de consolidation. Ne citer aucun arrêt sans l'authentifier via `juris` (`verify_citations`, `citator` / `subsequent_history`).
3. Étanchéité bijuridique : Exclure tout droit étranger (`.fr`, Belgique, Suisse ; art. 1240, 2224, 1641) et tout calque de common law (*duty of care*, *consideration*, *estoppel*, dommages punitifs sans loi habilitante sous l'art. 1621 C.c.Q.).
4. Lecture intégrale des arrêts : N'énoncer un ratio ou paragraphe d'arrêt que si le texte intégral officiel a été consulté en session. Sinon, laisser explicitement le marqueur :
   [RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]
5. Arrêt sur échec (`fail-closed`) : Si un connecteur retourne `401`, `404`, `429`, `[CLEF_ABSENTE]`, `[CLEF_REFUSEE]` ou `QUOTA_EPUISE`, s'arrêter sur le volet touché et signaler le rétablissement requis dans `acces.poirierlavoie.ca/moi`.

QUESTION JURIDIQUE ANONYMISÉE :
<Insérer ici la question de droit abstraitement formulée>
```

---

## Migration depuis `v1.x` (`pratique-civile-quebecoise`) -> `v2.1.0` (`droit-civil-quebecois`)

En `v2.x`, le greffon adopte l'identifiant `droit-civil-quebecois`, les clés `lois`/`juris`/`outils`, les 32 noms d'outils compacts `<= 64` caractères et l'authentification individuelle par titulaire sur `acces.poirierlavoie.ca` :

- **Claude Code :** désinstaller l'ancien greffon (`/plugin uninstall pratique-civile-quebecoise`), installer `jpoirierlavoie/droit-civil-quebecois` et exporter votre jeton `acces.poirierlavoie.ca` dans `MCP_LEGISLATION_SECRET` / `MCP_JURISPRUDENCE_SECRET`.
- **Google Antigravity :** exécuter `python scripts/synchroniser_plugin_gemini.py --apply` (retire automatiquement `~/.gemini/config/plugins/pratique-civile-quebecoise` et copie les gabarits `v2.1.0`), puis remplacer manuellement les valeurs de `MCP_LEGISLATION_SECRET` et `MCP_JURISPRUDENCE_SECRET` dans le gestionnaire de greffons ou vos variables d'environnement par votre jeton individuel `acces.poirierlavoie.ca`.
- **Gemini CLI :** exécuter `gemini extensions uninstall pratique-civile-quebecoise` puis installer `droit-civil-quebecois`.

---

## Vérification et qualité

```powershell
$env:PYTHONUTF8 = "1"
python verifier.py                                  # Contrôle statique strict (sortie muette, code 0)
python verifier.py --stats                          # Bilan de taille des compétences (< 140 KB)
python evals/executer_evals.py --auto-test          # Validation déterministe des 20 scénarios & 2 scripts
python verifier_tout.py --mode mock                 # Suite E2E multi-paliers locale (82 vérifications)
python verifier_tout.py --mode live                 # Vérification distante (requiert les 2 jetons env)
```

---

## Sécurité et licence

- Consulter [SECURITY.md](SECURITY.md) pour la politique de divulgation coordonnée, l'architecture BYOK CanLII, la gouvernance zéro-log et les règles propres aux modes Deep Research.
- Licence : **CC-BY-NC-SA-4.0** assortie d'une **Autorisation complémentaire de pratique professionnelle du droit** (*Companion Professional Legal Practice Grant*) pour les membres en règle du Barreau du Québec — voir [LICENSE](LICENSE).
