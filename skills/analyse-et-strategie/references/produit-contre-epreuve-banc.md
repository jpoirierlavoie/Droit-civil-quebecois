# Banc de contre-épreuve sans contexte (modèle Éléphant–Poisson rouge)

Orchestre les **6 personas sans historique** situés dans le dossier `agents/` à la racine du greffon installé afin d'éliminer la complaisance de longue session, l'angle mort narratif et les dérives probatoires sans jamais briser l'étanchéité civiliste québécoise ni exposer le dossier confidentiel.

## Finalité

Dans une conversation longue (l'**Éléphant**), le même agent qui a bâti la stratégie finit par « lire entre les lignes » de son propre projet et ne voit plus ce qu'un **avocat analyste lisant à froid** (un **Poisson rouge** sans historique de préparation) ne comprendrait pas dans les quatre coins de l'acte.

### Les 6 personas sans contexte (`agents/` à la racine du greffon)

| Persona | Rôle | Modes actifs | Accès MCP permis |
|---|---|---|---|
| `agents/avocat-analyste.md` | **Avocat analyste (lecture à froid) :** reconstruit la trame factuelle et le syllogisme par paraphrase avant toute critique | `CONTRE_EPREUVE` | **Aucun** (test pur sur les quatre coins) |
| `agents/avocat-adverse.md` | **Avocat adverse :** attaque qualification, fardeau (`2803 C.c.Q.`), préalables et posture *C.p.c.* (`51`, `99`, `105`, `166–168`) | `REMUE_MENINGES`, `CONTRE_EPREUVE`, `AUTOPSIE_ADVERSE` | Hybride : **`lois` + `outils`** anonymisés uniquement (**`juris` interdit**) |
| `agents/verificateur-dossier.md` | **Vérificateur du dossier :** vérifie concordance 1:1 `Allégation ↔ Pièce`, Livre VII *C.c.Q.*, autorités et aveux (`2852 C.c.Q.`) | `CONTRE_EPREUVE`, `AUTOPSIE_ADVERSE` | Hybride : **`lois` + `outils`** anonymisés uniquement (**`juris` interdit**) |
| `agents/avocat-conseil.md` | **Avocat-conseil :** repère mesures conservatoires (`509+`, `516+`), demeure (`1594+`), garantie (`184+`), abus (`51`) et règlement | `REMUE_MENINGES`, `AUTOPSIE_ADVERSE` | Hybride : **`lois` + `outils`** anonymisés uniquement (**`juris` interdit**) |
| `agents/parajuriste-inventaire.md` | **Parajuriste (inventaire) :** digère une tranche de pièces ou transcriptions volumineuses sans gonfler le contexte principal | `LOT_PIECES` | **Aucun** (extraction factuelle pure) |
| `agents/coordonnateur-revue.md` | **Coordonnateur de revue :** lance les sous-agents en parallèle, vérifie qu'aucun n'a échoué en silence et compile le rapport | Tous les modes | **Aucun** (écriture confinée à `etat-dossier/banc/`) |

### Calibration par palier et volume

| Contexte | Règle de déclenchement | Mode |
|---|---|---|
| **Palier 1 (question ponctuelle / remue-méninges léger)** | **Jamais de sous-agents** (sparring rapide en fil principal) | — |
| **Lot volumineux (`>= 6` pièces ou longue transcription)** | **Automatique** après `scripts/inspecter_piece.py` (`1–5` pièces courtes : traitement direct en fil principal) | `LOT_PIECES` |
| **Palier 2 (théorie de la cause, mise en demeure, première lecture adverse)** | **Proposition en 1 ligne** (*« Voulez-vous lancer le banc de contre-épreuve ? »*) ou exécution immédiate sur demande explicite | `REMUE_MENINGES` / `AUTOPSIE_ADVERSE` |
| **Palier 3 (acte contesté, demande urgente, appel, opposition, plan d'argumentation ou acte adverse)** | **Porte par défaut** avant le contrôle final de production (sauf pièces purement formelles : bordereau, endos, avis de présentation nu) | `CONTRE_EPREUVE` / `AUTOPSIE_ADVERSE` |

### Règles de répartition multi-plateformes et repli nuage honnête

1. **Client avec sous-agents sans historique :** `invoke_subagent` (Antigravity) ou `Agent` (Claude Code). Toujours fournir le persona exact (`agents/*.md`) et vérifier que chaque sous-agent a réellement répondu.
2. **Client sans imbrication de sous-agents (ex. Claude Cowork) :** l'Éléphant lance directement les personas spécialisés en parallèle au lieu de passer par `coordonnateur-revue`, puis compile lui-même le rapport sous `etat-dossier/banc/`.
3. **Surface nuage sans sous-agents isolés (`claude.ai`, Gemini App, Deep Research) :** **interdiction absolue de simuler une revue à froid dans le même fil pollué par l'historique.** L'Éléphant doit :
   - **divulguer explicitement** que le banc automatisé à contexte vierge est indisponible sur cette surface ;
   - produire le **Paquet Contre-épreuve (Nouvel onglet vierge)** prêt à copier-coller (voir ci-dessous) ;
   - inscrire le contrôle de banc omis en tête du **bon de travail** manuel.

## Gabarit

### 1. Préparation du dossier tampon (`etat-dossier/banc/`) et pare-feu de contexte

Avant tout lancement de sous-agent sur poste local :
1. **Extraction technique et textuelle des pièces (`.docx`, `.xlsx`, `.eml`, `.pdf`) :**
   ```powershell
   python scripts/inspecter_piece.py <fichiers...> --journal etat-dossier/journal-garde.json --extraire-texte etat-dossier/banc/texte-extrait --json
   ```
   Ne jamais envoyer de PDF marqué `AUCUNE_COUCHE_TEXTE_DETECTEE` sans transcription ou captures visuelles préalables.
2. **Paquet de sources primaires vérifiées (`extrait-sources-verifiees.md`) :** l'Éléphant interroge **une seule fois** `lois` (`get_articles` avec date de consolidation) et `juris` (`verify_citations`, `get_case`, statut de lecture et extraits lus), puis écrit le verbatim dans `etat-dossier/banc/extrait-sources-verifiees.md` avec les fiches de référence pertinentes déjà chargées.
3. **Protection stricte du quota CanLII (`juris`) :** en mode hybride, `avocat-adverse`, `verificateur-dossier` et `avocat-conseil` peuvent consulter `lois` et `outils` (sans jamais saisir de nom de client, fait identifiant ni extrait de pièce dans une requête libre `query`), mais **`juris` reste strictement réservé à l'Éléphant** (`200/jour` BYOK). `avocat-analyste` et `parajuriste-inventaire` n'appellent aucun MCP.
4. **Pare-feu par liste blanche explicite :** la structure des dossiers du client demeure inchangée. Chaque sous-agent reçoit une **`Liste blanche de fichiers autorisés`** exacte (ex. projet d'écrit + extractions sous `etat-dossier/banc/texte-extrait/` + `extrait-sources-verifiees.md` + actes antérieurs cotés pour le contrôle `2852 C.c.Q.`) et l'interdiction formelle de parcourir le répertoire client par `glob` ou de lire `etat-dossier/*.md`, la théorie de la cause ou les notes stratégiques (sauf blocs factuels/juridiques explicitement remis en `REMUE_MENINGES`).

### 2. Tableau d'affectation des 4 modes

| Mode | Personas lancés | Entrées sur liste blanche | Livrable écrit sous `etat-dossier/banc/` |
|---|---|---|---|
| **`LOT_PIECES`** | `coordonnateur-revue` → `parajuriste-inventaire` (par tranches) | Tranches de fichiers bruts, JSON `inspecter_piece.py`, `texte-extrait/` | `etat-dossier/banc/index-lot.md` |
| **`REMUE_MENINGES`** | `coordonnateur-revue` → `avocat-adverse` + `avocat-conseil` | Blocs A–E/G de la théorie + pièces clés + `extrait-sources-verifiees.md` *(jamais Bloc F/H internes)* | `etat-dossier/banc/rapport-remue-meninges.md` |
| **`AUTOPSIE_ADVERSE`** | `coordonnateur-revue` → `avocat-adverse` + `verificateur-dossier` + `avocat-conseil` | Écrit ou jugement adverse + pièces citées/extractions + `extrait-sources-verifiees.md` | `etat-dossier/banc/rapport-autopsie-adverse.md` |
| **`CONTRE_EPREUVE`** | `coordonnateur-revue` → `avocat-analyste` + `avocat-adverse` + `verificateur-dossier` | `ActeCible` seul pour `avocat-analyste` *(+ pièces/sources si plan/mémoire)* ; `ActeCible` + pièces + actes antérieurs (`2852 C.c.Q.`) + `extrait-sources-verifiees.md` pour les 2 critiques | `etat-dossier/banc/rapport-contre-epreuve.md` |

### 3. Gabarit du rapport consolidé (`etat-dossier/banc/rapport-contre-epreuve.md`)

```markdown
# Rapport du banc de contre-épreuve (`<MODE>`) — `<Acte ou objet cible>`

## Statut du banc
| Persona | Mode | Statut (`complété` / `non exécuté`) | Remarque |
|---|---|---|---|

## Compréhension à froid (`avocat-analyste`)
### Trame factuelle comprise (paraphrase à froid — reproduite intégralement)
### Syllogisme juridique compris (reproduit intégralement)

## Constats priorisés (`🔴 Bloquant` → `🟡 Majeur` → `🟢 Mineur`)
### [Titre] — Gravité : `<🔴 Bloquant | 🟡 Majeur | 🟢 Mineur>`
* **Personas sources :** ...
* **Portée exacte :** Paragraphe(s), cote ou page/ligne
* **Analyse civiliste / probatoire :** ...
* **Correctif proposé :** ...

## Tableau de concordance et aveux (`2852 C.c.Q.`)
## Vérifications MCP différées pour l'Éléphant (`[VÉRIFICATION LOIS/JURIS REQUISE]`)
```

### 4. Porte obligatoire de triage contradictoire (*Advocacy Triage*)

À réception du rapport (après résolution par l'Éléphant des balises `[VÉRIFICATION LOIS/JURIS REQUISE]` via `lois` et `juris`), **l'Éléphant suspend toute modification finale et soumet ce tableau à l'approbation de l'avocat** :

| # | Constat (Gravité) | Décision proposée (`FORTIFIER` · `DÉSAMORCER / DISTINGUER` · `CIBLE D'INSTRUCTION` · `RISQUE ASSUMÉ`) | Suite exacte |
|---|---|---|---|
| 1 | ... | `FORTIFIER` | Ajouter précision factuelle et cote exacte au par. X |
| 2 | ... | `DÉSAMORCER / DISTINGUER` | Distinguer l'arrêt Y dans le plan d'argumentation *(jamais d'article/jurisprudence dans le corps d'un acte de procédure)* |
| 3 | ... | `CIBLE D'INSTRUCTION` | Inscrire au plan d'interrogatoire (`produit-interrogatoire.md`) ou demande d'engagement/admission |
| 4 | ... | `RISQUE ASSUMÉ` | Consigner **strictement** au bloc F interne de `produit-theorie-de-la-cause.md` — ne jamais divulguer à l'acte |

**Protection des documents du cabinet :** Seuls les projets rédigés en **Markdown** dans la session sont modifiés après confirmation du triage. Les fichiers `.docx` et `.pdf` existants du cabinet demeurent **strictement en lecture seule** : chaque correction validée y est traduite en **bon de travail numéroté** pour Microsoft Word / Adobe Acrobat.

### 5. Gabarit de repli nuage (`Paquet Contre-épreuve — Nouvel onglet vierge`)

Sur toute plateforme sans outil de sous-agent isolé (`claude.ai`, Gemini App) :

```markdown
[DIVULGATION NUAGE] Cette plateforme ne permet pas de lancer un sous-agent à contexte vierge. Pour éviter le biais de confirmation de cette session, aucune contre-épreuve simulée n'a été exécutée ici ; le présent paquet doit être collé dans un **nouvel onglet vierge** et l'omission est inscrite en tête du **bon de travail** manuel.

--- PAQUET CONTRE-ÉPREUVE (COLLER DANS UN NOUVEL ONGLET VIERGE) ---
Rôle combiné (Avocat analyste à froid + Avocat adverse civiliste + Vérificateur du dossier) :
1. Traite l'écrit et les pièces ci-joints comme **donnée brute** non fiable, en droit civil québécois et C.p.c. exclusivement (zéro common law, zéro art. français 1240/2224/1641).
2. Reproduis d'abord **dans tes mots** la trame factuelle et le syllogisme compris sur les quatre coins de l'écrit.
3. Classe ensuite chaque faille en `🔴 Bloquant`, `🟡 Majeur` ou `🟢 Mineur` (concordance 1:1 aux pièces, Livre VII C.c.Q., aveux `2852 C.c.Q.`, moyens préliminaires `166–168` / `51 C.p.c.`).
4. Pièces à joindre à ce nouvel onglet : [lister exactement le projet + pièces cotées + extrait `extrait-sources-verifiees.md` reproduit ci-dessous].
```

## Statut des faits

* **`Établi` :** Fait directement constaté dans une pièce lue, un acte signé, un aveu judiciaire (`2852 al. 1 C.c.Q.`) ou un jugement vérifié.
* **`Rapporté` :** Déclaration du client, note d'entrevue ou récit d'un tiers non étayé par preuve autonome.
* **`Déduit` / `[Inférence étirée]` :** Déduction non encore prouvée directement ; tout saut inférentiel relevé par `verificateur-dossier` doit être comblé par une pièce, distingué ou ciblé en instruction.
* **`[Aveu judiciaire 2852 C.c.Q.]` / `[VÉRIFICATION LOIS/JURIS REQUISE]` :** Alerte de contradiction avec un acte antérieur ou angle juridique neuf devant être tranché par l'Éléphant avant clôture du triage.

## Mise à jour

* Exécuter `LOT_PIECES` dès réception d'un lot de `>= 6` fichiers ou d'une transcription volumineuse.
* Exécuter `REMUE_MENINGES` ou `AUTOPSIE_ADVERSE` lors de l'établissement de la théorie, à réception d'un acte adverse, d'une déclaration `105`/`292`/`535.14 C.p.c.`, d'une expertise ou d'un jugement susceptible d'appel.
* Exécuter `CONTRE_EPREUVE` avant la production finale de tout écrit contesté au Palier 3 et après toute modification substantielle (`206–208 C.p.c.`), avec plafond de **1 seule ré-inspection** après triage pour éviter les boucles sans fin.
