# Droit civil québécois (`v2.0.0`)

Greffon multiplateforme (Claude Code, Claude Desktop, claude.ai, Google Antigravity et Gemini CLI) regroupant **5 compétences de pratique juridique québécoise**, **17 feuilles de référence ciblées**, **2 scripts Python locaux** et **3 connecteurs MCP spécialisés** (`lois`, `juris`, `outils` — 32 outils officiels) pour le litige et le conseil en droit civil et commercial québécois.

---

## Philosophie de conception (`v2.0.0`)

La version `2.0.0` (`droit-civil-quebecois`) remplace l'ancienne architecture monolithique orientée vers un seul gestionnaire de dossiers par une structure agnostique conçue pour la pratique réelle d'un avocat au Québec :

1. **Découverte progressive à 3 niveaux (*3-Tier Progressive Discovery*) :**
   - **Niveau 1 — En-têtes et routeurs (`SKILL.md`) :** 5 descriptions YAML compactes (`<= 850` car.) et 5 routeurs synthétiques (`<= 1 000` mots) partageant un noyau de garde-fous canonique (`SAFETY-KERNEL`, identique au bit près par empreinte SHA-256).
   - **Niveau 2 — Feuilles terminales (« impasses ») :** 17 fiches ciblées (`<= 1 500` mots et `<= 12 Kio` chacune) chargées à la demande selon l'intention précise, sans renvois en chaîne infinis.
   - **Niveau 3 — Outillage déterministe local et connecteurs MCP :** 2 scripts Python utilisant uniquement la bibliothèque standard (`inspecter_piece.py`, `calcul_delai.py`) et 32 outils MCP distants à schémas durcis.
2. **Calibration de rigueur à 3 paliers :**
   - **Palier 1 — Triage / Question ponctuelle :** orientation rapide sur règle vérifiée, sans surproduction documentaire.
   - **Palier 2 — Travail de dossier / Analyse :** stratégie, remue-méninges, tri de preuve, matrices de concordance et plans d'argumentation.
   - **Palier 3 — Acte ou état prêt au dépôt / Cour :** procédure complète par défaut (en-tête de cour, avis d'assignation, corps allégué, conclusions, avis de présentation, endos de cour) — avec mode explicite *« bloc de contenu seul à copier-coller »* lorsque demandé.
3. **Sources primaires obligatoires (*fail-closed*) :** les connecteurs `lois`, `juris` et `outils` sont requis pour énoncer un article, un seuil indexé, un délai calculé ou une décision authentifiée. Si un connecteur requis est hors ligne ou non configuré (`401` / `404`), l'agent s'arrête, nomme le connecteur manquant et demande de le reconnecter ou de fournir le texte officiel. Au Palier 3, toute décision non lue intégralement en PDF CanLII utilise explicitement le marqueur de complétion `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`.
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

| Clé serveur | URL MCP | Authentification | Dépôt serveur |
|---|---|---|---|
| **`lois`** | `https://legislation.poirierlavoie.ca/mcp` | `Authorization: Bearer ${MCP_LEGISLATION_SECRET}` (garde non-oracle `404`) | [MCP-Legislation](https://github.com/jpoirierlavoie/MCP-Legislation) |
| **`juris`** | `https://jurisprudence.poirierlavoie.ca/mcp` | `Authorization: Bearer ${MCP_JURISPRUDENCE_SECRET}` (`401 WWW-Authenticate`) | [MCP-Jurisprudence](https://github.com/jpoirierlavoie/MCP-Jurisprudence) |
| **`outils`** | `https://outils.poirierlavoie.ca/mcp` | Accès public libre (sans secret) | [MCP-Outils](https://github.com/jpoirierlavoie/MCP-Outils) |

### Catalogue exact des 32 outils (`v2.0.0`)

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

> Les deux serveurs authentifiés (`lois` et `juris`) sont configurés par variables d'environnement uniquement (`MCP_LEGISLATION_SECRET` et `MCP_JURISPRUDENCE_SECRET`). Aucun secret n'est stocké dans le dépôt.

---

## Installation par plateforme

### 1. Claude Code

Définir d'abord les secrets dans l'environnement utilisateur, puis installer depuis la place de marché du dépôt :

```bash
export MCP_LEGISLATION_SECRET="<votre-secret-legislation>"
export MCP_JURISPRUDENCE_SECRET="<votre-secret-jurisprudence>"
```

```text
/plugin marketplace add jpoirierlavoie/droit-civil-quebecois
/plugin install droit-civil-quebecois@droit-civil-quebecois
```

### 2. Claude Desktop & `claude.ai`

1. Dans les connecteurs personnalisés, ajouter les trois URL MCP (`https://legislation.poirierlavoie.ca/mcp`, `https://jurisprudence.poirierlavoie.ca/mcp`, `https://outils.poirierlavoie.ca/mcp`) avec l'en-tête `Authorization: Bearer <secret>` pour `lois` et `juris`.
2. Importer les compétences depuis `skills/` ou installer le bundle `.claude-plugin/plugin.json`.

### 3. Google Antigravity

Synchroniser le greffon vers `~/.gemini/config/plugins/droit-civil-quebecois` et configurer `MCP_LEGISLATION_SECRET` / `MCP_JURISPRUDENCE_SECRET` dans le gestionnaire de greffons (tous les outils respectent nativement le plafond `<= 64` caractères, max 52 caractères sous Antigravity) :

```powershell
python scripts/synchroniser_plugin_gemini.py --apply
python scripts/regenerer_cache_mcp.py --apply   # optionnel : reconstruit le cache depuis les dépôts locaux
```

### 4. Gemini CLI

```bash
gemini extensions install https://github.com/jpoirierlavoie/droit-civil-quebecois
```

`gemini-extension.json` déclare `sensitive: true` sur `MCP_LEGISLATION_SECRET` et `MCP_JURISPRUDENCE_SECRET` et fixe `"contextFileName": []` afin que les consignes de développement (`GEMINI.md`) n'alourdissent jamais le contexte juridique de l'avocat.

---

## Migration depuis `v1.x` (`pratique-civile-quebecoise`) -> `v2.0.0` (`droit-civil-quebecois`)

En `v2.0.0`, le greffon change de nom (`droit-civil-quebecois`), de clés de serveurs (`lois`, `juris`, `outils`) et d'identifiants d'outils pour corriger le bogue de troncature `> 64` caractères et supprimer l'ancien couplage applicatif :

- **Claude Code :** désinstaller l'ancien greffon (`/plugin uninstall pratique-civile-quebecoise`), retirer l'ancienne place de marché si nécessaire, puis installer `jpoirierlavoie/droit-civil-quebecois`.
- **Google Antigravity :** exécuter `python scripts/synchroniser_plugin_gemini.py --apply` ; le script déploie `droit-civil-quebecois`, retire automatiquement l'ancien dossier `~/.gemini/config/plugins/pratique-civile-quebecoise` et purge les fichiers obsolètes. Si le cache local est régénéré via `python scripts/regenerer_cache_mcp.py --apply`, les anciens répertoires `pratique-civile-quebecoise_*` sont supprimés.
- **Gemini CLI :** exécuter `gemini extensions uninstall pratique-civile-quebecoise` puis installer `droit-civil-quebecois`.

---

## Vérification et qualité

```powershell
python verifier.py                                  # Contrôle statique strict (sortie muette, code 0)
python verifier.py --stats                          # Bilan de taille des compétences (< 140 KB)
python evals/executer_evals.py --auto-test          # Validation déterministe des 19 scénarios & 2 scripts
python verifier_tout.py --mode mock                 # Suite E2E multi-paliers locale (79 vérifications)
python verifier_tout.py --mode live                 # Vérification distante (requiert les 2 secrets env)
```

---

## Sécurité et licence

- Consulter [SECURITY.md](SECURITY.md) pour la politique de divulgation coordonnée, les règles de secret professionnel et les garanties de confidentialité des connecteurs.
- Licence : **CC-BY-NC-SA-4.0** — voir [LICENSE](LICENSE).
