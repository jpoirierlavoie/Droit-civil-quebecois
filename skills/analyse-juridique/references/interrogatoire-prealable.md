# Interrogatoire préalable : plan de préparation et extraction de transcription

Couvre à la fois la **préparation stratégique d'un interrogatoire oral ou écrit** et l'**extraction structurée d'une transcription** (engagements et objections).

## 1. Verrous procéduraux à lire via `lois.get_articles`

Avant de planifier ou d'analyser un interrogatoire, appeler `lois.get_articles(law="cpc", numbers=["221", "222", "223", "226", "227", "228", "229", "535.9"])` et `law="ccq", numbers=["2835", "2852"]`.

| Verrou | Règle à confirmer à la source (`cpc`) |
|---|---|
| **Seuil monétaire (`229 al. 1`)** | `[à confirmer via lois]` Aucun interrogatoire préalable permis lorsque la valeur en litige est inférieure à `50 000 $`. |
| **Cadre (`221`, `535.9`)** | En instance ordinaire : prévu au protocole (`148`). En régime simplifié C.Q. (`50 000 $` à `< 100 000 $`) : écrit plafonné à **3 pages** et au plus **1 interrogatoire oral** par partie sans autorisation (`535.9`). |
| **Budget de temps (`229 al. 2–3`)** | **3 h** (familial ou `< 100 000 $`, prolongeable à 4 h par entente) ou **5 h** (autres cas, prolongeable à 7 h); au-delà sur autorisation du tribunal. |
| **Délais et personnes (`221 al. 2`, `223`, `226`)** | Avis ou citation à l'oral **au moins 5 jours** avant (`226`); écrit avec réponse entre **15 jours et 1 mois** (`223`); personnes interrogables sans consentement limitées à `221 al. 2`. |

## 2. Préparation : plan d'interrogatoire préalable

Chaque module s'ancre sur les faits contestés et lacunes de preuve de la stratégie du dossier et vise l'un de quatre objectifs : obtenir un aveu (`2852 C.c.Q.`), faire reconnaître l'origine/auteur d'un écrit non signé (`2835 C.c.Q.`), figer une version avant procès, ou requérir un engagement précis (`221 al. 1 C.p.c.`).

* **Structure par défaut :**
  1. `VERROUS PROCÉDURAUX ET BUDGET DE TEMPS` *(incluant la réserve pour l'interrogatoire de sa propre partie ou d'un tiers)*
  2. `OBJECTIFS CIBLÉS (AVEUX ET ENGAGEMENTS)`
  3. `MODULES DE QUESTIONS (PAR THÈME)` en tableau : `| Fait cible | Pièce à exhiber (cote + vérification d'authenticité) | Questions (courtes, factuelles, chronologiques, 1 idée/question) | Relance / pièce de contradiction | Engagement souhaité (libellé sténographique) |`
  4. `OBJECTIONS ANTICIPÉES (ART. 228 C.P.C.)` *(préparer la réplique distinguant l'objection suspensive de l'objection de simple pertinence)*

## 3. Extraction obligatoire sur une transcription d'interrogatoire

Contrôler d'abord les mentions (`221, 227, 229 C.p.c.`) : date et durée (contrôle 3 h / 5 h), assermentation, procureurs, attestation du sténographe officiel. Rappeler que seule la partie qui a interrogé décide de produire la transcription en tout ou en extrait (`227 al. 2`), sous réserve des extraits indissociables.

Dresser **systématiquement deux tableaux avec renvoi exact `Page / Ligne`** :

### Tableau 1 — Engagements souscrits (`art. 221 al. 1 C.p.c.`)
`| Cote (E-1, E-2…) | Page / Ligne | Objet précis de l'engagement | Pièce ou renseignement promis | État (Reçu / En suspens) |`

### Tableau 2 — Objections soulevées (`art. 228 C.p.c.`)
`| Page / Ligne | Question visée | Motif invoqué | Nature (`228 al. 2` Suspensive vs `228 al. 3` Non suspensive) | Suite requise |`

* **Qualification `228 al. 2` vs `228 al. 3` :**
  * **Suspensive (`228 al. 2`) :** Refus de répondre fondé sur la **contraignabilité**, les **droits fondamentaux** (incluant secret professionnel), les faits présumés non pertinents (violence sexuelle/conjugale) ou un **intérêt légitime important** — **délai de 5 jours** pour la soumettre au tribunal (**signaler immédiatement pour calcul dans `administration-litige`**).
  * **Non suspensive (`228 al. 3`) :** Simple pertinence ou autre motif — le témoin **doit répondre sous réserve** et le tribunal tranche à l'instruction.
