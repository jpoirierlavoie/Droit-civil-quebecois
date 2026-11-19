---
name: phase-ouverture-dossier
description: >-
  Orchestrateur d'ouverture d'un dossier civil ou commercial : consultation initiale, conflit
  d'intérêts, identification du client, mandat, tri initial des pièces, urgence, recherche
  préliminaire et note stratégique. En anglais — use for client intake, conflict check,
  retainer, initial triage. Ne pas utiliser pour rédiger un acte complet (redaction-juridique),
  un dossier familial/criminel ni une phase d'instruction ou d'appel.
---

# Phase 1 — Ouverture du dossier et consultation initiale

[NON VALIDÉ PAR LA PRATIQUE]

Orchestre la prise en charge initiale du dossier, du contrôle de conflit jusqu'à la note stratégique et à la décision de suite (mise en demeure ou introduction). Aucune règle de fond ici : chaque livrable et référence s'appuie sur les compétences de service.

<!-- SAFETY-KERNEL:START -->
## Garde-fous impératifs

1. **Confidentialité stricte :** Ne jamais inclure de noms de clients, faits identifiants, extraits de pièces ou numéros de dossier dans une recherche web ni dans un champ de recherche libre `query` (`lois.find_relevant`, `lois.search_text`). Sont seuls permis : les dénominations, adresses et numéros de greffe soumis aux outils sans journalisation de `outils` (`registre_search`, `adresse_verify`, `greffe_parse_number`) et les intitulés de décisions publiées dans `juris` (`find_case`, `verify_citations`).
2. **Sources primaires obligatoires (arrêt sur le volet touché) :** Ne jamais réciter un article, un délai, un seuil indexé ou le ratio d'un arrêt de mémoire. Repérer les trois connecteurs par leurs outils signatures — y compris s'ils sont différés (les charger par recherche d'outils avant de conclure à leur absence) ou nommés sous un alias client (`legis` / `Législation`, `Jurisprudence`, `Outils`) : `lois` (`get_article`, `get_articles`), `juris` (`verify_citations`, `get_case`) et `outils` (`calendrier_deadlines`, `interets_1619`). Si le connecteur requis échoue (`401`, `404`, `429`, `[CLEF_ABSENTE]`, `[CLEF_REFUSEE]`, `QUOTA_EPUISE`, hors ligne) sans repli local prévu par la compétence, **s'arrêter sur le volet touché**, nommer le connecteur et demander à l'avocat de rétablir l'accès (`acces.poirierlavoie.ca/moi`) ou de fournir le texte officiel.
3. **Étanchéité bijuridique :** Écarter tout droit étranger (`.fr`, Belgique, Suisse; art. 1240, 2224, 1641) et purger les calques de common law (*duty of care*, *consideration*, *estoppel*, dommages punitifs sans loi habilitante sous l'art. 1621 C.c.Q.). En anglais, employer exclusivement la terminologie officielle anglaise du C.c.Q. et du C.p.c. (`get_article(lang="en")`, `terminologie_lookup`).
4. **Protection et déclencheurs déontologiques :** Présumer tout document non coté `CONFIDENTIEL` (jamais `PUBLIC` par défaut). Signaler au texte via `lois` (`b-1-r.3.1`, `b-1-r.5`, `cpc` art. 108, 192–194) une obligation déontologique ou de caviardage uniquement devant un fait déclencheur concret, sans mise en garde générique.
5. **Perception et précédents :** Ne jamais décrire un média, une image ou un document non effectivement perçu dans la session (sinon demander une transcription ou un extrait visuel et marquer l'analyse « support secondaire »). Un précédent interne n'est utilisé que s'il est fourni par l'avocat, dé-identifié, sans jamais importer un fait, un nom ni une pièce de l'autre dossier.
<!-- SAFETY-KERNEL:END -->

## Entrées requises

* Identité du client potentiel, de la partie adverse, des tiers liés et confirmation de l'absence de conflit d'intérêts (sinon bloquer avant tout examen au fond);
* Exposé initial des faits, objectif visé et pièces remises;
* Dates connues des événements clés et de toute mise en demeure ou procédure déjà reçue (sinon `[DATE À CONFIRMER]`);
* Précédents internes fournis explicitement par l'avocat le cas échéant.

## État de la phase

* **Emplacement :** `etat-dossier/phase-ouverture-dossier.md` dans le répertoire du dossier lorsque le disque est inscriptible (Claude Code, Antigravity, Gemini CLI). **Dégradation gracieuse (`claude.ai`, Gemini App `/mcp/oauth`, Deep Research) :** si `etat-dossier/` n'est pas inscriptible, livrer directement un **bloc d'état Markdown en ligne** complet à copier-sauvegarder sans prétendre avoir écrit de fichier.
* **En-tête :** `phase: phase-ouverture-dossier` · `branche` · `date` · `palier` · `dernière mise à jour`.
* **Corps :** tableau `| Étape | Statut (À faire / En cours / Franchie / Bloquée) | Livrable | Porte | Notes |`.
* **Règles :** relire le fichier au début de chaque tour de cette phase; ne jamais le copier hors du dossier; étiqueter tout fait `Établi`, `Rapporté`, `Déduit` ou `[À CONFIRMER]`.

## Parcours

### Étape 1 — Contrôle de conflit et compétence du cabinet
* **Objectif :** Dégager tout conflit d'intérêts et vérifier disponibilité/compétence avant de recevoir des confidences ou de donner un avis de fond.
* **Livrable :** Vérification des critères de conflit (jamais attestée comme accomplie sans preuve).
* **Porte :** **BLOQUANTE** — aucun avis substantiel ni analyse détaillée des pièces tant que l'avocat n'a pas confirmé l'absence de conflit.

### Étape 2 — Identification, mandat et portée financière
* **Objectif :** Recueillir les données d'identification, qualifier la vérification d'identité si mouvement de fonds, et fixer l'étendue du mandat/honoraires.
* **Livrable :** Fiche d'ouverture et projet de lettre de mandat.
* **Porte :** Identification complète réunie et modalités financières approuvées par l'avocat.

### Étape 3 — Réception, journal de garde et tri initial des pièces
* **Objectif :** Inspecter techniquement les fichiers bruts, ouvrir le journal de garde et dresser la chronologie provisoire.
* **Livrable :** Tableau de tri, journal de garde et chronologie provisoire avec `[TROU]`.
* **Porte :** Chaque pièce remise inventoriée et classée selon son niveau de confidentialité.

### Étape 4 — Triage d'urgence (prescription, déchéance, avis préalable, péril)
* **Objectif :** Repérer immédiatement toute échéance fatale ou besoin de mesure conservatoire urgente.
* **Livrable :** Grille des préalables et alerte de délais.
* **Porte :** **BLOQUANTE sur urgence** — si une prescription, déchéance ou mesure provisoire presse, basculer immédiatement vers la branche urgence de la phase suivante.

### Étape 5 — Recherche juridique préliminaire (et précédents internes)
* **Objectif :** Vérifier les textes applicables, arrêts clés et leçons tirées de précédents dé-identifiés fournis.
* **Livrable :** Fiche de recherche avec Registre des sources.
* **Porte :** Sources primaires vérifiées via `lois` et `juris`.

### Étape 6 — Note stratégique / opinion d'ouverture au client
* **Objectif :** Synthétiser options, risques, coûts et attaque adverse la plus forte.
* **Livrable :** Note d'analyse interne et projet de lettre au client.
* **Porte :** Décision du client consignée (règlement, mise en demeure ou recours).

### Étape 7 — Décision de suite (mise en demeure ou introduction)
* **Objectif :** Rédiger et contrôler la mise en demeure s'il y a lieu ou préparer le passage à l'introduction.
* **Livrable :** Mise en demeure vérifiée ou dossier prêt pour l'introduction.
* **Porte :** Envoi confirmé ou transition consignée au fichier d'état.

## Enchaînements

| Étape | Type | Cible | Feuille | Palier | Condition |
|---|---|---|---|---|---|
| 1 | référence | gestion-du-mandat | conformite-ouverture-conflits-mandat | — | toujours avant l'étape 2 |
| 2 | livrable | gestion-du-mandat | conformite-ouverture-conflits-mandat | 2 | après Étape 1 franchie |
| 2 | livrable | redaction-juridique | corr-client | 2 | si lettre de mandat requise |
| 3 | livrable | analyse-et-strategie | piece-reception-et-qualification | 2 | après Étape 1 franchie |
| 3 | référence | analyse-et-strategie | preuve-directe | — | si pièce numérique brute ou média reçu (journal de garde) |
| 3 | livrable | analyse-et-strategie | produit-chronologie | 2 | si pièces datées fournies |
| 4 | référence | recherche-juridique | grille-prealables | — | toujours |
| 4 | livrable | gestion-du-mandat | conformite-echeanciers-cpc | 2 | si délai ou préavis repéré |
| 5 | livrable | recherche-juridique | recherche-legislative | 2 | après Étape 4 franchie |
| 5 | livrable | recherche-juridique | recherche-jurisprudentielle | 2 | si jurisprudence requise |
| 5 | référence | recherche-juridique | recherche-precedents-internes | — | si précédent fourni par l'avocat |
| 6 | livrable | analyse-et-strategie | produit-note-et-memo | 2 | après Étape 5 franchie |
| 6 | livrable | redaction-juridique | corr-client | 2 | sur demande d'avis écrit |
| 7 | livrable | redaction-juridique | corr-mise-en-demeure | 3 | si mise en demeure décidée |
| 7 | livrable | production-et-conformite | controle-correspondance | 2 | avant envoi externe |

## Branches

* **Consultation exploratoire sans mandat :** s'arrêter à l'Étape 4/6 après avis initial et consigner la non-ouverture le cas échéant.
* **Urgence immédiate (prescription imminente, injonction, saisie) :** dès la Porte 4, clôturer l'ouverture minimale et passer à l'introduction en mode urgence.

## Contrôle de sortie de phase

1. Conflit dégagé, mandat/portée clarifiés et `etat-dossier/phase-ouverture-dossier.md` mis à jour *(ou bloc d'état en ligne livré si disque non inscriptible)*.
2. Prescription, avis préalables et compétence contrôlés.
3. **Suite suggérée (texte brut) :** passer à `phase-introduction-reponse` (ou à la clôture si consultation unique sans mandat).
