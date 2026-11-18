# Droit civil québécois (`v3.0.0`)

Greffon multiplateforme (Claude Code, Claude Desktop, claude.ai, Google Antigravity et Gemini CLI) pour le **litige civil et commercial québécois** *(hors droit familial et droit criminel)* regroupant **10 compétences** (5 orchestrateurs de phase et 5 compétences de service), **59 feuilles de référence granulaires**, **4 scripts Python locaux** (bibliothèque standard uniquement) et **3 connecteurs MCP spécialisés** (`lois`, `juris`, `outils` — 32 outils officiels).

---

## Philosophie de conception (`v3.0.0`)

1. **Orchestrateurs de phase + Services transversaux :**
   - **5 orchestrateurs de phase (`phase-*`) :** portent uniquement les listes de contrôle, séquences, portes bloquantes, fichiers d'état persistés (`etat-dossier/<phase>.md`) et tables d'enchaînements vérifiées vers les services (`## Enchaînements`).
   - **5 compétences de service :** détiennent l'ensemble des règles de fond, gabarits normalisés par famille et outillage déterministe, avec découvertes à 3 niveaux et chargement ciblé (socle + 1 ou 2 feuilles max, plafond `<= 64 Kio` par chargement).
2. **Noyau de sécurité canonique v3 (`SAFETY-KERNEL`) :** Identique au bit près sur les **10** `SKILL.md` (5 garde-fous : confidentialité stricte, sources primaires obligatoires *fail-closed*, étanchéité bijuridique, protection asymétrique `CONFIDENTIEL`, **honnêteté perceptuelle et dé-identification des précédents internes**).
3. **Calibration de rigueur à 3 paliers :**
   - **Palier 1 — Triage / Question ponctuelle :** orientation rapide sur règle vérifiée, sans surproduction.
   - **Palier 2 — Travail de dossier / Analyse :** stratégie, qualification probatoire, chronologie, matrice de concordance, note interne.
   - **Palier 3 — Acte ou cahier prêt au dépôt / Cour :** procédure complète par défaut (avec mode explicite *« bloc pour gabarit du cabinet »*), contrôle intégral `lois`/`juris` (`Lue (intégrale) [par. X]` ou marqueur `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`), audit technique et bon de travail.
4. **Vérifier, rapporter et émettre un bon de travail (`production-et-conformite`) :** Les 4 scripts locaux inspectent métadonnées, mise en page Word/PDF, OCR, signets et continuité des cotes en lecture seule, puis émettent un **bon de travail** précis pour les outils du cabinet (Microsoft Word, Adobe Acrobat / outil PDF).

---

## Cartographie des 10 compétences, 59 feuilles et 4 scripts (`skills/`)

### A. Cinq orchestrateurs de phase (`phase-*`)

| Phase | Rôle d'orchestration et portes | Feuilles de branche (`references/`) |
|---|---|---|
| **`phase-ouverture-dossier`** | Conflit (**porte bloquante**), identification/mandat, tri/garde des pièces, triage d'urgence, recherche préliminaire, note stratégique, mise en demeure ou suite | — |
| **`phase-introduction-reponse`** | Préalables et délai de réponse (**porte bloquante**), théorie/matrice, rédaction d'acte ou mesure urgente, bordereau/signification (**porte**), protocole | `branche-demandeur.md`, `branche-defendeur.md`, `branche-urgence.md` |
| **`phase-interrogatoires-instruction`** | Communication/caviardage, plan d'interrogatoire, séance, transcription (**porte**), engagements et objections `5 j` `228 al. 2` (**porte**), expertises, modifications `206–208` | — |
| **`phase-preparation-audience`** | Mise en état `173` (**porte bloquante**), CRA/règlement, témoins/fiches, cahiers (sources, pièces, procédures), plan d'argumentation, admissions, contrôle complet de production (**porte bloquante**) | `branche-audience-interlocutoire.md` |
| **`phase-jugement-et-suites`** | Réception du jugement, délai de rigueur appel/permission/rétractation (**porte bloquante**), analyse, rapport client, appel/rétractation, exécution, frais/intérêts `1619`, clôture et fidéicommis | — |

### B. Cinq compétences de service

| Service | Rôle principal | Feuilles (`references/`) et scripts (`scripts/`) |
|---|---|---|
| **`recherche-juridique`** | Préalables, législation (`lois`), jurisprudence (`juris`), doctrine admissible, précédents internes dé-identifiés (Q5), livrables et statuts de lecture | `grille-prealables.md`, `recherche-legislative.md`, `recherche-jurisprudentielle.md`, `recherche-doctrinale.md`, `recherche-precedents-internes.md`, `recherche-livrables.md` |
| **`analyse-et-strategie`** | Réception/qualification, preuve directe (honnêteté perceptuelle & journal de garde), preuve indirecte, documents judiciaires, recevabilité, privilèges/caviardage, théorie de la cause, notes, matrice, fiche témoins, chronologie, interrogatoires | `piece-reception-et-qualification.md`, `preuve-directe.md`, `preuve-indirecte.md`, `preuve-documents-judiciaires.md`, `preuve-recevabilite-force-probante.md`, `preuve-privilege-confidentialite-caviardage.md`, `produit-theorie-de-la-cause.md`, `produit-note-et-memo.md`, `produit-matrice-allegations.md`, `produit-fiche-preuve-et-temoins.md`, `produit-chronologie.md`, `produit-interrogatoire.md`, `scripts/inspecter_piece.py` |
| **`redaction-juridique`** | Actes de procédure complets (12 familles : demande introductive, défense/exposé, cours d'instance/206–208, moyens préliminaires, reconvention/garantie, injonction, saisie avant jugement, mesures provisionnelles, contrôle judiciaire, appel, rétractation, exécution), argumentation/mémoires (4), correspondance & contrats (7), socle et purge bilingue | `fondamentaux-actes.md`, `anti-contamination-bilingue.md`, `acte-*` (`12`), `arg-*` (`4`), `corr-*` (`3`), `contrat-*` (`4`) |
| **`production-et-conformite`** | Contrôle formel d'actes et correspondance, audit PDF (OCR, signets, liens, métadonnées, commentaires), cahier des sources, bordereaux & cahier des pièces, cahier des procédures, endos/dépôt/signification et bon de travail | `controle-acte-de-procedure.md`, `controle-correspondance.md`, `controle-pdf-et-metadonnees.md`, `cahier-des-sources.md`, `cahier-des-pieces-et-bordereaux.md`, `cahier-des-procedures.md`, `controle-endos-depot-signification.md`, `scripts/controler_document.py`, `scripts/verifier_cotes.py` |
| **`gestion-du-mandat`** | Ouverture/conflits/identification/mandat, radar déontologique (11 moments, 19 silences, IA), feuilles de temps et fidéicommis (`b-1-r.5`), échéanciers et délais C.p.c., tableaux quantum/Scott, intérêts `1619 C.c.Q.` et état des frais (`339–344`) | `conformite-ouverture-conflits-mandat.md`, `conformite-radar-deontologique.md`, `conformite-facturation-fideicommis.md`, `conformite-echeanciers-cpc.md`, `conformite-quantum-interets-frais.md`, `scripts/calcul_delai.py` |

---

## Les 3 connecteurs MCP et les 32 outils

| Clé serveur | URL MCP | Authentification | Dépôt serveur |
|---|---|---|---|
| **`lois`** | `https://legislation.poirierlavoie.ca/mcp` | `Authorization: Bearer ${MCP_LEGISLATION_SECRET}` (garde non-oracle `404`) | [MCP-Legislation](https://github.com/jpoirierlavoie/MCP-Legislation) |
| **`juris`** | `https://jurisprudence.poirierlavoie.ca/mcp` | `Authorization: Bearer ${MCP_JURISPRUDENCE_SECRET}` (`401 WWW-Authenticate`) | [MCP-Jurisprudence](https://github.com/jpoirierlavoie/MCP-Jurisprudence) |
| **`outils`** | `https://outils.poirierlavoie.ca/mcp` | Accès public libre (sans secret) | [MCP-Outils](https://github.com/jpoirierlavoie/MCP-Outils) |

> Les deux serveurs authentifiés (`lois` et `juris`) sont configurés par variables d'environnement uniquement (`MCP_LEGISLATION_SECRET` et `MCP_JURISPRUDENCE_SECRET`). Aucun secret n'est stocké dans le dépôt. Tous les identifiants composés d'outils respectent nativement le plafond `<= 64` caractères (max **62/64** sous Claude Code, **52/64** sous Antigravity).

---

## Installation par plateforme

### 1. Claude Code

```bash
export MCP_LEGISLATION_SECRET="<votre-secret-legislation>"
export MCP_JURISPRUDENCE_SECRET="<votre-secret-jurisprudence>"
```

```text
/plugin marketplace add jpoirierlavoie/droit-civil-quebecois
/plugin install droit-civil-quebecois@droit-civil-quebecois
```

### 2. Claude Desktop & `claude.ai`

1. Dans les connecteurs personnalisés, ajouter **`lois`** (`https://legislation.poirierlavoie.ca/mcp`), **`juris`** (`https://jurisprudence.poirierlavoie.ca/mcp`) et **`outils`** (`https://outils.poirierlavoie.ca/mcp`), avec l'en-tête `Authorization: Bearer <secret>` pour `lois` et `juris`.
2. Importer les compétences depuis `skills/` ou installer le bundle `.claude-plugin/plugin.json`.

### 3. Google Antigravity & Gemini CLI

```powershell
# Google Antigravity (synchronisation locale)
python scripts/synchroniser_plugin_gemini.py --apply
python scripts/regenerer_cache_mcp.py --apply   # optionnel depuis les dépôts locaux
```

```bash
# Gemini CLI
gemini extensions install https://github.com/jpoirierlavoie/droit-civil-quebecois
```

---

## Vérification et qualité

```powershell
python verifier.py                                  # Contrôle statique strict (muet, code 0)
python verifier.py --stats                          # Bilan des 10 compétences, descriptions et chargements
python verifier.py --release                        # Contrôle publication (zéro marqueur brouillon + couverture complète)
python evals/executer_evals.py --auto-test          # Validation des scénarios, 4 scripts locaux et fixtures vérificateur
python verifier_tout.py --mode mock                 # Suite E2E multi-paliers locale
python verifier_tout.py --mode live                 # Vérification distante (requiert les 2 secrets env)
```

---

## Sécurité et licence

- Consulter [SECURITY.md](SECURITY.md) pour la politique de divulgation coordonnée, les règles de secret professionnel et les garanties de confidentialité des connecteurs.
- Licence : **CC-BY-NC-SA-4.0** — voir [LICENSE](LICENSE).
