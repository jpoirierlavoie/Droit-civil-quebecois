---
name: phase-introduction-reponse
description: >-
  Orchestrateur d'introduction ou de réponse à une demande civile/commerciale : demande
  introductive, avis d'assignation, urgence (injonction, saisie, sauvegarde, contrôle
  judiciaire), réponse dans les délais, moyens préliminaires, défense, reconvention et
  protocole. En anglais — use to introduce or defend an action, urgent relief. Ne pas
  utiliser pour le droit familial/criminel ni les interrogatoires ou l'appel.
---

# Phase 2 — Introduction d'instance ou réponse

[NON VALIDÉ PAR LA PRATIQUE]

Orchestre la phase introductive du litige selon la posture (demandeur, défendeur ou voie rapide d'urgence), de la vérification des préalables jusqu'à la signification/notification et au protocole. Aucune règle de fond ici.

<!-- SAFETY-KERNEL:START -->
## Garde-fous impératifs

1. **Confidentialité stricte :** Ne jamais inclure de noms de clients, faits identifiants, extraits de pièces ou numéros de dossier dans une recherche web ni dans un champ de recherche libre `query` (`lois.find_relevant`, `lois.search_text`). Sont seuls permis : les dénominations, adresses et numéros de greffe soumis aux outils sans journalisation de `outils` (`registre_search`, `adresse_verify`, `greffe_parse_number`) et les intitulés de décisions publiées dans `juris` (`find_case`, `verify_citations`).
2. **Sources primaires obligatoires (arrêt sur le volet touché) :** Ne jamais réciter un article, un délai, un seuil indexé ou le ratio d'un arrêt de mémoire. Repérer les trois connecteurs par leurs outils signatures — y compris s'ils sont différés (les charger par recherche d'outils avant de conclure à leur absence) ou nommés sous un alias client (`legis` / `Législation`, `Jurisprudence`, `Outils`) : `lois` (`get_article`, `get_articles`), `juris` (`verify_citations`, `get_case`) et `outils` (`calendrier_deadlines`, `interets_1619`). Si le connecteur requis échoue (`401`, `404`, hors ligne) sans repli local prévu par la compétence, **s'arrêter sur le volet touché**, nommer le connecteur et demander à l'avocat de le reconnecter ou de fournir le texte officiel.
3. **Étanchéité bijuridique :** Écarter tout droit étranger (`.fr`, Belgique, Suisse; art. 1240, 2224, 1641) et purger les calques de common law (*duty of care*, *consideration*, *estoppel*, dommages punitifs sans loi habilitante sous l'art. 1621 C.c.Q.). En anglais, employer exclusivement la terminologie officielle anglaise du C.c.Q. et du C.p.c. (`get_article(lang="en")`, `terminologie_lookup`).
4. **Protection et déclencheurs déontologiques :** Présumer tout document non coté `CONFIDENTIEL` (jamais `PUBLIC` par défaut). Signaler au texte via `lois` (`b-1-r.3.1`, `b-1-r.5`, `cpc` art. 108, 192–194) une obligation déontologique ou de caviardage uniquement devant un fait déclencheur concret, sans mise en garde générique.
5. **Perception et précédents :** Ne jamais décrire un média, une image ou un document non effectivement perçu dans la session (sinon demander une transcription ou un extrait visuel et marquer l'analyse « support secondaire »). Un précédent interne n'est utilisé que s'il est fourni par l'avocat, dé-identifié, sans jamais importer un fait, un nom ni une pièce de l'autre dossier.
<!-- SAFETY-KERNEL:END -->

## Entrées requises

* Branche applicable (`demandeur`, `defendeur` ou `urgence`) et confirmation que le conflit est dégagé;
* Pièces au soutien et faits validés (ou demande introductive signifiée et procès-verbal de signification en défense);
* Mode de rédaction souhaité (`acte complet` par défaut au Palier 3 ou `bloc pour gabarit`).

## État de la phase

* **Emplacement :** `etat-dossier/phase-introduction-reponse.md` dans le répertoire du dossier (ou bloc à sauvegarder sur `claude.ai`).
* **En-tête :** `phase: phase-introduction-reponse` · `branche` · `date` · `palier` · `dernière mise à jour`.
* **Corps :** tableau `| Étape | Statut (À faire / En cours / Franchie / Bloquée) | Livrable | Porte | Notes |`.
* **Règles :** relire au début de chaque tour; jamais copié hors du dossier; faits tagués `Établi / Rapporté / Déduit / [À CONFIRMER]`.

## Parcours

### Étape 1 — Choix de branche, préalables et délais critiques
* **Objectif :** Confirmer les préalables (demandeur) ou calculer immédiatement les délais de réponse, protocole et moyens préliminaires (défendeur/urgence).
* **Livrable :** Tableau des échéances et préalables.
* **Porte :** **BLOQUANTE** en défense sur la date de réponse; en demande sur prescription/compétence.

### Étape 2 — Théorie de la cause et matrice de concordance
* **Objectif :** Fixer les fondements, allégations, cotes et lacunes de preuve avant d'écrire la procédure.
* **Livrable :** Théorie de la cause (8 blocs) et matrice `Allégation ↔ Pièce ↔ Témoin`.
* **Porte :** Chaque conclusion visée est appuyée par des faits identifiés.

### Étape 3 — Rédaction de l'acte approprié (ou mesure d'urgence)
* **Objectif :** Produire l'acte adapté à la branche (demande introductive, défense/exposé sommaire, moyen préliminaire, reconvention/garantie, ou injonction/saisie/contrôle judiciaire).
* **Livrable :** Projet d'acte complet (Palier 3) sans droit dans les allégations de fait.
* **Porte :** Cotes continues et faits manquants marqués `[À CONFIRMER]`.

### Étape 4 — Bordereau, contrôle de production et signification
* **Objectif :** Dresser le bordereau (`145`), purger métadonnées/caviardages (`108`), vérifier pagination (`535.3`/`535.6`) et préparer l'endos et la signification/notification.
* **Livrable :** Bordereau, endos et bon de travail de dépôt/signification.
* **Porte :** **BLOQUANTE** — zéro commentaire caché, zéro renseignement sensible non caviardé.

### Étape 5 — Protocole de l'instance (procédure ordinaire)
* **Objectif :** Rédiger et négocier le protocole de l'instance (`148 C.p.c.`, exclu sous régime simplifié C.Q. `535.2`).
* **Livrable :** Protocole daté et vérifié.
* **Porte :** Dépôt confirmé dans les délais légaux.

## Enchaînements

| Étape | Type | Cible | Feuille | Palier | Condition |
|---|---|---|---|---|---|
| 1 | référence | recherche-juridique | grille-prealables | — | toujours |
| 1 | livrable | gestion-du-mandat | conformite-ouverture-conflits-mandat | 2 | branche urgence (si conflit à revalider) |
| 1 | livrable | gestion-du-mandat | conformite-echeanciers-cpc | 3 | toujours (délais réponse/signification) |
| 2 | livrable | analyse-et-strategie | piece-reception-et-qualification | 2 | branche défendeur (pièces adverses) |
| 2 | livrable | analyse-et-strategie | preuve-directe | 2 | branche urgence (média/pièce clé et journal) |
| 2 | livrable | analyse-et-strategie | produit-theorie-de-la-cause | 2 | après Étape 1 franchie |
| 2 | livrable | analyse-et-strategie | produit-matrice-allegations | 2 | après Étape 1 franchie |
| 3 | référence | redaction-juridique | fondamentaux-actes | — | toujours pour un acte (incluant déclaration sous serment) |
| 3 | livrable | redaction-juridique | acte-demande-introductive | 3 | branche demandeur |
| 3 | livrable | redaction-juridique | acte-defense-et-expose-sommaire | 3 | branche défendeur |
| 3 | livrable | redaction-juridique | acte-moyens-preliminaires | 3 | si exception soulevée |
| 3 | livrable | redaction-juridique | acte-reconvention-intervention-garantie | 3 | si reconvention ou tiers |
| 3 | livrable | redaction-juridique | acte-injonction | 3 | branche urgence (injonction) |
| 3 | livrable | redaction-juridique | acte-saisie-avant-jugement | 3 | branche urgence (saisie) |
| 3 | livrable | redaction-juridique | acte-demandes-cours-instance | 3 | branche urgence (ordonnance de sauvegarde) |
| 3 | livrable | redaction-juridique | acte-mesures-provisionnelles-autres | 3 | branche urgence (séquestre / type Mareva) |
| 3 | livrable | redaction-juridique | acte-pourvoi-controle-judiciaire | 3 | si contrôle judiciaire |
| 4 | livrable | production-et-conformite | cahier-des-pieces-et-bordereaux | 3 | après Étape 3 franchie |
| 4 | livrable | production-et-conformite | controle-acte-de-procedure | 3 | avant dépôt ou signification |
| 4 | livrable | production-et-conformite | controle-pdf-et-metadonnees | 3 | avant dépôt PDF (dont urgence) |
| 4 | livrable | production-et-conformite | controle-endos-depot-signification | 3 | avant dépôt ou signification |
| 5 | livrable | redaction-juridique | contrat-protocole-instance | 3 | instance ordinaire uniquement |

## Branches

* **Branche demandeur :** `references/branche-demandeur.md`
* **Branche défendeur :** `references/branche-defendeur.md`
* **Voie rapide urgence :** `references/branche-urgence.md`

## Contrôle de sortie de phase

1. Actes signifiés/notifiés, preuve de signification archivée et `etat-dossier/phase-introduction-reponse.md` à jour.
2. Protocole déposé (ou calendrier simplifié C.Q. consigné) avec date limite de mise en état notée.
3. **Suite suggérée (texte brut) :** passer à `phase-interrogatoires-instruction` (ou `phase-preparation-audience` si audience urgente fixée à court terme).
